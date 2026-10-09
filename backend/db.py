"""Database engine / session factory.

DATABASE_URL env var selects the backend; defaults to a local SQLite file
so the app runs with zero setup. SQLite needs check_same_thread=False
because FastAPI may serve requests from multiple threads.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Some hosted providers still hand out the legacy postgres:// scheme, which
# SQLAlchemy 2 rejects — normalize it so those URLs work as-is.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]

# Pin the psycopg2 driver explicitly. A bare postgresql:// URL silently
# changed meaning in SQLAlchemy 2.1: its default dialect became psycopg (v3),
# whose package we do not install (requirements carry psycopg2-binary), so
# create_engine() died at import with "No module named 'psycopg'" — taking
# the whole app down on Vercel, where DATABASE_URL points at Postgres.
# Locally this stayed hidden because an unset DATABASE_URL means SQLite.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg2://" + DATABASE_URL[len("postgresql://"):]

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
