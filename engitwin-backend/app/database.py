import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

database_url = settings.DATABASE_URL

# Vercel's serverless filesystem is read-only except for /tmp, and /tmp is
# wiped on every cold start. If DATABASE_URL was left at its local-dev
# default (a relative sqlite file), redirect it into /tmp so the app can
# start instead of crashing with "unable to open database file".
#
# IMPORTANT: this only makes the app boot on Vercel - it does NOT give you
# persistent data. Every cold start gets a fresh empty /tmp, so signups,
# labs, attempts, etc. can vanish at any time. For real persistence, set
# DATABASE_URL in the Vercel dashboard to an external Postgres/MySQL
# instance (e.g. Neon, Supabase, Vercel Postgres) - once that's set, this
# fallback is skipped automatically.
if os.environ.get("VERCEL") and database_url.startswith("sqlite:///./"):
    database_url = "sqlite:////tmp/engitwin.db"

connect_args = {}
if database_url.startswith("sqlite"):
    # needed so SQLite works with FastAPI's threaded request handling
    connect_args = {"check_same_thread": False}

engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
