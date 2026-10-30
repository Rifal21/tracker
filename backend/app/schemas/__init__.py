from datetime import datetime

from pydantic import BaseModel, Field


class PhoneRequest(BaseModel):
    phone_number: str = Field(min_length=3, max_length=32)
    default_region: str | None = Field(default=None, min_length=2, max_length=2)


class PhoneInfo(BaseModel):
    phone_number: str
    international: str | None = None
    national: str | None = None
    country: str | None = None
    country_code: str | None = None
    calling_code: int | None = None
    prefix: str | None = None
    valid: bool
    possible: bool
    number_type: str | None = None
    carrier: str | None = None
    carrier_note: str | None = None
    region: str | None = None
    timezones: list[str] = []
    location_note: str = (
        "Informasi geografis adalah metadata penomoran, bukan lokasi aktual perangkat atau pemilik nomor."
    )
    error: str | None = None


class OsintSource(BaseModel):
    source_name: str
    source_url: str
    description: str | None = None
    checked_at: datetime


class OsintResponse(BaseModel):
    phone_number: str
    history_id: int
    sources: list[OsintSource]


class HistoryItem(BaseModel):
    id: int
    phone_number: str
    country_code: str | None
    is_valid: bool
    number_type: str | None
    carrier: str | None
    country: str | None
    search_source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryStats(BaseModel):
    total: int
    valid: int
    invalid: int
    per_day: dict[str, int]
    recent: list[HistoryItem]


class ShareCreate(BaseModel):
    ttl_minutes: int = Field(default=60, ge=1)


class ShareCreated(BaseModel):
    token: str
    share_url: str
    expires_at: datetime


class SubmitLocation(BaseModel):
    token: str = Field(min_length=16, max_length=128)
    consent: bool
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class TokenOnly(BaseModel):
    token: str = Field(min_length=16, max_length=128)


class ShareStatus(BaseModel):
    status: str
    expires_at: datetime
    latitude: float | None = None
    longitude: float | None = None
    consent_at: datetime | None = None
