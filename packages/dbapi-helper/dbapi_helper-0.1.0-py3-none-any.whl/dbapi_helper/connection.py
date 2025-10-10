"""
Base Connection implementation for DB API 2.0.

This module provides a base Connection class that implements the DB API 2.0
connection interface. Subclasses need to implement the cursor() method to
return their custom cursor type.
"""

from functools import wraps
from typing import Any, Callable, Generic, TypeVar, cast

from .cursor import Cursor
from .exceptions import ProgrammingError

# Type variable for custom cursor types
CursorType = TypeVar("CursorType", bound=Cursor)

CONNECTION_METHOD = TypeVar("CONNECTION_METHOD", bound=Callable[..., Any])


def check_closed(method: CONNECTION_METHOD) -> CONNECTION_METHOD:
    """Decorator that checks if a connection is closed before executing a method."""

    @wraps(method)
    def wrapper(self: "Connection[Any]", *args: Any, **kwargs: Any) -> Any:
        if self.closed:
            raise ProgrammingError(f"{self.__class__.__name__} already closed")
        return method(self, *args, **kwargs)

    return cast(CONNECTION_METHOD, wrapper)


class Connection(Generic[CursorType]):
    """
    Base connection implementation for DB API 2.0.

    This class implements the connection interface specified in PEP 249.
    Subclasses should implement the cursor() method to return their custom
    cursor type.

    The class is generic over the cursor type, allowing for proper type hints:
        class MyConnection(Connection[MyCursor]):
            def cursor(self) -> MyCursor:
                return MyCursor(self)

    Attributes:
        closed: Whether the connection is closed
        cursors: List of all cursors created from this connection
    """

    def __init__(self) -> None:
        """Initialize a new connection."""
        self.closed = False
        self.cursors: list[CursorType] = []

    @check_closed
    def close(self) -> None:
        """
        Close the connection now.

        The connection will be unusable from this point forward; a
        ProgrammingError will be raised if any operation is attempted with
        the connection. The same applies to all cursor objects trying to use
        the connection. All cursors will also be closed.
        """
        self.closed = True
        for cursor in self.cursors:
            if not cursor.closed:
                cursor.close()

    @check_closed
    def commit(self) -> None:
        """
        Commit any pending transaction to the database.

        This is a no-op in the base implementation. Subclasses should override
        this method if they support transactions.
        """

    @check_closed
    def rollback(self) -> None:
        """
        Roll back any pending transaction to the database.

        This is a no-op in the base implementation. Subclasses should override
        this method if they support transactions.
        """

    @check_closed
    def cursor(self) -> CursorType:
        """
        Return a new cursor object using the connection.

        Subclasses MUST implement this method to return their custom cursor type.

        Returns:
            A new cursor object

        Raises:
            NotImplementedError: Always (subclasses must implement this)
        """
        raise NotImplementedError(
            "Subclasses must implement the cursor() method. "
            "This method should create and return a new cursor instance."
        )

    @check_closed
    def execute(
        self,
        operation: str,
        parameters: tuple[Any, ...] | None = None,
    ) -> CursorType:
        """
        Execute a query on a new cursor (convenience method).

        This is a convenience method that creates a new cursor, executes the
        operation, and returns the cursor.

        Args:
            operation: SQL query or command to execute
            parameters: Optional tuple of parameters to substitute into the query

        Returns:
            A cursor with the query results
        """
        cursor = self.cursor()
        return cursor.execute(operation, parameters)  # type: ignore

    def __enter__(self) -> "Connection[CursorType]":
        """Enter the connection context manager."""
        return self

    def __exit__(self, *exc: Any) -> None:
        """
        Exit the connection context manager.

        Commits the transaction (if any) and closes the connection.
        """
        self.commit()
        self.close()
