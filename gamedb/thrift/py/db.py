import mysql.connector
from typing import Optional, Tuple
from contextlib import contextmanager
import sys
sys.path.append('../gen-py')

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
    if not hasattr(obj, 'thrift_spec') or obj.thrift_spec is None:
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
        'bool_value': None,
        'double_value': None,
        'vector3_x': None,
        'vector3_y': None,
        'vector3_z': None,
        'asset_id': None,
    }

    if attribute.value is not None:
        if isinstance(attribute.value, bool):
            fields['bool_value'] = attribute.value
        elif isinstance(attribute.value, (int, float)) and not isinstance(attribute.value, bool):
            fields['double_value'] = attribute.value
        elif isinstance(attribute.value, ItemVector3):
            fields['vector3_x'] = attribute.value.x
            fields['vector3_y'] = attribute.value.y
            fields['vector3_z'] = attribute.value.z
        elif isinstance(attribute.value, int):
            fields['asset_id'] = attribute.value

    return fields


# Type registry for dispatcher functions
TYPE_REGISTRY = {
    'Attribute': Attribute,
    'Item': Item,
    'ItemBlueprint': ItemBlueprint,
    'Inventory': Inventory,
    'Mobile': Mobile,
    'Player': Player,
}


class DB:
    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password
        self.connection: Optional[
            mysql.connector.connection.MySQLConnection
        ] = None

    def connect(self):
        if not self.connection or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                use_pure=True,
                ssl_disabled=True,
            )

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        Automatically commits on success, rolls back on exception.

        Usage:
            with self.transaction() as cursor:
                cursor.execute(...)
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute("START TRANSACTION;")
            yield cursor
            self.connection.commit()
        except Exception:
            if self.connection:
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
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("START TRANSACTION;")
            yield cursor
            self.connection.commit()
        except Exception:
            if self.connection:
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

    def get_items_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.items (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                internal_name VARCHAR(255) NOT NULL,
                max_stack_size BIGINT,
                item_type VARCHAR(50) NOT NULL,
                blueprint_id BIGINT
            );""",
        ]

    def get_item_blueprints_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.item_blueprints (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                bake_time_ms BIGINT NOT NULL
            );""",
        ]

    def get_item_blueprint_components_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.item_blueprint_components (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                item_blueprint_id BIGINT NOT NULL,
                component_item_id BIGINT NOT NULL,
                ratio DOUBLE NOT NULL,
                FOREIGN KEY (item_blueprint_id) REFERENCES {database}.item_blueprints(id)
            );""",
        ]

    def get_inventories_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.inventories (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                owner_id BIGINT NOT NULL,
                owner_type VARCHAR(50),
                max_entries BIGINT NOT NULL,
                max_volume DOUBLE NOT NULL,
                last_calculated_volume DOUBLE DEFAULT 0.0
            );""",
        ]

    def get_inventory_entries_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.inventory_entries (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                inventory_id BIGINT NOT NULL,
                item_id BIGINT NOT NULL,
                quantity DOUBLE NOT NULL,
                is_max_stacked BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (inventory_id) REFERENCES {database}.inventories(id)
            );""",
        ]

    def get_inventory_owners_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.inventory_owners (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                inventory_id BIGINT NOT NULL,
                mobile_id BIGINT,
                item_id BIGINT,
                asset_id BIGINT,
                player_id BIGINT,
                FOREIGN KEY (inventory_id) REFERENCES {database}.inventories(id)
            );""",
        ]

    def get_mobiles_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.mobiles (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                mobile_type VARCHAR(50) NOT NULL,
                owner_mobile_id BIGINT,
                owner_item_id BIGINT,
                owner_asset_id BIGINT,
                owner_player_id BIGINT
            );""",
        ]

    def get_players_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.players (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                what_we_call_you VARCHAR(255) NOT NULL,
                security_token VARCHAR(255) NOT NULL,
                over_13 BOOLEAN NOT NULL,
                year_of_birth BIGINT NOT NULL
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
            statements.append(f"DROP TABLE IF EXISTS {database}.{attribute_owners_table};")
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
            elif isinstance(obj.value, (int, float)) and not isinstance(obj.value, bool):
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
            if hasattr(obj.owner, 'mobile_id') and obj.owner.mobile_id is not None:
                mobile_id = str(obj.owner.mobile_id)
            elif hasattr(obj.owner, 'item_it') and obj.owner.item_it is not None:
                item_id = str(obj.owner.item_it)
            elif hasattr(obj.owner, 'asset_id') and obj.owner.asset_id is not None:
                asset_id = str(obj.owner.asset_id)
            elif hasattr(obj.owner, 'player_id') and obj.owner.player_id is not None:
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
                            value_fields['bool_value'],
                            value_fields['double_value'],
                            value_fields['vector3_x'],
                            value_fields['vector3_y'],
                            value_fields['vector3_z'],
                            value_fields['asset_id'],
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
                            value_fields['bool_value'],
                            value_fields['double_value'],
                            value_fields['vector3_x'],
                            value_fields['vector3_y'],
                            value_fields['vector3_z'],
                            value_fields['asset_id'],
                        ),
                    )

                # Insert attribute owner if specified
                if obj.owner:
                    mobile_id = None
                    item_id = None
                    asset_id = None
                    player_id = None

                    if hasattr(obj.owner, 'mobile_id') and obj.owner.mobile_id is not None:
                        mobile_id = obj.owner.mobile_id
                    elif hasattr(obj.owner, 'item_it') and obj.owner.item_it is not None:
                        item_id = obj.owner.item_it
                    elif hasattr(obj.owner, 'asset_id') and obj.owner.asset_id is not None:
                        asset_id = obj.owner.asset_id
                    elif hasattr(obj.owner, 'player_id') and obj.owner.player_id is not None:
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
                    message=MSG_CREATE_FAILED.format(type="Attribute", database=database, error=str(e)),
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
                elif isinstance(obj.value, (int, float)) and not isinstance(obj.value, bool):
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
                if hasattr(obj.owner, 'mobile_id') and obj.owner.mobile_id is not None:
                    mobile_id = str(obj.owner.mobile_id)
                elif hasattr(obj.owner, 'item_it') and obj.owner.item_it is not None:
                    item_id = str(obj.owner.item_it)
                elif hasattr(obj.owner, 'asset_id') and obj.owner.asset_id is not None:
                    asset_id = str(obj.owner.asset_id)
                elif hasattr(obj.owner, 'player_id') and obj.owner.player_id is not None:
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
            if attr_row['bool_value'] is not None:
                value = attr_row['bool_value']
            elif attr_row['double_value'] is not None:
                value = attr_row['double_value']
            elif attr_row['vector3_x'] is not None:
                value = ItemVector3(
                    x=attr_row['vector3_x'],
                    y=attr_row['vector3_y'],
                    z=attr_row['vector3_z'],
                )
            elif attr_row['asset_id'] is not None:
                value = attr_row['asset_id']

            # Load owner
            cursor.execute(
                f"SELECT * FROM {database}.{attribute_owners_table} WHERE attribute_id = %s;",
                (attribute_id,),
            )
            owner_row = cursor.fetchone()

            owner = None
            if owner_row:
                if owner_row['mobile_id']:
                    owner = owner_row['mobile_id']
                elif owner_row['item_id']:
                    owner = owner_row['item_id']
                elif owner_row['asset_id']:
                    owner = owner_row['asset_id']
                elif owner_row['player_id']:
                    owner = owner_row['player_id']

            # Import AttributeType enum
            from game.ttypes import AttributeType
            attr_type = AttributeType._NAMES_TO_VALUES[attr_row['attribute_type']]

            # Create Attribute object
            attribute = Attribute(
                id=attr_row['id'],
                internal_name=attr_row['internal_name'],
                visible=attr_row['visible'],
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

    def get_item_sql(
        self,
        database: str,
        obj: Item,
        table: Optional[str] = None,
        drop: bool = False,
        truncate: bool = False,
    ) -> list[str]:
        # If both drop and truncate are True, set truncate to False
        if drop and truncate:
            truncate = False

        item_table = table if table else "items"
        attributes_table = "attributes"
        attribute_owners_table = "attribute_owners"

        statements = []

        if drop:
            statements.append(f"DROP TABLE IF EXISTS {database}.{attribute_owners_table};")
            statements.append(f"DROP TABLE IF EXISTS {database}.{attributes_table};")
            statements.append(f"DROP TABLE IF EXISTS {database}.{item_table};")

        if truncate:
            statements.append(f"TRUNCATE TABLE {database}.{attribute_owners_table};")
            statements.append(f"TRUNCATE TABLE {database}.{attributes_table};")
            statements.append(f"TRUNCATE TABLE {database}.{item_table};")

        # Handle optional blueprint - reference by id
        blueprint_id = obj.blueprint.id if obj.blueprint else None

        # Insert the item
        from game.ttypes import ItemType as ItemTypeEnum
        item_type_name = ItemTypeEnum._VALUES_TO_NAMES[obj.item_type]

        max_stack = obj.max_stack_size if obj.max_stack_size else "NULL"
        blueprint_val = blueprint_id if blueprint_id else "NULL"

        if obj.id is None:
            statements.append(
                f"INSERT INTO {database}.{item_table} "
                f"(internal_name, max_stack_size, item_type, blueprint_id) "
                f"VALUES ('{obj.internal_name}', {max_stack}, '{item_type_name}', {blueprint_val});"
            )
        else:
            statements.append(
                f"INSERT INTO {database}.{item_table} "
                f"(id, internal_name, max_stack_size, item_type, blueprint_id) "
                f"VALUES ({obj.id}, '{obj.internal_name}', {max_stack}, '{item_type_name}', {blueprint_val});"
            )

        # Insert attributes (one-to-many relationship via attribute_owners)
        if obj.attributes:
            for attr_type, attribute in obj.attributes.items():
                # Build attribute value fields
                bool_val = "NULL"
                double_val = "NULL"
                vec3_x = "NULL"
                vec3_y = "NULL"
                vec3_z = "NULL"
                asset_val = "NULL"

                if attribute.value is not None:
                    if isinstance(attribute.value, bool):
                        bool_val = str(attribute.value)
                    elif isinstance(attribute.value, (int, float)) and not isinstance(attribute.value, bool):
                        double_val = str(attribute.value)
                    elif isinstance(attribute.value, ItemVector3):
                        vec3_x = str(attribute.value.x)
                        vec3_y = str(attribute.value.y)
                        vec3_z = str(attribute.value.z)
                    elif isinstance(attribute.value, int):
                        asset_val = str(attribute.value)

                # Insert attribute
                from game.ttypes import AttributeType as AttrTypeEnum2
                attr_type_name2 = AttrTypeEnum2._VALUES_TO_NAMES[attribute.attribute_type]

                statements.append(
                    f"INSERT INTO {database}.{attributes_table} "
                    f"(internal_name, visible, attribute_type, bool_value, double_value, "
                    f"vector3_x, vector3_y, vector3_z, asset_id) "
                    f"VALUES ('{attribute.internal_name}', {attribute.visible}, "
                    f"'{attr_type_name2}', {bool_val}, {double_val}, "
                    f"{vec3_x}, {vec3_y}, {vec3_z}, {asset_val});"
                )

                # Insert attribute owner relationship (use placeholder for attribute id and item id)
                statements.append(
                    f"INSERT INTO {database}.{attribute_owners_table} "
                    f"(attribute_id, item_id) "
                    f"VALUES ({{last_insert_id}}, {{item_id}});"
                )

        return statements

    def create_item(
        self,
        database: str,
        obj: Item,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            # If blueprint exists, save it first
            if obj.blueprint:
                blueprint_results = self.save_item_blueprint(database, obj.blueprint)
                if not is_ok(blueprint_results):
                    self.connection.rollback()
                    return blueprint_results

            # Get SQL statements
            statements = self.get_item_sql(database, obj, table)

            # Execute each statement and track last_insert_id
            last_id = None
            item_id_set = False
            for stmt in statements:
                # Replace placeholder with actual last_insert_id
                if '{last_insert_id}' in stmt:
                    if last_id is None:
                        raise Exception("Attempted to use last_insert_id but no previous insert occurred")
                    stmt = stmt.replace('{last_insert_id}', str(last_id))

                # Replace placeholder with actual item_id
                if '{item_id}' in stmt:
                    current_item_id = obj.id if obj.id is not None else last_id
                    if current_item_id is None:
                        raise Exception("Attempted to use item_id but no item insert occurred")
                    stmt = stmt.replace('{item_id}', str(current_item_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith('INSERT'):
                    last_id = cursor.lastrowid
                    # If this was the item insert and obj.id was None, set it now
                    if not item_id_set and obj.id is None and 'items' in stmt:
                        obj.id = last_id
                        item_id_set = True

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created Item id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to save Item id={obj.id}, internal_name={obj.internal_name} to database={database}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def update_item(
        self,
        database: str,
        obj: Item,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Item with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            # If blueprint exists, save it first (will create or update as needed)
            if obj.blueprint:
                blueprint_results = self.save_item_blueprint(database, obj.blueprint)
                if not is_ok(blueprint_results):
                    self.connection.rollback()
                    return blueprint_results

            item_table = table if table else "items"
            attributes_table = "attributes"
            attribute_owners_table = "attribute_owners"

            # Handle optional blueprint - reference by id
            blueprint_id = obj.blueprint.id if obj.blueprint else None

            from game.ttypes import ItemType as ItemTypeEnum
            item_type_name = ItemTypeEnum._VALUES_TO_NAMES[obj.item_type]

            max_stack = obj.max_stack_size if obj.max_stack_size else "NULL"
            blueprint_val = blueprint_id if blueprint_id else "NULL"

            # Update item
            cursor.execute(
                f"UPDATE {database}.{item_table} SET "
                f"internal_name = '{obj.internal_name}', "
                f"max_stack_size = {max_stack}, "
                f"item_type = '{item_type_name}', "
                f"blueprint_id = {blueprint_val} "
                f"WHERE id = {obj.id};"
            )

            # Delete existing attributes
            # First get the attribute IDs
            cursor.execute(
                f"SELECT attribute_id FROM {database}.{attribute_owners_table} WHERE item_id = {obj.id};"
            )
            attr_ids = [row[0] for row in cursor.fetchall()]

            # Delete from attribute_owners
            cursor.execute(
                f"DELETE FROM {database}.{attribute_owners_table} WHERE item_id = {obj.id};"
            )

            # Delete the attributes themselves
            if attr_ids:
                attr_ids_str = ','.join(str(aid) for aid in attr_ids)
                cursor.execute(
                    f"DELETE FROM {database}.{attributes_table} WHERE id IN ({attr_ids_str});"
                )

            # Insert new attributes
            if obj.attributes:
                for attr_type, attribute in obj.attributes.items():
                    # Build attribute value fields
                    bool_val = "NULL"
                    double_val = "NULL"
                    vec3_x = "NULL"
                    vec3_y = "NULL"
                    vec3_z = "NULL"
                    asset_val = "NULL"

                    if attribute.value is not None:
                        if isinstance(attribute.value, bool):
                            bool_val = str(attribute.value)
                        elif isinstance(attribute.value, (int, float)) and not isinstance(attribute.value, bool):
                            double_val = str(attribute.value)
                        elif isinstance(attribute.value, ItemVector3):
                            vec3_x = str(attribute.value.x)
                            vec3_y = str(attribute.value.y)
                            vec3_z = str(attribute.value.z)
                        elif isinstance(attribute.value, int):
                            asset_val = str(attribute.value)

                    from game.ttypes import AttributeType as AttrTypeEnum2
                    attr_type_name2 = AttrTypeEnum2._VALUES_TO_NAMES[attribute.attribute_type]

                    cursor.execute(
                        f"INSERT INTO {database}.{attributes_table} "
                        f"(internal_name, visible, attribute_type, bool_value, double_value, "
                        f"vector3_x, vector3_y, vector3_z, asset_id) "
                        f"VALUES ('{attribute.internal_name}', {attribute.visible}, "
                        f"'{attr_type_name2}', {bool_val}, {double_val}, "
                        f"{vec3_x}, {vec3_y}, {vec3_z}, {asset_val});"
                    )

                    last_attr_id = cursor.lastrowid

                    cursor.execute(
                        f"INSERT INTO {database}.{attribute_owners_table} "
                        f"(attribute_id, item_id) "
                        f"VALUES ({last_attr_id}, {obj.id});"
                    )

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated Item id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Item id={obj.id} in database={database}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def load_item(
        self,
        database: str,
        item_id: int,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[Item]]:
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            item_table = table if table else "items"
            attributes_table = "attributes"
            attribute_owners_table = "attribute_owners"

            # Load the item
            cursor.execute(
                f"SELECT * FROM {database}.{item_table} WHERE id = %s;",
                (item_id,),
            )
            item_row = cursor.fetchone()

            if not item_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Item id={item_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load blueprint if it exists
            blueprint = None
            if item_row['blueprint_id']:
                blueprint_result, blueprint = self.load_item_blueprint(
                    database,
                    item_row['blueprint_id'],
                )
                if not is_true(blueprint_result):
                    cursor.close()
                    return (blueprint_result, None)

            # Load attributes through attribute_owners
            cursor.execute(
                f"SELECT a.* FROM {database}.{attributes_table} a "
                f"INNER JOIN {database}.{attribute_owners_table} ao ON a.id = ao.attribute_id "
                f"WHERE ao.item_id = %s;",
                (item_id,),
            )
            attribute_rows = cursor.fetchall()

            # Build attributes map
            attributes = {}
            for row in attribute_rows:
                # Reconstruct AttributeValue union
                value = None
                if row['bool_value'] is not None:
                    value = row['bool_value']
                elif row['double_value'] is not None:
                    value = row['double_value']
                elif row['vector3_x'] is not None:
                    value = ItemVector3(
                        x=row['vector3_x'],
                        y=row['vector3_y'],
                        z=row['vector3_z'],
                    )
                elif row['asset_id'] is not None:
                    value = row['asset_id']

                # Reconstruct Owner union for this attribute
                cursor.execute(
                    f"SELECT * FROM {database}.{attribute_owners_table} WHERE attribute_id = %s;",
                    (row['id'],),
                )
                owner_row = cursor.fetchone()

                owner = None
                if owner_row:
                    if owner_row['mobile_id']:
                        owner = owner_row['mobile_id']
                    elif owner_row['item_id']:
                        owner = owner_row['item_id']
                    elif owner_row['asset_id']:
                        owner = owner_row['asset_id']
                    elif owner_row['player_id']:
                        owner = owner_row['player_id']

                # Import AttributeType enum
                from game.ttypes import AttributeType
                attr_type = AttributeType._NAMES_TO_VALUES[row['attribute_type']]

                attribute = Attribute(
                    id=row['id'],
                    internal_name=row['internal_name'],
                    visible=row['visible'],
                    value=value,
                    attribute_type=attr_type,
                    owner=owner,
                )
                attributes[attr_type] = attribute

            # Import ItemType enum
            from game.ttypes import ItemType
            item_type = ItemType._NAMES_TO_VALUES[item_row['item_type']]

            # Create Item object
            item = Item(
                id=item_row['id'],
                internal_name=item_row['internal_name'],
                attributes=attributes,
                max_stack_size=item_row['max_stack_size'],
                item_type=item_type,
                blueprint=blueprint,
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded Item id={item_id}",
                ),
                item,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Item id={item_id} from database={database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()


    def get_item_blueprint_sql(
        self,
        database: str,
        obj: ItemBlueprint,
        table: Optional[str] = None,
        drop: bool = False,
        truncate: bool = False,
    ) -> list[str]:
        # If both drop and truncate are True, set truncate to False
        if drop and truncate:
            truncate = False

        blueprint_table = table if table else "item_blueprints"
        components_table = "item_blueprint_components"

        statements = []

        if drop:
            statements.append(f"DROP TABLE IF EXISTS {database}.{components_table};")
            statements.append(f"DROP TABLE IF EXISTS {database}.{blueprint_table};")

        if truncate:
            statements.append(f"TRUNCATE TABLE {database}.{components_table};")
            statements.append(f"TRUNCATE TABLE {database}.{blueprint_table};")

        # Insert the blueprint
        if obj.id is None:
            statements.append(
                f"INSERT INTO {database}.{blueprint_table} (bake_time_ms) "
                f"VALUES ({obj.bake_time_ms});"
            )
        else:
            statements.append(
                f"INSERT INTO {database}.{blueprint_table} (id, bake_time_ms) "
                f"VALUES ({obj.id}, {obj.bake_time_ms});"
            )

        # Insert components (one-to-many relationship)
        if obj.components:
            for item_id, component in obj.components.items():
                statements.append(
                    f"INSERT INTO {database}.{components_table} "
                    f"(item_blueprint_id, component_item_id, ratio) "
                    f"VALUES ({{blueprint_id}}, {component.item_id}, {component.ratio});"
                )

        return statements

    def create_item_blueprint(
        self,
        database: str,
        obj: ItemBlueprint,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            # Get SQL statements
            statements = self.get_item_blueprint_sql(database, obj, table)

            # Execute each statement and track last_insert_id
            last_id = None
            blueprint_id_for_components = None
            for stmt in statements:
                # Replace placeholder with actual blueprint_id
                if '{blueprint_id}' in stmt:
                    blueprint_id = obj.id if obj.id is not None else blueprint_id_for_components
                    if blueprint_id is None:
                        raise Exception("Attempted to use blueprint_id but no blueprint insert occurred")
                    stmt = stmt.replace('{blueprint_id}', str(blueprint_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith('INSERT'):
                    last_id = cursor.lastrowid
                    # If this was the blueprint insert and obj.id was None, store it for components
                    if blueprint_id_for_components is None and obj.id is None and 'item_blueprints' in stmt:
                        blueprint_id_for_components = last_id

            # Set the id on the object if it was None
            if obj.id is None and blueprint_id_for_components is not None:
                obj.id = blueprint_id_for_components

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created ItemBlueprint id={obj.id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to save ItemBlueprint id={obj.id} to database={database}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def update_item_blueprint(
        self,
        database: str,
        obj: ItemBlueprint,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update ItemBlueprint with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            blueprint_table = table if table else "item_blueprints"
            components_table = "item_blueprint_components"

            # Update blueprint
            cursor.execute(
                f"UPDATE {database}.{blueprint_table} SET "
                f"bake_time_ms = {obj.bake_time_ms} "
                f"WHERE id = {obj.id};"
            )

            # Delete existing components
            cursor.execute(
                f"DELETE FROM {database}.{components_table} WHERE item_blueprint_id = {obj.id};"
            )

            # Insert new components
            if obj.components:
                for item_id, component in obj.components.items():
                    cursor.execute(
                        f"INSERT INTO {database}.{components_table} "
                        f"(item_blueprint_id, component_item_id, ratio) "
                        f"VALUES ({obj.id}, {component.item_id}, {component.ratio});"
                    )

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated ItemBlueprint id={obj.id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update ItemBlueprint id={obj.id} in database={database}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def load_item_blueprint(
        self,
        database: str,
        blueprint_id: int,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[ItemBlueprint]]:
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            blueprint_table = table if table else "item_blueprints"
            components_table = "item_blueprint_components"

            # Load the blueprint
            cursor.execute(
                f"SELECT * FROM {database}.{blueprint_table} WHERE id = %s;",
                (blueprint_id,),
            )
            blueprint_row = cursor.fetchone()

            if not blueprint_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"ItemBlueprint id={blueprint_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load components
            cursor.execute(
                f"SELECT * FROM {database}.{components_table} WHERE item_blueprint_id = %s;",
                (blueprint_id,),
            )
            component_rows = cursor.fetchall()

            # Build components map
            components = {}
            for row in component_rows:
                component = ItemBlueprintComponent(
                    ratio=row['ratio'],
                    item_id=row['component_item_id'],
                )
                components[row['component_item_id']] = component

            # Create ItemBlueprint object
            blueprint = ItemBlueprint(
                id=blueprint_row['id'],
                components=components,
                bake_time_ms=blueprint_row['bake_time_ms'],
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded ItemBlueprint id={blueprint_id}",
                ),
                blueprint,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load ItemBlueprint id={blueprint_id} from database={database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()


    def get_inventory_sql(
        self,
        database: str,
        obj: Inventory,
        table: Optional[str] = None,
        drop: bool = False,
        truncate: bool = False,
    ) -> list[str]:
        # If both drop and truncate are True, set truncate to False
        if drop and truncate:
            truncate = False

        inventory_table = table if table else "inventories"
        inventory_entries_table = "inventory_entries"
        inventory_owners_table = "inventory_owners"

        statements = []

        if drop:
            statements.append(f"DROP TABLE IF EXISTS {database}.{inventory_entries_table};")
            statements.append(f"DROP TABLE IF EXISTS {database}.{inventory_owners_table};")
            statements.append(f"DROP TABLE IF EXISTS {database}.{inventory_table};")

        if truncate:
            statements.append(f"TRUNCATE TABLE {database}.{inventory_entries_table};")
            statements.append(f"TRUNCATE TABLE {database}.{inventory_owners_table};")
            statements.append(f"TRUNCATE TABLE {database}.{inventory_table};")

        # Extract owner information
        from game.ttypes import Owner
        mobile_id = "NULL"
        item_id = "NULL"
        asset_id = "NULL"
        player_id = "NULL"
        owner_type = "NULL"
        owner_id = "NULL"

        if obj.owner is not None:
            # Thrift unions store the value directly as the union's value
            if isinstance(obj.owner, Owner):
                # It's an Owner object, check which field is set
                if hasattr(obj.owner, 'mobile_id') and obj.owner.mobile_id is not None:
                    mobile_id = str(obj.owner.mobile_id)
                    owner_id = mobile_id
                    owner_type = "'MOBILE'"
                elif hasattr(obj.owner, 'item_it') and obj.owner.item_it is not None:
                    item_id = str(obj.owner.item_it)
                    owner_id = item_id
                    owner_type = "'ITEM'"
                elif hasattr(obj.owner, 'asset_id') and obj.owner.asset_id is not None:
                    asset_id = str(obj.owner.asset_id)
                    owner_id = asset_id
                    owner_type = "'ASSET'"
                elif hasattr(obj.owner, 'player_id') and obj.owner.player_id is not None:
                    player_id = str(obj.owner.player_id)
                    owner_id = player_id
                    owner_type = "'PLAYER'"
            elif isinstance(obj.owner, int):
                # It's a plain int, assume it's a mobile_id for backwards compatibility
                mobile_id = str(obj.owner)
                owner_id = mobile_id
                owner_type = "'MOBILE'"

        # Insert inventory
        if obj.id is None:
            statements.append(
                f"INSERT INTO {database}.{inventory_table} "
                f"(owner_id, owner_type, max_entries, max_volume, last_calculated_volume) "
                f"VALUES ({owner_id}, {owner_type}, {obj.max_entries}, "
                f"{obj.max_volume}, {obj.last_calculated_volume});"
            )
        else:
            statements.append(
                f"INSERT INTO {database}.{inventory_table} "
                f"(id, owner_id, owner_type, max_entries, max_volume, last_calculated_volume) "
                f"VALUES ({obj.id}, {owner_id}, {owner_type}, {obj.max_entries}, "
                f"{obj.max_volume}, {obj.last_calculated_volume});"
            )

        # Insert inventory entries (one-to-many)
        if obj.entries:
            for entry in obj.entries:
                is_max_stacked = 1 if entry.is_max_stacked else 0
                statements.append(
                    f"INSERT INTO {database}.{inventory_entries_table} "
                    f"(inventory_id, item_id, quantity, is_max_stacked) "
                    f"VALUES ({{inventory_id}}, {entry.item_id}, {entry.quantity}, {is_max_stacked});"
                )

        # Insert inventory owner (one-to-one)
        statements.append(
            f"INSERT INTO {database}.{inventory_owners_table} "
            f"(inventory_id, mobile_id, item_id, asset_id, player_id) "
            f"VALUES ({{inventory_id}}, {mobile_id}, {item_id}, {asset_id}, {player_id});"
        )

        return statements

    def create_inventory(
        self,
        database: str,
        obj: Inventory,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            # Get SQL statements
            statements = self.get_inventory_sql(database, obj, table)

            # Execute each statement and track last_insert_id
            last_id = None
            inventory_id_set = False
            for stmt in statements:
                # Replace placeholder with actual inventory_id
                if '{inventory_id}' in stmt:
                    current_inventory_id = obj.id if obj.id is not None else last_id
                    if current_inventory_id is None:
                        raise Exception("Attempted to use inventory_id but no inventory insert occurred")
                    stmt = stmt.replace('{inventory_id}', str(current_inventory_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith('INSERT'):
                    last_id = cursor.lastrowid
                    # If this was the inventory insert and obj.id was None, set it now
                    if not inventory_id_set and obj.id is None and 'inventories' in stmt:
                        obj.id = last_id
                        inventory_id_set = True

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created Inventory id={obj.id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to save Inventory id={obj.id} to database={database}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def update_inventory(
        self,
        database: str,
        obj: Inventory,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Inventory with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            inventory_table = table if table else "inventories"
            inventory_entries_table = "inventory_entries"
            inventory_owners_table = "inventory_owners"

            # Extract owner information
            from game.ttypes import Owner
            mobile_id = "NULL"
            item_id = "NULL"
            asset_id = "NULL"
            player_id = "NULL"
            owner_type = "NULL"
            owner_id = "NULL"

            if obj.owner is not None:
                if isinstance(obj.owner, Owner):
                    if hasattr(obj.owner, 'mobile_id') and obj.owner.mobile_id is not None:
                        mobile_id = str(obj.owner.mobile_id)
                        owner_id = mobile_id
                        owner_type = "'MOBILE'"
                    elif hasattr(obj.owner, 'item_it') and obj.owner.item_it is not None:
                        item_id = str(obj.owner.item_it)
                        owner_id = item_id
                        owner_type = "'ITEM'"
                    elif hasattr(obj.owner, 'asset_id') and obj.owner.asset_id is not None:
                        asset_id = str(obj.owner.asset_id)
                        owner_id = asset_id
                        owner_type = "'ASSET'"
                    elif hasattr(obj.owner, 'player_id') and obj.owner.player_id is not None:
                        player_id = str(obj.owner.player_id)
                        owner_id = player_id
                        owner_type = "'PLAYER'"
                elif isinstance(obj.owner, int):
                    mobile_id = str(obj.owner)
                    owner_id = mobile_id
                    owner_type = "'MOBILE'"

            # Update inventory
            cursor.execute(
                f"UPDATE {database}.{inventory_table} SET "
                f"owner_id = {owner_id}, "
                f"owner_type = {owner_type}, "
                f"max_entries = {obj.max_entries}, "
                f"max_volume = {obj.max_volume}, "
                f"last_calculated_volume = {obj.last_calculated_volume} "
                f"WHERE id = {obj.id};"
            )

            # Delete existing entries
            cursor.execute(
                f"DELETE FROM {database}.{inventory_entries_table} WHERE inventory_id = {obj.id};"
            )

            # Insert new entries
            if obj.entries:
                for entry in obj.entries:
                    is_max_stacked = 1 if entry.is_max_stacked else 0
                    cursor.execute(
                        f"INSERT INTO {database}.{inventory_entries_table} "
                        f"(inventory_id, item_id, quantity, is_max_stacked) "
                        f"VALUES ({obj.id}, {entry.item_id}, {entry.quantity}, {is_max_stacked});"
                    )

            # Update owner (delete and re-insert)
            cursor.execute(
                f"DELETE FROM {database}.{inventory_owners_table} WHERE inventory_id = {obj.id};"
            )

            cursor.execute(
                f"INSERT INTO {database}.{inventory_owners_table} "
                f"(inventory_id, mobile_id, item_id, asset_id, player_id) "
                f"VALUES ({obj.id}, {mobile_id}, {item_id}, {asset_id}, {player_id});"
            )

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated Inventory id={obj.id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Inventory id={obj.id} in database={database}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def load_inventory(
        self,
        database: str,
        inventory_id: int,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[Inventory]]:
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            inventory_table = table if table else "inventories"
            inventory_entries_table = "inventory_entries"
            inventory_owners_table = "inventory_owners"

            # Load the inventory
            cursor.execute(
                f"SELECT * FROM {database}.{inventory_table} WHERE id = %s;",
                (inventory_id,),
            )
            inv_row = cursor.fetchone()

            if not inv_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Inventory id={inventory_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load inventory entries
            cursor.execute(
                f"SELECT * FROM {database}.{inventory_entries_table} WHERE inventory_id = %s;",
                (inventory_id,),
            )
            entry_rows = cursor.fetchall()

            # Build entries list
            entries = []
            for row in entry_rows:
                entry = InventoryEntry(
                    item_id=row['item_id'],
                    quantity=row['quantity'],
                    is_max_stacked=row['is_max_stacked'],
                )
                entries.append(entry)

            # Load owner
            cursor.execute(
                f"SELECT * FROM {database}.{inventory_owners_table} WHERE inventory_id = %s;",
                (inventory_id,),
            )
            owner_row = cursor.fetchone()

            owner = None
            if owner_row:
                if owner_row['mobile_id']:
                    owner = owner_row['mobile_id']
                elif owner_row['item_id']:
                    owner = owner_row['item_id']
                elif owner_row['asset_id']:
                    owner = owner_row['asset_id']
                elif owner_row['player_id']:
                    owner = owner_row['player_id']

            # Create Inventory object
            inventory = Inventory(
                id=inv_row['id'],
                max_entries=inv_row['max_entries'],
                max_volume=inv_row['max_volume'],
                entries=entries,
                last_calculated_volume=inv_row['last_calculated_volume'],
                owner=owner,
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded Inventory id={inventory_id}",
                ),
                inventory,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Inventory id={inventory_id} from database={database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def get_mobile_sql(
        self,
        database: str,
        obj: Mobile,
        table: Optional[str] = None,
        drop: bool = False,
        truncate: bool = False,
    ) -> list[str]:
        # If both drop and truncate are True, set truncate to False
        if drop and truncate:
            truncate = False

        mobile_table = table if table else "mobiles"
        attributes_table = "attributes"
        attribute_owners_table = "attribute_owners"

        statements = []

        if drop:
            statements.append(f"DROP TABLE IF EXISTS {database}.{attribute_owners_table};")
            statements.append(f"DROP TABLE IF EXISTS {database}.{attributes_table};")
            statements.append(f"DROP TABLE IF EXISTS {database}.{mobile_table};")

        if truncate:
            statements.append(f"TRUNCATE TABLE {database}.{attribute_owners_table};")
            statements.append(f"TRUNCATE TABLE {database}.{attributes_table};")
            statements.append(f"TRUNCATE TABLE {database}.{mobile_table};")

        # Insert the mobile
        from game.ttypes import MobileType as MobileTypeEnum, Owner
        mobile_type_name = MobileTypeEnum._VALUES_TO_NAMES[obj.mobile_type]

        # Extract owner information
        owner_mobile_id = "NULL"
        owner_item_id = "NULL"
        owner_asset_id = "NULL"
        owner_player_id = "NULL"

        if hasattr(obj, 'owner') and obj.owner is not None:
            if isinstance(obj.owner, Owner):
                if hasattr(obj.owner, 'mobile_id') and obj.owner.mobile_id is not None:
                    owner_mobile_id = str(obj.owner.mobile_id)
                elif hasattr(obj.owner, 'item_it') and obj.owner.item_it is not None:
                    owner_item_id = str(obj.owner.item_it)
                elif hasattr(obj.owner, 'asset_id') and obj.owner.asset_id is not None:
                    owner_asset_id = str(obj.owner.asset_id)
                elif hasattr(obj.owner, 'player_id') and obj.owner.player_id is not None:
                    owner_player_id = str(obj.owner.player_id)
            elif isinstance(obj.owner, int):
                owner_mobile_id = str(obj.owner)

        if obj.id is None:
            statements.append(
                f"INSERT INTO {database}.{mobile_table} "
                f"(mobile_type, owner_mobile_id, owner_item_id, owner_asset_id, owner_player_id) "
                f"VALUES ('{mobile_type_name}', {owner_mobile_id}, {owner_item_id}, {owner_asset_id}, {owner_player_id});"
            )
        else:
            statements.append(
                f"INSERT INTO {database}.{mobile_table} "
                f"(id, mobile_type, owner_mobile_id, owner_item_id, owner_asset_id, owner_player_id) "
                f"VALUES ({obj.id}, '{mobile_type_name}', {owner_mobile_id}, {owner_item_id}, {owner_asset_id}, {owner_player_id});"
            )

        # Insert attributes (one-to-many relationship via attribute_owners)
        if obj.attributes:
            for attr_type, attribute in obj.attributes.items():
                # Build attribute value fields
                bool_val = "NULL"
                double_val = "NULL"
                vec3_x = "NULL"
                vec3_y = "NULL"
                vec3_z = "NULL"
                asset_val = "NULL"

                if attribute.value is not None:
                    if isinstance(attribute.value, bool):
                        bool_val = str(attribute.value)
                    elif isinstance(attribute.value, (int, float)) and not isinstance(attribute.value, bool):
                        double_val = str(attribute.value)
                    elif isinstance(attribute.value, ItemVector3):
                        vec3_x = str(attribute.value.x)
                        vec3_y = str(attribute.value.y)
                        vec3_z = str(attribute.value.z)
                    elif isinstance(attribute.value, int):
                        asset_val = str(attribute.value)

                # Insert attribute
                from game.ttypes import AttributeType as AttrTypeEnum2
                attr_type_name2 = AttrTypeEnum2._VALUES_TO_NAMES[attribute.attribute_type]

                statements.append(
                    f"INSERT INTO {database}.{attributes_table} "
                    f"(internal_name, visible, attribute_type, bool_value, double_value, "
                    f"vector3_x, vector3_y, vector3_z, asset_id) "
                    f"VALUES ('{attribute.internal_name}', {attribute.visible}, "
                    f"'{attr_type_name2}', {bool_val}, {double_val}, "
                    f"{vec3_x}, {vec3_y}, {vec3_z}, {asset_val});"
                )

                # Insert attribute owner relationship (use placeholder for attribute id and mobile id)
                statements.append(
                    f"INSERT INTO {database}.{attribute_owners_table} "
                    f"(attribute_id, mobile_id) "
                    f"VALUES ({{last_insert_id}}, {{mobile_id}});"
                )

        return statements

    def create_mobile(
        self,
        database: str,
        obj: Mobile,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            # Get SQL statements
            statements = self.get_mobile_sql(database, obj, table)

            # Execute each statement and track last_insert_id
            last_id = None
            mobile_id_set = False
            for stmt in statements:
                # Replace placeholder with actual last_insert_id
                if '{last_insert_id}' in stmt:
                    if last_id is None:
                        raise Exception("Attempted to use last_insert_id but no previous insert occurred")
                    stmt = stmt.replace('{last_insert_id}', str(last_id))

                # Replace placeholder with actual mobile_id
                if '{mobile_id}' in stmt:
                    current_mobile_id = obj.id if obj.id is not None else last_id
                    if current_mobile_id is None:
                        raise Exception("Attempted to use mobile_id but no mobile insert occurred")
                    stmt = stmt.replace('{mobile_id}', str(current_mobile_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith('INSERT'):
                    last_id = cursor.lastrowid
                    # If this was the mobile insert and obj.id was None, set it now
                    if not mobile_id_set and obj.id is None and 'mobiles' in stmt:
                        obj.id = last_id
                        mobile_id_set = True

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created Mobile id={obj.id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to save Mobile id={obj.id} to database={database}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def update_mobile(
        self,
        database: str,
        obj: Mobile,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Mobile with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            mobile_table = table if table else "mobiles"
            attributes_table = "attributes"
            attribute_owners_table = "attribute_owners"

            from game.ttypes import MobileType as MobileTypeEnum, Owner
            mobile_type_name = MobileTypeEnum._VALUES_TO_NAMES[obj.mobile_type]

            # Extract owner information
            owner_mobile_id = "NULL"
            owner_item_id = "NULL"
            owner_asset_id = "NULL"
            owner_player_id = "NULL"

            if hasattr(obj, 'owner') and obj.owner is not None:
                if isinstance(obj.owner, Owner):
                    if hasattr(obj.owner, 'mobile_id') and obj.owner.mobile_id is not None:
                        owner_mobile_id = str(obj.owner.mobile_id)
                    elif hasattr(obj.owner, 'item_it') and obj.owner.item_it is not None:
                        owner_item_id = str(obj.owner.item_it)
                    elif hasattr(obj.owner, 'asset_id') and obj.owner.asset_id is not None:
                        owner_asset_id = str(obj.owner.asset_id)
                    elif hasattr(obj.owner, 'player_id') and obj.owner.player_id is not None:
                        owner_player_id = str(obj.owner.player_id)
                elif isinstance(obj.owner, int):
                    owner_mobile_id = str(obj.owner)

            # Update mobile
            cursor.execute(
                f"UPDATE {database}.{mobile_table} SET "
                f"mobile_type = '{mobile_type_name}', "
                f"owner_mobile_id = {owner_mobile_id}, "
                f"owner_item_id = {owner_item_id}, "
                f"owner_asset_id = {owner_asset_id}, "
                f"owner_player_id = {owner_player_id} "
                f"WHERE id = {obj.id};"
            )

            # Delete existing attributes
            # First get the attribute IDs
            cursor.execute(
                f"SELECT attribute_id FROM {database}.{attribute_owners_table} WHERE mobile_id = {obj.id};"
            )
            attr_ids = [row[0] for row in cursor.fetchall()]

            # Delete from attribute_owners
            cursor.execute(
                f"DELETE FROM {database}.{attribute_owners_table} WHERE mobile_id = {obj.id};"
            )

            # Delete the attributes themselves
            if attr_ids:
                attr_ids_str = ','.join(str(aid) for aid in attr_ids)
                cursor.execute(
                    f"DELETE FROM {database}.{attributes_table} WHERE id IN ({attr_ids_str});"
                )

            # Insert new attributes
            if obj.attributes:
                for attr_type, attribute in obj.attributes.items():
                    # Build attribute value fields
                    bool_val = "NULL"
                    double_val = "NULL"
                    vec3_x = "NULL"
                    vec3_y = "NULL"
                    vec3_z = "NULL"
                    asset_val = "NULL"

                    if attribute.value is not None:
                        if isinstance(attribute.value, bool):
                            bool_val = str(attribute.value)
                        elif isinstance(attribute.value, (int, float)) and not isinstance(attribute.value, bool):
                            double_val = str(attribute.value)
                        elif isinstance(attribute.value, ItemVector3):
                            vec3_x = str(attribute.value.x)
                            vec3_y = str(attribute.value.y)
                            vec3_z = str(attribute.value.z)
                        elif isinstance(attribute.value, int):
                            asset_val = str(attribute.value)

                    from game.ttypes import AttributeType as AttrTypeEnum2
                    attr_type_name2 = AttrTypeEnum2._VALUES_TO_NAMES[attribute.attribute_type]

                    cursor.execute(
                        f"INSERT INTO {database}.{attributes_table} "
                        f"(internal_name, visible, attribute_type, bool_value, double_value, "
                        f"vector3_x, vector3_y, vector3_z, asset_id) "
                        f"VALUES ('{attribute.internal_name}', {attribute.visible}, "
                        f"'{attr_type_name2}', {bool_val}, {double_val}, "
                        f"{vec3_x}, {vec3_y}, {vec3_z}, {asset_val});"
                    )

                    last_attr_id = cursor.lastrowid

                    cursor.execute(
                        f"INSERT INTO {database}.{attribute_owners_table} "
                        f"(attribute_id, mobile_id) "
                        f"VALUES ({last_attr_id}, {obj.id});"
                    )

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated Mobile id={obj.id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Mobile id={obj.id} in database={database}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def load_mobile(
        self,
        database: str,
        mobile_id: int,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[Mobile]]:
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            mobile_table = table if table else "mobiles"
            attributes_table = "attributes"
            attribute_owners_table = "attribute_owners"

            # Load the mobile
            cursor.execute(
                f"SELECT * FROM {database}.{mobile_table} WHERE id = %s;",
                (mobile_id,),
            )
            mobile_row = cursor.fetchone()

            if not mobile_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Mobile id={mobile_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load attributes through attribute_owners
            cursor.execute(
                f"SELECT a.* FROM {database}.{attributes_table} a "
                f"INNER JOIN {database}.{attribute_owners_table} ao ON a.id = ao.attribute_id "
                f"WHERE ao.mobile_id = %s;",
                (mobile_id,),
            )
            attribute_rows = cursor.fetchall()

            # Build attributes map
            attributes = {}
            for row in attribute_rows:
                # Reconstruct AttributeValue union
                value = None
                if row['bool_value'] is not None:
                    value = row['bool_value']
                elif row['double_value'] is not None:
                    value = row['double_value']
                elif row['vector3_x'] is not None:
                    value = ItemVector3(
                        x=row['vector3_x'],
                        y=row['vector3_y'],
                        z=row['vector3_z'],
                    )
                elif row['asset_id'] is not None:
                    value = row['asset_id']

                # Reconstruct Owner union for this attribute
                cursor.execute(
                    f"SELECT * FROM {database}.{attribute_owners_table} WHERE attribute_id = %s;",
                    (row['id'],),
                )
                owner_row = cursor.fetchone()

                owner = None
                if owner_row:
                    if owner_row['mobile_id']:
                        owner = owner_row['mobile_id']
                    elif owner_row['item_id']:
                        owner = owner_row['item_id']
                    elif owner_row['asset_id']:
                        owner = owner_row['asset_id']

                # Import AttributeType enum
                from game.ttypes import AttributeType
                attr_type = AttributeType._NAMES_TO_VALUES[row['attribute_type']]

                attribute = Attribute(
                    id=row['id'],
                    internal_name=row['internal_name'],
                    visible=row['visible'],
                    value=value,
                    attribute_type=attr_type,
                    owner=owner,
                )
                attributes[attr_type] = attribute

            # Import MobileType enum
            from game.ttypes import MobileType, Owner
            mobile_type = MobileType._NAMES_TO_VALUES[mobile_row['mobile_type']]

            # Reconstruct owner
            owner = None
            if mobile_row['owner_mobile_id']:
                owner = Owner()
                owner.mobile_id = mobile_row['owner_mobile_id']
            elif mobile_row['owner_item_id']:
                owner = Owner()
                owner.item_it = mobile_row['owner_item_id']
            elif mobile_row['owner_asset_id']:
                owner = Owner()
                owner.asset_id = mobile_row['owner_asset_id']
            elif mobile_row['owner_player_id']:
                owner = Owner()
                owner.player_id = mobile_row['owner_player_id']

            # Create Mobile object
            mobile = Mobile(
                id=mobile_row['id'],
                mobile_type=mobile_type,
                attributes=attributes,
                owner=owner,
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded Mobile id={mobile_id}",
                ),
                mobile,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Mobile id={mobile_id} from database={database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def create_player(
        self,
        database: str,
        obj: Player,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            with self.transaction() as cursor:
                players_table = table if table else TABLE_PLAYERS

                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {database}.{players_table} "
                        f"(full_name, what_we_call_you, security_token, over_13, year_of_birth) "
                        f"VALUES (%s, %s, %s, %s, %s)",
                        (
                            obj.full_name,
                            obj.what_we_call_you,
                            obj.security_token,
                            obj.over_13,
                            obj.year_of_birth,
                        ),
                    )
                    obj.id = cursor.lastrowid
                else:
                    cursor.execute(
                        f"INSERT INTO {database}.{players_table} "
                        f"(id, full_name, what_we_call_you, security_token, over_13, year_of_birth) "
                        f"VALUES (%s, %s, %s, %s, %s, %s)",
                        (
                            obj.id,
                            obj.full_name,
                            obj.what_we_call_you,
                            obj.security_token,
                            obj.over_13,
                            obj.year_of_birth,
                        ),
                    )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_CREATED.format(type="Player", id=obj.id),
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_CREATE_FAILED.format(type="Player", database=database, error=str(e)),
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def update_player(
        self,
        database: str,
        obj: Player,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Player with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            with self.transaction() as cursor:
                players_table = table if table else TABLE_PLAYERS

                cursor.execute(
                    f"UPDATE {database}.{players_table} SET "
                    f"full_name = %s, "
                    f"what_we_call_you = %s, "
                    f"security_token = %s, "
                    f"over_13 = %s, "
                    f"year_of_birth = %s "
                    f"WHERE id = %s",
                    (
                        obj.full_name,
                        obj.what_we_call_you,
                        obj.security_token,
                        obj.over_13,
                        obj.year_of_birth,
                        obj.id,
                    ),
                )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_UPDATED.format(type="Player", id=obj.id),
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_UPDATE_FAILED.format(type="Player", id=obj.id, database=database, error=str(e)),
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def load_player(
        self,
        database: str,
        player_id: int,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[Player]]:
        try:
            with self.transaction_dict() as cursor:
                players_table = table if table else TABLE_PLAYERS

                cursor.execute(
                    f"SELECT * FROM {database}.{players_table} WHERE id = %s;",
                    (player_id,),
                )
                player_row = cursor.fetchone()

                if not player_row:
                    return (
                        GameResult(
                            status=StatusType.FAILURE,
                            message=MSG_NOT_FOUND.format(type="Player", id=player_id, database=database),
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                        None,
                    )

                player = Player(
                    id=player_row['id'],
                    full_name=player_row['full_name'],
                    what_we_call_you=player_row['what_we_call_you'],
                    security_token=player_row['security_token'],
                    over_13=player_row['over_13'],
                    year_of_birth=player_row['year_of_birth'],
                )

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_LOADED.format(type="Player", id=player_id),
                ),
                player,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_LOAD_FAILED.format(type="Player", id=player_id, database=database, error=str(e)),
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )

    def destroy_player(
        self,
        database: str,
        player_id: int,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            with self.transaction() as cursor:
                players_table = table if table else TABLE_PLAYERS

                cursor.execute(
                    f"DELETE FROM {database}.{players_table} WHERE id = %s;",
                    (player_id,),
                )

                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=MSG_NOT_FOUND.format(type="Player", id=player_id, database=database),
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_DESTROYED.format(type="Player", id=player_id),
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_DESTROY_FAILED.format(type="Player", id=player_id, database=database, error=str(e)),
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    # Save functions that delegate to create or update based on id
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

    def save_item_blueprint(
        self,
        database: str,
        obj: ItemBlueprint,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        if obj.id is None:
            return self.create_item_blueprint(database, obj, table)
        else:
            return self.update_item_blueprint(database, obj, table)

    def save_item(
        self,
        database: str,
        obj: Item,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        if obj.id is None:
            return self.create_item(database, obj, table)
        else:
            return self.update_item(database, obj, table)

    def save_inventory(
        self,
        database: str,
        obj: Inventory,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        if obj.id is None:
            return self.create_inventory(database, obj, table)
        else:
            return self.update_inventory(database, obj, table)

    def save_mobile(
        self,
        database: str,
        obj: Mobile,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        if obj.id is None:
            return self.create_mobile(database, obj, table)
        else:
            return self.update_mobile(database, obj, table)

    def save_player(
        self,
        database: str,
        obj: Player,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        if obj.id is None:
            return self.create_player(database, obj, table)
        else:
            return self.update_player(database, obj, table)

    # Destroy functions to delete records from database
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

    def destroy_item_blueprint(
        self,
        database: str,
        blueprint_id: int,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            blueprint_table = table if table else "item_blueprints"
            components_table = "item_blueprint_components"

            # Delete components first (foreign key)
            cursor.execute(
                f"DELETE FROM {database}.{components_table} WHERE item_blueprint_id = {blueprint_id};"
            )

            # Delete the blueprint
            cursor.execute(
                f"DELETE FROM {database}.{blueprint_table} WHERE id = {blueprint_id};"
            )

            # Check if any rows were affected
            if cursor.rowcount == 0:
                self.connection.rollback()
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"ItemBlueprint id={blueprint_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                ]

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed ItemBlueprint id={blueprint_id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy ItemBlueprint id={blueprint_id} in database={database}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def destroy_item(
        self,
        database: str,
        item_id: int,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            item_table = table if table else "items"
            attributes_table = "attributes"
            attribute_owners_table = "attribute_owners"

            # Get attribute IDs first
            cursor.execute(
                f"SELECT attribute_id FROM {database}.{attribute_owners_table} WHERE item_id = {item_id};"
            )
            attr_ids = [row[0] for row in cursor.fetchall()]

            # Delete attribute owners
            cursor.execute(
                f"DELETE FROM {database}.{attribute_owners_table} WHERE item_id = {item_id};"
            )

            # Delete attributes
            if attr_ids:
                attr_ids_str = ','.join(str(aid) for aid in attr_ids)
                cursor.execute(
                    f"DELETE FROM {database}.{attributes_table} WHERE id IN ({attr_ids_str});"
                )

            # Delete the item
            cursor.execute(
                f"DELETE FROM {database}.{item_table} WHERE id = {item_id};"
            )

            # Check if any rows were affected
            if cursor.rowcount == 0:
                self.connection.rollback()
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Item id={item_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                ]

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Item id={item_id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Item id={item_id} in database={database}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def destroy_inventory(
        self,
        database: str,
        inventory_id: int,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            inventory_table = table if table else "inventories"
            inventory_entries_table = "inventory_entries"
            inventory_owners_table = "inventory_owners"

            # Delete inventory entries first (foreign key)
            cursor.execute(
                f"DELETE FROM {database}.{inventory_entries_table} WHERE inventory_id = {inventory_id};"
            )

            # Delete inventory owner
            cursor.execute(
                f"DELETE FROM {database}.{inventory_owners_table} WHERE inventory_id = {inventory_id};"
            )

            # Delete the inventory
            cursor.execute(
                f"DELETE FROM {database}.{inventory_table} WHERE id = {inventory_id};"
            )

            # Check if any rows were affected
            if cursor.rowcount == 0:
                self.connection.rollback()
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Inventory id={inventory_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                ]

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Inventory id={inventory_id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Inventory id={inventory_id} in database={database}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    def destroy_mobile(
        self,
        database: str,
        mobile_id: int,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            mobile_table = table if table else "mobiles"
            attributes_table = "attributes"
            attribute_owners_table = "attribute_owners"

            # Get attribute IDs first
            cursor.execute(
                f"SELECT attribute_id FROM {database}.{attribute_owners_table} WHERE mobile_id = {mobile_id};"
            )
            attr_ids = [row[0] for row in cursor.fetchall()]

            # Delete attribute owners
            cursor.execute(
                f"DELETE FROM {database}.{attribute_owners_table} WHERE mobile_id = {mobile_id};"
            )

            # Delete attributes
            if attr_ids:
                attr_ids_str = ','.join(str(aid) for aid in attr_ids)
                cursor.execute(
                    f"DELETE FROM {database}.{attributes_table} WHERE id IN ({attr_ids_str});"
                )

            # Delete the mobile
            cursor.execute(
                f"DELETE FROM {database}.{mobile_table} WHERE id = {mobile_id};"
            )

            # Check if any rows were affected
            if cursor.rowcount == 0:
                self.connection.rollback()
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Mobile id={mobile_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                ]

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Mobile id={mobile_id}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Mobile id={mobile_id} in database={database}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]
        finally:
            if cursor:
                cursor.close()

    # ========================================================================
    # Unified Dispatcher Functions
    # ========================================================================

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

        dispatch_map = {
            'Attribute': self.save_attribute,
            'Item': self.save_item,
            'ItemBlueprint': self.save_item_blueprint,
            'Inventory': self.save_inventory,
            'Mobile': self.save_mobile,
            'Player': self.save_player,
        }

        if type_name not in dispatch_map:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Unknown type for save: {type_name}",
                    error_code=GameError.DB_INVALID_DATA,
                ),
            ]

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

        dispatch_map = {
            'Attribute': self.create_attribute,
            'Item': self.create_item,
            'ItemBlueprint': self.create_item_blueprint,
            'Inventory': self.create_inventory,
            'Mobile': self.create_mobile,
            'Player': self.create_player,
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

        dispatch_map = {
            'Attribute': self.update_attribute,
            'Item': self.update_item,
            'ItemBlueprint': self.update_item_blueprint,
            'Inventory': self.update_inventory,
            'Mobile': self.update_mobile,
            'Player': self.update_player,
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
        if hasattr(obj_or_id, '__class__') and hasattr(obj_or_id, 'id'):
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
            'Attribute': self.destroy_attribute,
            'Item': self.destroy_item,
            'ItemBlueprint': self.destroy_item_blueprint,
            'Inventory': self.destroy_inventory,
            'Mobile': self.destroy_mobile,
            'Player': self.destroy_player,
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
            'Attribute': self.load_attribute,
            'Item': self.load_item,
            'ItemBlueprint': self.load_item_blueprint,
            'Inventory': self.load_inventory,
            'Mobile': self.load_mobile,
            'Player': self.load_player,
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

