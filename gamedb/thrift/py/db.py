import mysql.connector
from typing import Optional, Tuple
from contextlib import contextmanager
import logging
import sys

sys.path.append("../gen-py")

# Configure logging
logger = logging.getLogger(__name__)

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    ItemVector3,
    Attribute,
    Item,
    ItemBlueprintComponent,
    ItemBlueprint,
    ItemDb,
    InventoryEntry,
    Inventory,
    Mobile,
    Player,
)
from common import is_ok, is_true
from dbinc import ItemMixin, InventoryMixin, MobileMixin, PlayerMixin


# ============================================================================
# Constants
# ============================================================================

# Table names
TABLE_ATTRIBUTES = "attributes"
TABLE_ATTRIBUTE_OWNERS = "attribute_owners"
TABLE_ITEMS = "items"
TABLE_ITEM_BLUEPRINTS = "item_blueprints"
TABLE_ITEM_BLUEPRINT_COMPONENTS = "item_blueprint_components"
TABLE_INVENTORIES = "inventories"
TABLE_INVENTORY_ENTRIES = "inventory_entries"
TABLE_INVENTORY_OWNERS = "inventory_owners"
TABLE_MOBILES = "mobiles"
TABLE_PLAYERS = "players"

# Error message templates
MSG_CREATED = "Successfully created {type} id={id}"
MSG_UPDATED = "Successfully updated {type} id={id}"
MSG_DESTROYED = "Successfully destroyed {type} id={id}"
MSG_LOADED = "Successfully loaded {type} id={id}"
MSG_CREATE_FAILED = "Failed to create {type} in database={database}: {error}"
MSG_UPDATE_FAILED = "Failed to update {type} id={id} in database={database}: {error}"
MSG_DESTROY_FAILED = "Failed to destroy {type} id={id} in database={database}: {error}"
MSG_LOAD_FAILED = "Failed to load {type} id={id} from database={database}: {error}"
MSG_NOT_FOUND = "{type} id={id} not found in database={database}"


# ============================================================================
# Utility Functions for Thrift Struct Introspection and SQL Generation
# ============================================================================


def get_struct_fields(obj) -> dict:
    """
    Get all field names and values from a thrift struct.
    Returns a dict of {field_name: value}.
    """
    if not hasattr(obj, "thrift_spec") or obj.thrift_spec is None:
        return {}

    fields = {}
    for field_spec in obj.thrift_spec:
        if field_spec is None:
            continue
        field_name = field_spec[2]
        if hasattr(obj, field_name):
            fields[field_name] = getattr(obj, field_name)

    return fields


def get_struct_type_name(obj) -> str:
    """Get the type name of a thrift struct."""
    return obj.__class__.__name__


def attribute_value_to_sql_fields(attribute: Attribute) -> dict:
    """
    Convert an Attribute's value to SQL field values.
    Returns a dict with keys: bool_value, double_value, vector3_x, vector3_y, vector3_z, asset_id
    """
    fields = {
        "bool_value": None,
        "double_value": None,
        "vector3_x": None,
        "vector3_y": None,
        "vector3_z": None,
        "asset_id": None,
    }

    if attribute.value is not None:
        if isinstance(attribute.value, bool):
            fields["bool_value"] = attribute.value
        elif isinstance(attribute.value, (int, float)) and not isinstance(
            attribute.value, bool
        ):
            fields["double_value"] = attribute.value
        elif isinstance(attribute.value, ItemVector3):
            fields["vector3_x"] = attribute.value.x
            fields["vector3_y"] = attribute.value.y
            fields["vector3_z"] = attribute.value.z
        elif isinstance(attribute.value, int):
            fields["asset_id"] = attribute.value

    return fields


# Type registry for dispatcher functions
TYPE_REGISTRY = {
    "Attribute": Attribute,
    "Item": Item,
    "ItemBlueprint": ItemBlueprint,
    "Inventory": Inventory,
    "Mobile": Mobile,
    "Player": Player,
}


class DB(ItemMixin, InventoryMixin, MobileMixin, PlayerMixin):
    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password
        self.connection: Optional[mysql.connector.connection.MySQLConnection] = None

    def connect(self):
        if not self.connection or not self.connection.is_connected():
            logger.debug(f"Connecting to database: host={self.host}, user={self.user}")
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
                f"Transaction failed (dict cursor): {type(e).__name__}: {str(e)}"
            )
            if self.connection:
                logger.debug("Rolling back transaction (dict cursor)")
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def get_attributes_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.attributes (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                internal_name VARCHAR(255) NOT NULL,
                visible BOOLEAN NOT NULL,
                attribute_type VARCHAR(50) NOT NULL,
                bool_value BOOLEAN,
                double_value DOUBLE,
                vector3_x DOUBLE,
                vector3_y DOUBLE,
                vector3_z DOUBLE,
                asset_id BIGINT
            );""",
        ]

    def get_attribute_owners_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.attribute_owners (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                attribute_id BIGINT NOT NULL,
                mobile_id BIGINT,
                item_id BIGINT,
                asset_id BIGINT,
                player_id BIGINT,
                FOREIGN KEY (attribute_id) REFERENCES {database}.attributes(id)
            );""",
        ]

    def get_attribute_sql(
        self,
        database: str,
        obj: Attribute,
        table: Optional[str] = None,
        drop: bool = False,
        truncate: bool = False,
    ) -> list[str]:
        # If both drop and truncate are True, set truncate to False
        if drop and truncate:
            truncate = False

        attributes_table = table if table else "attributes"
        attribute_owners_table = "attribute_owners"

        statements = []

        if drop:
            statements.append(
                f"DROP TABLE IF EXISTS {database}.{attribute_owners_table};"
            )
            statements.append(f"DROP TABLE IF EXISTS {database}.{attributes_table};")

        if truncate:
            statements.append(f"TRUNCATE TABLE {database}.{attribute_owners_table};")
            statements.append(f"TRUNCATE TABLE {database}.{attributes_table};")

        # Build attribute value fields (flattened AttributeValue union)
        bool_val = "NULL"
        double_val = "NULL"
        vec3_x = "NULL"
        vec3_y = "NULL"
        vec3_z = "NULL"
        asset_val = "NULL"

        if obj.value is not None:
            if isinstance(obj.value, bool):
                bool_val = str(obj.value)
            elif isinstance(obj.value, (int, float)) and not isinstance(
                obj.value, bool
            ):
                double_val = str(obj.value)
            elif isinstance(obj.value, ItemVector3):
                vec3_x = str(obj.value.x)
                vec3_y = str(obj.value.y)
                vec3_z = str(obj.value.z)
            elif isinstance(obj.value, int):
                asset_val = str(obj.value)

        # Insert attribute
        from game.ttypes import AttributeType as AttrTypeEnum

        attr_type_name = AttrTypeEnum._VALUES_TO_NAMES[obj.attribute_type]

        statements.append(
            f"INSERT INTO {database}.{attributes_table} "
            f"(internal_name, visible, attribute_type, bool_value, double_value, "
            f"vector3_x, vector3_y, vector3_z, asset_id) "
            f"VALUES ('{obj.internal_name}', {obj.visible}, "
            f"'{attr_type_name}', {bool_val}, {double_val}, "
            f"{vec3_x}, {vec3_y}, {vec3_z}, {asset_val});"
        )

        # Insert owner (one-to-one relationship)
        mobile_id = "NULL"
        item_id = "NULL"
        asset_id = "NULL"
        player_id = "NULL"

        if obj.owner:
            if hasattr(obj.owner, "mobile_id") and obj.owner.mobile_id is not None:
                mobile_id = str(obj.owner.mobile_id)
            elif hasattr(obj.owner, "item_id") and obj.owner.item_id is not None:
                item_id = str(obj.owner.item_id)
            elif hasattr(obj.owner, "asset_id") and obj.owner.asset_id is not None:
                asset_id = str(obj.owner.asset_id)
            elif hasattr(obj.owner, "player_id") and obj.owner.player_id is not None:
                player_id = str(obj.owner.player_id)

        statements.append(
            f"INSERT INTO {database}.{attribute_owners_table} "
            f"(attribute_id, mobile_id, item_id, asset_id, player_id) "
            f"VALUES ({{last_insert_id}}, {mobile_id}, {item_id}, {asset_id}, {player_id});"
        )

        return statements

    def create_attribute(
        self,
        database: str,
        obj: Attribute,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            attributes_table = table if table else TABLE_ATTRIBUTES

            with self.transaction() as cursor:
                # Convert attribute value to SQL fields using helper
                value_fields = attribute_value_to_sql_fields(obj)

                # Get attribute type name
                from game.ttypes import AttributeType as AttrTypeEnum

                attr_type_name = AttrTypeEnum._VALUES_TO_NAMES[obj.attribute_type]

                # Insert attribute with parameterized query
                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {database}.{attributes_table} "
                        f"(internal_name, visible, attribute_type, bool_value, double_value, "
                        f"vector3_x, vector3_y, vector3_z, asset_id) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            obj.internal_name,
                            obj.visible,
                            attr_type_name,
                            value_fields["bool_value"],
                            value_fields["double_value"],
                            value_fields["vector3_x"],
                            value_fields["vector3_y"],
                            value_fields["vector3_z"],
                            value_fields["asset_id"],
                        ),
                    )
                    obj.id = cursor.lastrowid
                else:
                    cursor.execute(
                        f"INSERT INTO {database}.{attributes_table} "
                        f"(id, internal_name, visible, attribute_type, bool_value, double_value, "
                        f"vector3_x, vector3_y, vector3_z, asset_id) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (
                            obj.id,
                            obj.internal_name,
                            obj.visible,
                            attr_type_name,
                            value_fields["bool_value"],
                            value_fields["double_value"],
                            value_fields["vector3_x"],
                            value_fields["vector3_y"],
                            value_fields["vector3_z"],
                            value_fields["asset_id"],
                        ),
                    )

                # Insert attribute owner if specified
                if obj.owner:
                    mobile_id = None
                    item_id = None
                    asset_id = None
                    player_id = None

                    if (
                        hasattr(obj.owner, "mobile_id")
                        and obj.owner.mobile_id is not None
                    ):
                        mobile_id = obj.owner.mobile_id
                    elif (
                        hasattr(obj.owner, "item_id") and obj.owner.item_id is not None
                    ):
                        item_id = obj.owner.item_id
                    elif (
                        hasattr(obj.owner, "asset_id")
                        and obj.owner.asset_id is not None
                    ):
                        asset_id = obj.owner.asset_id
                    elif (
                        hasattr(obj.owner, "player_id")
                        and obj.owner.player_id is not None
                    ):
                        player_id = obj.owner.player_id

                    cursor.execute(
                        f"INSERT INTO {database}.{TABLE_ATTRIBUTE_OWNERS} "
                        f"(attribute_id, mobile_id, item_id, asset_id, player_id) "
                        f"VALUES (%s, %s, %s, %s, %s)",
                        (obj.id, mobile_id, item_id, asset_id, player_id),
                    )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_CREATED.format(type="Attribute", id=obj.id),
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_CREATE_FAILED.format(
                        type="Attribute", database=database, error=str(e)
                    ),
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def update_attribute(
        self,
        database: str,
        obj: Attribute,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Attribute with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            attributes_table = table if table else "attributes"
            attribute_owners_table = "attribute_owners"

            # Build attribute value fields
            bool_val = "NULL"
            double_val = "NULL"
            vec3_x = "NULL"
            vec3_y = "NULL"
            vec3_z = "NULL"
            asset_val = "NULL"

            if obj.value is not None:
                if isinstance(obj.value, bool):
                    bool_val = str(obj.value)
                elif isinstance(obj.value, (int, float)) and not isinstance(
                    obj.value, bool
                ):
                    double_val = str(obj.value)
                elif isinstance(obj.value, ItemVector3):
                    vec3_x = str(obj.value.x)
                    vec3_y = str(obj.value.y)
                    vec3_z = str(obj.value.z)
                elif isinstance(obj.value, int):
                    asset_val = str(obj.value)

            from game.ttypes import AttributeType as AttrTypeEnum

            attr_type_name = AttrTypeEnum._VALUES_TO_NAMES[obj.attribute_type]

            # Update attribute
            cursor.execute(
                f"UPDATE {database}.{attributes_table} SET "
                f"internal_name = '{obj.internal_name}', "
                f"visible = {obj.visible}, "
                f"attribute_type = '{attr_type_name}', "
                f"bool_value = {bool_val}, "
                f"double_value = {double_val}, "
                f"vector3_x = {vec3_x}, "
                f"vector3_y = {vec3_y}, "
                f"vector3_z = {vec3_z}, "
                f"asset_id = {asset_val} "
                f"WHERE id = {obj.id};"
            )

            # Update owner (delete and re-insert)
            cursor.execute(
                f"DELETE FROM {database}.{attribute_owners_table} WHERE attribute_id = {obj.id};"
            )

            mobile_id = "NULL"
            item_id = "NULL"
            asset_id = "NULL"
            player_id = "NULL"

            if obj.owner:
                if hasattr(obj.owner, "mobile_id") and obj.owner.mobile_id is not None:
                    mobile_id = str(obj.owner.mobile_id)
                elif hasattr(obj.owner, "item_id") and obj.owner.item_id is not None:
                    item_id = str(obj.owner.item_id)
                elif hasattr(obj.owner, "asset_id") and obj.owner.asset_id is not None:
                    asset_id = str(obj.owner.asset_id)
                elif (
                    hasattr(obj.owner, "player_id") and obj.owner.player_id is not None
                ):
                    player_id = str(obj.owner.player_id)

            cursor.execute(
                f"INSERT INTO {database}.{attribute_owners_table} "
                f"(attribute_id, mobile_id, item_id, asset_id, player_id) "
                f"VALUES ({obj.id}, {mobile_id}, {item_id}, {asset_id}, {player_id});"
            )

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated Attribute id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Attribute id={obj.id} in database={database}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def load_attribute(
        self,
        database: str,
        attribute_id: int,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[Attribute]]:
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            attributes_table = table if table else "attributes"
            attribute_owners_table = "attribute_owners"

            # Load the attribute
            cursor.execute(
                f"SELECT * FROM {database}.{attributes_table} WHERE id = %s;",
                (attribute_id,),
            )
            attr_row = cursor.fetchone()

            if not attr_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Attribute id={attribute_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Reconstruct AttributeValue union
            value = None
            if attr_row["bool_value"] is not None:
                value = attr_row["bool_value"]
            elif attr_row["double_value"] is not None:
                value = attr_row["double_value"]
            elif attr_row["vector3_x"] is not None:
                value = ItemVector3(
                    x=attr_row["vector3_x"],
                    y=attr_row["vector3_y"],
                    z=attr_row["vector3_z"],
                )
            elif attr_row["asset_id"] is not None:
                value = attr_row["asset_id"]

            # Load owner
            cursor.execute(
                f"SELECT * FROM {database}.{attribute_owners_table} WHERE attribute_id = %s;",
                (attribute_id,),
            )
            owner_row = cursor.fetchone()

            owner = None
            if owner_row:
                if owner_row["mobile_id"]:
                    owner = owner_row["mobile_id"]
                elif owner_row["item_id"]:
                    owner = owner_row["item_id"]
                elif owner_row["asset_id"]:
                    owner = owner_row["asset_id"]
                elif owner_row["player_id"]:
                    owner = owner_row["player_id"]

            # Import AttributeType enum
            from game.ttypes import AttributeType

            attr_type = AttributeType._NAMES_TO_VALUES[attr_row["attribute_type"]]

            # Create Attribute object
            attribute = Attribute(
                id=attr_row["id"],
                internal_name=attr_row["internal_name"],
                visible=attr_row["visible"],
                value=value,
                attribute_type=attr_type,
                owner=owner,
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded Attribute id={attribute_id}",
                ),
                attribute,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Attribute id={attribute_id} from database={database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def save_attribute(
        self,
        database: str,
        obj: Attribute,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        if obj.id is None:
            return self.create_attribute(database, obj, table)
        else:
            return self.update_attribute(database, obj, table)

    def destroy_attribute(
        self,
        database: str,
        attribute_id: int,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            attributes_table = table if table else "attributes"
            attribute_owners_table = "attribute_owners"

            # Delete attribute owner first (foreign key)
            cursor.execute(
                f"DELETE FROM {database}.{attribute_owners_table} WHERE attribute_id = {attribute_id};"
            )

            # Delete the attribute
            cursor.execute(
                f"DELETE FROM {database}.{attributes_table} WHERE id = {attribute_id};"
            )

            # Check if any rows were affected
            if cursor.rowcount == 0:
                self.connection.rollback()
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Attribute id={attribute_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                ]

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Attribute id={attribute_id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Attribute id={attribute_id} in database={database}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def save(
        self,
        database: str,
        obj,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        """
        Unified save function that dispatches to the appropriate save_* method
        based on object type.
        """
        type_name = get_struct_type_name(obj)
        obj_id = getattr(obj, "id", None) if hasattr(obj, "id") else None
        logger.info(
            f"=== SAVE (dispatch): type={type_name}, id={obj_id}, database={database}"
        )

        dispatch_map = {
            "Attribute": self.save_attribute,
            "Item": self.save_item,
            "ItemBlueprint": self.save_item_blueprint,
            "Inventory": self.save_inventory,
            "Mobile": self.save_mobile,
            "Player": self.save_player,
        }

        if type_name not in dispatch_map:
            logger.warning(f"Unknown type for save: {type_name}")
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Unknown type for save: {type_name}",
                    error_code=GameError.DB_INVALID_DATA,
                ),
            ]

        logger.debug(f"Dispatching to save_{type_name.lower()}")
        return dispatch_map[type_name](database, obj, table)

    def create(
        self,
        database: str,
        obj,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        """
        Unified create function that dispatches to the appropriate create_* method
        based on object type.
        """
        type_name = get_struct_type_name(obj)
        obj_id = getattr(obj, 'id', None) if hasattr(obj, 'id') else None
        logger.info(f"=== CREATE (dispatch): type={type_name}, id={obj_id}, database={database}")

        dispatch_map = {
            "Attribute": self.create_attribute,
            "Item": self.create_item,
            "ItemBlueprint": self.create_item_blueprint,
            "Inventory": self.create_inventory,
            "Mobile": self.create_mobile,
            "Player": self.create_player,
        }

        if type_name not in dispatch_map:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Unknown type for create: {type_name}",
                    error_code=GameError.DB_INVALID_DATA,
                ),
            ]

        return dispatch_map[type_name](database, obj, table)

    def update(
        self,
        database: str,
        obj,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        """
        Unified update function that dispatches to the appropriate update_* method
        based on object type.
        """
        type_name = get_struct_type_name(obj)
        obj_id = getattr(obj, 'id', None) if hasattr(obj, 'id') else None
        logger.info(f"=== UPDATE (dispatch): type={type_name}, id={obj_id}, database={database}")

        dispatch_map = {
            "Attribute": self.update_attribute,
            "Item": self.update_item,
            "ItemBlueprint": self.update_item_blueprint,
            "Inventory": self.update_inventory,
            "Mobile": self.update_mobile,
            "Player": self.update_player,
        }

        if type_name not in dispatch_map:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Unknown type for update: {type_name}",
                    error_code=GameError.DB_INVALID_DATA,
                ),
            ]

        return dispatch_map[type_name](database, obj, table)

    def destroy(
        self,
        database: str,
        obj_or_id,
        obj_type: Optional[str] = None,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        """
        Unified destroy function that dispatches to the appropriate destroy_* method.
        Can accept either an object (will use its id) or an id with obj_type specified.
        """
        # If obj_or_id is an object, extract its type and id
        logger.info(f"=== DESTROY (dispatch): obj_or_id={obj_or_id}, obj_type={obj_type}, database={database}")
        if hasattr(obj_or_id, "__class__") and hasattr(obj_or_id, "id"):
            type_name = get_struct_type_name(obj_or_id)
            obj_id = obj_or_id.id
        elif obj_type:
            type_name = obj_type
            obj_id = obj_or_id
        else:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"destroy() requires either an object or obj_type to be specified",
                    error_code=GameError.DB_INVALID_DATA,
                ),
            ]

        dispatch_map = {
            "Attribute": self.destroy_attribute,
            "Item": self.destroy_item,
            "ItemBlueprint": self.destroy_item_blueprint,
            "Inventory": self.destroy_inventory,
            "Mobile": self.destroy_mobile,
            "Player": self.destroy_player,
        }

        if type_name not in dispatch_map:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Unknown type for destroy: {type_name}",
                    error_code=GameError.DB_INVALID_DATA,
                ),
            ]

        return dispatch_map[type_name](database, obj_id, table)

    def load(
        self,
        database: str,
        obj_id: int,
        obj_type: str,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[any]]:
        """
        Unified load function that dispatches to the appropriate load_* method.
        Requires obj_type to be specified (e.g., 'Item', 'Mobile', etc.).
        """
        dispatch_map = {
            "Attribute": self.load_attribute,
            "Item": self.load_item,
            "ItemBlueprint": self.load_item_blueprint,
            "Inventory": self.load_inventory,
            "Mobile": self.load_mobile,
            "Player": self.load_player,
        }

        if obj_type not in dispatch_map:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Unknown type for load: {obj_type}",
                    error_code=GameError.DB_INVALID_DATA,
                ),
                None,
            )

        return dispatch_map[obj_type](database, obj_id, table)
