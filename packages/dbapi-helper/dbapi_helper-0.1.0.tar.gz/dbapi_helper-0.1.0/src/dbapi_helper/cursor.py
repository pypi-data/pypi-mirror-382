"""
Base Cursor implementation for DB API 2.0.

This module provides a base Cursor class that implements most of the DB API 2.0
cursor interface. Subclasses only need to implement the execute() method.
"""

import itertools
from collections.abc import Iterator
from functools import wraps
from typing import Any, Callable, TypeVar, cast

from .exceptions import NotSupportedError, ProgrammingError

# Type for cursor description (column metadata)
Description = (
    tuple[
        str,  # name
        type | None,  # type_code
        int | None,  # display_size
        int | None,  # internal_size
        int | None,  # precision
        int | None,  # scale
        bool | None,  # null_ok
    ]
    | None
)


CURSOR_METHOD = TypeVar("CURSOR_METHOD", bound=Callable[..., Any])


def check_closed(method: CURSOR_METHOD) -> CURSOR_METHOD:
    """Decorator that checks if a cursor is closed before executing a method."""

    @wraps(method)
    def wrapper(self: "Cursor", *args: Any, **kwargs: Any) -> Any:
        if self.closed:
            raise ProgrammingError(f"{self.__class__.__name__} already closed")
        return method(self, *args, **kwargs)

    return cast(CURSOR_METHOD, wrapper)


def check_result(method: CURSOR_METHOD) -> CURSOR_METHOD:
    """Decorator that checks if the cursor has results from execute()."""

    @wraps(method)
    def wrapper(self: "Cursor", *args: Any, **kwargs: Any) -> Any:
        if self._results is None:
            raise ProgrammingError("Called before execute()")
        return method(self, *args, **kwargs)

    return cast(CURSOR_METHOD, wrapper)


class Cursor:
    """
    Base cursor implementation for DB API 2.0.

    This class implements most of the cursor interface specified in PEP 249.
    Subclasses only need to implement the execute() method to handle query
    execution and set self._results to an iterator of result rows.

    Attributes:
        arraysize: Number of rows to fetch at a time with fetchmany() (default: 1)
        closed: Whether the cursor is closed
        description: Column metadata after a query (set by subclass in execute())
        rowcount: Number of rows affected/returned by last query
    """

    def __init__(self) -> None:
        """Initialize a new cursor."""
        # Number of rows to fetch at a time with fetchmany()
        self.arraysize = 1

        # Cursor state
        self.closed = False

        # Column metadata (set by subclass in execute())
        self.description: Description = None

        # Result iterator (set by subclass in execute())
        self._results: Iterator[tuple[Any, ...]] | None = None

        # Row count tracking
        self._rowcount = -1

        # Last executed operation (for debugging)
        self.operation: str | None = None

    @property
    @check_closed
    def rowcount(self) -> int:
        """
        Return the number of rows affected/returned by the last query.

        This property may consume the result iterator to count rows.
        Returns -1 if no query has been executed.
        """
        try:
            results = list(self._results)  # type: ignore
        except TypeError:
            return -1

        n = len(results)
        self._results = iter(results)
        return max(0, self._rowcount) + n

    @check_closed
    def close(self) -> None:
        """
        Close the cursor.

        The cursor will be unusable from this point forward; a ProgrammingError
        will be raised if any operation is attempted with the cursor.
        """
        self.closed = True

    @check_closed
    def execute(
        self,
        operation: str,
        parameters: tuple[Any, ...] | None = None,
    ) -> "Cursor":
        """
        Execute a database operation (query or command).

        Subclasses MUST implement this method. The implementation should:
        1. Execute the operation with the given parameters
        2. Set self.description to column metadata (or None for non-SELECT)
        3. Set self._results to an iterator of result tuples
        4. Set self.operation to the operation string
        5. Return self

        Args:
            operation: SQL query or command to execute
            parameters: Optional tuple of parameters to substitute into the query

        Returns:
            The cursor itself

        Raises:
            NotImplementedError: Always (subclasses must implement this)
        """
        raise NotImplementedError(
            "Subclasses must implement the execute() method. "
            "See the documentation for details on what to set."
        )

    @check_closed
    def executemany(
        self,
        operation: str,
        seq_of_parameters: list[tuple[Any, ...]] | None = None,
    ) -> "Cursor":
        """
        Execute a database operation multiple times.

        This method is provided for compatibility but is not currently supported.
        Use execute() in a loop instead.

        Args:
            operation: SQL query or command to execute
            seq_of_parameters: Sequence of parameter tuples

        Returns:
            The cursor itself

        Raises:
            NotSupportedError: Always (not currently supported)
        """
        raise NotSupportedError(
            "executemany() is not supported, use execute() in a loop instead"
        )

    @check_result
    @check_closed
    def fetchone(self) -> tuple[Any, ...] | None:
        """
        Fetch the next row of a query result set.

        Returns:
            A tuple representing the next row, or None when no more data is available

        Raises:
            ProgrammingError: If called before execute()
        """
        try:
            row = self.__next__()
        except StopIteration:
            return None

        self._rowcount = max(0, self._rowcount) + 1
        return row

    @check_result
    @check_closed
    def fetchmany(self, size: int | None = None) -> list[tuple[Any, ...]]:
        """
        Fetch the next set of rows of a query result.

        Args:
            size: Number of rows to fetch (defaults to arraysize)

        Returns:
            A list of tuples representing the rows (empty list when no more rows)

        Raises:
            ProgrammingError: If called before execute()
        """
        size = size or self.arraysize
        results = list(itertools.islice(self, size))
        return results

    @check_result
    @check_closed
    def fetchall(self) -> list[tuple[Any, ...]]:
        """
        Fetch all remaining rows of a query result.

        Returns:
            A list of tuples representing all remaining rows

        Raises:
            ProgrammingError: If called before execute()
        """
        return list(self)

    @check_closed
    def setinputsizes(self, sizes: int) -> None:
        """
        Predefine memory areas for parameters (optional, no-op in this implementation).

        This method is provided for DB API 2.0 compatibility but does nothing.

        Args:
            sizes: Parameter size specification
        """

    @check_closed
    def setoutputsizes(self, size: int, column: int | None = None) -> None:
        """
        Set a column buffer size for fetches of large columns (optional, no-op).

        This method is provided for DB API 2.0 compatibility but does nothing.

        Args:
            size: Buffer size
            column: Optional column index
        """

    @check_result
    @check_closed
    def __iter__(self) -> Iterator[tuple[Any, ...]]:
        """
        Iterate over query results.

        Yields:
            Tuples representing each row

        Raises:
            ProgrammingError: If called before execute()
        """
        for row in self._results:  # type: ignore
            self._rowcount = max(0, self._rowcount) + 1
            yield row

    @check_result
    @check_closed
    def __next__(self) -> tuple[Any, ...]:
        """
        Get the next row from the result set.

        Returns:
            A tuple representing the next row

        Raises:
            StopIteration: When no more rows are available
            ProgrammingError: If called before execute()
        """
        return next(self._results)  # type: ignore

    # Python 2 compatibility alias
    next = __next__
