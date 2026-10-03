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
