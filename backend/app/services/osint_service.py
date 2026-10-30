"""OSINT berbasis sumber publik.

Hanya membangun tautan pencarian ke sumber publik yang sah dan (opsional) memeriksa
ketersediaannya. Tidak ada bypass autentikasi atau scraping data privat.
"""
from datetime import datetime, timezone
from urllib.parse import quote_plus

import httpx

from ..schemas import OsintSource, PhoneInfo

# (nama, template URL, deskripsi) — {q} = query ter-encode
SOURCES = [
    ("DuckDuckGo", "https://duckduckgo.com/?q={q}", "Pencarian web publik untuk nomor (format internasional)."),
    ("Bing", "https://www.bing.com/search?q={q}", "Pencarian web publik alternatif."),
    ("Google", "https://www.google.com/search?q={q}", "Pencarian web publik."),
    ("Who Called Me (spam report)", "https://www.google.com/search?q={q}+spam+OR+scam+OR+penipuan",
     "Pencarian laporan spam/penipuan dari halaman publik."),
]


def build_sources(info: PhoneInfo, check: bool = False) -> list[OsintSource]:
    now = datetime.now(timezone.utc)
    queries = [info.phone_number, info.national or ""]
    q = quote_plus(f'"{info.phone_number}"')
    out = [
        OsintSource(source_name=n, source_url=u.format(q=q), description=d, checked_at=now)
        for n, u, d in SOURCES
    ]
    if info.prefix:
        pq = quote_plus(f"prefix {info.prefix} operator {info.country or ''}")
        out.append(OsintSource(
            source_name="Info prefix", source_url=f"https://duckduckgo.com/?q={pq}",
            description="Informasi publik mengenai prefix/operator.", checked_at=now))
    if check:
        with httpx.Client(timeout=5, follow_redirects=True) as c:
            for s in out:
                try:
                    r = c.head(s.source_url)
                    s.description = f"{s.description} [HTTP {r.status_code}]"
                except httpx.HTTPError:
                    s.description = f"{s.description} [tidak dapat dijangkau]"
                s.checked_at = datetime.now(timezone.utc)
    return out
