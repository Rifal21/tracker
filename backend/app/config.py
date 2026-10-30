import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


class Settings:
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'data' / 'fkphone.db'}")
    api_key: str = os.getenv("API_KEY", "")
    default_region: str = os.getenv("DEFAULT_REGION", "ID")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    history_retention_days: int = int(os.getenv("HISTORY_RETENTION_DAYS", "90"))
    location_max_ttl_minutes: int = int(os.getenv("LOCATION_MAX_TTL_MINUTES", "1440"))
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")


settings = Settings()
