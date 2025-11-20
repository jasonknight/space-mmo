import mysql.connector
from typing import Optional, Tuple
import sys
sys.path.append('gen-py')

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
)
from common import is_ok, is_true


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
                id BIGINT PRIMARY KEY,
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
                id BIGINT PRIMARY KEY,
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
                id BIGINT PRIMARY KEY,
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
                id BIGINT PRIMARY KEY,
                mobile_type VARCHAR(50) NOT NULL
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

        if obj.owner:
            if hasattr(obj.owner, 'mobile_id') and obj.owner.mobile_id is not None:
                mobile_id = str(obj.owner.mobile_id)
            elif hasattr(obj.owner, 'item_it') and obj.owner.item_it is not None:
                item_id = str(obj.owner.item_it)
            elif hasattr(obj.owner, 'asset_id') and obj.owner.asset_id is not None:
                asset_id = str(obj.owner.asset_id)

        statements.append(
            f"INSERT INTO {database}.{attribute_owners_table} "
            f"(attribute_id, mobile_id, item_id, asset_id) "
            f"VALUES ({{last_insert_id}}, {mobile_id}, {item_id}, {asset_id});"
        )

        return statements

    def save_attribute(
        self,
        database: str,
        obj: Attribute,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            self.connect()
            cursor = self.connection.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION;")

            # Get SQL statements
            statements = self.get_attribute_sql(database, obj, table)

            # Execute each statement and track last_insert_id
            last_id = None
            for stmt in statements:
                # Replace placeholder with actual last_insert_id
                if '{last_insert_id}' in stmt:
                    if last_id is None:
                        raise Exception("Attempted to use last_insert_id but no previous insert occurred")
                    stmt = stmt.replace('{last_insert_id}', str(last_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith('INSERT'):
                    last_id = cursor.lastrowid

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully saved Attribute internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to save Attribute internal_name={obj.internal_name} to database={database}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
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

                # Insert attribute owner relationship (use placeholder for attribute id)
                statements.append(
                    f"INSERT INTO {database}.{attribute_owners_table} "
                    f"(attribute_id, item_id) "
                    f"VALUES ({{last_insert_id}}, {obj.id});"
                )

        return statements

    def save_item(
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
            for stmt in statements:
                # Replace placeholder with actual last_insert_id
                if '{last_insert_id}' in stmt:
                    if last_id is None:
                        raise Exception("Attempted to use last_insert_id but no previous insert occurred")
                    stmt = stmt.replace('{last_insert_id}', str(last_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith('INSERT'):
                    last_id = cursor.lastrowid

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully saved Item id={obj.id}, internal_name={obj.internal_name}",
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
                    f"VALUES ({obj.id}, {component.item_id}, {component.ratio});"
                )

        return statements

    def save_item_blueprint(
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

            # Execute each statement
            for stmt in statements:
                cursor.execute(stmt)

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully saved ItemBlueprint id={obj.id}",
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
            elif isinstance(obj.owner, int):
                # It's a plain int, assume it's a mobile_id for backwards compatibility
                mobile_id = str(obj.owner)
                owner_id = mobile_id
                owner_type = "'MOBILE'"

        # Insert inventory
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
                    f"VALUES ({obj.id}, {entry.item_id}, {entry.quantity}, {is_max_stacked});"
                )

        # Insert inventory owner (one-to-one)
        statements.append(
            f"INSERT INTO {database}.{inventory_owners_table} "
            f"(inventory_id, mobile_id, item_id, asset_id) "
            f"VALUES ({obj.id}, {mobile_id}, {item_id}, {asset_id});"
        )

        return statements

    def save_inventory(
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

            # Execute each statement
            for stmt in statements:
                cursor.execute(stmt)

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully saved Inventory id={obj.id}",
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
        from game.ttypes import MobileType as MobileTypeEnum
        mobile_type_name = MobileTypeEnum._VALUES_TO_NAMES[obj.mobile_type]

        statements.append(
            f"INSERT INTO {database}.{mobile_table} (id, mobile_type) "
            f"VALUES ({obj.id}, '{mobile_type_name}');"
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

                # Insert attribute owner relationship (use placeholder for attribute id)
                statements.append(
                    f"INSERT INTO {database}.{attribute_owners_table} "
                    f"(attribute_id, mobile_id) "
                    f"VALUES ({{last_insert_id}}, {obj.id});"
                )

        return statements

    def save_mobile(
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
            for stmt in statements:
                # Replace placeholder with actual last_insert_id
                if '{last_insert_id}' in stmt:
                    if last_id is None:
                        raise Exception("Attempted to use last_insert_id but no previous insert occurred")
                    stmt = stmt.replace('{last_insert_id}', str(last_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith('INSERT'):
                    last_id = cursor.lastrowid

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully saved Mobile id={obj.id}",
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
            from game.ttypes import MobileType
            mobile_type = MobileType._NAMES_TO_VALUES[mobile_row['mobile_type']]

            # Create Mobile object
            mobile = Mobile(
                id=mobile_row['id'],
                mobile_type=mobile_type,
                attributes=attributes,
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
