"""Vercel serverless entrypoint.

Vercel's Python runtime serves the ASGI `app` exported here. The FastAPI
application itself lives in ../backend (a flat module layout: main.py does
`from db import ...`, `from routes import ...`), so put backend/ on sys.path
before importing it. backend/main.py also inserts its own directory, which
keeps its internal imports working unchanged — locally, in Docker, and here.
"""

import os
import sys

_BACKEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"
)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from main import app  # noqa: E402

__all__ = ["app"]
