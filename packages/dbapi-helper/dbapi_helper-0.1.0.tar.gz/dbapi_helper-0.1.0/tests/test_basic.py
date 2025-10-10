"""
Basic tests for dbapi-helper.

These tests verify that the base classes work correctly.
"""

import os
import sys

import pytest

# Add src to path for tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from dbapi_helper import (
    Connection,
    Cursor,
    NotSupportedError,
    ProgrammingError,
    apilevel,
    paramstyle,
    threadsafety,
)
from dbapi_helper.connection import check_closed as check_connection_closed
from dbapi_helper.cursor import check_closed as check_cursor_closed


class SimpleCursor(Cursor):
    """Simple cursor implementation for testing."""

    @check_cursor_closed
    def execute(self, operation, parameters=None):
        """Execute a simple query."""
        # Simulate a SELECT query
        if operation.upper().startswith("SELECT"):
            self.description = (
                ("id", int, None, None, None, None, None),
                ("name", str, None, None, None, None, None),
            )
            self._results = iter(
                [
                    (1, "Alice"),
                    (2, "Bob"),
                    (3, "Charlie"),
                ]
            )
        else:
            self.description = None
            self._results = iter([])

        self.operation = operation
        return self


class SimpleConnection(Connection[SimpleCursor]):
    """Simple connection implementation for testing."""

    @check_connection_closed
    def cursor(self):
        """Create a new cursor."""
        cursor = SimpleCursor()
        self.cursors.append(cursor)
        return cursor


def test_module_attributes():
    """Test DB API 2.0 module attributes."""
    assert apilevel == "2.0"
    assert threadsafety == 2
    assert paramstyle == "qmark"


def test_connection_cursor_creation():
    """Test that connections can create cursors."""
    conn = SimpleConnection()
    cursor = conn.cursor()

    assert cursor is not None
    assert isinstance(cursor, SimpleCursor)
    assert cursor in conn.cursors
    assert not cursor.closed
    assert not conn.closed


def test_cursor_execute():
    """Test basic cursor execute functionality."""
    conn = SimpleConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")

    assert cursor.operation == "SELECT * FROM users"
    assert cursor.description is not None
    assert len(cursor.description) == 2
    assert cursor.description[0][0] == "id"
    assert cursor.description[1][0] == "name"


def test_cursor_fetchone():
    """Test fetching one row at a time."""
    conn = SimpleConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    row1 = cursor.fetchone()
    assert row1 == (1, "Alice")

    row2 = cursor.fetchone()
    assert row2 == (2, "Bob")

    row3 = cursor.fetchone()
    assert row3 == (3, "Charlie")

    row4 = cursor.fetchone()
    assert row4 is None


def test_cursor_fetchall():
    """Test fetching all rows."""
    conn = SimpleConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    rows = cursor.fetchall()
    assert len(rows) == 3
    assert rows[0] == (1, "Alice")
    assert rows[1] == (2, "Bob")
    assert rows[2] == (3, "Charlie")


def test_cursor_fetchmany():
    """Test fetching multiple rows."""
    conn = SimpleConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    rows = cursor.fetchmany(2)
    assert len(rows) == 2
    assert rows[0] == (1, "Alice")
    assert rows[1] == (2, "Bob")

    rows = cursor.fetchmany(2)
    assert len(rows) == 1
    assert rows[0] == (3, "Charlie")


def test_cursor_iterator():
    """Test iterating over cursor results."""
    conn = SimpleConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    rows = list(cursor)
    assert len(rows) == 3
    assert rows[0] == (1, "Alice")


def test_cursor_close():
    """Test closing a cursor."""
    conn = SimpleConnection()
    cursor = conn.cursor()

    assert not cursor.closed
    cursor.close()
    assert cursor.closed

    # Should raise error when using closed cursor
    with pytest.raises(ProgrammingError):
        cursor.execute("SELECT * FROM users")


def test_connection_close():
    """Test closing a connection."""
    conn = SimpleConnection()
    cursor1 = conn.cursor()
    cursor2 = conn.cursor()

    assert not conn.closed
    assert not cursor1.closed
    assert not cursor2.closed

    conn.close()

    assert conn.closed
    assert cursor1.closed
    assert cursor2.closed

    # Should raise error when using closed connection
    with pytest.raises(ProgrammingError):
        conn.cursor()


def test_connection_execute():
    """Test connection.execute() convenience method."""
    conn = SimpleConnection()
    cursor = conn.execute("SELECT * FROM users")

    assert isinstance(cursor, SimpleCursor)
    assert cursor.operation == "SELECT * FROM users"

    rows = cursor.fetchall()
    assert len(rows) == 3


def test_context_manager():
    """Test using connection as context manager."""
    with SimpleConnection() as conn:
        cursor = conn.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        assert len(rows) == 3

    # Connection should be closed after exiting context
    assert conn.closed


def test_executemany_not_supported():
    """Test that executemany raises NotSupportedError."""
    conn = SimpleConnection()
    cursor = conn.cursor()

    with pytest.raises(NotSupportedError):
        cursor.executemany(
            "INSERT INTO users VALUES (?, ?)", [(1, "Alice"), (2, "Bob")]
        )


def test_check_result_decorator():
    """Test that methods requiring results raise error if called before execute."""
    conn = SimpleConnection()
    cursor = conn.cursor()

    # These should raise ProgrammingError before execute
    with pytest.raises(ProgrammingError, match="Called before execute"):
        cursor.fetchone()

    with pytest.raises(ProgrammingError, match="Called before execute"):
        cursor.fetchall()

    with pytest.raises(ProgrammingError, match="Called before execute"):
        cursor.fetchmany()


def test_arraysize():
    """Test arraysize attribute."""
    conn = SimpleConnection()
    cursor = conn.cursor()

    assert cursor.arraysize == 1
    cursor.arraysize = 5
    assert cursor.arraysize == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
