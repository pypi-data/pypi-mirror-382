import os
from pathlib import Path
from setuptools import setup


try:
    long_description = (Path(__file__).parent.parent / "README.md").read_text(
        encoding="utf8"
    )
except FileNotFoundError:
    long_description = "See docs at https://github.com/RichtersFinger/teilen"


setup(
    version=os.environ.get("VERSION", "0.5.0"),
    name="teilen",
    description="a simple application to share data via http with python flask backend and react frontend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Steffen Richters-Finger",
    author_email="srichters@uni-muenster.de",
    license="MIT",
    url="https://pypi.org/project/teilen/",
    project_urls={"Source": "https://github.com/RichtersFinger/python-teilen"},
    python_requires=">=3.10",
    install_requires=[
        "Flask>=3,<4",
        "gunicorn",
    ],
    packages=[
        "teilen",
    ],
    package_data={"teilen": ["client/**/*"]},
    entry_points={
        "console_scripts": [
            "teilen = teilen.app:run",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications",
        "Topic :: Communications :: File Sharing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
    ],
)
