import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["API_KEY"] = "testkey"
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import database  # noqa: E402
from app.main import app  # noqa: E402
from app.services.phone_service import mask  # noqa: E402

H = {"X-API-Key": "testkey"}


@pytest.fixture(scope="module")
def client():
    database.engine.dispose()
    from sqlalchemy import create_engine
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    database.SessionLocal.configure(bind=eng)
    database.Base.metadata.create_all(eng)
    from app import models  # noqa: F401
    with TestClient(app) as c:
        yield c


def test_mask():
    assert mask("+6281234567890") == "+628********90"


def test_auth_required(client):
    assert client.post("/api/v1/phone/lookup", json={"phone_number": "+6281234567890"}).status_code == 401


def test_lookup_valid(client):
    r = client.post("/api/v1/phone/lookup", json={"phone_number": "+6281234567890"}, headers=H).json()
    assert r["valid"] and r["country_code"] == "ID" and r["number_type"] == "MOBILE"


def test_lookup_local_format(client):
    r = client.post("/api/v1/phone/lookup", json={"phone_number": "081234567890"}, headers=H).json()
    assert r["phone_number"] == "+6281234567890"


def test_invalid(client):
    r = client.post("/api/v1/phone/validate", json={"phone_number": "+62123"}, headers=H).json()
    assert not r["valid"]


def test_history_and_delete(client):
    items = client.get("/api/v1/history", headers=H).json()
    assert len(items) >= 3
    assert client.delete(f"/api/v1/history/{items[0]['id']}", headers=H).status_code == 200
    s = client.get("/api/v1/history/stats", headers=H).json()
    assert s["total"] == s["valid"] + s["invalid"]


def test_osint(client):
    r = client.post("/api/v1/osint/search", json={"phone_number": "+6281234567890"}, headers=H).json()
    assert len(r["sources"]) >= 4


def test_location_flow(client):
    s = client.post("/api/v1/location/share", json={"ttl_minutes": 5}, headers=H).json()
    tok = s["token"]
    body = {"token": tok, "latitude": -6.2, "longitude": 106.8}
    assert client.post("/api/v1/location/submit", json={**body, "consent": False}).status_code == 400
    assert client.post("/api/v1/location/submit", json={**body, "consent": True}).status_code == 200
    v = client.post("/api/v1/location/view", json={"token": tok}, headers=H).json()
    assert v["status"] == "active" and v["latitude"] == -6.2
    assert client.post("/api/v1/location/revoke", json={"token": tok}).status_code == 200
    v = client.post("/api/v1/location/view", json={"token": tok}, headers=H).json()
    assert v["status"] == "revoked" and v["latitude"] is None
    assert client.post("/api/v1/location/submit", json={**body, "consent": True}).status_code == 410
