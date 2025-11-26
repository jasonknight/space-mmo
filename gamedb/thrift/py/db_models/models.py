#!/usr/bin/env python3
"""
Auto-generated model classes for all database tables.
Generated from database schema - do not modify manually.
"""

from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, Iterator, Union
import mysql.connector
import os

# Load environment variables
load_dotenv()

# Database configuration from environment
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')


class AttributeOwner:
    """
    ActiveRecord-style model for the attribute_owners table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `attribute_owners` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `attribute_id` bigint NOT NULL,
          `mobile_id` bigint DEFAULT NULL,
          `item_id` bigint DEFAULT NULL,
          `asset_id` bigint DEFAULT NULL,
          `player_id` bigint DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `attribute_id` (`attribute_id`),
          CONSTRAINT `attribute_owners_ibfk_1` FOREIGN KEY (`attribute_id`) REFERENCES `attributes` (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=421 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_attribute_id(self) -> int:
        """Get the value of attribute_id."""
        return self._data.get('attribute_id')

    def get_mobile_id(self) -> Optional[int]:
        """Get the value of mobile_id."""
        return self._data.get('mobile_id')

    def get_item_id(self) -> Optional[int]:
        """Get the value of item_id."""
        return self._data.get('item_id')

    def get_asset_id(self) -> Optional[int]:
        """Get the value of asset_id."""
        return self._data.get('asset_id')

    def get_player_id(self) -> Optional[int]:
        """Get the value of player_id."""
        return self._data.get('player_id')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_attribute_id(self, value: int) -> None:
        """Set the value of attribute_id."""
        self._data['attribute_id'] = value
        self._dirty = True

    def set_mobile_id(self, value: Optional[int]) -> None:
        """Set the value of mobile_id."""
        self._data['mobile_id'] = value
        self._dirty = True

    def set_item_id(self, value: Optional[int]) -> None:
        """Set the value of item_id."""
        self._data['item_id'] = value
        self._dirty = True

    def set_asset_id(self, value: Optional[int]) -> None:
        """Set the value of asset_id."""
        self._data['asset_id'] = value
        self._dirty = True

    def set_player_id(self, value: Optional[int]) -> None:
        """Set the value of player_id."""
        self._data['player_id'] = value
        self._dirty = True

    def get_attribute(self, strict: bool = False) -> 'Attribute':
        """
        Get the associated Attribute for this attribute relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_attribute_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_attribute_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Attribute.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has attribute_id={fk_value} but no Attribute record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_attribute(self, model: 'Attribute') -> None:
        """
        Set the associated Attribute for this attribute relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Attribute instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_attribute_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_attribute_id(None)
        else:
            self.set_attribute_id(model.get_id())

    def get_mobile(self, strict: bool = False) -> Optional['Mobile']:
        """
        Get the associated Mobile for this mobile relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_mobile_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_mobile_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Mobile.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has mobile_id={fk_value} but no Mobile record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_mobile(self, model: Optional['Mobile']) -> None:
        """
        Set the associated Mobile for this mobile relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Mobile instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_mobile_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_id(None)
        else:
            self.set_mobile_id(model.get_id())

    def get_item(self, strict: bool = False) -> Optional['Item']:
        """
        Get the associated Item for this item relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_item_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_item_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Item.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has item_id={fk_value} but no Item record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_item(self, model: Optional['Item']) -> None:
        """
        Set the associated Item for this item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_id(None)
        else:
            self.set_item_id(model.get_id())

    def get_player(self, strict: bool = False) -> Optional['Player']:
        """
        Get the associated Player for this player relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_player_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_player_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Player.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has player_id={fk_value} but no Player record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_player(self, model: Optional['Player']) -> None:
        """
        Set the associated Player for this player relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Player instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_player_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_player_id(None)
        else:
            self.set_player_id(model.get_id())



    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                # Save attribute if cached and dirty
                cache_key = '_attribute_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['attribute_id'] = related.get_id()
# Save mobile if cached and dirty
                cache_key = '_mobile_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['mobile_id'] = related.get_id()
# Save item if cached and dirty
                cache_key = '_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_id'] = related.get_id()
# Save player if cached and dirty
                cache_key = '_player_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['player_id'] = related.get_id()

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `attribute_owners` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `attribute_owners` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                pass  # No has-many relationships

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['AttributeOwner']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = AttributeOwner()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `attribute_owners` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_attribute_id(value: int) -> List['AttributeOwner']:
        """
        Find all records by attribute_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `attribute_owners` WHERE `attribute_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = AttributeOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_mobile_id(value: int) -> List['AttributeOwner']:
        """
        Find all records by mobile_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `attribute_owners` WHERE `mobile_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = AttributeOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_item_id(value: int) -> List['AttributeOwner']:
        """
        Find all records by item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `attribute_owners` WHERE `item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = AttributeOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_asset_id(value: int) -> List['AttributeOwner']:
        """
        Find all records by asset_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `attribute_owners` WHERE `asset_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = AttributeOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_player_id(value: int) -> List['AttributeOwner']:
        """
        Find all records by player_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `attribute_owners` WHERE `player_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = AttributeOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class Attribute:
    """
    ActiveRecord-style model for the attributes table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `attributes` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `internal_name` varchar(255) NOT NULL,
          `visible` tinyint(1) NOT NULL,
          `attribute_type` varchar(50) NOT NULL,
          `bool_value` tinyint(1) DEFAULT NULL,
          `double_value` double DEFAULT NULL,
          `vector3_x` double DEFAULT NULL,
          `vector3_y` double DEFAULT NULL,
          `vector3_z` double DEFAULT NULL,
          `asset_id` bigint DEFAULT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=420 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_internal_name(self) -> str:
        """Get the value of internal_name."""
        return self._data.get('internal_name')

    def get_visible(self) -> int:
        """Get the value of visible."""
        return self._data.get('visible')

    def get_attribute_type(self) -> str:
        """Get the value of attribute_type."""
        return self._data.get('attribute_type')

    def get_bool_value(self) -> Optional[int]:
        """Get the value of bool_value."""
        return self._data.get('bool_value')

    def get_double_value(self) -> Optional[float]:
        """Get the value of double_value."""
        return self._data.get('double_value')

    def get_vector3_x(self) -> Optional[float]:
        """Get the value of vector3_x."""
        return self._data.get('vector3_x')

    def get_vector3_y(self) -> Optional[float]:
        """Get the value of vector3_y."""
        return self._data.get('vector3_y')

    def get_vector3_z(self) -> Optional[float]:
        """Get the value of vector3_z."""
        return self._data.get('vector3_z')

    def get_asset_id(self) -> Optional[int]:
        """Get the value of asset_id."""
        return self._data.get('asset_id')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_internal_name(self, value: str) -> None:
        """Set the value of internal_name."""
        self._data['internal_name'] = value
        self._dirty = True

    def set_visible(self, value: int) -> None:
        """Set the value of visible."""
        self._data['visible'] = value
        self._dirty = True

    def set_attribute_type(self, value: str) -> None:
        """Set the value of attribute_type."""
        self._data['attribute_type'] = value
        self._dirty = True

    def set_bool_value(self, value: Optional[int]) -> None:
        """Set the value of bool_value."""
        self._data['bool_value'] = value
        self._dirty = True

    def set_double_value(self, value: Optional[float]) -> None:
        """Set the value of double_value."""
        self._data['double_value'] = value
        self._dirty = True

    def set_vector3_x(self, value: Optional[float]) -> None:
        """Set the value of vector3_x."""
        self._data['vector3_x'] = value
        self._dirty = True

    def set_vector3_y(self, value: Optional[float]) -> None:
        """Set the value of vector3_y."""
        self._data['vector3_y'] = value
        self._dirty = True

    def set_vector3_z(self, value: Optional[float]) -> None:
        """Set the value of vector3_z."""
        self._data['vector3_z'] = value
        self._dirty = True

    def set_asset_id(self, value: Optional[int]) -> None:
        """Set the value of asset_id."""
        self._data['asset_id'] = value
        self._dirty = True



    def get_attribute_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated AttributeOwner records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[AttributeOwner] or Iterator[AttributeOwner]
        """
        cache_key = '_attribute_owners_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = AttributeOwner.find_by_attribute_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                pass  # No belongs-to relationships

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `attributes` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `attributes` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                # Save attribute_owners if cached
                cache_key = '_attribute_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['Attribute']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = Attribute()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `attributes` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_asset_id(value: int) -> List['Attribute']:
        """
        Find all records by asset_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `attributes` WHERE `asset_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = Attribute()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class Inventory:
    """
    ActiveRecord-style model for the inventories table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `inventories` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `owner_id` bigint NOT NULL,
          `owner_type` varchar(50) DEFAULT NULL,
          `max_entries` bigint NOT NULL,
          `max_volume` double NOT NULL,
          `last_calculated_volume` double DEFAULT '0',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_owner_id(self) -> int:
        """Get the value of owner_id."""
        return self._data.get('owner_id')

    def get_owner_type(self) -> Optional[str]:
        """Get the value of owner_type."""
        return self._data.get('owner_type')

    def get_max_entries(self) -> int:
        """Get the value of max_entries."""
        return self._data.get('max_entries')

    def get_max_volume(self) -> float:
        """Get the value of max_volume."""
        return self._data.get('max_volume')

    def get_last_calculated_volume(self) -> Optional[float]:
        """Get the value of last_calculated_volume."""
        return self._data.get('last_calculated_volume')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_owner_id(self, value: int) -> None:
        """Set the value of owner_id."""
        self._data['owner_id'] = value
        self._dirty = True

    def set_owner_type(self, value: Optional[str]) -> None:
        """Set the value of owner_type."""
        self._data['owner_type'] = value
        self._dirty = True

    def set_max_entries(self, value: int) -> None:
        """Set the value of max_entries."""
        self._data['max_entries'] = value
        self._dirty = True

    def set_max_volume(self, value: float) -> None:
        """Set the value of max_volume."""
        self._data['max_volume'] = value
        self._dirty = True

    def set_last_calculated_volume(self, value: Optional[float]) -> None:
        """Set the value of last_calculated_volume."""
        self._data['last_calculated_volume'] = value
        self._dirty = True



    def get_inventory_entries(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated InventoryEntry records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryEntry] or Iterator[InventoryEntry]
        """
        cache_key = '_inventory_entries_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = InventoryEntry.find_by_inventory_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_inventory_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated InventoryOwner records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryOwner] or Iterator[InventoryOwner]
        """
        cache_key = '_inventory_owners_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = InventoryOwner.find_by_inventory_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                pass  # No belongs-to relationships

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `inventories` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `inventories` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                # Save inventory_entries if cached
                cache_key = '_inventory_entries_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save inventory_owners if cached
                cache_key = '_inventory_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['Inventory']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = Inventory()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `inventories` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_owner_id(value: int) -> List['Inventory']:
        """
        Find all records by owner_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventories` WHERE `owner_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = Inventory()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class InventoryEntry:
    """
    ActiveRecord-style model for the inventory_entries table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `inventory_entries` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `inventory_id` bigint NOT NULL,
          `item_id` bigint NOT NULL,
          `quantity` double NOT NULL,
          `is_max_stacked` tinyint(1) DEFAULT '0',
          `mobile_item_id` bigint DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `inventory_id` (`inventory_id`),
          CONSTRAINT `inventory_entries_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventories` (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_inventory_id(self) -> int:
        """Get the value of inventory_id."""
        return self._data.get('inventory_id')

    def get_item_id(self) -> int:
        """Get the value of item_id."""
        return self._data.get('item_id')

    def get_quantity(self) -> float:
        """Get the value of quantity."""
        return self._data.get('quantity')

    def get_is_max_stacked(self) -> Optional[int]:
        """Get the value of is_max_stacked."""
        return self._data.get('is_max_stacked')

    def get_mobile_item_id(self) -> Optional[int]:
        """Get the value of mobile_item_id."""
        return self._data.get('mobile_item_id')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_inventory_id(self, value: int) -> None:
        """Set the value of inventory_id."""
        self._data['inventory_id'] = value
        self._dirty = True

    def set_item_id(self, value: int) -> None:
        """Set the value of item_id."""
        self._data['item_id'] = value
        self._dirty = True

    def set_quantity(self, value: float) -> None:
        """Set the value of quantity."""
        self._data['quantity'] = value
        self._dirty = True

    def set_is_max_stacked(self, value: Optional[int]) -> None:
        """Set the value of is_max_stacked."""
        self._data['is_max_stacked'] = value
        self._dirty = True

    def set_mobile_item_id(self, value: Optional[int]) -> None:
        """Set the value of mobile_item_id."""
        self._data['mobile_item_id'] = value
        self._dirty = True

    def get_inventory(self, strict: bool = False) -> 'Inventory':
        """
        Get the associated Inventory for this inventory relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_inventory_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_inventory_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Inventory.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has inventory_id={fk_value} but no Inventory record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_inventory(self, model: 'Inventory') -> None:
        """
        Set the associated Inventory for this inventory relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Inventory instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_inventory_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_inventory_id(None)
        else:
            self.set_inventory_id(model.get_id())

    def get_item(self, strict: bool = False) -> 'Item':
        """
        Get the associated Item for this item relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_item_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_item_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Item.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has item_id={fk_value} but no Item record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_item(self, model: 'Item') -> None:
        """
        Set the associated Item for this item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_id(None)
        else:
            self.set_item_id(model.get_id())

    def get_mobile_item(self, strict: bool = False) -> Optional['MobileItem']:
        """
        Get the associated MobileItem for this mobile_item relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_mobile_item_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_mobile_item_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = MobileItem.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has mobile_item_id={fk_value} but no MobileItem record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_mobile_item(self, model: Optional['MobileItem']) -> None:
        """
        Set the associated MobileItem for this mobile_item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The MobileItem instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_mobile_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_item_id(None)
        else:
            self.set_mobile_item_id(model.get_id())



    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                # Save inventory if cached and dirty
                cache_key = '_inventory_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['inventory_id'] = related.get_id()
# Save item if cached and dirty
                cache_key = '_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_id'] = related.get_id()
# Save mobile_item if cached and dirty
                cache_key = '_mobile_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['mobile_item_id'] = related.get_id()

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `inventory_entries` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `inventory_entries` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                pass  # No has-many relationships

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['InventoryEntry']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = InventoryEntry()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `inventory_entries` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_inventory_id(value: int) -> List['InventoryEntry']:
        """
        Find all records by inventory_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventory_entries` WHERE `inventory_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = InventoryEntry()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_item_id(value: int) -> List['InventoryEntry']:
        """
        Find all records by item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventory_entries` WHERE `item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = InventoryEntry()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_mobile_item_id(value: int) -> List['InventoryEntry']:
        """
        Find all records by mobile_item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventory_entries` WHERE `mobile_item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = InventoryEntry()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class InventoryOwner:
    """
    ActiveRecord-style model for the inventory_owners table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `inventory_owners` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `inventory_id` bigint NOT NULL,
          `mobile_id` bigint DEFAULT NULL,
          `item_id` bigint DEFAULT NULL,
          `asset_id` bigint DEFAULT NULL,
          `player_id` bigint DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `inventory_id` (`inventory_id`),
          CONSTRAINT `inventory_owners_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventories` (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_inventory_id(self) -> int:
        """Get the value of inventory_id."""
        return self._data.get('inventory_id')

    def get_mobile_id(self) -> Optional[int]:
        """Get the value of mobile_id."""
        return self._data.get('mobile_id')

    def get_item_id(self) -> Optional[int]:
        """Get the value of item_id."""
        return self._data.get('item_id')

    def get_asset_id(self) -> Optional[int]:
        """Get the value of asset_id."""
        return self._data.get('asset_id')

    def get_player_id(self) -> Optional[int]:
        """Get the value of player_id."""
        return self._data.get('player_id')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_inventory_id(self, value: int) -> None:
        """Set the value of inventory_id."""
        self._data['inventory_id'] = value
        self._dirty = True

    def set_mobile_id(self, value: Optional[int]) -> None:
        """Set the value of mobile_id."""
        self._data['mobile_id'] = value
        self._dirty = True

    def set_item_id(self, value: Optional[int]) -> None:
        """Set the value of item_id."""
        self._data['item_id'] = value
        self._dirty = True

    def set_asset_id(self, value: Optional[int]) -> None:
        """Set the value of asset_id."""
        self._data['asset_id'] = value
        self._dirty = True

    def set_player_id(self, value: Optional[int]) -> None:
        """Set the value of player_id."""
        self._data['player_id'] = value
        self._dirty = True

    def get_inventory(self, strict: bool = False) -> 'Inventory':
        """
        Get the associated Inventory for this inventory relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_inventory_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_inventory_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Inventory.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has inventory_id={fk_value} but no Inventory record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_inventory(self, model: 'Inventory') -> None:
        """
        Set the associated Inventory for this inventory relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Inventory instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_inventory_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_inventory_id(None)
        else:
            self.set_inventory_id(model.get_id())

    def get_mobile(self, strict: bool = False) -> Optional['Mobile']:
        """
        Get the associated Mobile for this mobile relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_mobile_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_mobile_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Mobile.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has mobile_id={fk_value} but no Mobile record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_mobile(self, model: Optional['Mobile']) -> None:
        """
        Set the associated Mobile for this mobile relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Mobile instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_mobile_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_id(None)
        else:
            self.set_mobile_id(model.get_id())

    def get_item(self, strict: bool = False) -> Optional['Item']:
        """
        Get the associated Item for this item relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_item_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_item_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Item.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has item_id={fk_value} but no Item record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_item(self, model: Optional['Item']) -> None:
        """
        Set the associated Item for this item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_id(None)
        else:
            self.set_item_id(model.get_id())

    def get_player(self, strict: bool = False) -> Optional['Player']:
        """
        Get the associated Player for this player relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_player_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_player_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Player.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has player_id={fk_value} but no Player record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_player(self, model: Optional['Player']) -> None:
        """
        Set the associated Player for this player relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Player instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_player_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_player_id(None)
        else:
            self.set_player_id(model.get_id())



    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                # Save inventory if cached and dirty
                cache_key = '_inventory_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['inventory_id'] = related.get_id()
# Save mobile if cached and dirty
                cache_key = '_mobile_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['mobile_id'] = related.get_id()
# Save item if cached and dirty
                cache_key = '_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_id'] = related.get_id()
# Save player if cached and dirty
                cache_key = '_player_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['player_id'] = related.get_id()

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `inventory_owners` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `inventory_owners` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                pass  # No has-many relationships

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['InventoryOwner']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = InventoryOwner()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `inventory_owners` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_inventory_id(value: int) -> List['InventoryOwner']:
        """
        Find all records by inventory_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventory_owners` WHERE `inventory_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = InventoryOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_mobile_id(value: int) -> List['InventoryOwner']:
        """
        Find all records by mobile_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventory_owners` WHERE `mobile_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = InventoryOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_item_id(value: int) -> List['InventoryOwner']:
        """
        Find all records by item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventory_owners` WHERE `item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = InventoryOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_asset_id(value: int) -> List['InventoryOwner']:
        """
        Find all records by asset_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventory_owners` WHERE `asset_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = InventoryOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_player_id(value: int) -> List['InventoryOwner']:
        """
        Find all records by player_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `inventory_owners` WHERE `player_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = InventoryOwner()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class ItemBlueprintComponent:
    """
    ActiveRecord-style model for the item_blueprint_components table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `item_blueprint_components` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `item_blueprint_id` bigint NOT NULL,
          `component_item_id` bigint NOT NULL,
          `ratio` double NOT NULL,
          PRIMARY KEY (`id`),
          KEY `item_blueprint_id` (`item_blueprint_id`),
          CONSTRAINT `item_blueprint_components_ibfk_1` FOREIGN KEY (`item_blueprint_id`) REFERENCES `item_blueprints` (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_item_blueprint_id(self) -> int:
        """Get the value of item_blueprint_id."""
        return self._data.get('item_blueprint_id')

    def get_component_item_id(self) -> int:
        """Get the value of component_item_id."""
        return self._data.get('component_item_id')

    def get_ratio(self) -> float:
        """Get the value of ratio."""
        return self._data.get('ratio')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_item_blueprint_id(self, value: int) -> None:
        """Set the value of item_blueprint_id."""
        self._data['item_blueprint_id'] = value
        self._dirty = True

    def set_component_item_id(self, value: int) -> None:
        """Set the value of component_item_id."""
        self._data['component_item_id'] = value
        self._dirty = True

    def set_ratio(self, value: float) -> None:
        """Set the value of ratio."""
        self._data['ratio'] = value
        self._dirty = True

    def get_item_blueprint(self, strict: bool = False) -> 'ItemBlueprint':
        """
        Get the associated ItemBlueprint for this item_blueprint relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_item_blueprint_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_item_blueprint_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = ItemBlueprint.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has item_blueprint_id={fk_value} but no ItemBlueprint record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_item_blueprint(self, model: 'ItemBlueprint') -> None:
        """
        Set the associated ItemBlueprint for this item_blueprint relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The ItemBlueprint instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_item_blueprint_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_blueprint_id(None)
        else:
            self.set_item_blueprint_id(model.get_id())



    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                # Save item_blueprint if cached and dirty
                cache_key = '_item_blueprint_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_blueprint_id'] = related.get_id()

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `item_blueprint_components` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `item_blueprint_components` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                pass  # No has-many relationships

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['ItemBlueprintComponent']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = ItemBlueprintComponent()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `item_blueprint_components` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_item_blueprint_id(value: int) -> List['ItemBlueprintComponent']:
        """
        Find all records by item_blueprint_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `item_blueprint_components` WHERE `item_blueprint_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = ItemBlueprintComponent()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_component_item_id(value: int) -> List['ItemBlueprintComponent']:
        """
        Find all records by component_item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `item_blueprint_components` WHERE `component_item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = ItemBlueprintComponent()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class ItemBlueprint:
    """
    ActiveRecord-style model for the item_blueprints table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `item_blueprints` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `bake_time_ms` bigint NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_bake_time_ms(self) -> int:
        """Get the value of bake_time_ms."""
        return self._data.get('bake_time_ms')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_bake_time_ms(self, value: int) -> None:
        """Set the value of bake_time_ms."""
        self._data['bake_time_ms'] = value
        self._dirty = True



    def get_item_blueprint_components(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated ItemBlueprintComponent records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[ItemBlueprintComponent] or Iterator[ItemBlueprintComponent]
        """
        cache_key = '_item_blueprint_components_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = ItemBlueprintComponent.find_by_item_blueprint_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                pass  # No belongs-to relationships

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `item_blueprints` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `item_blueprints` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                # Save item_blueprint_components if cached
                cache_key = '_item_blueprint_components_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['ItemBlueprint']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = ItemBlueprint()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `item_blueprints` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    # No find_by methods (no columns ending with _id)



class Item:
    """
    ActiveRecord-style model for the items table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `items` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `internal_name` varchar(255) NOT NULL,
          `max_stack_size` bigint DEFAULT NULL,
          `item_type` varchar(50) NOT NULL,
          `blueprint_id` bigint DEFAULT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1091 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_internal_name(self) -> str:
        """Get the value of internal_name."""
        return self._data.get('internal_name')

    def get_max_stack_size(self) -> Optional[int]:
        """Get the value of max_stack_size."""
        return self._data.get('max_stack_size')

    def get_item_type(self) -> str:
        """Get the value of item_type."""
        return self._data.get('item_type')

    def get_blueprint_id(self) -> Optional[int]:
        """Get the value of blueprint_id."""
        return self._data.get('blueprint_id')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_internal_name(self, value: str) -> None:
        """Set the value of internal_name."""
        self._data['internal_name'] = value
        self._dirty = True

    def set_max_stack_size(self, value: Optional[int]) -> None:
        """Set the value of max_stack_size."""
        self._data['max_stack_size'] = value
        self._dirty = True

    def set_item_type(self, value: str) -> None:
        """Set the value of item_type."""
        self._data['item_type'] = value
        self._dirty = True

    def set_blueprint_id(self, value: Optional[int]) -> None:
        """Set the value of blueprint_id."""
        self._data['blueprint_id'] = value
        self._dirty = True



    def get_attribute_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated AttributeOwner records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[AttributeOwner] or Iterator[AttributeOwner]
        """
        cache_key = '_attribute_owners_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = AttributeOwner.find_by_item_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_inventory_entries(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated InventoryEntry records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryEntry] or Iterator[InventoryEntry]
        """
        cache_key = '_inventory_entries_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = InventoryEntry.find_by_item_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_inventory_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated InventoryOwner records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryOwner] or Iterator[InventoryOwner]
        """
        cache_key = '_inventory_owners_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = InventoryOwner.find_by_item_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_mobile_items(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated MobileItem records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[MobileItem] or Iterator[MobileItem]
        """
        cache_key = '_mobile_items_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = MobileItem.find_by_item_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_mobiles(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated Mobile records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[Mobile] or Iterator[Mobile]
        """
        cache_key = '_mobiles_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = Mobile.find_by_owner_item_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                pass  # No belongs-to relationships

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `items` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `items` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                # Save attribute_owners if cached
                cache_key = '_attribute_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save inventory_entries if cached
                cache_key = '_inventory_entries_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save inventory_owners if cached
                cache_key = '_inventory_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save mobile_items if cached
                cache_key = '_mobile_items_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save mobiles if cached
                cache_key = '_mobiles_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['Item']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = Item()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `items` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_blueprint_id(value: int) -> List['Item']:
        """
        Find all records by blueprint_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `items` WHERE `blueprint_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = Item()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class MobileItemAttribute:
    """
    ActiveRecord-style model for the mobile_item_attributes table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `mobile_item_attributes` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `mobile_item_id` bigint NOT NULL,
          `internal_name` varchar(255) NOT NULL,
          `visible` tinyint(1) NOT NULL,
          `attribute_type` varchar(50) NOT NULL,
          `bool_value` tinyint(1) DEFAULT NULL,
          `double_value` double DEFAULT NULL,
          `vector3_x` double DEFAULT NULL,
          `vector3_y` double DEFAULT NULL,
          `vector3_z` double DEFAULT NULL,
          `asset_id` bigint DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `mobile_item_id` (`mobile_item_id`),
          CONSTRAINT `mobile_item_attributes_ibfk_1` FOREIGN KEY (`mobile_item_id`) REFERENCES `mobile_items` (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_mobile_item_id(self) -> int:
        """Get the value of mobile_item_id."""
        return self._data.get('mobile_item_id')

    def get_internal_name(self) -> str:
        """Get the value of internal_name."""
        return self._data.get('internal_name')

    def get_visible(self) -> int:
        """Get the value of visible."""
        return self._data.get('visible')

    def get_attribute_type(self) -> str:
        """Get the value of attribute_type."""
        return self._data.get('attribute_type')

    def get_bool_value(self) -> Optional[int]:
        """Get the value of bool_value."""
        return self._data.get('bool_value')

    def get_double_value(self) -> Optional[float]:
        """Get the value of double_value."""
        return self._data.get('double_value')

    def get_vector3_x(self) -> Optional[float]:
        """Get the value of vector3_x."""
        return self._data.get('vector3_x')

    def get_vector3_y(self) -> Optional[float]:
        """Get the value of vector3_y."""
        return self._data.get('vector3_y')

    def get_vector3_z(self) -> Optional[float]:
        """Get the value of vector3_z."""
        return self._data.get('vector3_z')

    def get_asset_id(self) -> Optional[int]:
        """Get the value of asset_id."""
        return self._data.get('asset_id')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_mobile_item_id(self, value: int) -> None:
        """Set the value of mobile_item_id."""
        self._data['mobile_item_id'] = value
        self._dirty = True

    def set_internal_name(self, value: str) -> None:
        """Set the value of internal_name."""
        self._data['internal_name'] = value
        self._dirty = True

    def set_visible(self, value: int) -> None:
        """Set the value of visible."""
        self._data['visible'] = value
        self._dirty = True

    def set_attribute_type(self, value: str) -> None:
        """Set the value of attribute_type."""
        self._data['attribute_type'] = value
        self._dirty = True

    def set_bool_value(self, value: Optional[int]) -> None:
        """Set the value of bool_value."""
        self._data['bool_value'] = value
        self._dirty = True

    def set_double_value(self, value: Optional[float]) -> None:
        """Set the value of double_value."""
        self._data['double_value'] = value
        self._dirty = True

    def set_vector3_x(self, value: Optional[float]) -> None:
        """Set the value of vector3_x."""
        self._data['vector3_x'] = value
        self._dirty = True

    def set_vector3_y(self, value: Optional[float]) -> None:
        """Set the value of vector3_y."""
        self._data['vector3_y'] = value
        self._dirty = True

    def set_vector3_z(self, value: Optional[float]) -> None:
        """Set the value of vector3_z."""
        self._data['vector3_z'] = value
        self._dirty = True

    def set_asset_id(self, value: Optional[int]) -> None:
        """Set the value of asset_id."""
        self._data['asset_id'] = value
        self._dirty = True

    def get_mobile_item(self, strict: bool = False) -> 'MobileItem':
        """
        Get the associated MobileItem for this mobile_item relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_mobile_item_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_mobile_item_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = MobileItem.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has mobile_item_id={fk_value} but no MobileItem record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_mobile_item(self, model: 'MobileItem') -> None:
        """
        Set the associated MobileItem for this mobile_item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The MobileItem instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_mobile_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_item_id(None)
        else:
            self.set_mobile_item_id(model.get_id())



    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                # Save mobile_item if cached and dirty
                cache_key = '_mobile_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['mobile_item_id'] = related.get_id()

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `mobile_item_attributes` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `mobile_item_attributes` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                pass  # No has-many relationships

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['MobileItemAttribute']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = MobileItemAttribute()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_attributes` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_mobile_item_id(value: int) -> List['MobileItemAttribute']:
        """
        Find all records by mobile_item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_attributes` WHERE `mobile_item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = MobileItemAttribute()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_asset_id(value: int) -> List['MobileItemAttribute']:
        """
        Find all records by asset_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_attributes` WHERE `asset_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = MobileItemAttribute()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class MobileItemBlueprintComponent:
    """
    ActiveRecord-style model for the mobile_item_blueprint_components table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `mobile_item_blueprint_components` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `item_blueprint_id` bigint NOT NULL,
          `component_item_id` bigint NOT NULL,
          `ratio` double NOT NULL,
          PRIMARY KEY (`id`),
          KEY `item_blueprint_id` (`item_blueprint_id`),
          CONSTRAINT `mobile_item_blueprint_components_ibfk_1` FOREIGN KEY (`item_blueprint_id`) REFERENCES `mobile_item_blueprints` (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_item_blueprint_id(self) -> int:
        """Get the value of item_blueprint_id."""
        return self._data.get('item_blueprint_id')

    def get_component_item_id(self) -> int:
        """Get the value of component_item_id."""
        return self._data.get('component_item_id')

    def get_ratio(self) -> float:
        """Get the value of ratio."""
        return self._data.get('ratio')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_item_blueprint_id(self, value: int) -> None:
        """Set the value of item_blueprint_id."""
        self._data['item_blueprint_id'] = value
        self._dirty = True

    def set_component_item_id(self, value: int) -> None:
        """Set the value of component_item_id."""
        self._data['component_item_id'] = value
        self._dirty = True

    def set_ratio(self, value: float) -> None:
        """Set the value of ratio."""
        self._data['ratio'] = value
        self._dirty = True

    def get_item_blueprint(self, strict: bool = False) -> 'MobileItemBlueprint':
        """
        Get the associated MobileItemBlueprint for this item_blueprint relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_item_blueprint_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_item_blueprint_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = MobileItemBlueprint.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has item_blueprint_id={fk_value} but no MobileItemBlueprint record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_item_blueprint(self, model: 'MobileItemBlueprint') -> None:
        """
        Set the associated MobileItemBlueprint for this item_blueprint relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The MobileItemBlueprint instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_item_blueprint_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_blueprint_id(None)
        else:
            self.set_item_blueprint_id(model.get_id())



    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                # Save item_blueprint if cached and dirty
                cache_key = '_item_blueprint_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_blueprint_id'] = related.get_id()

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `mobile_item_blueprint_components` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `mobile_item_blueprint_components` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                pass  # No has-many relationships

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['MobileItemBlueprintComponent']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = MobileItemBlueprintComponent()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_blueprint_components` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_item_blueprint_id(value: int) -> List['MobileItemBlueprintComponent']:
        """
        Find all records by item_blueprint_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_blueprint_components` WHERE `item_blueprint_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = MobileItemBlueprintComponent()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_component_item_id(value: int) -> List['MobileItemBlueprintComponent']:
        """
        Find all records by component_item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_blueprint_components` WHERE `component_item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = MobileItemBlueprintComponent()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class MobileItemBlueprint:
    """
    ActiveRecord-style model for the mobile_item_blueprints table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `mobile_item_blueprints` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `bake_time_ms` bigint NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_bake_time_ms(self) -> int:
        """Get the value of bake_time_ms."""
        return self._data.get('bake_time_ms')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_bake_time_ms(self, value: int) -> None:
        """Set the value of bake_time_ms."""
        self._data['bake_time_ms'] = value
        self._dirty = True



    def get_mobile_item_blueprint_components(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated MobileItemBlueprintComponent records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[MobileItemBlueprintComponent] or Iterator[MobileItemBlueprintComponent]
        """
        cache_key = '_mobile_item_blueprint_components_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = MobileItemBlueprintComponent.find_by_item_blueprint_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                pass  # No belongs-to relationships

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `mobile_item_blueprints` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `mobile_item_blueprints` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                # Save mobile_item_blueprint_components if cached
                cache_key = '_mobile_item_blueprint_components_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['MobileItemBlueprint']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = MobileItemBlueprint()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_blueprints` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    # No find_by methods (no columns ending with _id)



class MobileItem:
    """
    ActiveRecord-style model for the mobile_items table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `mobile_items` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `mobile_id` bigint NOT NULL,
          `internal_name` varchar(255) NOT NULL,
          `max_stack_size` bigint DEFAULT NULL,
          `item_type` varchar(50) NOT NULL,
          `blueprint_id` bigint DEFAULT NULL,
          `item_id` bigint NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_mobile_id(self) -> int:
        """Get the value of mobile_id."""
        return self._data.get('mobile_id')

    def get_internal_name(self) -> str:
        """Get the value of internal_name."""
        return self._data.get('internal_name')

    def get_max_stack_size(self) -> Optional[int]:
        """Get the value of max_stack_size."""
        return self._data.get('max_stack_size')

    def get_item_type(self) -> str:
        """Get the value of item_type."""
        return self._data.get('item_type')

    def get_blueprint_id(self) -> Optional[int]:
        """Get the value of blueprint_id."""
        return self._data.get('blueprint_id')

    def get_item_id(self) -> int:
        """Get the value of item_id."""
        return self._data.get('item_id')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_mobile_id(self, value: int) -> None:
        """Set the value of mobile_id."""
        self._data['mobile_id'] = value
        self._dirty = True

    def set_internal_name(self, value: str) -> None:
        """Set the value of internal_name."""
        self._data['internal_name'] = value
        self._dirty = True

    def set_max_stack_size(self, value: Optional[int]) -> None:
        """Set the value of max_stack_size."""
        self._data['max_stack_size'] = value
        self._dirty = True

    def set_item_type(self, value: str) -> None:
        """Set the value of item_type."""
        self._data['item_type'] = value
        self._dirty = True

    def set_blueprint_id(self, value: Optional[int]) -> None:
        """Set the value of blueprint_id."""
        self._data['blueprint_id'] = value
        self._dirty = True

    def set_item_id(self, value: int) -> None:
        """Set the value of item_id."""
        self._data['item_id'] = value
        self._dirty = True

    def get_mobile(self, strict: bool = False) -> 'Mobile':
        """
        Get the associated Mobile for this mobile relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_mobile_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_mobile_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Mobile.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has mobile_id={fk_value} but no Mobile record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_mobile(self, model: 'Mobile') -> None:
        """
        Set the associated Mobile for this mobile relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Mobile instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_mobile_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_id(None)
        else:
            self.set_mobile_id(model.get_id())

    def get_item(self, strict: bool = False) -> 'Item':
        """
        Get the associated Item for this item relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_item_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_item_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Item.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has item_id={fk_value} but no Item record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_item(self, model: 'Item') -> None:
        """
        Set the associated Item for this item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_id(None)
        else:
            self.set_item_id(model.get_id())

    def get_inventory_entries(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated InventoryEntry records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryEntry] or Iterator[InventoryEntry]
        """
        cache_key = '_inventory_entries_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = InventoryEntry.find_by_mobile_item_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_mobile_item_attributes(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated MobileItemAttribute records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[MobileItemAttribute] or Iterator[MobileItemAttribute]
        """
        cache_key = '_mobile_item_attributes_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = MobileItemAttribute.find_by_mobile_item_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                # Save mobile if cached and dirty
                cache_key = '_mobile_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['mobile_id'] = related.get_id()
# Save item if cached and dirty
                cache_key = '_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_id'] = related.get_id()

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `mobile_items` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `mobile_items` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                # Save inventory_entries if cached
                cache_key = '_inventory_entries_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save mobile_item_attributes if cached
                cache_key = '_mobile_item_attributes_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['MobileItem']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = MobileItem()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobile_items` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_mobile_id(value: int) -> List['MobileItem']:
        """
        Find all records by mobile_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobile_items` WHERE `mobile_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = MobileItem()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_blueprint_id(value: int) -> List['MobileItem']:
        """
        Find all records by blueprint_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobile_items` WHERE `blueprint_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = MobileItem()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_item_id(value: int) -> List['MobileItem']:
        """
        Find all records by item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobile_items` WHERE `item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = MobileItem()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class Mobile:
    """
    ActiveRecord-style model for the mobiles table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `mobiles` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `mobile_type` varchar(50) NOT NULL,
          `owner_mobile_id` bigint DEFAULT NULL,
          `owner_item_id` bigint DEFAULT NULL,
          `owner_asset_id` bigint DEFAULT NULL,
          `owner_player_id` bigint DEFAULT NULL,
          `what_we_call_you` varchar(255) NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_mobile_type(self) -> str:
        """Get the value of mobile_type."""
        return self._data.get('mobile_type')

    def get_owner_mobile_id(self) -> Optional[int]:
        """Get the value of owner_mobile_id."""
        return self._data.get('owner_mobile_id')

    def get_owner_item_id(self) -> Optional[int]:
        """Get the value of owner_item_id."""
        return self._data.get('owner_item_id')

    def get_owner_asset_id(self) -> Optional[int]:
        """Get the value of owner_asset_id."""
        return self._data.get('owner_asset_id')

    def get_owner_player_id(self) -> Optional[int]:
        """Get the value of owner_player_id."""
        return self._data.get('owner_player_id')

    def get_what_we_call_you(self) -> str:
        """Get the value of what_we_call_you."""
        return self._data.get('what_we_call_you')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_mobile_type(self, value: str) -> None:
        """Set the value of mobile_type."""
        self._data['mobile_type'] = value
        self._dirty = True

    def set_owner_mobile_id(self, value: Optional[int]) -> None:
        """Set the value of owner_mobile_id."""
        self._data['owner_mobile_id'] = value
        self._dirty = True

    def set_owner_item_id(self, value: Optional[int]) -> None:
        """Set the value of owner_item_id."""
        self._data['owner_item_id'] = value
        self._dirty = True

    def set_owner_asset_id(self, value: Optional[int]) -> None:
        """Set the value of owner_asset_id."""
        self._data['owner_asset_id'] = value
        self._dirty = True

    def set_owner_player_id(self, value: Optional[int]) -> None:
        """Set the value of owner_player_id."""
        self._data['owner_player_id'] = value
        self._dirty = True

    def set_what_we_call_you(self, value: str) -> None:
        """Set the value of what_we_call_you."""
        self._data['what_we_call_you'] = value
        self._dirty = True

    def get_owner_mobile(self, strict: bool = False) -> Optional['Mobile']:
        """
        Get the associated Mobile for this owner_mobile relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_owner_mobile_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_owner_mobile_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Mobile.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has owner_mobile_id={fk_value} but no Mobile record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_owner_mobile(self, model: Optional['Mobile']) -> None:
        """
        Set the associated Mobile for this owner_mobile relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Mobile instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_owner_mobile_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_owner_mobile_id(None)
        else:
            self.set_owner_mobile_id(model.get_id())

    def get_owner_item(self, strict: bool = False) -> Optional['Item']:
        """
        Get the associated Item for this owner_item relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_owner_item_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_owner_item_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Item.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has owner_item_id={fk_value} but no Item record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_owner_item(self, model: Optional['Item']) -> None:
        """
        Set the associated Item for this owner_item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_owner_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_owner_item_id(None)
        else:
            self.set_owner_item_id(model.get_id())

    def get_owner_player(self, strict: bool = False) -> Optional['Player']:
        """
        Get the associated Player for this owner_player relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_owner_player_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_owner_player_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = Player.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has owner_player_id={fk_value} but no Player record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_owner_player(self, model: Optional['Player']) -> None:
        """
        Set the associated Player for this owner_player relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Player instance to associate, or None to clear.
        """
        # Update cache
        cache_key = '_owner_player_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_owner_player_id(None)
        else:
            self.set_owner_player_id(model.get_id())

    def get_attribute_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated AttributeOwner records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[AttributeOwner] or Iterator[AttributeOwner]
        """
        cache_key = '_attribute_owners_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = AttributeOwner.find_by_mobile_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_inventory_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated InventoryOwner records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryOwner] or Iterator[InventoryOwner]
        """
        cache_key = '_inventory_owners_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = InventoryOwner.find_by_mobile_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_mobile_items(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated MobileItem records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[MobileItem] or Iterator[MobileItem]
        """
        cache_key = '_mobile_items_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = MobileItem.find_by_mobile_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                # Save owner_mobile if cached and dirty
                cache_key = '_owner_mobile_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['owner_mobile_id'] = related.get_id()
# Save owner_item if cached and dirty
                cache_key = '_owner_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['owner_item_id'] = related.get_id()
# Save owner_player if cached and dirty
                cache_key = '_owner_player_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['owner_player_id'] = related.get_id()

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `mobiles` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `mobiles` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                # Save attribute_owners if cached
                cache_key = '_attribute_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save inventory_owners if cached
                cache_key = '_inventory_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save mobile_items if cached
                cache_key = '_mobile_items_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['Mobile']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = Mobile()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobiles` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    @staticmethod
    def find_by_owner_mobile_id(value: int) -> List['Mobile']:
        """
        Find all records by owner_mobile_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobiles` WHERE `owner_mobile_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = Mobile()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_owner_item_id(value: int) -> List['Mobile']:
        """
        Find all records by owner_item_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobiles` WHERE `owner_item_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = Mobile()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_owner_asset_id(value: int) -> List['Mobile']:
        """
        Find all records by owner_asset_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobiles` WHERE `owner_asset_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = Mobile()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results

    @staticmethod
    def find_by_owner_player_id(value: int) -> List['Mobile']:
        """
        Find all records by owner_player_id.
        Returns a list of instances with matching records.
        """
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `mobiles` WHERE `owner_player_id` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = Mobile()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results



class Player:
    """
    ActiveRecord-style model for the players table.
    Auto-generated - do not modify manually.
    """

    # CREATE TABLE statement for this model
    CREATE_TABLE_STATEMENT = """
        CREATE TABLE `players` (
          `id` bigint NOT NULL AUTO_INCREMENT,
          `full_name` varchar(255) NOT NULL,
          `what_we_call_you` varchar(255) NOT NULL,
          `security_token` varchar(255) NOT NULL,
          `over_13` tinyint(1) NOT NULL,
          `year_of_birth` bigint NOT NULL,
          `email` varchar(255) NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE,
                auth_plugin='mysql_native_password',
                ssl_disabled=True,
                use_pure=True,
            )

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        """Get the value of id."""
        return self._data.get('id')

    def get_full_name(self) -> str:
        """Get the value of full_name."""
        return self._data.get('full_name')

    def get_what_we_call_you(self) -> str:
        """Get the value of what_we_call_you."""
        return self._data.get('what_we_call_you')

    def get_security_token(self) -> str:
        """Get the value of security_token."""
        return self._data.get('security_token')

    def get_over_13(self) -> int:
        """Get the value of over_13."""
        return self._data.get('over_13')

    def get_year_of_birth(self) -> int:
        """Get the value of year_of_birth."""
        return self._data.get('year_of_birth')

    def get_email(self) -> str:
        """Get the value of email."""
        return self._data.get('email')

    def set_id(self, value: int) -> None:
        """Set the value of id."""
        self._data['id'] = value
        self._dirty = True

    def set_full_name(self, value: str) -> None:
        """Set the value of full_name."""
        self._data['full_name'] = value
        self._dirty = True

    def set_what_we_call_you(self, value: str) -> None:
        """Set the value of what_we_call_you."""
        self._data['what_we_call_you'] = value
        self._dirty = True

    def set_security_token(self, value: str) -> None:
        """Set the value of security_token."""
        self._data['security_token'] = value
        self._dirty = True

    def set_over_13(self, value: int) -> None:
        """Set the value of over_13."""
        self._data['over_13'] = value
        self._dirty = True

    def set_year_of_birth(self, value: int) -> None:
        """Set the value of year_of_birth."""
        self._data['year_of_birth'] = value
        self._dirty = True

    def set_email(self, value: str) -> None:
        """Set the value of email."""
        self._data['email'] = value
        self._dirty = True



    def get_attribute_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated AttributeOwner records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[AttributeOwner] or Iterator[AttributeOwner]
        """
        cache_key = '_attribute_owners_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = AttributeOwner.find_by_player_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_inventory_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated InventoryOwner records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryOwner] or Iterator[InventoryOwner]
        """
        cache_key = '_inventory_owners_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = InventoryOwner.find_by_player_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def get_mobiles(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated Mobile records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[Mobile] or Iterator[Mobile]
        """
        cache_key = '_mobiles_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = Mobile.find_by_owner_player_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results

    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Skip save if not dirty
        if not self._dirty:
            return

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction
            connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first
            if cascade:
                pass  # No belongs-to relationships

            cursor = connection.cursor()

            if 'id' in self._data and self._data['id'] is not None:
                # UPDATE existing record
                set_clause = ', '.join([f"`{col}` = %s" for col in self._data.keys() if col != 'id'])
                values = [self._data[col] for col in self._data.keys() if col != 'id']
                values.append(self._data['id'])

                query = f"UPDATE `players` SET {set_clause} WHERE `id` = %s"
                cursor.execute(query, tuple(values))
            else:
                # INSERT new record
                columns = [col for col in self._data.keys() if col != 'id']
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f"`{col}`" for col in columns])
                values = [self._data[col] for col in columns]

                query = f"INSERT INTO `players` ({column_names}) VALUES ({placeholders})"
                cursor.execute(query, tuple(values))
                self._data['id'] = cursor.lastrowid

            # Mark as clean after successful save
            self._dirty = False

            # Cascade save has-many relationships
            if cascade:
                # Save attribute_owners if cached
                cache_key = '_attribute_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save inventory_owners if cached
                cache_key = '_inventory_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save mobiles if cached
                cache_key = '_mobiles_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)

            # Only commit if we own the connection
            if owns_connection:
                connection.commit()

        except Exception as e:
            if owns_connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def find(id: int) -> Optional['Player']:
        """
        Find a record by its primary key (id).
        Returns an instance with the record loaded, or None if not found.
        """
        instance = Player()
        instance._connect()
        cursor = instance._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `players` WHERE `id` = %s", (id,))
            row = cursor.fetchone()
            if row:
                instance._data = row
                return instance
            return None
        finally:
            cursor.close()

    # No find_by methods (no columns ending with _id)


