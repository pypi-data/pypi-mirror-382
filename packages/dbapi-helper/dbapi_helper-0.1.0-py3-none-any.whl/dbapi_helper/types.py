"""
DB API 2.0 type objects and constructors.

This module defines type objects and constructors specified in PEP 249
(Python Database API Specification v2.0).
"""

import datetime
from typing import Any


class DBAPITypeObject:
    """
    Type object for DB API 2.0.

    Type objects are used to describe columns in the database that are compatible
    with the given type.
    """

    def __init__(self, *values: Any) -> None:
        self.values = values

    def __eq__(self, other: Any) -> bool:
        """Check if a value is compatible with this type."""
        if isinstance(other, DBAPITypeObject):
            return self.values == other.values
        return other in self.values

    def __hash__(self) -> int:
        return hash(self.values)

    def __repr__(self) -> str:
        return f"DBAPITypeObject({', '.join(repr(v) for v in self.values)})"


# Type Objects (mandated by DB API 2.0)
STRING = DBAPITypeObject(str)
BINARY = DBAPITypeObject(bytes, bytearray, memoryview)
NUMBER = DBAPITypeObject(int, float)
DATETIME = DBAPITypeObject(datetime.datetime, datetime.date, datetime.time)
ROWID = DBAPITypeObject(int)


# Constructors (mandated by DB API 2.0)
def Date(year: int, month: int, day: int) -> datetime.date:
    """
    Construct a date object.

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        day: Day (1-31)

    Returns:
        A date object
    """
    return datetime.date(year, month, day)


def Time(hour: int, minute: int, second: int) -> datetime.time:
    """
    Construct a time object.

    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59)

    Returns:
        A time object
    """
    return datetime.time(hour, minute, second)


def Timestamp(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> datetime.datetime:
    """
    Construct a datetime object.

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59)

    Returns:
        A datetime object
    """
    return datetime.datetime(year, month, day, hour, minute, second)


def DateFromTicks(ticks: float) -> datetime.date:
    """
    Construct a date object from a UNIX timestamp.

    Args:
        ticks: UNIX timestamp (seconds since epoch)

    Returns:
        A date object
    """
    return datetime.date.fromtimestamp(ticks)


def TimeFromTicks(ticks: float) -> datetime.time:
    """
    Construct a time object from a UNIX timestamp.

    Args:
        ticks: UNIX timestamp (seconds since epoch)

    Returns:
        A time object
    """
    return datetime.datetime.fromtimestamp(ticks).time()


def TimestampFromTicks(ticks: float) -> datetime.datetime:
    """
    Construct a datetime object from a UNIX timestamp.

    Args:
        ticks: UNIX timestamp (seconds since epoch)

    Returns:
        A datetime object
    """
    return datetime.datetime.fromtimestamp(ticks)


def Binary(data: bytes | bytearray | str) -> bytes:
    """
    Construct a binary object.

    Args:
        data: Binary data as bytes, bytearray, or string

    Returns:
        A bytes object
    """
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, str):
        return data.encode("utf-8")
    raise TypeError(f"Cannot convert {type(data)} to bytes")
