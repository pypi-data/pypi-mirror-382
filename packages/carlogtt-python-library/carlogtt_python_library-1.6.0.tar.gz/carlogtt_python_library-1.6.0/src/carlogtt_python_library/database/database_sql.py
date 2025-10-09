# ======================================================================
# MODULE DETAILS
# This section provides metadata about the module, including its
# creation date, author, copyright information, and a brief description
# of the module's purpose and functionality.
# ======================================================================

#   __|    \    _ \  |      _ \   __| __ __| __ __|
#  (      _ \     /  |     (   | (_ |    |      |
# \___| _/  _\ _|_\ ____| \___/ \___|   _|     _|

# src/carlogtt_python_library/database/database_sql.py
# Created 9/25/23 - 2:34 PM UK Time (London) by carlogtt
# Copyright (c) Amazon.com Inc. All Rights Reserved.
# AMAZON.COM CONFIDENTIAL

"""
This module ...
"""

# ======================================================================
# EXCEPTIONS
# This section documents any exceptions made or code quality rules.
# These exceptions may be necessary due to specific coding requirements
# or to bypass false positives.
# ======================================================================
#

# ======================================================================
# IMPORTS
# Importing required libraries and modules for the application.
# ======================================================================

# Standard Library Imports
import abc
import datetime
import decimal
import logging
import pathlib
import sqlite3
import time
from collections.abc import Generator, Iterable, Sequence
from typing import Any, Generic, Optional, TypeVar, Union

# Third Party Library Imports
import mysql.connector
import mysql.connector.cursor
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection

# Local Folder (Relative) Imports
from .. import exceptions, utils
from . import database_utils

# psycopg2 is defined as an optional dependency. We use this try/except
# to gracefully handle environments where psycopg2 is not installed
# (e.g., on older systems or when Postgres support is not needed).
# If you do need Postgres support, run:
#     pip install "carlogtt-python-library[postgres]"
try:
    import psycopg2
    import psycopg2.extensions
    import psycopg2.extras

except ImportError:
    # Setting up logger for current module
    module_logger = logging.getLogger(__name__)
    module_logger.debug(
        "psycopg2 is not installed. Please install manually or use 'pip install"
        " \"carlogtt-python-library[postgres]\"'."
    )

    psycopg2 = None  # type: ignore

# END IMPORTS
# ======================================================================


# List of public names in the module
__all__ = [
    'Database',
    'MySQL',
    'PostgreSQL',
    'SQLite',
]

# Setting up logger for current module
module_logger = logging.getLogger(__name__)

# Type aliases
MySQLConn = Union[MySQLConnectionAbstract, PooledMySQLConnection]
if psycopg2 is not None:
    PostgreSQLConn = psycopg2.extensions.connection
else:
    PostgreSQLConn = None  # type: ignore
SQLiteConn = sqlite3.Connection
ConnT = TypeVar("ConnT", MySQLConn, PostgreSQLConn, SQLiteConn)
SQLValueType = Union[
    bool,
    bytes,
    float,
    int,
    str,
    decimal.Decimal,
    datetime.date,
    datetime.time,
    datetime.datetime,
    datetime.timedelta,
    time.struct_time,
    None,
]


class Database(abc.ABC, Generic[ConnT]):

    db_utils: database_utils.DatabaseUtils

    @property
    @abc.abstractmethod
    def db_connection(self) -> ConnT:
        pass

    @abc.abstractmethod
    def open_db_connection(self) -> None:
        pass

    @abc.abstractmethod
    def close_db_connection(self) -> None:
        pass

    @abc.abstractmethod
    def send_to_db(self, sql_query: str, sql_values: Sequence[SQLValueType] = ()) -> None:
        pass

    @abc.abstractmethod
    def send_many_to_db(self, sql_query: str, sql_values: Iterable[Sequence[SQLValueType]]) -> None:
        pass

    @abc.abstractmethod
    def fetch_from_db(
        self,
        sql_query: str,
        sql_values: Sequence[SQLValueType] = (),
        *,
        fetch_one: bool = False,
    ) -> Generator[dict[str, Any], None, None]:
        pass


class MySQL(Database[MySQLConn]):
    """
    Handles MySQL database connections.

    :param host: Hostname or IP address of the MySQL server.
    :param user: Username to authenticate with the MySQL server.
    :param password: Password to authenticate with the MySQL server.
    :param port: Port number of the MySQL server.
    :param database_schema: Name of the database schema to use.

    **Attributes**

    ``db_utils``
        Instance of :class:`~database_utils.DatabaseUtils`
        (helper for reading external SQL files, etc.).
    """

    def __init__(self, host: str, user: str, password: str, port: str, database_schema: str):
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._database_schema = database_schema
        self._db_connection: Optional[MySQLConn] = None
        self.db_utils = database_utils.DatabaseUtils()

    @property
    def db_connection(self) -> MySQLConn:
        """
        Gets the active db connection. If there is not an active
        connection it creates one.
        """

        if not self._db_connection:
            self.open_db_connection()

        assert isinstance(self._db_connection, MySQLConnectionAbstract) or isinstance(
            self._db_connection, PooledMySQLConnection
        ), "Expected self._db_connection to be type MySQLConn"

        return self._db_connection

    @utils.retry(exception_to_check=exceptions.MySQLError)
    def open_db_connection(self) -> None:
        """
        Open a MySQL db connection.
        Auto retry up to 4 times on connection error.

        :raise MySQLError: If the operation fails.
        """

        try:
            self._db_connection = mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                port=self._port,
                database=self._database_schema,
            )

        except mysql.connector.Error as ex:
            message = (
                f"While connecting to host [{self._host}] operation failed! traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.MySQLError(message) from None

    @utils.retry(exception_to_check=exceptions.MySQLError)
    def close_db_connection(self) -> None:
        """
        Close the MySQL db connection.
        Auto retry up to 4 times on connection error.

        :raise MySQLError: If the operation fails.
        """

        try:
            if self._db_connection:
                self._db_connection.close()
                self._db_connection = None

        except mysql.connector.Error as ex:
            message = f"While closing [{self._host}] operation failed! traceback: {repr(ex)}"
            module_logger.error(message)
            raise exceptions.MySQLError(message) from None

    def send_to_db(self, sql_query: str, sql_values: Sequence[SQLValueType] = ()) -> None:
        """
        Send data to MySQL database.

        :param sql_query: SQL query to be executed.
        :param sql_values: Values to be substituted in the SQL query.
        :raise MySQLError: If the operation fails.
        """

        db_cursor = self.db_connection.cursor(prepared=True)

        try:
            with utils.retry(exception_to_check=Exception) as retryer:
                retryer(db_cursor.execute, sql_query, sql_values)
                retryer(self.db_connection.commit)

            module_logger.debug(f"Database SQL query {sql_query=} executed successfully")

        except mysql.connector.Error as ex:
            message = (
                f"While executing SQL query {sql_query=} on host [{self._host}] operation failed!"
                f" traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.MySQLError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()

    def send_many_to_db(self, sql_query: str, sql_values: Iterable[Sequence[SQLValueType]]) -> None:
        """
        Execute the same SQL statement many times in a single
        ACID‑compliant transaction. Commit only if every execution
        succeeds, otherwise roll back.

        :param sql_query: The parametrized SQL string.
        :param sql_values: Any iterable yielding values to be
            substituted in the SQL query.
        :raise MySQLError: (after rollback) If the operation fails.
        """

        db_cursor = self.db_connection.cursor(prepared=True)

        try:
            # executemany sends the whole batch; server handles each row
            # list() ensures we don’t exhaust a generator if retries
            with utils.retry(exception_to_check=Exception) as retryer:
                retryer(db_cursor.executemany, sql_query, list(sql_values))
                retryer(self.db_connection.commit)

            module_logger.debug(
                "Database atomic batch executed and committed successfully: "
                f"{db_cursor.rowcount} rows affected by SQL query {sql_query=}"
            )

        except mysql.connector.Error as ex:
            # Atomicity guarantee
            self.db_connection.rollback()

            message = (
                f"Database atomic batch for SQL query {sql_query} failed on host [{self._host}]. "
                f"Rolled back the entire transaction. Traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.MySQLError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()

    @utils.retry(exception_to_check=exceptions.MySQLError, delay_secs=2)
    def fetch_from_db(
        self, sql_query: str, sql_values: Sequence[SQLValueType] = (), *, fetch_one: bool = False
    ) -> Generator[dict[str, Any], None, None]:
        """
        Fetch data from MySQL database.

        :param sql_query: SQL query to be executed.
        :param sql_values: Values to be substituted in the SQL query.
        :param fetch_one: If True, only fetch the first row.
        :return: Generator of dictionaries containing the fetched rows.
        :raise MySQLError: If the operation fails.
        """

        db_cursor = self.db_connection.cursor(prepared=True, dictionary=True)
        assert isinstance(db_cursor, mysql.connector.cursor.MySQLCursorDict)

        try:
            db_cursor.execute(sql_query, sql_values)

            module_logger.debug(f"Database SQL query {sql_query=} executed successfully")

            if fetch_one:
                next_row = db_cursor.fetchone()
                if next_row is None:
                    # Nothing to yield
                    yield from ()
                else:
                    yield next_row

            else:
                next_row = db_cursor.fetchone()
                if next_row is None:
                    # Nothing to yield
                    yield from ()
                else:
                    yield next_row
                    # db_cursor.fetchone will return None when at the
                    # end so the sentinel is met by the iter function
                    yield from iter(db_cursor.fetchone, None)

        except mysql.connector.Error as ex:
            message = (
                f"While executing SQL query {sql_query=} on host [{self._host}] operation failed!"
                f" traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.MySQLError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()


class PostgreSQL(Database[PostgreSQLConn]):
    """
    Handles PostgreSQL database connections.

    :param host: Hostname or IP address of the Postgres server.
    :param user: Username to authenticate with the Postgres server.
    :param password: Password to authenticate with the Postgres server.
    :param port: Port number of the Postgres server.
    :param database_schema: Name of the database schema to use.

    **Attributes**

    ``db_utils``
        Instance of :class:`~database_utils.DatabaseUtils`
        (helper for reading external SQL files, etc.).
    """

    def __init__(self, host: str, user: str, password: str, port: str, database_schema: str):
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._database_schema = database_schema
        self._db_connection: Optional[PostgreSQLConn] = None
        self.db_utils = database_utils.DatabaseUtils()

    @property
    def db_connection(self) -> PostgreSQLConn:
        """
        Gets the active db connection. If there is not an active
        connection it creates one.
        """

        if not self._db_connection:
            self.open_db_connection()

        assert isinstance(
            self._db_connection, psycopg2.extensions.connection
        ), "Expected self._db_connection to be type psycopg2.extensions.connection"

        return self._db_connection

    @utils.retry(exception_to_check=exceptions.PostgresError)
    def open_db_connection(self) -> None:
        """
        Open a PostgreSQL db connection.
        Auto retry up to 4 times on connection error.

        :raise PostgresError: If the operation fails.
        """

        try:
            self._db_connection = psycopg2.connect(
                dbname=self._database_schema,
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port,
            )

        except psycopg2.Error as ex:
            message = (
                f"While connecting to host [{self._host}] operation failed! traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.PostgresError(message) from None

    @utils.retry(exception_to_check=exceptions.PostgresError)
    def close_db_connection(self) -> None:
        """
        Close the PostgreSQL db connection.
        Auto retry up to 4 times on connection error.

        :raise PostgresError: If the operation fails.
        """

        try:
            if self._db_connection:
                self._db_connection.close()
                self._db_connection = None

        except psycopg2.Error as ex:
            message = f"While closing [{self._host}] operation failed! traceback: {repr(ex)}"
            module_logger.error(message)
            raise exceptions.PostgresError(message) from None

    def send_to_db(self, sql_query: str, sql_values: Sequence[SQLValueType] = ()) -> None:
        """
        Send data to PostgreSQL database.

        :param sql_query: SQL query to be executed.
        :param sql_values: Values to be substituted in the SQL query.
        :raise PostgresError: If the operation fails.
        """

        db_cursor = self.db_connection.cursor()

        try:
            with utils.retry(exception_to_check=Exception) as retryer:
                retryer(db_cursor.execute, sql_query, sql_values)
                retryer(self.db_connection.commit)

            module_logger.debug(f"Database SQL query {sql_query=} executed successfully")

        except psycopg2.Error as ex:
            message = (
                f"While executing SQL query {sql_query=} on host [{self._host}] "
                f"operation failed! traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.PostgresError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()

    def send_many_to_db(self, sql_query: str, sql_values: Iterable[Sequence[SQLValueType]]) -> None:
        """
        Execute the same SQL statement many times in a single
        ACID‑compliant transaction. Commit only if every execution
        succeeds, otherwise roll back.

        :param sql_query: The parametrized SQL string.
        :param sql_values: Any iterable yielding values to be
            substituted in the SQL query.
        :raise PostgresError: (after rollback) If the operation fails.
        """

        db_cursor = self.db_connection.cursor()

        try:
            # executemany sends the whole batch; server handles each row
            # list() ensures we don’t exhaust a generator if retries
            with utils.retry(exception_to_check=Exception) as retryer:
                retryer(db_cursor.executemany, sql_query, list(sql_values))
                retryer(self.db_connection.commit)

            module_logger.debug(
                "Database atomic batch executed and committed successfully: "
                f"{db_cursor.rowcount} rows affected by SQL query {sql_query=}"
            )

        except psycopg2.Error as ex:
            # Atomicity guarantee
            self.db_connection.rollback()

            message = (
                f"Database atomic batch for SQL query {sql_query} failed on host [{self._host}]. "
                f"Rolled back the entire transaction. Traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.PostgresError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()

    @utils.retry(exception_to_check=exceptions.PostgresError, delay_secs=2)
    def fetch_from_db(
        self, sql_query: str, sql_values: Sequence[SQLValueType] = (), *, fetch_one: bool = False
    ) -> Generator[dict[str, Any], None, None]:
        """
        Fetch data from PostgreSQL database.

        :param sql_query: SQL query to be executed.
        :param sql_values: Values to be substituted in the SQL query.
        :param fetch_one: If True, only fetch the first row.
        :return: Generator of dictionaries containing the fetched rows.
        :raise PostgresError: If the operation fails.
        """

        # Create a cursor that returns rows as dictionaries
        db_cursor = self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            db_cursor.execute(sql_query, sql_values)

            module_logger.debug(f"Database SQL query {sql_query=} executed successfully")

            if fetch_one:
                next_row = db_cursor.fetchone()
                if next_row is None:
                    # Nothing to yield
                    yield from ()
                else:
                    yield dict(next_row)

            else:
                next_row = db_cursor.fetchone()
                if next_row is None:
                    # Nothing to yield
                    yield from ()
                else:
                    yield dict(next_row)
                    # Fetch the rest one by one until None is returned
                    yield from (dict(row) for row in iter(db_cursor.fetchone, None))

        except psycopg2.Error as ex:
            message = (
                f"While executing SQL query {sql_query=} on host [{self._host}] operation failed!"
                f" traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.PostgresError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()


class SQLite(Database[SQLiteConn]):
    """
    Handles SQLite database connections.

    :param sqlite_db_path: Fullpath to the SQLite database file.
    :param filename: Name of the SQLite database file.

    **Attributes**

    ``db_utils``
        Instance of :class:`~database_utils.DatabaseUtils`
        (helper for reading external SQL files, etc.).
    """

    def __init__(self, sqlite_db_path: Union[str, pathlib.Path], filename: str):
        self._sqlite_db_path = sqlite_db_path
        self._filename = filename
        self._db_connection: Optional[SQLiteConn] = None
        self.db_utils = database_utils.DatabaseUtils()

    @property
    def db_connection(self) -> SQLiteConn:
        """
        Gets the active db connection. If there is not an active
        connection it creates one.
        """

        if not self._db_connection:
            self.open_db_connection()

        assert isinstance(
            self._db_connection, sqlite3.Connection
        ), "Expected self._db_connection to be type SQLiteConn"

        return self._db_connection

    def open_db_connection(self) -> None:
        """
        Open a SQLite db connection and cache it for quick access.
        To equal the style of MySQL it enables some features by default:
        - Set the cursor to return dictionary instead of tuples.
        - Enable foreign key constraint.

        :raise SQLiteError: If the operation fails.
        """

        try:
            self._db_connection = sqlite3.connect(self._sqlite_db_path)

            # Row to the row_factory of connection creates what some
            # people call a 'dictionary cursor'. Instead of tuples,
            # it starts returning 'dictionary'
            self._db_connection.row_factory = sqlite3.Row

            # Foreign key constraint must be enabled by the application
            # at runtime using the PRAGMA command
            self._db_connection.execute("PRAGMA foreign_keys = ON;")

        except sqlite3.Error as ex:
            message = (
                f"While connecting to host [{self._filename}] operation failed! traceback:"
                f" {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.SQLiteError(message) from None

    def close_db_connection(self) -> None:
        """
        Close the SQLite db connection.

        :raise SQLiteError: If the operation fails.
        """

        try:
            if self._db_connection:
                self._db_connection.close()
                self._db_connection = None

        except sqlite3.Error as ex:
            message = f"While closing [{self._filename}] operation failed! traceback: {repr(ex)}"
            module_logger.error(message)
            raise exceptions.SQLiteError(message) from None

    def send_to_db(self, sql_query: str, sql_values: Sequence[SQLValueType] = ()) -> None:
        """
        Send data to SQLite database.

        :param sql_query: SQL query to be executed.
        :param sql_values: Values to be substituted in the SQL query.
        :raise SQLiteError: If the operation fails.
        """

        db_cursor = self.db_connection.cursor()

        try:
            db_cursor.execute(sql_query, sql_values)

            self.db_connection.commit()

            module_logger.debug(f"Database SQL query {sql_query=} executed successfully")

        except sqlite3.Error as ex:
            message = (
                f"While executing SQL query {sql_query=} on host [{self._filename}] operation"
                f" failed! traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.SQLiteError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()

    def send_many_to_db(self, sql_query: str, sql_values: Iterable[Sequence[SQLValueType]]) -> None:
        """
        Execute the same SQL statement many times in a single
        ACID‑compliant transaction. Commit only if every execution
        succeeds, otherwise roll back.

        :param sql_query: The parametrized SQL string.
        :param sql_values: Any iterable yielding values to be
            substituted in the SQL query.
        :raise SQLiteError: (after rollback) If the operation fails.
        """

        db_cursor = self.db_connection.cursor()

        try:
            # executemany sends the whole batch; server handles each row
            # list() ensures we don’t exhaust a generator if retries
            db_cursor.executemany(sql_query, list(sql_values))

            self.db_connection.commit()

            module_logger.debug(
                "Database atomic batch executed and committed successfully: "
                f"{db_cursor.rowcount} rows affected by SQL query {sql_query=}"
            )

        except sqlite3.Error as ex:
            # Atomicity guarantee
            self.db_connection.rollback()

            message = (
                f"Database atomic batch for SQL query {sql_query} failed on host"
                f" [{self._filename}]. Rolled back the entire transaction. Traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.SQLiteError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()

    def fetch_from_db(
        self, sql_query: str, sql_values: Sequence[SQLValueType] = (), *, fetch_one: bool = False
    ) -> Generator[dict[str, Any], None, None]:
        """
        Fetch data from SQLite database.

        :param sql_query: SQL query to be executed.
        :param sql_values: Values to be substituted in the SQL query.
        :param fetch_one: If True, only fetch the first row.
        :return: Generator of dictionaries containing the fetched rows.
        :raise SQLiteError: If the operation fails.
        """

        db_cursor = self.db_connection.cursor()

        try:
            db_cursor.execute(sql_query, sql_values)

            module_logger.debug(f"Database SQL query {sql_query=} executed successfully")

            if fetch_one:
                next_row = self._next_row_dict(db_cursor=db_cursor)
                if next_row is None:
                    # Nothing to yield
                    yield from ()
                else:
                    yield next_row

            else:
                next_row = self._next_row_dict(db_cursor=db_cursor)
                if next_row is None:
                    # Nothing to yield
                    yield from ()
                else:
                    yield next_row
                    # _next_row_dict will return None when at the end
                    # so the sentinel is met by the iter function
                    yield from iter(lambda: self._next_row_dict(db_cursor=db_cursor), None)

        except sqlite3.Error as ex:
            message = (
                f"While executing SQL query {sql_query=} on host [{self._filename}] operation"
                f" failed! traceback: {repr(ex)}"
            )
            module_logger.error(message)
            raise exceptions.SQLiteError(message) from None

        finally:
            db_cursor.close()
            self.close_db_connection()

    def _next_row_dict(self, db_cursor: sqlite3.Cursor) -> Optional[dict[str, Any]]:
        """
        Returns the next row as a dictionary or None if no
        more rows.

        :return: The next row as a dictionary or None.
        """

        row_fetched = db_cursor.fetchone()
        if row_fetched is None:
            return None
        else:
            return dict(row_fetched)
