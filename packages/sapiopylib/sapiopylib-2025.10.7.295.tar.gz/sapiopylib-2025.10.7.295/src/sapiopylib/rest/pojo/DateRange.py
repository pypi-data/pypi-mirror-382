import datetime
from functools import total_ordering
from typing import Optional, List


@total_ordering
class DateRange:
    """
    This represents values of a date range field.
    """
    start_time: int
    end_time: int

    def __init__(self, start_time: int, end_time: int):
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return str(self.start_time) + "/" + str(self.end_time)

    def __hash__(self):
        return hash((self.start_time, self.end_time))

    def __eq__(self, other):
        if not isinstance(other, DateRange):
            return False
        return self.start_time == other.start_time and self.end_time == other.end_time

    def __le__(self, other):
        if self.__eq__(other):
            return True
        if not isinstance(other, DateRange):
            return False
        if self.start_time < other.start_time:
            return True
        return self.end_time < other.end_time

    def get_start_datetime(self) -> datetime.datetime:
        """
        Get the start date in Python datetime class.
        """
        from sapiopylib.rest.utils.SapioDateUtils import java_millis_to_datetime
        return java_millis_to_datetime(self.start_time)

    def get_end_datetime(self) -> datetime.datetime:
        """
        Get the end date in Python datetime class.
        """
        from sapiopylib.rest.utils.SapioDateUtils import java_millis_to_datetime
        return java_millis_to_datetime(self.end_time)

    @staticmethod
    def from_str(text: Optional[str]):
        """
        Create a DateRange object from its string representation.
        """
        if not text:
            return None
        splits: List[str] = text.split('/')
        return DateRange(int(splits[0]), int(splits[1]))

    @staticmethod
    def from_date_time(start_datetime: datetime.datetime, end_datetime: datetime.datetime):
        """
        Create a DateRange object from its Python datetime representation.
        """
        from sapiopylib.rest.utils.SapioDateUtils import date_time_to_java_millis
        return DateRange(date_time_to_java_millis(start_datetime), date_time_to_java_millis(end_datetime))