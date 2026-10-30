from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import ROOT, settings


def _resolve_url(url: str) -> str:
    parsed = make_url(url)
    if parsed.get_backend_name() == "sqlite" and parsed.database not in (None, "", ":memory:"):
        path = ROOT / parsed.database
        path.parent.mkdir(parents=True, exist_ok=True)
        parsed = parsed.set(database=str(path))
    return parsed.render_as_string(hide_password=False)


_url = _resolve_url(settings.database_url)
_args = {"check_same_thread": False} if _url.startswith("sqlite") else {}
engine = create_engine(_url, connect_args=_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models  # noqa: F401

    Base.metadata.create_all(engine)
