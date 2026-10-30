import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import SessionLocal, init_db
from .routers import history, location, lookup, osint
from .services.location_service import purge_expired

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        purge_expired(db)
    yield


app = FastAPI(title="FKPhone Tracker", version="1.0.0", lifespan=lifespan)
for r in (lookup.router, osint.router, history.router, location.router):
    app.include_router(r)


@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}
