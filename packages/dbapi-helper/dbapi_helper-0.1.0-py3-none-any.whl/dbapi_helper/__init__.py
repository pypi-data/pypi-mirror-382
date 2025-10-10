"""
dbapi-helper: A helper library for implementing Python DB API 2.0 database drivers.

This library provides base classes and utilities to make it easier to implement
Python DB API 2.0 compliant database drivers, especially for REST-based SQL
services. Subclasses only need to implement the cursor.execute() method and
connection.cursor() method.

Example:
    >>> from dbapi_helper import Connection, Cursor
    >>>
    >>> class MyCursor(Cursor):
    ...     def execute(self, operation, parameters=None):
    ...         # Your REST API call here
    ...         response = my_rest_api.query(operation, parameters)
    ...         self.description = response.description
    ...         self._results = iter(response.rows)
    ...         self.operation = operation
    ...         return self
    >>>
    >>> class MyConnection(Connection[MyCursor]):
    ...     def cursor(self):
    ...         return MyCursor()
"""

# Base classes
from .connection import Connection
from .cursor import Cursor, Description

# Exceptions
from .exceptions import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Warning,
)

# Type objects
from .types import (
    BINARY,
    DATETIME,
    NUMBER,
    ROWID,
    STRING,
    Binary,
    Date,
    DateFromTicks,
    DBAPITypeObject,
    Time,
    TimeFromTicks,
    Timestamp,
    TimestampFromTicks,
)

# DB API 2.0 version and module attributes
apilevel = "2.0"
threadsafety = 2  # Threads may share the module and connections
paramstyle = "qmark"  # Question mark style, e.g., '...WHERE name=?'


__version__ = "0.1.0"

__all__ = [
    # Module attributes
    "apilevel",
    "threadsafety",
    "paramstyle",
    # Base classes
    "Connection",
    "Cursor",
    "Description",
    # Exceptions
    "Error",
    "Warning",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    # Type objects
    "STRING",
    "BINARY",
    "NUMBER",
    "DATETIME",
    "ROWID",
    "DBAPITypeObject",
    # Type constructors
    "Date",
    "Time",
    "Timestamp",
    "DateFromTicks",
    "TimeFromTicks",
    "TimestampFromTicks",
    "Binary",
]
