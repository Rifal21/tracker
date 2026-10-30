from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import SearchHistory
from ..schemas import HistoryItem, HistoryStats
from ..security import protected

router = APIRouter(prefix="/api/v1/history", tags=["history"], dependencies=protected)


def _purge_old(db: Session):
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.history_retention_days)
    db.query(SearchHistory).filter(SearchHistory.created_at < cutoff).delete()
    db.commit()


@router.get("", response_model=list[HistoryItem])
def list_history(start: date | None = None, end: date | None = None, limit: int = 200,
                 db: Session = Depends(get_db)):
    _purge_old(db)
    q = db.query(SearchHistory)
    if start:
        q = q.filter(SearchHistory.created_at >= datetime.combine(start, time.min, timezone.utc))
    if end:
        q = q.filter(SearchHistory.created_at <= datetime.combine(end, time.max, timezone.utc))
    return q.order_by(SearchHistory.created_at.desc()).limit(min(limit, 1000)).all()


@router.get("/stats", response_model=HistoryStats)
def stats(db: Session = Depends(get_db)):
    rows = db.query(SearchHistory).order_by(SearchHistory.created_at.desc()).all()
    per_day: dict[str, int] = {}
    for r in rows:
        d = r.created_at.date().isoformat()
        per_day[d] = per_day.get(d, 0) + 1
    valid = sum(r.is_valid for r in rows)
    return HistoryStats(total=len(rows), valid=valid, invalid=len(rows) - valid,
                        per_day=dict(sorted(per_day.items())), recent=rows[:10])


@router.delete("/{history_id}")
def delete_one(history_id: int, db: Session = Depends(get_db)):
    row = db.get(SearchHistory, history_id)
    if not row:
        raise HTTPException(404, "Tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"deleted": history_id}


@router.delete("")
def delete_all(db: Session = Depends(get_db)):
    n = db.query(SearchHistory).delete()
    db.commit()
    return {"deleted": n}
