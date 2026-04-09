import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()


@lru_cache(maxsize=1)
def _engine():
    return create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)


@lru_cache(maxsize=1)
def _factory():
    return sessionmaker(bind=_engine())


def SessionLocal() -> Session:
    """Open a new DB session (used in background tasks that outlive the request)."""
    return _factory()()


def get_db():
    db = _factory()()
    try:
        yield db
    finally:
        db.close()


DB = Annotated[Session, Depends(get_db)]
