import hmac
import time
from collections import defaultdict, deque

from fastapi import Depends, Header, HTTPException, Request

from .config import settings

_hits: dict[str, deque] = defaultdict(deque)


def require_api_key(x_api_key: str | None = Header(default=None)):
    if not settings.api_key:
        raise HTTPException(503, "API_KEY belum dikonfigurasi di server")
    if not x_api_key or not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(401, "API key tidak valid")


def rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    q = _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= settings.rate_limit_per_minute:
        raise HTTPException(429, "Terlalu banyak permintaan")
    q.append(now)


protected = [Depends(rate_limit), Depends(require_api_key)]
public = [Depends(rate_limit)]
