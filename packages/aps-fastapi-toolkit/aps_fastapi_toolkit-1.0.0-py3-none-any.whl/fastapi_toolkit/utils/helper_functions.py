from datetime import datetime, timezone


def current_time_utc() -> datetime:
    """
    Get the current UTC time.
    """
    return datetime.now(timezone.utc)
