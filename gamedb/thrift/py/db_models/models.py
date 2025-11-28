#!/usr/bin/env python3
"""
Auto-generated model classes for all database tables.
Generated from database schema - do not modify manually.
"""

import sys
import os

# Add Thrift generated code to path
thrift_gen_path = '/vagrant/gamedb/thrift/gen-py'
if thrift_gen_path not in sys.path:
    sys.path.insert(0, thrift_gen_path)

from dotenv import load_dotenv
from game.ttypes import GameResult as ThriftGameResult, StatusType as ThriftStatusType, GameError as ThriftGameError, Owner as ThriftOwner, AttributeValue as ThriftAttributeValue, AttributeType as ThriftAttributeType, ItemType as ThriftItemType, ItemVector3 as ThriftItemVector3, Attribute as ThriftAttribute, Item as ThriftItem, Mobile as ThriftMobile, Player as ThriftPlayer, MobileItem as ThriftMobileItem, Inventory as ThriftInventory, InventoryEntry as ThriftInventoryEntry, ItemBlueprint as ThriftItemBlueprint, ItemBlueprintComponent as ThriftItemBlueprintComponent
from typing import Dict, List, Optional, Any, Iterator, Union, Tuple
import mysql.connector

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
        ) ENGINE=InnoDB AUTO_INCREMENT=1523 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = AttributeOwner._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_attribute_id(self) -> int:
        return self._data.get('attribute_id')

    def get_mobile_id(self) -> Optional[int]:
        return self._data.get('mobile_id')

    def get_item_id(self) -> Optional[int]:
        return self._data.get('item_id')

    def get_asset_id(self) -> Optional[int]:
        return self._data.get('asset_id')

    def get_player_id(self) -> Optional[int]:
        return self._data.get('player_id')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_attribute_id(self, value: int) -> 'self.__class__':
        self._data['attribute_id'] = value
        self._dirty = True
        return self

    def set_mobile_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['mobile_id'] = value
        self._dirty = True
        return self

    def set_item_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['item_id'] = value
        self._dirty = True
        return self

    def set_asset_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['asset_id'] = value
        self._dirty = True
        return self

    def set_player_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['player_id'] = value
        self._dirty = True
        return self

    def is_mobile(self) -> bool:
        """Check if this pivot record belongs to a mobile."""
        return self.get_mobile_id() is not None


    def is_item(self) -> bool:
        """Check if this pivot record belongs to a item."""
        return self.get_item_id() is not None


    def is_asset(self) -> bool:
        """Check if this pivot record belongs to a asset."""
        return self.get_asset_id() is not None


    def is_player(self) -> bool:
        """Check if this pivot record belongs to a player."""
        return self.get_player_id() is not None


    def get_attribute(self, strict: bool = False) -> Optional['Attribute']:
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

    def set_attribute(self, model: 'Attribute') -> 'self.__class__':
        """
        Set the associated Attribute for this attribute relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Attribute instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_attribute_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_attribute_id(None)
        else:
            self.set_attribute_id(model.get_id())
        return self

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

    def set_mobile(self, model: Optional['Mobile']) -> 'self.__class__':
        """
        Set the associated Mobile for this mobile relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Mobile instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_mobile_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_id(None)
        else:
            self.set_mobile_id(model.get_id())
        return self

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

    def set_item(self, model: Optional['Item']) -> 'self.__class__':
        """
        Set the associated Item for this item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_id(None)
        else:
            self.set_item_id(model.get_id())
        return self

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

    def set_player(self, model: Optional['Player']) -> 'self.__class__':
        """
        Set the associated Player for this player relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Player instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_player_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_player_id(None)
        else:
            self.set_player_id(model.get_id())
        return self






    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
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

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                pass  # No cascade destroys needed

            # Delete the record itself
            cursor.execute(f"DELETE FROM `attribute_owners` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `attribute_owners` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_attribute_id(value: int) -> List['AttributeOwner']:
        """
        Find all records by attribute_id.
        Returns a list of instances with matching records.
        """
        connection = AttributeOwner._create_connection()
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
        connection = AttributeOwner._create_connection()
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
        connection = AttributeOwner._create_connection()
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
        connection = AttributeOwner._create_connection()
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
        connection = AttributeOwner._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=1809 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = Attribute._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_internal_name(self) -> str:
        return self._data.get('internal_name')

    def get_visible(self) -> int:
        return self._data.get('visible')

    def get_attribute_type(self) -> ThriftAttributeType:
        value = self._data.get('attribute_type')
        return getattr(ThriftAttributeType, value) if value is not None else None

    def get_bool_value(self) -> Optional[int]:
        return self._data.get('bool_value')

    def get_double_value(self) -> Optional[float]:
        return self._data.get('double_value')

    def get_vector3_x(self) -> Optional[float]:
        return self._data.get('vector3_x')

    def get_vector3_y(self) -> Optional[float]:
        return self._data.get('vector3_y')

    def get_vector3_z(self) -> Optional[float]:
        return self._data.get('vector3_z')

    def get_asset_id(self) -> Optional[int]:
        return self._data.get('asset_id')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_internal_name(self, value: str) -> 'self.__class__':
        self._data['internal_name'] = value
        self._dirty = True
        return self

    def set_visible(self, value: int) -> 'self.__class__':
        self._data['visible'] = value
        self._dirty = True
        return self

    def set_attribute_type(self, value: int) -> 'self.__class__':
        """
        Set the attribute_type field value.

        Python Thrift Enum Implementation Note:
        ----------------------------------------
        In Python, Thrift enums are implemented as integer constants on a class, not
        as a separate enum type. For example:
            - ThriftAttributeType.STRENGTH is just an int (e.g., 0)
            - ThriftAttributeType.DEXTERITY is just an int (e.g., 1)

        This is different from languages like Java or C++ where enums are distinct types.
        Python Thrift enums are essentially namespaced integer constants.

        Why this method accepts int:
        - Thrift enums in Python ARE ints, not a distinct type
        - Using isinstance(value, ThriftAttributeType) would fail (it's not a class you can instantiate)
        - Type checkers understand this: passing ThriftAttributeType.STRENGTH satisfies int type hint
        - This validates the value is a legitimate enum constant, rejecting invalid integers

        The method validates the integer is a valid enum value by reverse-lookup against
        the Thrift enum class constants, then stores the enum name as a string in the database.

        Args:
            value: Integer value of a ThriftAttributeType enum constant (e.g., ThriftAttributeType.STRENGTH)

        Returns:
            self for method chaining

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is not a valid ThriftAttributeType enum constant
        """
        if value is not None and not isinstance(value, int):
            raise TypeError(f"{value} must be an integer (Thrift enum), got {type(value).__name__}")
        # Convert enum integer to string name for storage
        if value is not None:
            # Reverse lookup: find the name for this enum value
            enum_name = None
            for attr_name in dir(ThriftAttributeType):
                if not attr_name.startswith('_'):
                    attr_val = getattr(ThriftAttributeType, attr_name)
                    if isinstance(attr_val, int) and attr_val == value:
                        enum_name = attr_name
                        break
            if enum_name is None:
                raise ValueError(f"{value} is not a valid ThriftAttributeType enum value")
            self._data['attribute_type'] = enum_name
        else:
            self._data['attribute_type'] = None
        self._dirty = True
        return self

    def set_bool_value(self, value: Optional[int]) -> 'self.__class__':
        self._data['bool_value'] = value
        self._dirty = True
        return self

    def set_double_value(self, value: Optional[float]) -> 'self.__class__':
        self._data['double_value'] = value
        self._dirty = True
        return self

    def set_vector3_x(self, value: Optional[float]) -> 'self.__class__':
        self._data['vector3_x'] = value
        self._dirty = True
        return self

    def set_vector3_y(self, value: Optional[float]) -> 'self.__class__':
        self._data['vector3_y'] = value
        self._dirty = True
        return self

    def set_vector3_z(self, value: Optional[float]) -> 'self.__class__':
        self._data['vector3_z'] = value
        self._dirty = True
        return self

    def set_asset_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['asset_id'] = value
        self._dirty = True
        return self




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



    def from_thrift(self, thrift_obj: 'Attribute') -> 'Attribute':
        """
        Populate this Model instance from a Thrift Attribute object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift Attribute instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'internal_name'):
            self._data['internal_name'] = thrift_obj.internal_name
        if hasattr(thrift_obj, 'visible'):
            self._data['visible'] = thrift_obj.visible
        if hasattr(thrift_obj, 'attribute_type'):
            if thrift_obj.attribute_type is not None:
                self._data['attribute_type'] = ThriftAttributeType._VALUES_TO_NAMES[thrift_obj.attribute_type]
            else:
                self._data['attribute_type'] = None

        # Convert ThriftAttributeValue union to flattened database columns
        if hasattr(thrift_obj, 'value') and thrift_obj.value is not None:
            value = thrift_obj.value
            # Reset all value fields to None first
            self._data['bool_value'] = None
            self._data['double_value'] = None
            self._data['vector3_x'] = None
            self._data['vector3_y'] = None
            self._data['vector3_z'] = None
            self._data['asset_id'] = None

            # Set the appropriate field based on which union field is set
            # Priority: vector3 -> asset_id -> double_value -> bool_value (default)
            if hasattr(value, 'vector3') and value.vector3 is not None:
                self._data['vector3_x'] = value.vector3.x
                self._data['vector3_y'] = value.vector3.y
                self._data['vector3_z'] = value.vector3.z
            elif hasattr(value, 'asset_id') and value.asset_id is not None:
                self._data['asset_id'] = value.asset_id
            elif hasattr(value, 'double_value') and value.double_value is not None:
                self._data['double_value'] = value.double_value
            else:
                # bool_value is the default/fallback
                if hasattr(value, 'bool_value') and value.bool_value is not None:
                    self._data['bool_value'] = value.bool_value
                else:
                    self._data['bool_value'] = False

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['Attribute']]:
        """
        Convert this Model instance to a Thrift Attribute object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['internal_name'] = self._data.get('internal_name')
            thrift_params['visible'] = self._data.get('visible')
            thrift_params['attribute_type'] = getattr(ThriftAttributeType, self._data.get('attribute_type')) if self._data.get('attribute_type') is not None else None

            # Convert flattened database columns to ThriftAttributeValue union
            # Priority: vector3 -> asset_id -> double_value -> bool_value (default)
            value = None
            if self._data.get('vector3_x') is not None:
                value = ThriftAttributeValue(
                    vector3=ThriftItemVector3(
                        x=self._data['vector3_x'],
                        y=self._data['vector3_y'],
                        z=self._data['vector3_z'],
                    ),
                )
            elif self._data.get('asset_id') is not None:
                value = ThriftAttributeValue(asset_id=self._data['asset_id'])
            elif self._data.get('double_value') is not None:
                value = ThriftAttributeValue(double_value=self._data['double_value'])
            else:
                # bool_value is the default/fallback
                value = ThriftAttributeValue(bool_value=self._data.get('bool_value', False))
            thrift_params['value'] = value

            # Create Thrift object
            thrift_obj = ThriftAttribute(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                pass  # No belongs-to relationships

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                # Cascade destroy attribute_owners children
                cache_key = '_attribute_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_attribute_owners(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist

            # Delete the record itself
            cursor.execute(f"DELETE FROM `attributes` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `attributes` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_asset_id(value: int) -> List['Attribute']:
        """
        Find all records by asset_id.
        Returns a list of instances with matching records.
        """
        connection = Attribute._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=511 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = Inventory._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_owner_id(self) -> int:
        return self._data.get('owner_id')

    def get_owner_type(self) -> Optional[str]:
        return self._data.get('owner_type')

    def get_max_entries(self) -> int:
        return self._data.get('max_entries')

    def get_max_volume(self) -> float:
        return self._data.get('max_volume')

    def get_last_calculated_volume(self) -> Optional[float]:
        return self._data.get('last_calculated_volume')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_owner_id(self, value: int) -> 'self.__class__':
        self._data['owner_id'] = value
        self._dirty = True
        return self

    def set_owner_type(self, value: Optional[str]) -> 'self.__class__':
        self._data['owner_type'] = value
        self._dirty = True
        return self

    def set_max_entries(self, value: int) -> 'self.__class__':
        self._data['max_entries'] = value
        self._dirty = True
        return self

    def set_max_volume(self, value: float) -> 'self.__class__':
        self._data['max_volume'] = value
        self._dirty = True
        return self

    def set_last_calculated_volume(self, value: Optional[float]) -> 'self.__class__':
        self._data['last_calculated_volume'] = value
        self._dirty = True
        return self


    def validate_owner(self) -> None:
        """
        Validate Owner union: exactly one owner must be set and must be valid type.

        Raises:
            ValueError: If validation fails
        """
        owner_fks = {
            'player': self.get_owner_player_id(),
            'mobile': self.get_owner_mobile_id(),
            'item': self.get_owner_item_id(),
            'asset': self.get_owner_asset_id(),
        }

        # Check exactly one is set
        set_owners = [k for k, v in owner_fks.items() if v is not None]
        if len(set_owners) == 0:
            raise ValueError("Inventory must have exactly one owner (none set)")
        if len(set_owners) > 1:
            raise ValueError(f"Inventory must have exactly one owner (multiple set: {set_owners})")

        # Check valid type for this table
        valid_types = ['player', 'mobile', 'item', 'asset']
        if set_owners[0] not in valid_types:
            raise ValueError(f"Inventory cannot be owned by {set_owners[0]} (valid types: {valid_types})")





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



    def from_thrift(self, thrift_obj: 'Inventory') -> 'Inventory':
        """
        Populate this Model instance from a Thrift Inventory object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift Inventory instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'max_entries'):
            self._data['max_entries'] = thrift_obj.max_entries
        if hasattr(thrift_obj, 'max_volume'):
            self._data['max_volume'] = thrift_obj.max_volume
        if hasattr(thrift_obj, 'last_calculated_volume'):
            self._data['last_calculated_volume'] = thrift_obj.last_calculated_volume

        # Convert ThriftOwner union to database owner_id and owner_type columns
        if hasattr(thrift_obj, 'owner') and thrift_obj.owner is not None:
            owner = thrift_obj.owner
            # Determine owner_id and owner_type based on which union field is set
            if hasattr(owner, 'player_id') and owner.player_id is not None:
                self._data['owner_id'] = owner.player_id
                self._data['owner_type'] = 'player'
            elif hasattr(owner, 'mobile_id') and owner.mobile_id is not None:
                self._data['owner_id'] = owner.mobile_id
                self._data['owner_type'] = 'mobile'
            elif hasattr(owner, 'item_id') and owner.item_id is not None:
                self._data['owner_id'] = owner.item_id
                self._data['owner_type'] = 'item'
            elif hasattr(owner, 'asset_id') and owner.asset_id is not None:
                self._data['owner_id'] = owner.asset_id
                self._data['owner_type'] = 'asset'

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['Inventory']]:
        """
        Convert this Model instance to a Thrift Inventory object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['max_entries'] = self._data.get('max_entries')
            thrift_params['max_volume'] = self._data.get('max_volume')
            thrift_params['last_calculated_volume'] = self._data.get('last_calculated_volume')

            # Convert database owner_id and owner_type to ThriftOwner union
            owner = None
            owner_id = self._data.get('owner_id')
            owner_type = self._data.get('owner_type')
            if owner_id is not None and owner_type is not None:
                if owner_type == 'player':
                    owner = ThriftOwner(player_id=owner_id)
                elif owner_type == 'mobile':
                    owner = ThriftOwner(mobile_id=owner_id)
                elif owner_type == 'item':
                    owner = ThriftOwner(item_id=owner_id)
                elif owner_type == 'asset':
                    owner = ThriftOwner(asset_id=owner_id)
            thrift_params['owner'] = owner

            # Create Thrift object
            thrift_obj = ThriftInventory(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                pass  # No belongs-to relationships

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                # Cascade destroy inventory_entries children
                cache_key = '_inventory_entries_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_inventory_entries(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy inventory_owners children
                cache_key = '_inventory_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_inventory_owners(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist

            # Delete the record itself
            cursor.execute(f"DELETE FROM `inventories` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `inventories` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_owner_id(value: int) -> List['Inventory']:
        """
        Find all records by owner_id.
        Returns a list of instances with matching records.
        """
        connection = Inventory._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=540 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = InventoryEntry._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_inventory_id(self) -> int:
        return self._data.get('inventory_id')

    def get_item_id(self) -> int:
        return self._data.get('item_id')

    def get_quantity(self) -> float:
        return self._data.get('quantity')

    def get_is_max_stacked(self) -> Optional[int]:
        return self._data.get('is_max_stacked')

    def get_mobile_item_id(self) -> Optional[int]:
        return self._data.get('mobile_item_id')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_inventory_id(self, value: int) -> 'self.__class__':
        self._data['inventory_id'] = value
        self._dirty = True
        return self

    def set_item_id(self, value: int) -> 'self.__class__':
        self._data['item_id'] = value
        self._dirty = True
        return self

    def set_quantity(self, value: float) -> 'self.__class__':
        self._data['quantity'] = value
        self._dirty = True
        return self

    def set_is_max_stacked(self, value: Optional[int]) -> 'self.__class__':
        self._data['is_max_stacked'] = value
        self._dirty = True
        return self

    def set_mobile_item_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['mobile_item_id'] = value
        self._dirty = True
        return self


    def get_inventory(self, strict: bool = False) -> Optional['Inventory']:
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

    def set_inventory(self, model: 'Inventory') -> 'self.__class__':
        """
        Set the associated Inventory for this inventory relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Inventory instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_inventory_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_inventory_id(None)
        else:
            self.set_inventory_id(model.get_id())
        return self

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

    def set_item(self, model: 'Item') -> 'self.__class__':
        """
        Set the associated Item for this item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_id(None)
        else:
            self.set_item_id(model.get_id())
        return self

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

    def set_mobile_item(self, model: Optional['MobileItem']) -> 'self.__class__':
        """
        Set the associated MobileItem for this mobile_item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The MobileItem instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_mobile_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_item_id(None)
        else:
            self.set_mobile_item_id(model.get_id())
        return self





    def from_thrift(self, thrift_obj: 'InventoryEntry') -> 'InventoryEntry':
        """
        Populate this Model instance from a Thrift InventoryEntry object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift InventoryEntry instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'inventory_id'):
            self._data['inventory_id'] = thrift_obj.inventory_id
        if hasattr(thrift_obj, 'item_id'):
            self._data['item_id'] = thrift_obj.item_id
        if hasattr(thrift_obj, 'quantity'):
            self._data['quantity'] = thrift_obj.quantity
        if hasattr(thrift_obj, 'is_max_stacked'):
            self._data['is_max_stacked'] = thrift_obj.is_max_stacked
        if hasattr(thrift_obj, 'mobile_item_id'):
            self._data['mobile_item_id'] = thrift_obj.mobile_item_id

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['InventoryEntry']]:
        """
        Convert this Model instance to a Thrift InventoryEntry object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['quantity'] = self._data.get('quantity')
            thrift_params['is_max_stacked'] = self._data.get('is_max_stacked')

            # Create Thrift object
            thrift_obj = ThriftInventoryEntry(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
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

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                pass  # No cascade destroys needed

            # Delete the record itself
            cursor.execute(f"DELETE FROM `inventory_entries` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `inventory_entries` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_inventory_id(value: int) -> List['InventoryEntry']:
        """
        Find all records by inventory_id.
        Returns a list of instances with matching records.
        """
        connection = InventoryEntry._create_connection()
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
        connection = InventoryEntry._create_connection()
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
        connection = InventoryEntry._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=803 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = InventoryOwner._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_inventory_id(self) -> int:
        return self._data.get('inventory_id')

    def get_mobile_id(self) -> Optional[int]:
        return self._data.get('mobile_id')

    def get_item_id(self) -> Optional[int]:
        return self._data.get('item_id')

    def get_asset_id(self) -> Optional[int]:
        return self._data.get('asset_id')

    def get_player_id(self) -> Optional[int]:
        return self._data.get('player_id')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_inventory_id(self, value: int) -> 'self.__class__':
        self._data['inventory_id'] = value
        self._dirty = True
        return self

    def set_mobile_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['mobile_id'] = value
        self._dirty = True
        return self

    def set_item_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['item_id'] = value
        self._dirty = True
        return self

    def set_asset_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['asset_id'] = value
        self._dirty = True
        return self

    def set_player_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['player_id'] = value
        self._dirty = True
        return self

    def is_mobile(self) -> bool:
        """Check if this pivot record belongs to a mobile."""
        return self.get_mobile_id() is not None


    def is_item(self) -> bool:
        """Check if this pivot record belongs to a item."""
        return self.get_item_id() is not None


    def is_asset(self) -> bool:
        """Check if this pivot record belongs to a asset."""
        return self.get_asset_id() is not None


    def is_player(self) -> bool:
        """Check if this pivot record belongs to a player."""
        return self.get_player_id() is not None


    def get_inventory(self, strict: bool = False) -> Optional['Inventory']:
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

    def set_inventory(self, model: 'Inventory') -> 'self.__class__':
        """
        Set the associated Inventory for this inventory relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Inventory instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_inventory_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_inventory_id(None)
        else:
            self.set_inventory_id(model.get_id())
        return self

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

    def set_mobile(self, model: Optional['Mobile']) -> 'self.__class__':
        """
        Set the associated Mobile for this mobile relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Mobile instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_mobile_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_id(None)
        else:
            self.set_mobile_id(model.get_id())
        return self

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

    def set_item(self, model: Optional['Item']) -> 'self.__class__':
        """
        Set the associated Item for this item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_id(None)
        else:
            self.set_item_id(model.get_id())
        return self

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

    def set_player(self, model: Optional['Player']) -> 'self.__class__':
        """
        Set the associated Player for this player relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Player instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_player_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_player_id(None)
        else:
            self.set_player_id(model.get_id())
        return self






    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
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

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                pass  # No cascade destroys needed

            # Delete the record itself
            cursor.execute(f"DELETE FROM `inventory_owners` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `inventory_owners` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_inventory_id(value: int) -> List['InventoryOwner']:
        """
        Find all records by inventory_id.
        Returns a list of instances with matching records.
        """
        connection = InventoryOwner._create_connection()
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
        connection = InventoryOwner._create_connection()
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
        connection = InventoryOwner._create_connection()
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
        connection = InventoryOwner._create_connection()
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
        connection = InventoryOwner._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=325 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = ItemBlueprintComponent._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_item_blueprint_id(self) -> int:
        return self._data.get('item_blueprint_id')

    def get_component_item_id(self) -> int:
        return self._data.get('component_item_id')

    def get_ratio(self) -> float:
        return self._data.get('ratio')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_item_blueprint_id(self, value: int) -> 'self.__class__':
        self._data['item_blueprint_id'] = value
        self._dirty = True
        return self

    def set_component_item_id(self, value: int) -> 'self.__class__':
        self._data['component_item_id'] = value
        self._dirty = True
        return self

    def set_ratio(self, value: float) -> 'self.__class__':
        self._data['ratio'] = value
        self._dirty = True
        return self


    def get_item_blueprint(self, strict: bool = False) -> Optional['ItemBlueprint']:
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

    def set_item_blueprint(self, model: 'ItemBlueprint') -> 'self.__class__':
        """
        Set the associated ItemBlueprint for this item_blueprint relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The ItemBlueprint instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_item_blueprint_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_blueprint_id(None)
        else:
            self.set_item_blueprint_id(model.get_id())
        return self





    def from_thrift(self, thrift_obj: 'ItemBlueprintComponent') -> 'ItemBlueprintComponent':
        """
        Populate this Model instance from a Thrift ItemBlueprintComponent object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift ItemBlueprintComponent instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'item_blueprint_id'):
            self._data['item_blueprint_id'] = thrift_obj.item_blueprint_id
        if hasattr(thrift_obj, 'component_item_id'):
            self._data['component_item_id'] = thrift_obj.component_item_id
        if hasattr(thrift_obj, 'ratio'):
            self._data['ratio'] = thrift_obj.ratio

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['ItemBlueprintComponent']]:
        """
        Convert this Model instance to a Thrift ItemBlueprintComponent object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['component_item_id'] = self._data.get('component_item_id')
            thrift_params['ratio'] = self._data.get('ratio')

            # Create Thrift object
            thrift_obj = ThriftItemBlueprintComponent(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                # Save item_blueprint if cached and dirty
                cache_key = '_item_blueprint_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_blueprint_id'] = related.get_id()

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                pass  # No cascade destroys needed

            # Delete the record itself
            cursor.execute(f"DELETE FROM `item_blueprint_components` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `item_blueprint_components` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_item_blueprint_id(value: int) -> List['ItemBlueprintComponent']:
        """
        Find all records by item_blueprint_id.
        Returns a list of instances with matching records.
        """
        connection = ItemBlueprintComponent._create_connection()
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
        connection = ItemBlueprintComponent._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=623 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = ItemBlueprint._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_bake_time_ms(self) -> int:
        return self._data.get('bake_time_ms')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_bake_time_ms(self, value: int) -> 'self.__class__':
        self._data['bake_time_ms'] = value
        self._dirty = True
        return self




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

    def get_items(self, reload: bool = False, lazy: bool = False):
        """
        Get all associated Item records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[Item] or Iterator[Item]
        """
        cache_key = '_items_cache'

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

        results = Item.find_by_blueprint_id(my_id)

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

        results = MobileItem.find_by_blueprint_id(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results



    def from_thrift(self, thrift_obj: 'ItemBlueprint') -> 'ItemBlueprint':
        """
        Populate this Model instance from a Thrift ItemBlueprint object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift ItemBlueprint instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'bake_time_ms'):
            self._data['bake_time_ms'] = thrift_obj.bake_time_ms

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['ItemBlueprint']]:
        """
        Convert this Model instance to a Thrift ItemBlueprint object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['bake_time_ms'] = self._data.get('bake_time_ms')

            # Create Thrift object
            thrift_obj = ThriftItemBlueprint(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                pass  # No belongs-to relationships

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
            if cascade:
                # Save item_blueprint_components if cached
                cache_key = '_item_blueprint_components_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)
# Save items if cached
                cache_key = '_items_cache'
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                # Cascade destroy item_blueprint_components children
                cache_key = '_item_blueprint_components_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_item_blueprint_components(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy items children
                cache_key = '_items_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_items(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy mobile_items children
                cache_key = '_mobile_items_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_mobile_items(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist

            # Delete the record itself
            cursor.execute(f"DELETE FROM `item_blueprints` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `item_blueprints` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
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
        ) ENGINE=InnoDB AUTO_INCREMENT=3225 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = Item._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_internal_name(self) -> str:
        return self._data.get('internal_name')

    def get_max_stack_size(self) -> Optional[int]:
        return self._data.get('max_stack_size')

    def get_item_type(self) -> ThriftItemType:
        value = self._data.get('item_type')
        return getattr(ThriftItemType, value) if value is not None else None

    def get_blueprint_id(self) -> Optional[int]:
        return self._data.get('blueprint_id')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_internal_name(self, value: str) -> 'self.__class__':
        self._data['internal_name'] = value
        self._dirty = True
        return self

    def set_max_stack_size(self, value: Optional[int]) -> 'self.__class__':
        self._data['max_stack_size'] = value
        self._dirty = True
        return self

    def set_item_type(self, value: int) -> 'self.__class__':
        """
        Set the item_type field value.

        Python Thrift Enum Implementation Note:
        ----------------------------------------
        In Python, Thrift enums are implemented as integer constants on a class, not
        as a separate enum type. For example:
            - ThriftAttributeType.STRENGTH is just an int (e.g., 0)
            - ThriftAttributeType.DEXTERITY is just an int (e.g., 1)

        This is different from languages like Java or C++ where enums are distinct types.
        Python Thrift enums are essentially namespaced integer constants.

        Why this method accepts int:
        - Thrift enums in Python ARE ints, not a distinct type
        - Using isinstance(value, ThriftAttributeType) would fail (it's not a class you can instantiate)
        - Type checkers understand this: passing ThriftAttributeType.STRENGTH satisfies int type hint
        - This validates the value is a legitimate enum constant, rejecting invalid integers

        The method validates the integer is a valid enum value by reverse-lookup against
        the Thrift enum class constants, then stores the enum name as a string in the database.

        Args:
            value: Integer value of a ThriftItemType enum constant (e.g., ThriftItemType.STRENGTH)

        Returns:
            self for method chaining

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is not a valid ThriftItemType enum constant
        """
        if value is not None and not isinstance(value, int):
            raise TypeError(f"{value} must be an integer (Thrift enum), got {type(value).__name__}")
        # Convert enum integer to string name for storage
        if value is not None:
            # Reverse lookup: find the name for this enum value
            enum_name = None
            for attr_name in dir(ThriftItemType):
                if not attr_name.startswith('_'):
                    attr_val = getattr(ThriftItemType, attr_name)
                    if isinstance(attr_val, int) and attr_val == value:
                        enum_name = attr_name
                        break
            if enum_name is None:
                raise ValueError(f"{value} is not a valid ThriftItemType enum value")
            self._data['item_type'] = enum_name
        else:
            self._data['item_type'] = None
        self._dirty = True
        return self

    def set_blueprint_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['blueprint_id'] = value
        self._dirty = True
        return self


    def get_blueprint(self, strict: bool = False) -> Optional['ItemBlueprint']:
        """
        Get the associated ItemBlueprint for this blueprint relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_blueprint_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_blueprint_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = ItemBlueprint.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has blueprint_id={fk_value} but no ItemBlueprint record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_blueprint(self, model: Optional['ItemBlueprint']) -> 'self.__class__':
        """
        Set the associated ItemBlueprint for this blueprint relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The ItemBlueprint instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_blueprint_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_blueprint_id(None)
        else:
            self.set_blueprint_id(model.get_id())
        return self

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

    def get_attributes(self, reload: bool = False) -> List['Attribute']:
        """
        Get all attributes for this Item through the attribute_owners pivot table.
        Returns a list of Attribute objects.
        """
        cache_key = '_attributes_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        if self.get_id() is None:
            return []

        # Query through pivot table
        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        results = []

        try:
            query = """
                SELECT r.*
                FROM attributes r
                INNER JOIN attribute_owners p ON r.id = p.attribute_id
                WHERE p.item_id = %s
            """
            cursor.execute(query, (self.get_id(),))
            rows = cursor.fetchall()

            for row in rows:
                instance = Attribute()
                instance._data = row
                instance._dirty = False
                results.append(instance)
        finally:
            cursor.close()

        # Cache results
        setattr(self, cache_key, results)
        return results

    def get_attribute_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all AttributeOwner pivot records for this Item.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[AttributeOwner] or Iterator[AttributeOwner]
        """
        cache_key = '_attribute_owners_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return iter(cached) if lazy else cached

        if self.get_id() is None:
            return iter([]) if lazy else []

        results = AttributeOwner.find_by_item_id(self.get_id())

        # Cache results
        setattr(self, cache_key, results)
        return iter(results) if lazy else results

    def add_attribute(self, attribute: 'Attribute') -> None:
        """
        Add a attribute to this Item through the attribute_owners pivot table.
        Creates the pivot record and saves the attribute if it's new or dirty.
        """
        if self.get_id() is None:
            raise ValueError("Cannot add attribute to unsaved Item. Save the Item first.")

        # Save the related object if it's new or dirty
        if attribute._dirty:
            attribute.save()

        # Create pivot record
        pivot = AttributeOwner()
        pivot.set_item_id(self.get_id())
        pivot.set_attribute_id(attribute.get_id())

        # Set all other owner FKs to NULL explicitly
        # This ensures only one owner FK is set per pivot record
        for attr_name in dir(pivot):
            if attr_name.startswith('set_') and attr_name.endswith('_id') and attr_name != 'set_id' and attr_name != 'set_item_id' and attr_name != 'set_attribute_id':
                setter = getattr(pivot, attr_name)
                setter(None)

        pivot.save()

        # Clear cache
        cache_key = '_attributes_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_attribute_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def remove_attribute(self, attribute: 'Attribute') -> None:
        """
        Remove a attribute from this Item through the attribute_owners pivot table.
        Deletes both the pivot record and the attribute record (cascade delete).
        """
        if self.get_id() is None or attribute.get_id() is None:
            return

        # Use a fresh connection to avoid transaction conflicts
        connection = Item._create_connection()
        cursor = connection.cursor()

        try:
            # Start transaction
            connection.start_transaction()

            # Delete pivot record first
            cursor.execute(
                f"DELETE FROM attribute_owners WHERE item_id = %s AND attribute_id = %s",
                (self.get_id(), attribute.get_id()),
            )

            # Delete the related record
            cursor.execute(
                f"DELETE FROM attributes WHERE id = %s",
                (attribute.get_id(),),
            )

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

        # Clear cache
        cache_key = '_attributes_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_attribute_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def set_attributes(self, attributes_list: List['Attribute']) -> None:
        """
        Replace all attributes for this Item.
        Removes all existing attributes and adds the new ones.
        """
        if self.get_id() is None:
            raise ValueError("Cannot set attributes on unsaved Item. Save the Item first.")

        self._connect()

        try:
            # Start transaction for all operations only if one isn't already active
            if not self._connection.in_transaction:
                self._connection.start_transaction()

            # Get existing attributes
            existing = self.get_attributes(reload=True)

            # Delete all existing pivot records and related records
            cursor = self._connection.cursor()
            for item in existing:
                if item.get_id() is not None:
                    # Delete pivot record
                    cursor.execute(
                        f"DELETE FROM attribute_owners WHERE item_id = %s AND attribute_id = %s",
                        (self.get_id(), item.get_id()),
                    )
                    # Delete related record
                    cursor.execute(
                        f"DELETE FROM attributes WHERE id = %s",
                        (item.get_id(),),
                    )
            cursor.close()

            # Add new ones within the same transaction
            for item in attributes_list:
                # Save the related object if needed
                if item._dirty:
                    item.save(self._connection)

                # Create pivot record manually to avoid nested transactions
                pivot = AttributeOwner()
                pivot.set_item_id(self.get_id())
                pivot.set_attribute_id(item.get_id())
                pivot.save(self._connection)

            # Commit all operations
            self._connection.commit()

            # Clear cache
            cache_key = '_attributes_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)
            cache_key = '_attribute_owners_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)

        except Exception as e:
            self._connection.rollback()
            raise


    def get_inventories(self, reload: bool = False) -> List['Inventory']:
        """
        Get all inventories for this Item through the inventory_owners pivot table.
        Returns a list of Inventory objects.
        """
        cache_key = '_inventories_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        if self.get_id() is None:
            return []

        # Query through pivot table
        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        results = []

        try:
            query = """
                SELECT r.*
                FROM inventories r
                INNER JOIN inventory_owners p ON r.id = p.inventory_id
                WHERE p.item_id = %s
            """
            cursor.execute(query, (self.get_id(),))
            rows = cursor.fetchall()

            for row in rows:
                instance = Inventory()
                instance._data = row
                instance._dirty = False
                results.append(instance)
        finally:
            cursor.close()

        # Cache results
        setattr(self, cache_key, results)
        return results

    def get_inventory_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all InventoryOwner pivot records for this Item.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryOwner] or Iterator[InventoryOwner]
        """
        cache_key = '_inventory_owners_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return iter(cached) if lazy else cached

        if self.get_id() is None:
            return iter([]) if lazy else []

        results = InventoryOwner.find_by_item_id(self.get_id())

        # Cache results
        setattr(self, cache_key, results)
        return iter(results) if lazy else results

    def add_inventory(self, inventory: 'Inventory') -> None:
        """
        Add a inventory to this Item through the inventory_owners pivot table.
        Creates the pivot record and saves the inventory if it's new or dirty.
        """
        if self.get_id() is None:
            raise ValueError("Cannot add inventory to unsaved Item. Save the Item first.")

        # Save the related object if it's new or dirty
        if inventory._dirty:
            inventory.save()

        # Create pivot record
        pivot = InventoryOwner()
        pivot.set_item_id(self.get_id())
        pivot.set_inventory_id(inventory.get_id())

        # Set all other owner FKs to NULL explicitly
        # This ensures only one owner FK is set per pivot record
        for attr_name in dir(pivot):
            if attr_name.startswith('set_') and attr_name.endswith('_id') and attr_name != 'set_id' and attr_name != 'set_item_id' and attr_name != 'set_inventory_id':
                setter = getattr(pivot, attr_name)
                setter(None)

        pivot.save()

        # Clear cache
        cache_key = '_inventories_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_inventory_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def remove_inventory(self, inventory: 'Inventory') -> None:
        """
        Remove a inventory from this Item through the inventory_owners pivot table.
        Deletes both the pivot record and the inventory record (cascade delete).
        """
        if self.get_id() is None or inventory.get_id() is None:
            return

        # Use a fresh connection to avoid transaction conflicts
        connection = Item._create_connection()
        cursor = connection.cursor()

        try:
            # Start transaction
            connection.start_transaction()

            # Delete pivot record first
            cursor.execute(
                f"DELETE FROM inventory_owners WHERE item_id = %s AND inventory_id = %s",
                (self.get_id(), inventory.get_id()),
            )

            # Delete the related record
            cursor.execute(
                f"DELETE FROM inventories WHERE id = %s",
                (inventory.get_id(),),
            )

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

        # Clear cache
        cache_key = '_inventories_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_inventory_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def set_inventories(self, inventories_list: List['Inventory']) -> None:
        """
        Replace all inventories for this Item.
        Removes all existing inventories and adds the new ones.
        """
        if self.get_id() is None:
            raise ValueError("Cannot set inventories on unsaved Item. Save the Item first.")

        self._connect()

        try:
            # Start transaction for all operations only if one isn't already active
            if not self._connection.in_transaction:
                self._connection.start_transaction()

            # Get existing inventories
            existing = self.get_inventories(reload=True)

            # Delete all existing pivot records and related records
            cursor = self._connection.cursor()
            for item in existing:
                if item.get_id() is not None:
                    # Delete pivot record
                    cursor.execute(
                        f"DELETE FROM inventory_owners WHERE item_id = %s AND inventory_id = %s",
                        (self.get_id(), item.get_id()),
                    )
                    # Delete related record
                    cursor.execute(
                        f"DELETE FROM inventories WHERE id = %s",
                        (item.get_id(),),
                    )
            cursor.close()

            # Add new ones within the same transaction
            for item in inventories_list:
                # Save the related object if needed
                if item._dirty:
                    item.save(self._connection)

                # Create pivot record manually to avoid nested transactions
                pivot = InventoryOwner()
                pivot.set_item_id(self.get_id())
                pivot.set_inventory_id(item.get_id())
                pivot.save(self._connection)

            # Commit all operations
            self._connection.commit()

            # Clear cache
            cache_key = '_inventories_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)
            cache_key = '_inventory_owners_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)

        except Exception as e:
            self._connection.rollback()
            raise



    def from_thrift(self, thrift_obj: 'Item') -> 'Item':
        """
        Populate this Model instance from a Thrift Item object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift Item instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'internal_name'):
            self._data['internal_name'] = thrift_obj.internal_name
        if hasattr(thrift_obj, 'max_stack_size'):
            self._data['max_stack_size'] = thrift_obj.max_stack_size
        if hasattr(thrift_obj, 'item_type'):
            if thrift_obj.item_type is not None:
                self._data['item_type'] = ThriftItemType._VALUES_TO_NAMES[thrift_obj.item_type]
            else:
                self._data['item_type'] = None
        if hasattr(thrift_obj, 'blueprint_id'):
            self._data['blueprint_id'] = thrift_obj.blueprint_id

        # Store attributes map for later conversion via set_attributes()
        # The actual pivot table records will be created when save() is called
        if hasattr(thrift_obj, 'attributes') and thrift_obj.attributes is not None:
            # Convert thrift attributes to Attribute models
            self._pending_attributes = []
            for attr_type, attr_thrift in thrift_obj.attributes.items():
                # Import Attribute model (assumes it's available)
                attr_model = Attribute()
                attr_model.from_thrift(attr_thrift)
                self._pending_attributes.append((attr_type, attr_model))

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['Item']]:
        """
        Convert this Model instance to a Thrift Item object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['internal_name'] = self._data.get('internal_name')
            thrift_params['max_stack_size'] = self._data.get('max_stack_size')
            thrift_params['item_type'] = getattr(ThriftItemType, self._data.get('item_type')) if self._data.get('item_type') is not None else None

            # Load attributes via pivot table and convert to map<AttributeType, Attribute>
            attributes_map = {}
            if self.get_id() is not None:
                # Get attributes through the pivot relationship
                attribute_models = self.get_attributes(reload=True)
                for attr_model in attribute_models:
                    # Convert each attribute model to Thrift
                    attr_results, attr_thrift = attr_model.into_thrift()
                    if attr_thrift is not None:
                        # Use attribute_type as the map key
                        attributes_map[attr_thrift.attribute_type] = attr_thrift
            thrift_params['attributes'] = attributes_map

            # Create Thrift object
            thrift_obj = ThriftItem(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                # Save blueprint if cached and dirty
                cache_key = '_blueprint_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['blueprint_id'] = related.get_id()

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                # Cascade destroy attribute_owners children
                cache_key = '_attribute_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_attribute_owners(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy inventory_entries children
                cache_key = '_inventory_entries_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_inventory_entries(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy inventory_owners children
                cache_key = '_inventory_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_inventory_owners(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy mobile_items children
                cache_key = '_mobile_items_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_mobile_items(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy mobiles children
                cache_key = '_mobiles_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_mobiles(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Clean up attribute_owners associations and cascade delete attributes
                if self.get_id() is not None:
                    # First, cascade delete the related objects
                    try:
                        related_objects = self.get_attributes(reload=True)
                        for obj in related_objects:
                            if hasattr(obj, 'destroy'):
                                obj.destroy(connection=connection, cascade=cascade)
                    except:
                        pass  # Method may not exist

                    # Then delete the pivot table associations
                    cursor.execute(
                        "DELETE FROM `attribute_owners` WHERE `item_id` = %s",
                        (self.get_id(),),
                    )
# Clean up inventory_owners associations and cascade delete inventories
                if self.get_id() is not None:
                    # First, cascade delete the related objects
                    try:
                        related_objects = self.get_inventories(reload=True)
                        for obj in related_objects:
                            if hasattr(obj, 'destroy'):
                                obj.destroy(connection=connection, cascade=cascade)
                    except:
                        pass  # Method may not exist

                    # Then delete the pivot table associations
                    cursor.execute(
                        "DELETE FROM `inventory_owners` WHERE `item_id` = %s",
                        (self.get_id(),),
                    )

            # Delete the record itself
            cursor.execute(f"DELETE FROM `items` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `items` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_blueprint_id(value: int) -> List['Item']:
        """
        Find all records by blueprint_id.
        Returns a list of instances with matching records.
        """
        connection = Item._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=219 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = MobileItemAttribute._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_mobile_item_id(self) -> int:
        return self._data.get('mobile_item_id')

    def get_internal_name(self) -> str:
        return self._data.get('internal_name')

    def get_visible(self) -> int:
        return self._data.get('visible')

    def get_attribute_type(self) -> str:
        return self._data.get('attribute_type')

    def get_bool_value(self) -> Optional[int]:
        return self._data.get('bool_value')

    def get_double_value(self) -> Optional[float]:
        return self._data.get('double_value')

    def get_vector3_x(self) -> Optional[float]:
        return self._data.get('vector3_x')

    def get_vector3_y(self) -> Optional[float]:
        return self._data.get('vector3_y')

    def get_vector3_z(self) -> Optional[float]:
        return self._data.get('vector3_z')

    def get_asset_id(self) -> Optional[int]:
        return self._data.get('asset_id')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_mobile_item_id(self, value: int) -> 'self.__class__':
        self._data['mobile_item_id'] = value
        self._dirty = True
        return self

    def set_internal_name(self, value: str) -> 'self.__class__':
        self._data['internal_name'] = value
        self._dirty = True
        return self

    def set_visible(self, value: int) -> 'self.__class__':
        self._data['visible'] = value
        self._dirty = True
        return self

    def set_attribute_type(self, value: str) -> 'self.__class__':
        self._data['attribute_type'] = value
        self._dirty = True
        return self

    def set_bool_value(self, value: Optional[int]) -> 'self.__class__':
        self._data['bool_value'] = value
        self._dirty = True
        return self

    def set_double_value(self, value: Optional[float]) -> 'self.__class__':
        self._data['double_value'] = value
        self._dirty = True
        return self

    def set_vector3_x(self, value: Optional[float]) -> 'self.__class__':
        self._data['vector3_x'] = value
        self._dirty = True
        return self

    def set_vector3_y(self, value: Optional[float]) -> 'self.__class__':
        self._data['vector3_y'] = value
        self._dirty = True
        return self

    def set_vector3_z(self, value: Optional[float]) -> 'self.__class__':
        self._data['vector3_z'] = value
        self._dirty = True
        return self

    def set_asset_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['asset_id'] = value
        self._dirty = True
        return self


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

    def set_mobile_item(self, model: 'MobileItem') -> 'self.__class__':
        """
        Set the associated MobileItem for this mobile_item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The MobileItem instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_mobile_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_item_id(None)
        else:
            self.set_mobile_item_id(model.get_id())
        return self






    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                # Save mobile_item if cached and dirty
                cache_key = '_mobile_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['mobile_item_id'] = related.get_id()

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                pass  # No cascade destroys needed

            # Delete the record itself
            cursor.execute(f"DELETE FROM `mobile_item_attributes` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_attributes` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_mobile_item_id(value: int) -> List['MobileItemAttribute']:
        """
        Find all records by mobile_item_id.
        Returns a list of instances with matching records.
        """
        connection = MobileItemAttribute._create_connection()
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
        connection = MobileItemAttribute._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=295 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = MobileItemBlueprintComponent._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_item_blueprint_id(self) -> int:
        return self._data.get('item_blueprint_id')

    def get_component_item_id(self) -> int:
        return self._data.get('component_item_id')

    def get_ratio(self) -> float:
        return self._data.get('ratio')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_item_blueprint_id(self, value: int) -> 'self.__class__':
        self._data['item_blueprint_id'] = value
        self._dirty = True
        return self

    def set_component_item_id(self, value: int) -> 'self.__class__':
        self._data['component_item_id'] = value
        self._dirty = True
        return self

    def set_ratio(self, value: float) -> 'self.__class__':
        self._data['ratio'] = value
        self._dirty = True
        return self


    def get_item_blueprint(self, strict: bool = False) -> Optional['MobileItemBlueprint']:
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

    def set_item_blueprint(self, model: 'MobileItemBlueprint') -> 'self.__class__':
        """
        Set the associated MobileItemBlueprint for this item_blueprint relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The MobileItemBlueprint instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_item_blueprint_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_blueprint_id(None)
        else:
            self.set_item_blueprint_id(model.get_id())
        return self






    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                # Save item_blueprint if cached and dirty
                cache_key = '_item_blueprint_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_blueprint_id'] = related.get_id()

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                pass  # No cascade destroys needed

            # Delete the record itself
            cursor.execute(f"DELETE FROM `mobile_item_blueprint_components` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_blueprint_components` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_item_blueprint_id(value: int) -> List['MobileItemBlueprintComponent']:
        """
        Find all records by item_blueprint_id.
        Returns a list of instances with matching records.
        """
        connection = MobileItemBlueprintComponent._create_connection()
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
        connection = MobileItemBlueprintComponent._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=495 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = MobileItemBlueprint._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_bake_time_ms(self) -> int:
        return self._data.get('bake_time_ms')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_bake_time_ms(self, value: int) -> 'self.__class__':
        self._data['bake_time_ms'] = value
        self._dirty = True
        return self




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
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                pass  # No belongs-to relationships

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                # Cascade destroy mobile_item_blueprint_components children
                cache_key = '_mobile_item_blueprint_components_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_mobile_item_blueprint_components(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist

            # Delete the record itself
            cursor.execute(f"DELETE FROM `mobile_item_blueprints` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobile_item_blueprints` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
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
        ) ENGINE=InnoDB AUTO_INCREMENT=787 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = MobileItem._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_mobile_id(self) -> int:
        return self._data.get('mobile_id')

    def get_internal_name(self) -> str:
        return self._data.get('internal_name')

    def get_max_stack_size(self) -> Optional[int]:
        return self._data.get('max_stack_size')

    def get_item_type(self) -> ThriftItemType:
        value = self._data.get('item_type')
        return getattr(ThriftItemType, value) if value is not None else None

    def get_blueprint_id(self) -> Optional[int]:
        return self._data.get('blueprint_id')

    def get_item_id(self) -> int:
        return self._data.get('item_id')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_mobile_id(self, value: int) -> 'self.__class__':
        self._data['mobile_id'] = value
        self._dirty = True
        return self

    def set_internal_name(self, value: str) -> 'self.__class__':
        self._data['internal_name'] = value
        self._dirty = True
        return self

    def set_max_stack_size(self, value: Optional[int]) -> 'self.__class__':
        self._data['max_stack_size'] = value
        self._dirty = True
        return self

    def set_item_type(self, value: int) -> 'self.__class__':
        """
        Set the item_type field value.

        Python Thrift Enum Implementation Note:
        ----------------------------------------
        In Python, Thrift enums are implemented as integer constants on a class, not
        as a separate enum type. For example:
            - ThriftAttributeType.STRENGTH is just an int (e.g., 0)
            - ThriftAttributeType.DEXTERITY is just an int (e.g., 1)

        This is different from languages like Java or C++ where enums are distinct types.
        Python Thrift enums are essentially namespaced integer constants.

        Why this method accepts int:
        - Thrift enums in Python ARE ints, not a distinct type
        - Using isinstance(value, ThriftAttributeType) would fail (it's not a class you can instantiate)
        - Type checkers understand this: passing ThriftAttributeType.STRENGTH satisfies int type hint
        - This validates the value is a legitimate enum constant, rejecting invalid integers

        The method validates the integer is a valid enum value by reverse-lookup against
        the Thrift enum class constants, then stores the enum name as a string in the database.

        Args:
            value: Integer value of a ThriftItemType enum constant (e.g., ThriftItemType.STRENGTH)

        Returns:
            self for method chaining

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is not a valid ThriftItemType enum constant
        """
        if value is not None and not isinstance(value, int):
            raise TypeError(f"{value} must be an integer (Thrift enum), got {type(value).__name__}")
        # Convert enum integer to string name for storage
        if value is not None:
            # Reverse lookup: find the name for this enum value
            enum_name = None
            for attr_name in dir(ThriftItemType):
                if not attr_name.startswith('_'):
                    attr_val = getattr(ThriftItemType, attr_name)
                    if isinstance(attr_val, int) and attr_val == value:
                        enum_name = attr_name
                        break
            if enum_name is None:
                raise ValueError(f"{value} is not a valid ThriftItemType enum value")
            self._data['item_type'] = enum_name
        else:
            self._data['item_type'] = None
        self._dirty = True
        return self

    def set_blueprint_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['blueprint_id'] = value
        self._dirty = True
        return self

    def set_item_id(self, value: int) -> 'self.__class__':
        self._data['item_id'] = value
        self._dirty = True
        return self


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

    def set_mobile(self, model: 'Mobile') -> 'self.__class__':
        """
        Set the associated Mobile for this mobile relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Mobile instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_mobile_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_mobile_id(None)
        else:
            self.set_mobile_id(model.get_id())
        return self

    def get_blueprint(self, strict: bool = False) -> Optional['ItemBlueprint']:
        """
        Get the associated ItemBlueprint for this blueprint relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        """
        # Check cache first
        cache_key = '_blueprint_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_blueprint_id()
        if fk_value is None:
            return None

        # Lazy load from database
        related = ItemBlueprint.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{self.__class__.__name__} has blueprint_id={fk_value} but no ItemBlueprint record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related

    def set_blueprint(self, model: Optional['ItemBlueprint']) -> 'self.__class__':
        """
        Set the associated ItemBlueprint for this blueprint relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The ItemBlueprint instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_blueprint_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_blueprint_id(None)
        else:
            self.set_blueprint_id(model.get_id())
        return self

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

    def set_item(self, model: 'Item') -> 'self.__class__':
        """
        Set the associated Item for this item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_item_id(None)
        else:
            self.set_item_id(model.get_id())
        return self

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


    def get_attributes(self, reload: bool = False) -> List['Attribute']:
        """
        Get all attributes for this MobileItem from mobile_item_attributes table.
        Converts to standard Attribute objects for Thrift compatibility.

        Args:
            reload: If True, ignore cache and reload from database
        """
        # Check cache first
        cache_key = '_attributes_cache'
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return []

        # Get direct attribute records
        direct_attrs = MobileItemAttribute.find_by_mobile_item_id(my_id)

        # Convert to standard Attribute objects
        attributes = []
        for direct_attr in direct_attrs:
            attr = Attribute()
            attr._data['internal_name'] = direct_attr.get_internal_name()
            attr._data['visible'] = direct_attr.get_visible()
            attr._data['attribute_type'] = direct_attr.get_attribute_type()
            attr._data['bool_value'] = direct_attr.get_bool_value()
            attr._data['double_value'] = direct_attr.get_double_value()
            attr._data['vector3_x'] = direct_attr.get_vector3_x()
            attr._data['vector3_y'] = direct_attr.get_vector3_y()
            attr._data['vector3_z'] = direct_attr.get_vector3_z()
            attr._data['asset_id'] = direct_attr.get_asset_id()
            attributes.append(attr)

        # Cache results
        setattr(self, cache_key, attributes)
        return attributes


    def from_thrift(self, thrift_obj: 'MobileItem') -> 'MobileItem':
        """
        Populate this Model instance from a Thrift MobileItem object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift MobileItem instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'mobile_id'):
            self._data['mobile_id'] = thrift_obj.mobile_id
        if hasattr(thrift_obj, 'internal_name'):
            self._data['internal_name'] = thrift_obj.internal_name
        if hasattr(thrift_obj, 'max_stack_size'):
            self._data['max_stack_size'] = thrift_obj.max_stack_size
        if hasattr(thrift_obj, 'item_type'):
            if thrift_obj.item_type is not None:
                self._data['item_type'] = ThriftItemType._VALUES_TO_NAMES[thrift_obj.item_type]
            else:
                self._data['item_type'] = None
        if hasattr(thrift_obj, 'blueprint_id'):
            self._data['blueprint_id'] = thrift_obj.blueprint_id
        if hasattr(thrift_obj, 'item_id'):
            self._data['item_id'] = thrift_obj.item_id

        # Store attributes for direct table conversion
        if hasattr(thrift_obj, 'attributes') and thrift_obj.attributes is not None:
            self._pending_attributes = thrift_obj.attributes

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['MobileItem']]:
        """
        Convert this Model instance to a Thrift MobileItem object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['internal_name'] = self._data.get('internal_name')
            thrift_params['max_stack_size'] = self._data.get('max_stack_size')
            thrift_params['item_type'] = getattr(ThriftItemType, self._data.get('item_type')) if self._data.get('item_type') is not None else None

            # Load attributes via pivot table and convert to map<AttributeType, Attribute>
            attributes_map = {}
            if self.get_id() is not None:
                # Get attributes through the pivot relationship
                attribute_models = self.get_attributes(reload=True)
                for attr_model in attribute_models:
                    # Convert each attribute model to Thrift
                    attr_results, attr_thrift = attr_model.into_thrift()
                    if attr_thrift is not None:
                        # Use attribute_type as the map key
                        attributes_map[attr_thrift.attribute_type] = attr_thrift
            thrift_params['attributes'] = attributes_map

            # Create Thrift object
            thrift_obj = ThriftMobileItem(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                # Save mobile if cached and dirty
                cache_key = '_mobile_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['mobile_id'] = related.get_id()
# Save blueprint if cached and dirty
                cache_key = '_blueprint_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['blueprint_id'] = related.get_id()
# Save item if cached and dirty
                cache_key = '_item_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['item_id'] = related.get_id()

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                # Cascade destroy inventory_entries children
                cache_key = '_inventory_entries_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_inventory_entries(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy mobile_item_attributes children
                cache_key = '_mobile_item_attributes_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_mobile_item_attributes(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist

            # Delete the record itself
            cursor.execute(f"DELETE FROM `mobile_items` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobile_items` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_mobile_id(value: int) -> List['MobileItem']:
        """
        Find all records by mobile_id.
        Returns a list of instances with matching records.
        """
        connection = MobileItem._create_connection()
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
        connection = MobileItem._create_connection()
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
        connection = MobileItem._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=2213 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = Mobile._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_mobile_type(self) -> str:
        return self._data.get('mobile_type')

    def get_owner_mobile_id(self) -> Optional[int]:
        return self._data.get('owner_mobile_id')

    def get_owner_item_id(self) -> Optional[int]:
        return self._data.get('owner_item_id')

    def get_owner_asset_id(self) -> Optional[int]:
        return self._data.get('owner_asset_id')

    def get_owner_player_id(self) -> Optional[int]:
        return self._data.get('owner_player_id')

    def get_what_we_call_you(self) -> str:
        return self._data.get('what_we_call_you')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_mobile_type(self, value: str) -> 'self.__class__':
        self._data['mobile_type'] = value
        self._dirty = True
        return self

    def set_owner_mobile_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['owner_mobile_id'] = value
        self._data['owner_player_id'] = None
        self._data['owner_item_id'] = None
        self._data['owner_asset_id'] = None
        self._dirty = True
        return self

    def set_owner_item_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['owner_item_id'] = value
        self._data['owner_player_id'] = None
        self._data['owner_mobile_id'] = None
        self._data['owner_asset_id'] = None
        self._dirty = True
        return self

    def set_owner_asset_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['owner_asset_id'] = value
        self._data['owner_player_id'] = None
        self._data['owner_mobile_id'] = None
        self._data['owner_item_id'] = None
        self._dirty = True
        return self

    def set_owner_player_id(self, value: Optional[int]) -> 'self.__class__':
        self._data['owner_player_id'] = value
        self._data['owner_mobile_id'] = None
        self._data['owner_item_id'] = None
        self._data['owner_asset_id'] = None
        self._dirty = True
        return self

    def set_what_we_call_you(self, value: str) -> 'self.__class__':
        self._data['what_we_call_you'] = value
        self._dirty = True
        return self


    def validate_owner(self) -> None:
        """
        Validate Owner union: exactly one owner must be set and must be valid type.

        Raises:
            ValueError: If validation fails
        """
        owner_fks = {
            'player': self.get_owner_player_id(),
            'mobile': self.get_owner_mobile_id(),
            'item': self.get_owner_item_id(),
            'asset': self.get_owner_asset_id(),
        }

        # Check exactly one is set
        set_owners = [k for k, v in owner_fks.items() if v is not None]
        if len(set_owners) == 0:
            raise ValueError("Mobile must have exactly one owner (none set)")
        if len(set_owners) > 1:
            raise ValueError(f"Mobile must have exactly one owner (multiple set: {set_owners})")

        # Check valid type for this table
        valid_types = ['player', 'mobile']
        if set_owners[0] not in valid_types:
            raise ValueError(f"Mobile cannot be owned by {set_owners[0]} (valid types: {valid_types})")



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

    def set_owner_mobile(self, model: Optional['Mobile']) -> 'self.__class__':
        """
        Set the associated Mobile for this owner_mobile relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Mobile instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_owner_mobile_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_owner_mobile_id(None)
        else:
            self.set_owner_mobile_id(model.get_id())
        return self

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

    def set_owner_item(self, model: Optional['Item']) -> 'self.__class__':
        """
        Set the associated Item for this owner_item relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Item instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_owner_item_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_owner_item_id(None)
        else:
            self.set_owner_item_id(model.get_id())
        return self

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

    def set_owner_player(self, model: Optional['Player']) -> 'self.__class__':
        """
        Set the associated Player for this owner_player relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The Player instance to associate, or None to clear.

        Returns:
            self for method chaining
        """
        # Update cache
        cache_key = '_owner_player_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_owner_player_id(None)
        else:
            self.set_owner_player_id(model.get_id())
        return self

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

    def get_attributes(self, reload: bool = False) -> List['Attribute']:
        """
        Get all attributes for this Mobile through the attribute_owners pivot table.
        Returns a list of Attribute objects.
        """
        cache_key = '_attributes_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        if self.get_id() is None:
            return []

        # Query through pivot table
        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        results = []

        try:
            query = """
                SELECT r.*
                FROM attributes r
                INNER JOIN attribute_owners p ON r.id = p.attribute_id
                WHERE p.mobile_id = %s
            """
            cursor.execute(query, (self.get_id(),))
            rows = cursor.fetchall()

            for row in rows:
                instance = Attribute()
                instance._data = row
                instance._dirty = False
                results.append(instance)
        finally:
            cursor.close()

        # Cache results
        setattr(self, cache_key, results)
        return results

    def get_attribute_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all AttributeOwner pivot records for this Mobile.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[AttributeOwner] or Iterator[AttributeOwner]
        """
        cache_key = '_attribute_owners_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return iter(cached) if lazy else cached

        if self.get_id() is None:
            return iter([]) if lazy else []

        results = AttributeOwner.find_by_mobile_id(self.get_id())

        # Cache results
        setattr(self, cache_key, results)
        return iter(results) if lazy else results

    def add_attribute(self, attribute: 'Attribute') -> None:
        """
        Add a attribute to this Mobile through the attribute_owners pivot table.
        Creates the pivot record and saves the attribute if it's new or dirty.
        """
        if self.get_id() is None:
            raise ValueError("Cannot add attribute to unsaved Mobile. Save the Mobile first.")

        # Save the related object if it's new or dirty
        if attribute._dirty:
            attribute.save()

        # Create pivot record
        pivot = AttributeOwner()
        pivot.set_mobile_id(self.get_id())
        pivot.set_attribute_id(attribute.get_id())

        # Set all other owner FKs to NULL explicitly
        # This ensures only one owner FK is set per pivot record
        for attr_name in dir(pivot):
            if attr_name.startswith('set_') and attr_name.endswith('_id') and attr_name != 'set_id' and attr_name != 'set_mobile_id' and attr_name != 'set_attribute_id':
                setter = getattr(pivot, attr_name)
                setter(None)

        pivot.save()

        # Clear cache
        cache_key = '_attributes_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_attribute_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def remove_attribute(self, attribute: 'Attribute') -> None:
        """
        Remove a attribute from this Mobile through the attribute_owners pivot table.
        Deletes both the pivot record and the attribute record (cascade delete).
        """
        if self.get_id() is None or attribute.get_id() is None:
            return

        # Use a fresh connection to avoid transaction conflicts
        connection = Mobile._create_connection()
        cursor = connection.cursor()

        try:
            # Start transaction
            connection.start_transaction()

            # Delete pivot record first
            cursor.execute(
                f"DELETE FROM attribute_owners WHERE mobile_id = %s AND attribute_id = %s",
                (self.get_id(), attribute.get_id()),
            )

            # Delete the related record
            cursor.execute(
                f"DELETE FROM attributes WHERE id = %s",
                (attribute.get_id(),),
            )

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

        # Clear cache
        cache_key = '_attributes_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_attribute_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def set_attributes(self, attributes_list: List['Attribute']) -> None:
        """
        Replace all attributes for this Mobile.
        Removes all existing attributes and adds the new ones.
        """
        if self.get_id() is None:
            raise ValueError("Cannot set attributes on unsaved Mobile. Save the Mobile first.")

        self._connect()

        try:
            # Start transaction for all operations only if one isn't already active
            if not self._connection.in_transaction:
                self._connection.start_transaction()

            # Get existing attributes
            existing = self.get_attributes(reload=True)

            # Delete all existing pivot records and related records
            cursor = self._connection.cursor()
            for item in existing:
                if item.get_id() is not None:
                    # Delete pivot record
                    cursor.execute(
                        f"DELETE FROM attribute_owners WHERE mobile_id = %s AND attribute_id = %s",
                        (self.get_id(), item.get_id()),
                    )
                    # Delete related record
                    cursor.execute(
                        f"DELETE FROM attributes WHERE id = %s",
                        (item.get_id(),),
                    )
            cursor.close()

            # Add new ones within the same transaction
            for item in attributes_list:
                # Save the related object if needed
                if item._dirty:
                    item.save(self._connection)

                # Create pivot record manually to avoid nested transactions
                pivot = AttributeOwner()
                pivot.set_mobile_id(self.get_id())
                pivot.set_attribute_id(item.get_id())
                pivot.save(self._connection)

            # Commit all operations
            self._connection.commit()

            # Clear cache
            cache_key = '_attributes_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)
            cache_key = '_attribute_owners_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)

        except Exception as e:
            self._connection.rollback()
            raise


    def get_inventories(self, reload: bool = False) -> List['Inventory']:
        """
        Get all inventories for this Mobile through the inventory_owners pivot table.
        Returns a list of Inventory objects.
        """
        cache_key = '_inventories_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        if self.get_id() is None:
            return []

        # Query through pivot table
        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        results = []

        try:
            query = """
                SELECT r.*
                FROM inventories r
                INNER JOIN inventory_owners p ON r.id = p.inventory_id
                WHERE p.mobile_id = %s
            """
            cursor.execute(query, (self.get_id(),))
            rows = cursor.fetchall()

            for row in rows:
                instance = Inventory()
                instance._data = row
                instance._dirty = False
                results.append(instance)
        finally:
            cursor.close()

        # Cache results
        setattr(self, cache_key, results)
        return results

    def get_inventory_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all InventoryOwner pivot records for this Mobile.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryOwner] or Iterator[InventoryOwner]
        """
        cache_key = '_inventory_owners_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return iter(cached) if lazy else cached

        if self.get_id() is None:
            return iter([]) if lazy else []

        results = InventoryOwner.find_by_mobile_id(self.get_id())

        # Cache results
        setattr(self, cache_key, results)
        return iter(results) if lazy else results

    def add_inventory(self, inventory: 'Inventory') -> None:
        """
        Add a inventory to this Mobile through the inventory_owners pivot table.
        Creates the pivot record and saves the inventory if it's new or dirty.
        """
        if self.get_id() is None:
            raise ValueError("Cannot add inventory to unsaved Mobile. Save the Mobile first.")

        # Save the related object if it's new or dirty
        if inventory._dirty:
            inventory.save()

        # Create pivot record
        pivot = InventoryOwner()
        pivot.set_mobile_id(self.get_id())
        pivot.set_inventory_id(inventory.get_id())

        # Set all other owner FKs to NULL explicitly
        # This ensures only one owner FK is set per pivot record
        for attr_name in dir(pivot):
            if attr_name.startswith('set_') and attr_name.endswith('_id') and attr_name != 'set_id' and attr_name != 'set_mobile_id' and attr_name != 'set_inventory_id':
                setter = getattr(pivot, attr_name)
                setter(None)

        pivot.save()

        # Clear cache
        cache_key = '_inventories_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_inventory_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def remove_inventory(self, inventory: 'Inventory') -> None:
        """
        Remove a inventory from this Mobile through the inventory_owners pivot table.
        Deletes both the pivot record and the inventory record (cascade delete).
        """
        if self.get_id() is None or inventory.get_id() is None:
            return

        # Use a fresh connection to avoid transaction conflicts
        connection = Mobile._create_connection()
        cursor = connection.cursor()

        try:
            # Start transaction
            connection.start_transaction()

            # Delete pivot record first
            cursor.execute(
                f"DELETE FROM inventory_owners WHERE mobile_id = %s AND inventory_id = %s",
                (self.get_id(), inventory.get_id()),
            )

            # Delete the related record
            cursor.execute(
                f"DELETE FROM inventories WHERE id = %s",
                (inventory.get_id(),),
            )

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

        # Clear cache
        cache_key = '_inventories_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_inventory_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def set_inventories(self, inventories_list: List['Inventory']) -> None:
        """
        Replace all inventories for this Mobile.
        Removes all existing inventories and adds the new ones.
        """
        if self.get_id() is None:
            raise ValueError("Cannot set inventories on unsaved Mobile. Save the Mobile first.")

        self._connect()

        try:
            # Start transaction for all operations only if one isn't already active
            if not self._connection.in_transaction:
                self._connection.start_transaction()

            # Get existing inventories
            existing = self.get_inventories(reload=True)

            # Delete all existing pivot records and related records
            cursor = self._connection.cursor()
            for item in existing:
                if item.get_id() is not None:
                    # Delete pivot record
                    cursor.execute(
                        f"DELETE FROM inventory_owners WHERE mobile_id = %s AND inventory_id = %s",
                        (self.get_id(), item.get_id()),
                    )
                    # Delete related record
                    cursor.execute(
                        f"DELETE FROM inventories WHERE id = %s",
                        (item.get_id(),),
                    )
            cursor.close()

            # Add new ones within the same transaction
            for item in inventories_list:
                # Save the related object if needed
                if item._dirty:
                    item.save(self._connection)

                # Create pivot record manually to avoid nested transactions
                pivot = InventoryOwner()
                pivot.set_mobile_id(self.get_id())
                pivot.set_inventory_id(item.get_id())
                pivot.save(self._connection)

            # Commit all operations
            self._connection.commit()

            # Clear cache
            cache_key = '_inventories_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)
            cache_key = '_inventory_owners_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)

        except Exception as e:
            self._connection.rollback()
            raise



    def from_thrift(self, thrift_obj: 'Mobile') -> 'Mobile':
        """
        Populate this Model instance from a Thrift Mobile object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift Mobile instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'mobile_type'):
            self._data['mobile_type'] = thrift_obj.mobile_type
        if hasattr(thrift_obj, 'what_we_call_you'):
            self._data['what_we_call_you'] = thrift_obj.what_we_call_you

        # Convert ThriftOwner union to database owner_* columns
        if hasattr(thrift_obj, 'owner') and thrift_obj.owner is not None:
            owner = thrift_obj.owner
            # Reset all owner fields to None first
            self._data['owner_player_id'] = None
            self._data['owner_mobile_id'] = None
            self._data['owner_item_id'] = None
            self._data['owner_asset_id'] = None

            # Set the appropriate owner field based on which union field is set
            if hasattr(owner, 'player_id') and owner.player_id is not None:
                self._data['owner_player_id'] = owner.player_id
            elif hasattr(owner, 'mobile_id') and owner.mobile_id is not None:
                self._data['owner_mobile_id'] = owner.mobile_id
            elif hasattr(owner, 'item_id') and owner.item_id is not None:
                self._data['owner_item_id'] = owner.item_id
            elif hasattr(owner, 'asset_id') and owner.asset_id is not None:
                self._data['owner_asset_id'] = owner.asset_id

        # Store attributes map for later conversion via set_attributes()
        # The actual pivot table records will be created when save() is called
        if hasattr(thrift_obj, 'attributes') and thrift_obj.attributes is not None:
            # Convert thrift attributes to Attribute models
            self._pending_attributes = []
            for attr_type, attr_thrift in thrift_obj.attributes.items():
                # Import Attribute model (assumes it's available)
                attr_model = Attribute()
                attr_model.from_thrift(attr_thrift)
                self._pending_attributes.append((attr_type, attr_model))

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['Mobile']]:
        """
        Convert this Model instance to a Thrift Mobile object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['mobile_type'] = self._data.get('mobile_type')
            thrift_params['what_we_call_you'] = self._data.get('what_we_call_you')

            # Convert database owner_* columns to ThriftOwner union
            owner = None
            if self._data.get('owner_player_id') is not None:
                owner = ThriftOwner(player_id=self._data['owner_player_id'])
            elif self._data.get('owner_mobile_id') is not None:
                owner = ThriftOwner(mobile_id=self._data['owner_mobile_id'])
            elif self._data.get('owner_item_id') is not None:
                owner = ThriftOwner(item_id=self._data['owner_item_id'])
            elif self._data.get('owner_asset_id') is not None:
                owner = ThriftOwner(asset_id=self._data['owner_asset_id'])
            thrift_params['owner'] = owner

            # Load attributes via pivot table and convert to map<AttributeType, Attribute>
            attributes_map = {}
            if self.get_id() is not None:
                # Get attributes through the pivot relationship
                attribute_models = self.get_attributes(reload=True)
                for attr_model in attribute_models:
                    # Convert each attribute model to Thrift
                    attr_results, attr_thrift = attr_model.into_thrift()
                    if attr_thrift is not None:
                        # Use attribute_type as the map key
                        attributes_map[attr_thrift.attribute_type] = attr_thrift
            thrift_params['attributes'] = attributes_map

            # Create Thrift object
            thrift_obj = ThriftMobile(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
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

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                # Cascade destroy attribute_owners children
                cache_key = '_attribute_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_attribute_owners(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy inventory_owners children
                cache_key = '_inventory_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_inventory_owners(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy mobile_items children
                cache_key = '_mobile_items_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_mobile_items(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Clean up attribute_owners associations and cascade delete attributes
                if self.get_id() is not None:
                    # First, cascade delete the related objects
                    try:
                        related_objects = self.get_attributes(reload=True)
                        for obj in related_objects:
                            if hasattr(obj, 'destroy'):
                                obj.destroy(connection=connection, cascade=cascade)
                    except:
                        pass  # Method may not exist

                    # Then delete the pivot table associations
                    cursor.execute(
                        "DELETE FROM `attribute_owners` WHERE `mobile_id` = %s",
                        (self.get_id(),),
                    )
# Clean up inventory_owners associations and cascade delete inventories
                if self.get_id() is not None:
                    # First, cascade delete the related objects
                    try:
                        related_objects = self.get_inventories(reload=True)
                        for obj in related_objects:
                            if hasattr(obj, 'destroy'):
                                obj.destroy(connection=connection, cascade=cascade)
                    except:
                        pass  # Method may not exist

                    # Then delete the pivot table associations
                    cursor.execute(
                        "DELETE FROM `inventory_owners` WHERE `mobile_id` = %s",
                        (self.get_id(),),
                    )

            # Delete the record itself
            cursor.execute(f"DELETE FROM `mobiles` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `mobiles` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    @staticmethod
    def find_by_owner_mobile_id(value: int) -> List['Mobile']:
        """
        Find all records by owner_mobile_id.
        Returns a list of instances with matching records.
        """
        connection = Mobile._create_connection()
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
        connection = Mobile._create_connection()
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
        connection = Mobile._create_connection()
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
        connection = Mobile._create_connection()
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
        ) ENGINE=InnoDB AUTO_INCREMENT=898 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """

    def __init__(self):
        """Initialize the model."""
        self._data: Dict[str, Any] = {}
        self._connection: Optional[mysql.connector.connection.MySQLConnection] = None
        self._dirty: bool = True  # New models are dirty by default

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )

    def _connect(self) -> None:
        """Establish database connection if not already connected."""
        if not self._connection or not self._connection.is_connected():
            self._connection = Player._create_connection()

    def _disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    def get_id(self) -> int:
        return self._data.get('id')

    def get_full_name(self) -> str:
        return self._data.get('full_name')

    def get_what_we_call_you(self) -> str:
        return self._data.get('what_we_call_you')

    def get_security_token(self) -> str:
        return self._data.get('security_token')

    def get_over_13(self) -> int:
        return self._data.get('over_13')

    def get_year_of_birth(self) -> int:
        return self._data.get('year_of_birth')

    def get_email(self) -> str:
        return self._data.get('email')

    def _set_id(self, value: int) -> 'self.__class__':
        self._data['id'] = value
        self._dirty = True
        return self

    def set_full_name(self, value: str) -> 'self.__class__':
        self._data['full_name'] = value
        self._dirty = True
        return self

    def set_what_we_call_you(self, value: str) -> 'self.__class__':
        self._data['what_we_call_you'] = value
        self._dirty = True
        return self

    def set_security_token(self, value: str) -> 'self.__class__':
        self._data['security_token'] = value
        self._dirty = True
        return self

    def set_over_13(self, value: int) -> 'self.__class__':
        self._data['over_13'] = value
        self._dirty = True
        return self

    def set_year_of_birth(self, value: int) -> 'self.__class__':
        self._data['year_of_birth'] = value
        self._dirty = True
        return self

    def set_email(self, value: str) -> 'self.__class__':
        self._data['email'] = value
        self._dirty = True
        return self




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

    def get_mobile(self, reload: bool = False):
        """
        Get the associated Mobile record (1-to-1 relationship).

        Args:
            reload: If True, bypass cache and fetch fresh from database.

        Returns:
            Optional[Mobile]
        """
        cache_key = '_mobile_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            return getattr(self, cache_key)

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return None

        results = Mobile.find_by_owner_player_id(my_id)

        # Should only be one result for 1-to-1
        result = results[0] if results else None

        # Cache result
        setattr(self, cache_key, result)

        return result

    def get_attributes(self, reload: bool = False) -> List['Attribute']:
        """
        Get all attributes for this Player through the attribute_owners pivot table.
        Returns a list of Attribute objects.
        """
        cache_key = '_attributes_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        if self.get_id() is None:
            return []

        # Query through pivot table
        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        results = []

        try:
            query = """
                SELECT r.*
                FROM attributes r
                INNER JOIN attribute_owners p ON r.id = p.attribute_id
                WHERE p.player_id = %s
            """
            cursor.execute(query, (self.get_id(),))
            rows = cursor.fetchall()

            for row in rows:
                instance = Attribute()
                instance._data = row
                instance._dirty = False
                results.append(instance)
        finally:
            cursor.close()

        # Cache results
        setattr(self, cache_key, results)
        return results

    def get_attribute_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all AttributeOwner pivot records for this Player.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[AttributeOwner] or Iterator[AttributeOwner]
        """
        cache_key = '_attribute_owners_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return iter(cached) if lazy else cached

        if self.get_id() is None:
            return iter([]) if lazy else []

        results = AttributeOwner.find_by_player_id(self.get_id())

        # Cache results
        setattr(self, cache_key, results)
        return iter(results) if lazy else results

    def add_attribute(self, attribute: 'Attribute') -> None:
        """
        Add a attribute to this Player through the attribute_owners pivot table.
        Creates the pivot record and saves the attribute if it's new or dirty.
        """
        if self.get_id() is None:
            raise ValueError("Cannot add attribute to unsaved Player. Save the Player first.")

        # Save the related object if it's new or dirty
        if attribute._dirty:
            attribute.save()

        # Create pivot record
        pivot = AttributeOwner()
        pivot.set_player_id(self.get_id())
        pivot.set_attribute_id(attribute.get_id())

        # Set all other owner FKs to NULL explicitly
        # This ensures only one owner FK is set per pivot record
        for attr_name in dir(pivot):
            if attr_name.startswith('set_') and attr_name.endswith('_id') and attr_name != 'set_id' and attr_name != 'set_player_id' and attr_name != 'set_attribute_id':
                setter = getattr(pivot, attr_name)
                setter(None)

        pivot.save()

        # Clear cache
        cache_key = '_attributes_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_attribute_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def remove_attribute(self, attribute: 'Attribute') -> None:
        """
        Remove a attribute from this Player through the attribute_owners pivot table.
        Deletes both the pivot record and the attribute record (cascade delete).
        """
        if self.get_id() is None or attribute.get_id() is None:
            return

        # Use a fresh connection to avoid transaction conflicts
        connection = Player._create_connection()
        cursor = connection.cursor()

        try:
            # Start transaction
            connection.start_transaction()

            # Delete pivot record first
            cursor.execute(
                f"DELETE FROM attribute_owners WHERE player_id = %s AND attribute_id = %s",
                (self.get_id(), attribute.get_id()),
            )

            # Delete the related record
            cursor.execute(
                f"DELETE FROM attributes WHERE id = %s",
                (attribute.get_id(),),
            )

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

        # Clear cache
        cache_key = '_attributes_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_attribute_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def set_attributes(self, attributes_list: List['Attribute']) -> None:
        """
        Replace all attributes for this Player.
        Removes all existing attributes and adds the new ones.
        """
        if self.get_id() is None:
            raise ValueError("Cannot set attributes on unsaved Player. Save the Player first.")

        self._connect()

        try:
            # Start transaction for all operations only if one isn't already active
            if not self._connection.in_transaction:
                self._connection.start_transaction()

            # Get existing attributes
            existing = self.get_attributes(reload=True)

            # Delete all existing pivot records and related records
            cursor = self._connection.cursor()
            for item in existing:
                if item.get_id() is not None:
                    # Delete pivot record
                    cursor.execute(
                        f"DELETE FROM attribute_owners WHERE player_id = %s AND attribute_id = %s",
                        (self.get_id(), item.get_id()),
                    )
                    # Delete related record
                    cursor.execute(
                        f"DELETE FROM attributes WHERE id = %s",
                        (item.get_id(),),
                    )
            cursor.close()

            # Add new ones within the same transaction
            for item in attributes_list:
                # Save the related object if needed
                if item._dirty:
                    item.save(self._connection)

                # Create pivot record manually to avoid nested transactions
                pivot = AttributeOwner()
                pivot.set_player_id(self.get_id())
                pivot.set_attribute_id(item.get_id())
                pivot.save(self._connection)

            # Commit all operations
            self._connection.commit()

            # Clear cache
            cache_key = '_attributes_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)
            cache_key = '_attribute_owners_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)

        except Exception as e:
            self._connection.rollback()
            raise


    def get_inventories(self, reload: bool = False) -> List['Inventory']:
        """
        Get all inventories for this Player through the inventory_owners pivot table.
        Returns a list of Inventory objects.
        """
        cache_key = '_inventories_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        if self.get_id() is None:
            return []

        # Query through pivot table
        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        results = []

        try:
            query = """
                SELECT r.*
                FROM inventories r
                INNER JOIN inventory_owners p ON r.id = p.inventory_id
                WHERE p.player_id = %s
            """
            cursor.execute(query, (self.get_id(),))
            rows = cursor.fetchall()

            for row in rows:
                instance = Inventory()
                instance._data = row
                instance._dirty = False
                results.append(instance)
        finally:
            cursor.close()

        # Cache results
        setattr(self, cache_key, results)
        return results

    def get_inventory_owners(self, reload: bool = False, lazy: bool = False):
        """
        Get all InventoryOwner pivot records for this Player.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[InventoryOwner] or Iterator[InventoryOwner]
        """
        cache_key = '_inventory_owners_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return iter(cached) if lazy else cached

        if self.get_id() is None:
            return iter([]) if lazy else []

        results = InventoryOwner.find_by_player_id(self.get_id())

        # Cache results
        setattr(self, cache_key, results)
        return iter(results) if lazy else results

    def add_inventory(self, inventory: 'Inventory') -> None:
        """
        Add a inventory to this Player through the inventory_owners pivot table.
        Creates the pivot record and saves the inventory if it's new or dirty.
        """
        if self.get_id() is None:
            raise ValueError("Cannot add inventory to unsaved Player. Save the Player first.")

        # Save the related object if it's new or dirty
        if inventory._dirty:
            inventory.save()

        # Create pivot record
        pivot = InventoryOwner()
        pivot.set_player_id(self.get_id())
        pivot.set_inventory_id(inventory.get_id())

        # Set all other owner FKs to NULL explicitly
        # This ensures only one owner FK is set per pivot record
        for attr_name in dir(pivot):
            if attr_name.startswith('set_') and attr_name.endswith('_id') and attr_name != 'set_id' and attr_name != 'set_player_id' and attr_name != 'set_inventory_id':
                setter = getattr(pivot, attr_name)
                setter(None)

        pivot.save()

        # Clear cache
        cache_key = '_inventories_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_inventory_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def remove_inventory(self, inventory: 'Inventory') -> None:
        """
        Remove a inventory from this Player through the inventory_owners pivot table.
        Deletes both the pivot record and the inventory record (cascade delete).
        """
        if self.get_id() is None or inventory.get_id() is None:
            return

        # Use a fresh connection to avoid transaction conflicts
        connection = Player._create_connection()
        cursor = connection.cursor()

        try:
            # Start transaction
            connection.start_transaction()

            # Delete pivot record first
            cursor.execute(
                f"DELETE FROM inventory_owners WHERE player_id = %s AND inventory_id = %s",
                (self.get_id(), inventory.get_id()),
            )

            # Delete the related record
            cursor.execute(
                f"DELETE FROM inventories WHERE id = %s",
                (inventory.get_id(),),
            )

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

        # Clear cache
        cache_key = '_inventories_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_inventory_owners_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def set_inventories(self, inventories_list: List['Inventory']) -> None:
        """
        Replace all inventories for this Player.
        Removes all existing inventories and adds the new ones.
        """
        if self.get_id() is None:
            raise ValueError("Cannot set inventories on unsaved Player. Save the Player first.")

        self._connect()

        try:
            # Start transaction for all operations only if one isn't already active
            if not self._connection.in_transaction:
                self._connection.start_transaction()

            # Get existing inventories
            existing = self.get_inventories(reload=True)

            # Delete all existing pivot records and related records
            cursor = self._connection.cursor()
            for item in existing:
                if item.get_id() is not None:
                    # Delete pivot record
                    cursor.execute(
                        f"DELETE FROM inventory_owners WHERE player_id = %s AND inventory_id = %s",
                        (self.get_id(), item.get_id()),
                    )
                    # Delete related record
                    cursor.execute(
                        f"DELETE FROM inventories WHERE id = %s",
                        (item.get_id(),),
                    )
            cursor.close()

            # Add new ones within the same transaction
            for item in inventories_list:
                # Save the related object if needed
                if item._dirty:
                    item.save(self._connection)

                # Create pivot record manually to avoid nested transactions
                pivot = InventoryOwner()
                pivot.set_player_id(self.get_id())
                pivot.set_inventory_id(item.get_id())
                pivot.save(self._connection)

            # Commit all operations
            self._connection.commit()

            # Clear cache
            cache_key = '_inventories_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)
            cache_key = '_inventory_owners_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)

        except Exception as e:
            self._connection.rollback()
            raise



    def from_thrift(self, thrift_obj: 'Player') -> 'Player':
        """
        Populate this Model instance from a Thrift Player object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift Player instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
        if hasattr(thrift_obj, 'id'):
            self._data['id'] = thrift_obj.id
        if hasattr(thrift_obj, 'full_name'):
            self._data['full_name'] = thrift_obj.full_name
        if hasattr(thrift_obj, 'what_we_call_you'):
            self._data['what_we_call_you'] = thrift_obj.what_we_call_you
        if hasattr(thrift_obj, 'security_token'):
            self._data['security_token'] = thrift_obj.security_token
        if hasattr(thrift_obj, 'over_13'):
            self._data['over_13'] = thrift_obj.over_13
        if hasattr(thrift_obj, 'year_of_birth'):
            self._data['year_of_birth'] = thrift_obj.year_of_birth
        if hasattr(thrift_obj, 'email'):
            self._data['email'] = thrift_obj.email

        # Handle embedded mobile (1-to-1 relationship)
        if hasattr(thrift_obj, 'mobile') and thrift_obj.mobile is not None:
            mobile_obj = Mobile()
            mobile_obj.from_thrift(thrift_obj.mobile)
            # Set the foreign key to link to this parent
            mobile_obj.set_owner_player_id(self.get_id())
            # Cache the embedded object
            self._cached_mobile = mobile_obj

        self._dirty = True
        return self


    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['Player']]:
        """
        Convert this Model instance to a Thrift Player object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {}

            thrift_params['id'] = self._data.get('id')
            thrift_params['full_name'] = self._data.get('full_name')
            thrift_params['what_we_call_you'] = self._data.get('what_we_call_you')
            thrift_params['security_token'] = self._data.get('security_token')
            thrift_params['over_13'] = self._data.get('over_13')
            thrift_params['year_of_birth'] = self._data.get('year_of_birth')
            thrift_params['email'] = self._data.get('email')

            # Load embedded mobile (1-to-1 relationship)
            mobile_model = self.get_mobile()
            if mobile_model is not None:
                mobile_results, mobile_thrift = mobile_model.into_thrift()
                if mobile_thrift is not None:
                    thrift_params['mobile'] = mobile_thrift
                else:
                    results.extend(mobile_results)

            # Create Thrift object
            thrift_obj = ThriftPlayer(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {self.__class__.__name__} id={self.get_id()} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {self.__class__.__name__} to Thrift: {str(e)}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )


    def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Save the record to the database with transaction support and cascading saves.
        If id is set, performs UPDATE. Otherwise performs INSERT.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade save to related models in belongs_to relationships.
        """
        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            # Cascade save belongs-to relationships first (even if parent not dirty)
            if cascade:
                pass  # No belongs-to relationships

            # Only execute SQL if this record is dirty
            if self._dirty:
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

            # Cascade save has-many relationships (even if parent not dirty)
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

    def destroy(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
        """
        Delete this record from the database with transaction support and cascading deletes.

        Args:
            connection: Optional database connection for transaction support.
                       If provided, uses this connection and doesn't commit (caller manages transaction).
            cascade: If True, cascade destroy to related models (has-many children and pivot associations).
        """
        if self.get_id() is None:
            raise ValueError("Cannot destroy a record without an id")

        # Determine if we own the connection
        owns_connection = connection is None
        if owns_connection:
            self._connect()
            connection = self._connection
            # Start transaction only if one isn't already active
            if not connection.in_transaction:
                connection.start_transaction()

        cursor = None
        try:
            cursor = connection.cursor()

            # Cascade destroy children and clean up associations first
            if cascade:
                # Cascade destroy attribute_owners children
                cache_key = '_attribute_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_attribute_owners(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy inventory_owners children
                cache_key = '_inventory_owners_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_inventory_owners(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Cascade destroy mobiles children
                cache_key = '_mobiles_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.get_mobiles(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist
# Clean up attribute_owners associations and cascade delete attributes
                if self.get_id() is not None:
                    # First, cascade delete the related objects
                    try:
                        related_objects = self.get_attributes(reload=True)
                        for obj in related_objects:
                            if hasattr(obj, 'destroy'):
                                obj.destroy(connection=connection, cascade=cascade)
                    except:
                        pass  # Method may not exist

                    # Then delete the pivot table associations
                    cursor.execute(
                        "DELETE FROM `attribute_owners` WHERE `player_id` = %s",
                        (self.get_id(),),
                    )
# Clean up inventory_owners associations and cascade delete inventories
                if self.get_id() is not None:
                    # First, cascade delete the related objects
                    try:
                        related_objects = self.get_inventories(reload=True)
                        for obj in related_objects:
                            if hasattr(obj, 'destroy'):
                                obj.destroy(connection=connection, cascade=cascade)
                    except:
                        pass  # Method may not exist

                    # Then delete the pivot table associations
                    cursor.execute(
                        "DELETE FROM `inventory_owners` WHERE `player_id` = %s",
                        (self.get_id(),),
                    )

            # Delete the record itself
            cursor.execute(f"DELETE FROM `players` WHERE `id` = %s", (self.get_id(),))

            # Clear the id to mark as deleted
            self._data['id'] = None

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

    def reload(self) -> None:
        """
        Reload this record from the database and reload cached relationships.
        """
        if self.get_id() is None:
            raise ValueError("Cannot reload a record without an id")

        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM `players` WHERE `id` = %s", (self.get_id(),))
            row = cursor.fetchone()
            if row:
                self._data = row
                self._dirty = False

                # Reload cached relationships by iterating over cache attributes
                for attr_name in dir(self):
                    if attr_name.endswith('_cache') and not attr_name.startswith('_'):
                        cached_value = getattr(self, attr_name, None)
                        if cached_value is not None:
                            # Reload cached relationships recursively
                            if hasattr(cached_value, 'reload'):
                                cached_value.reload()
                            elif isinstance(cached_value, list):
                                for item in cached_value:
                                    if hasattr(item, 'reload'):
                                        item.reload()
            else:
                raise ValueError(f"Record with id={self.get_id()} not found in database")
        finally:
            cursor.close()

    # No find_by methods (no columns ending with _id)


