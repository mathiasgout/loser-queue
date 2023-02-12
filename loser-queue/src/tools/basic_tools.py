from src import logger
from src.tools.error_tools import exception

from datetime import datetime, timezone


@exception(logger)
def get_timestamp_utc() -> int:
    """Get the current timestamp utc
    Returns:
        int: utc current timestamp
    """
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    return utc_timestamp
