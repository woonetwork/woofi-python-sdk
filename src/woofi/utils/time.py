from datetime import datetime, timezone


def unix_to_iso_utc(timestamp: str | int) -> str:
    """Convert a Unix epoch (seconds) to ISO 8601 UTC string."""
    dt = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    return dt.isoformat()
