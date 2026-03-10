from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional, Tuple

from sqlalchemy import JSON, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False)


def _default_sqlite_url() -> str:
   
    return "sqlite:///./arses.db"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", _default_sqlite_url())


def init_engine():
    url = get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, connect_args=connect_args)


ENGINE = init_engine()


def init_db() -> None:
    Base.metadata.create_all(bind=ENGINE)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = Session(bind=ENGINE)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def db_info() -> Tuple[bool, Optional[str]]:
    url = get_database_url()
    enabled = bool(os.getenv("DATABASE_URL")) or url.startswith("sqlite")
    dialect = ENGINE.dialect.name if ENGINE is not None else None
    return enabled, dialect

