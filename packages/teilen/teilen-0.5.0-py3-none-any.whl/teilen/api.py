"""teilen api-definition"""

from typing import Optional
from functools import wraps
from pathlib import Path
from urllib.parse import unquote
from datetime import datetime
from tempfile import mkdtemp
import zipfile
from uuid import uuid4
import multiprocessing
from shutil import rmtree
import atexit

from flask import (
    Flask,
    Response,
    jsonify,
    request,
    session,
    send_file,
    send_from_directory,
)

from teilen.config import AppConfig


def login_required(password: Optional[str]):
    """
    Protect endpoint with auth via 'teilen_session'-cookie or
    'X-Teilen-Auth'-header.
    """

    def decorator(route):
        @wraps(route)
        def __():
            if (
                session.get("password", request.headers.get("X-Teilen-Auth"))
                != password
            ):
                return Response("FAILED", mimetype="text/plain", status=401)
            return route()

        return __

    return decorator


def create_archive(
    id_: str,
    source: Path,
    tmp_dir: Path,
    progress,  # multiprocessing.managers.SyncManager.dict
):
    """
    Builds an archive from the data in `source` in
    `tmp_dir/id_/(source.name + ".zip")`. Progress updates are written
    to synced dict `progress`.
    """
    progress["status"] = "running"
    working_dir: Path = tmp_dir / id_
    working_dir.mkdir()
    destination: Path = working_dir / (source.name + ".zip")
    print(
        f"[{datetime.now().isoformat()} - {id_}] Creating archive for "
        + f"'{source}' in '{destination}'."
    )

    # create archive
    files = list(filter(Path.is_file, source.glob("**/*")))
    progress["totalFiles"] = len(files)
    progress["processedFiles"] = 0
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_STORED) as archive:
        for f in files:
            progress["currentFile"] = str(
                f.resolve().relative_to(source.parent.resolve())
            )
            archive.write(
                f,
                f.resolve().relative_to(source.parent.resolve()),
            )
            progress["archiveSize"] = destination.stat().st_size
            progress["processedFiles"] += 1

    progress["currentFile"] = None
    # finalize
    print(
        f"[{datetime.now().isoformat()} - {id_}] Building archive successful."
    )
    progress["artifact"] = destination.name
    progress["status"] = "completed"


def silentfail(callback):
    """
    Returns a callable that run the given callback while silently
    capturing all exceptions.
    """

    def _(*args, **kwargs):
        try:
            callback(*args, **kwargs)
        # pylint: disable=broad-exception-caught
        except Exception:
            pass

    return _


def register_api(app: Flask, config: AppConfig):
    """Sets up api endpoints."""

    archive_store = {}
    mp_manager = multiprocessing.Manager()  # inter-process communication
    # use silentfail to avoid errors due to gunicorn master + workers
    # running this function
    atexit.register(silentfail(mp_manager.shutdown))

    tmp_dir = Path(mkdtemp(prefix="teilen-")).resolve()
    # use silentfail to avoid errors due to gunicorn master + workers
    # running this function
    atexit.register(silentfail(rmtree), tmp_dir)

    @app.route("/configuration", methods=["GET"])
    def get_configuration():
        """
        Get basic info on configuration.
        """
        return jsonify({"passwordRequired": config.PASSWORD is not None}), 200

    @app.route("/login", methods=["GET"])
    @login_required(config.PASSWORD)
    def get_login():
        """Test login."""
        session["password"] = config.PASSWORD
        return Response("OK", mimetype="text/plain", status=200)

    def get_location(provide_default: bool = True) -> Optional[Path]:
        """Parse and return location-arg."""
        if request.args.get("location") is None:
            if provide_default:
                return config.WORKING_DIR
            return None
        return (
            config.WORKING_DIR / unquote(request.args["location"])
        ).resolve()

    @app.route("/contents", methods=["GET"])
    @login_required(config.PASSWORD)
    def get_contents():
        """
        Returns contents for given location.
        """
        _location = get_location()

        # check for problems
        if (
            config.WORKING_DIR != _location
            and config.WORKING_DIR not in _location.parents
        ):
            return Response("Not allowed.", mimetype="text/plain", status=403)
        if not _location.is_dir():
            return Response(
                "Does not exist.", mimetype="text/plain", status=404
            )

        contents = list(_location.glob("*"))
        folders = filter(lambda p: p.is_dir(), contents)
        files = filter(lambda p: p.is_file(), contents)
        return (
            jsonify(
                [
                    {
                        "type": "folder",
                        "name": f.name,
                        "mtime": f.stat().st_mtime,
                    }
                    for f in folders
                ]
                + [
                    {
                        "type": "file",
                        "name": f.name,
                        "mtime": f.stat().st_mtime,
                        "size": f.stat().st_size,
                    }
                    for f in files
                ]
            ),
            200,
        )

    @app.route("/content", methods=["GET"])
    @login_required(config.PASSWORD)
    def get_content():
        """
        Returns file for given location or an id for an archive-job.
        """
        _location = get_location(False)
        # if forStatus, client only wants to validate request
        for_status = request.args.get("forStatus") is not None

        if _location is None:
            return Response(
                "Missing 'location' arg.", mimetype="text/plain", status=400
            )

        # check for problems
        if config.WORKING_DIR not in _location.parents:
            return Response("Not allowed.", mimetype="text/plain", status=403)
        if not _location.exists():
            return Response(
                "Does not exist.", mimetype="text/plain", status=404
            )

        if _location.is_file():
            if for_status:
                return Response("OK", mimetype="text/plain", status=200)
            return send_from_directory(
                config.WORKING_DIR,
                _location.relative_to(config.WORKING_DIR),
                as_attachment=True,
            )

        # create asynchronous job to build archive
        if _location.is_dir():
            # check already running jobs
            n_jobs = 0
            for job in archive_store.values():
                if "process" in job and job["process"].is_alive():
                    n_jobs += 1
            if n_jobs > config.ARCHIVE_BUILD_CONCURRENCY:
                return Response("BUSY", mimetype="text/plain", status=503)

            # run job
            # no threading-lock needed here because of uuids
            job_id = str(uuid4())
            progress = mp_manager.dict(
                {
                    "status": "queued",
                }
            )
            archive_store[job_id] = {
                "id": job_id,
                "progress": progress,
                "process": multiprocessing.Process(
                    target=create_archive,
                    args=(
                        job_id,
                        _location.resolve(),
                        tmp_dir,
                        progress,
                    ),
                    daemon=True,
                ),
            }
            archive_store[job_id]["process"].start()

            return jsonify({"id": job_id}), 202

        return Response("Unkown type.", mimetype="text/plain", status=501)

    @app.route("/archive-progress", methods=["GET"])
    @login_required(config.PASSWORD)
    def get_archive_progress():
        """Returns progress of an archive-job if available."""
        job_id = request.args.get("id")

        # validate etc.
        if job_id is None:
            return Response("MISSING ID", mimetype="text/plain", status=400)

        if job_id not in archive_store:
            return Response("UNKNOWN ID", mimetype="text/plain", status=404)

        return (
            jsonify(
                dict(
                    # this converts from DictProxy to regular dict
                    archive_store[job_id].get(
                        "progress", {"status": "unknown"}
                    )
                )
            ),
            200,
        )

    @app.route("/archive", methods=["GET"])
    @login_required(config.PASSWORD)
    def get_archive():
        """Returns result of an archive-job if ready."""
        job_id = request.args.get("id")
        # if forStatus, client only wants to validate request
        for_status = request.args.get("forStatus") is not None

        # validate etc.
        if job_id is None:
            return Response("MISSING ID", mimetype="text/plain", status=400)

        if job_id not in archive_store:
            return Response("UNKNOWN ID", mimetype="text/plain", status=404)

        if (
            archive_store[job_id]["process"].is_alive()
            or archive_store[job_id]["progress"]["status"] != "completed"
        ):
            return Response("NOT YET", mimetype="text/plain", status=202)

        archive = (
            tmp_dir / job_id / archive_store[job_id]["progress"]["artifact"]
        )

        if not archive.is_file():
            return Response(
                "FILE NOT FOUND", mimetype="text/plain", status=404
            )

        # return result
        if for_status:
            return Response("OK", mimetype="text/plain", status=200)
        return send_file(archive, as_attachment=True)

    @app.route("/archive", methods=["DELETE"])
    @login_required(config.PASSWORD)
    def delete_archive():
        """Clean up created archive or abort creation."""
        job_id = request.args.get("id")

        # validate etc.
        if job_id is None:
            return Response("MISSING ID", mimetype="text/plain", status=400)

        if job_id not in archive_store:
            return Response("UNKNOWN ID", mimetype="text/plain", status=404)

        # abort and delete artifacts
        if archive_store[job_id]["process"].is_alive():
            archive_store[job_id]["process"].kill()
            archive_store[job_id]["process"].join()

        rmtree(tmp_dir / job_id)
        return Response("DELETED", mimetype="text/plain", status=200)
