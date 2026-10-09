"""AI Mock Interviewer API.

Run:  uvicorn main:app --reload --port 8000
"""

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import Base, engine  # noqa: E402
from routes import execute, sessions  # noqa: E402

app = FastAPI(title="AI Mock Interviewer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(execute.router)


@app.on_event("startup")
def _create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Production single-container deploy: serve the built React frontend.
# When frontend/dist exists (it does inside the Docker image), FastAPI serves
# the SPA from the same origin as the API, so the frontend's relative /api
# calls just work. In local dev the dist folder is absent (Vite serves the
# frontend on :5173 and proxies /api here), so this block is skipped and
# nothing changes. Registered last so real API routes always win.
# ---------------------------------------------------------------------------
_FRONTEND_DIST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "frontend", "dist"
)
if os.path.isdir(_FRONTEND_DIST):
    from fastapi import HTTPException  # noqa: E402
    from fastapi.responses import FileResponse  # noqa: E402
    from fastapi.staticfiles import StaticFiles  # noqa: E402

    _DIST_ROOT = os.path.realpath(_FRONTEND_DIST)
    _ASSETS_DIR = os.path.join(_FRONTEND_DIST, "assets")
    if os.path.isdir(_ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=_ASSETS_DIR), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def _spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = os.path.realpath(os.path.join(_FRONTEND_DIST, full_path))
        if full_path and candidate.startswith(_DIST_ROOT) and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))
