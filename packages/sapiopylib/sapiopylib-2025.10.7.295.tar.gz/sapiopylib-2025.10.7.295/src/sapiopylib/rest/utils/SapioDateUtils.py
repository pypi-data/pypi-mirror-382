from datetime import datetime
from typing import Optional


def java_millis_to_datetime(java_time_millis: Optional[int]) -> Optional[datetime]:
    """
    Convert from Java Time Millis to Python Date Time.
    :param java_time_millis:
    :return:
    """
    if java_time_millis is None:
        return None
    return datetime.fromtimestamp(java_time_millis / 1000.0)


def date_time_to_java_millis(time: Optional[datetime]) -> Optional[int]:
    """
    Convert from Python date time to Java/SQL milliseconds format.
    :param time: The Python date time, or None.
    """
    if time is None:
        return None
    return int(time.timestamp() * 1000.0)
