import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..config import settings
from ..models import LocationShare, utcnow


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _aware(dt: datetime | None) -> datetime | None:
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def create_share(db: Session, ttl_minutes: int) -> tuple[str, LocationShare]:
    ttl = min(ttl_minutes, settings.location_max_ttl_minutes)
    token = secrets.token_urlsafe(32)
    share = LocationShare(share_token_hash=hash_token(token), expires_at=utcnow() + timedelta(minutes=ttl))
    db.add(share)
    db.commit()
    return token, share


def get_share(db: Session, token: str) -> LocationShare | None:
    return db.query(LocationShare).filter_by(share_token_hash=hash_token(token)).first()


def status_of(share: LocationShare) -> str:
    if share.revoked_at:
        return "revoked"
    if _aware(share.expires_at) <= utcnow():
        return "expired"
    return "active" if share.consent_at else "pending"


def submit(db: Session, share: LocationShare, lat: float, lon: float) -> None:
    share.latitude, share.longitude, share.consent_at = lat, lon, utcnow()
    db.commit()


def revoke(db: Session, share: LocationShare) -> None:
    """Cabut persetujuan: koordinat dihapus, tidak disimpan."""
    share.revoked_at = utcnow()
    share.latitude = share.longitude = None
    db.commit()


def purge_expired(db: Session) -> int:
    now = utcnow()
    rows = db.query(LocationShare).filter(LocationShare.expires_at <= now, LocationShare.latitude.isnot(None)).all()
    for r in rows:
        r.latitude = r.longitude = None
    db.commit()
    return len(rows)
