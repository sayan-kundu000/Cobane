from datetime import datetime, timezone

def get_utc_now() -> datetime:
    """Returns the current timezone-aware UTC datetime object."""
    return datetime.now(timezone.utc)

def format_iso_datetime(dt: datetime) -> str:
    """Formats a datetime object to standard ISO 8601 string representation."""
    return dt.isoformat()
