from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SearchHistory
from ..schemas import PhoneInfo, PhoneRequest
from ..security import protected
from ..services import phone_service

router = APIRouter(prefix="/api/v1/phone", tags=["phone"], dependencies=protected)


@router.post("/lookup", response_model=PhoneInfo)
def lookup(req: PhoneRequest, db: Session = Depends(get_db)):
    info = phone_service.analyze(req.phone_number, req.default_region)
    db.add(SearchHistory(
        phone_number=info.phone_number, country_code=info.country_code, is_valid=info.valid,
        number_type=info.number_type, carrier=info.carrier, country=info.country, search_source="lookup"))
    db.commit()
    return info


@router.post("/validate")
def validate(req: PhoneRequest):
    info = phone_service.analyze(req.phone_number, req.default_region)
    return {"phone_number": info.phone_number, "valid": info.valid, "possible": info.possible,
            "e164": info.phone_number if info.valid else None, "number_type": info.number_type,
            "is_mobile": info.number_type in ("MOBILE", "FIXED_LINE_OR_MOBILE"),
            "is_fixed_line": info.number_type in ("FIXED_LINE", "FIXED_LINE_OR_MOBILE"),
            "is_voip": info.number_type == "VOIP", "error": info.error}
