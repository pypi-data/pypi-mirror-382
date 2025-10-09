"""teilen flask-backend configuration."""

import os
from pathlib import Path
from uuid import uuid4


# pylint: disable=R0903:too-few-public-methods
class AppConfig:
    """teilen-backend configuration."""

    MODE = os.environ.get("MODE", "prod")  # "prod" | "dev"
    DEV_CORS_FRONTEND_URL = os.environ.get(
        "DEV_CORS_FRONTEND_URL", "http://localhost:3000"
    )
    PORT = os.environ.get("PORT", "27183" if MODE == "prod" else "5000")
    FLASK_THREADS = 5
    GUNICORN_OPTIONS = None

    STATIC_PATH = Path(__file__).parent / "client"
    SESSION_COOKIE_NAME = "teilen_session"
    SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid4()))
    WORKING_DIR = Path(os.environ.get("WORKING_DIR", Path.cwd())).resolve()
    PASSWORD = os.environ.get("PASSWORD")
    ARCHIVE_BUILD_CONCURRENCY = int(
        os.environ.get("ARCHIVE_BUILD_CONCURRENCY", 3)
    )
