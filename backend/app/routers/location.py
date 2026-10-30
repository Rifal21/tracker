from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..schemas import ShareCreate, ShareCreated, ShareStatus, SubmitLocation, TokenOnly
from ..security import protected, public
from ..services import location_service as svc

router = APIRouter(tags=["location"])
PAGE = Path(__file__).resolve().parents[1] / "static" / "share.html"


@router.post("/api/v1/location/share", response_model=ShareCreated, dependencies=protected)
def create(req: ShareCreate, db: Session = Depends(get_db)):
    token, share = svc.create_share(db, req.ttl_minutes)
    return ShareCreated(token=token, share_url=f"{settings.public_base_url}/share/{token}",
                        expires_at=share.expires_at)


@router.post("/api/v1/location/submit", dependencies=public)
def submit(req: SubmitLocation, db: Session = Depends(get_db)):
    """Dipanggil dari halaman persetujuan milik pemilik lokasi (token = otorisasi)."""
    if not req.consent:
        raise HTTPException(400, "Persetujuan eksplisit diperlukan")
    share = svc.get_share(db, req.token)
    if not share:
        raise HTTPException(404, "Token tidak dikenal")
    st = svc.status_of(share)
    if st in ("revoked", "expired"):
        raise HTTPException(410, f"Tautan {st}")
    svc.submit(db, share, req.latitude, req.longitude)
    return {"status": "active"}


@router.post("/api/v1/location/revoke", dependencies=public)
def revoke(req: TokenOnly, db: Session = Depends(get_db)):
    share = svc.get_share(db, req.token)
    if not share:
        raise HTTPException(404, "Token tidak dikenal")
    svc.revoke(db, share)
    return {"status": "revoked"}


@router.post("/api/v1/location/view", response_model=ShareStatus, dependencies=protected)
def view(req: TokenOnly, db: Session = Depends(get_db)):
    share = svc.get_share(db, req.token)
    if not share:
        raise HTTPException(404, "Token tidak dikenal")
    st = svc.status_of(share)
    live = st == "active"
    return ShareStatus(status=st, expires_at=share.expires_at, consent_at=share.consent_at,
                       latitude=share.latitude if live else None, longitude=share.longitude if live else None)


@router.get("/share/{token}", include_in_schema=False, dependencies=public)
def page(token: str):
    return FileResponse(PAGE, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
