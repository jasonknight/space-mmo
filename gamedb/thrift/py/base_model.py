import mysql.connector
import logging
import sys
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any
from contextlib import contextmanager

sys.path.append("../gen-py")

from game.ttypes import GameResult

# Configure logging
logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Base model class for database operations.
    Provides connection management and transaction support.
    All model classes should inherit from this.
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection: Optional[mysql.connector.connection.MySQLConnection] = None

    def connect(self):
        """Establish database connection if not already connected."""
        if not self.connection or not self.connection.is_connected():
            logger.debug(
                f"Connecting to database: host={self.host}, user={self.user}, database={self.database}",
            )
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                auth_plugin="mysql_native_password",
                ssl_disabled=True,
                use_pure=True,
            )
            logger.debug("Database connection established")

    def disconnect(self):
        """Close database connection if connected."""
        if self.connection and self.connection.is_connected():
            logger.debug("Disconnecting from database")
            self.connection.close()
            logger.debug("Database connection closed")

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        Automatically commits on success, rolls back on exception.

        Usage:
            with self.transaction() as cursor:
                cursor.execute(...)
        """
        logger.debug("Starting transaction context")
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute("START TRANSACTION;")
            logger.debug("Transaction started")
            yield cursor
            logger.debug("Committing transaction")
            self.connection.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            logger.error(f"Transaction failed: {type(e).__name__}: {str(e)}")
            if self.connection:
                logger.debug("Rolling back transaction")
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @contextmanager
    def transaction_dict(self):
        """
        Context manager for database transactions with dictionary cursor.
        Automatically commits on success, rolls back on exception.
        """
        logger.debug("Starting transaction_dict context")
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("START TRANSACTION;")
            logger.debug("Transaction started (dict cursor)")
            yield cursor
            logger.debug("Committing transaction (dict cursor)")
            self.connection.commit()
            logger.debug("Transaction committed (dict cursor)")
        except Exception as e:
            logger.error(
                f"Transaction failed (dict cursor): {type(e).__name__}: {str(e)}",
            )
            if self.connection:
                logger.debug("Rolling back transaction (dict cursor)")
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    # Abstract methods that subclasses must implement
    @abstractmethod
    def create(
        self,
        obj: Any,
    ) -> list[GameResult]:
        """Create a new record in the database."""
        pass

    @abstractmethod
    def load(
        self,
        obj_id: int,
    ) -> Tuple[GameResult, Optional[Any]]:
        """Load a record from the database by ID."""
        pass

    @abstractmethod
    def update(
        self,
        obj: Any,
    ) -> list[GameResult]:
        """Update an existing record in the database."""
        pass

    @abstractmethod
    def destroy(
        self,
        obj_id: int,
    ) -> list[GameResult]:
        """Delete a record from the database by ID."""
        pass

    def save(
        self,
        obj: Any,
    ) -> list[GameResult]:
        """
        Save an object (create if id is None, otherwise update).
        This is a convenience method that dispatches to create or update.
        """
        if hasattr(obj, "id") and obj.id is None:
            return self.create(obj)
        else:
            return self.update(obj)

    @abstractmethod
    def search(
        self,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[Any]], int]:
        """
        Search for records with pagination.
        Returns (GameResult, list of objects, total count).
        """
        pass
