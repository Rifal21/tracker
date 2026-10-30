from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import OsintResult, SearchHistory
from ..schemas import OsintResponse, PhoneRequest
from ..security import protected
from ..services import osint_service, phone_service

router = APIRouter(prefix="/api/v1/osint", tags=["osint"], dependencies=protected)


@router.post("/search", response_model=OsintResponse)
def search(req: PhoneRequest, check: bool = False, db: Session = Depends(get_db)):
    info = phone_service.analyze(req.phone_number, req.default_region)
    if info.error:
        raise HTTPException(422, info.error)
    hist = SearchHistory(
        phone_number=info.phone_number, country_code=info.country_code, is_valid=info.valid,
        number_type=info.number_type, carrier=info.carrier, country=info.country, search_source="osint")
    db.add(hist)
    db.flush()
    sources = osint_service.build_sources(info, check=check)
    for s in sources:
        db.add(OsintResult(search_history_id=hist.id, **s.model_dump()))
    db.commit()
    return OsintResponse(phone_number=info.phone_number, history_id=hist.id, sources=sources)
