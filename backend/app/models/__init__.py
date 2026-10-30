from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SearchHistory(Base):
    __tablename__ = "search_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(32), index=True)
    country_code: Mapped[str | None] = mapped_column(String(8))
    is_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    number_type: Mapped[str | None] = mapped_column(String(32))
    carrier: Mapped[str | None] = mapped_column(String(64))
    country: Mapped[str | None] = mapped_column(String(64))
    search_source: Mapped[str] = mapped_column(String(32), default="lookup")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    osint_results: Mapped[list["OsintResult"]] = relationship(
        back_populates="search", cascade="all, delete-orphan"
    )


class OsintResult(Base):
    __tablename__ = "osint_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    search_history_id: Mapped[int] = mapped_column(ForeignKey("search_histories.id", ondelete="CASCADE"))
    source_name: Mapped[str] = mapped_column(String(64))
    source_url: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    search: Mapped[SearchHistory] = relationship(back_populates="osint_results")


class LocationShare(Base):
    __tablename__ = "location_shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    share_token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
