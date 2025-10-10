"""
DB API 2.0 standard exceptions.

This module defines all the exceptions specified in PEP 249 (Python Database API
Specification v2.0).
"""


class Error(Exception):
    """
    Base class for all database exceptions.

    This is the base exception for all other exceptions in this module.
    """


class Warning(Exception):  # noqa: A001
    """
    Exception raised for important warnings.

    Examples include data truncations while inserting, etc.
    """


class InterfaceError(Error):
    """
    Exception raised for errors related to the database interface.

    This should be raised for errors that are related to the database interface
    rather than the database itself.
    """


class DatabaseError(Error):
    """
    Exception raised for errors related to the database.

    This is the base exception for all other database-related exceptions
    (OperationalError, IntegrityError, InternalError, ProgrammingError, and
    NotSupportedError).
    """


class DataError(DatabaseError):
    """
    Exception raised for errors due to problems with the processed data.

    Examples include division by zero, numeric value out of range, etc.
    """


class OperationalError(DatabaseError):
    """
    Exception raised for errors related to the database's operation.

    These errors are not necessarily under the control of the programmer.
    Examples include an unexpected disconnect, the data source name not found,
    a transaction could not be processed, a memory allocation error during
    processing, etc.
    """


class IntegrityError(DatabaseError):
    """
    Exception raised when the relational integrity of the database is affected.

    Examples include a foreign key check failure.
    """


class InternalError(DatabaseError):
    """
    Exception raised when the database encounters an internal error.

    Examples include the cursor is not valid anymore, the transaction is out of
    sync, etc.
    """


class ProgrammingError(DatabaseError):
    """
    Exception raised for programming errors.

    Examples include table not found or already exists, syntax error in SQL
    statement, wrong number of parameters specified, etc.
    """


class NotSupportedError(DatabaseError):
    """
    Exception raised when a method or database API is not supported.

    Examples include calling the rollback() method on a connection that does not
    support transactions or has transactions turned off.
    """
