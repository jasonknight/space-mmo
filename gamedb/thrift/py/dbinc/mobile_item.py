"""Item and ItemBlueprint database operations."""

import sys
from typing import Optional, Tuple

sys.path.append("../../gen-py")
sys.path.append("../")

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    ItemVector3,
    Item,
    MobileItem,
    ItemBlueprint,
    ItemBlueprintComponent,
    BackingTable,
    Owner,
)
from game.constants import TABLE2STR

from common import STR2TABLE
from db_tables import get_table_sql

# Note: is_ok and is_true are imported from common in the parent scope


class MobileItemMixin:
    """Mixin class for MobileItem and ItemBlueprint database operations."""

    def get_mobile_items_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.mobile_items (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                item_id BIGINT,
                internal_name VARCHAR(255) NOT NULL,
                max_stack_size BIGINT,
                item_type VARCHAR(50) NOT NULL,
                blueprint_id BIGINT
            );""",
        ]

    def get_mobile_item_blueprints_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.mobile_item_blueprints (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                bake_time_ms BIGINT NOT NULL
            );""",
        ]

    def get_mobile_item_blueprint_components_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.mobile_item_blueprint_components (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                mobile_item_blueprint_id BIGINT NOT NULL,
                component_item_id BIGINT NOT NULL,
                ratio DOUBLE NOT NULL,
                FOREIGN KEY (mobile_item_blueprint_id) REFERENCES {database}.mobile_item_blueprints(id)
            );""",
        ]

    def get_mobile_item_sql(
        self,
        database: str,
        obj: Item,
        table: Optional[str] = None,
        drop: bool = False,
        truncate: bool = False,
        attributes_table: Optional[str] = None,
        attribute_owners_table: Optional[str] = None,
    ) -> list[str]:
        # If both drop and truncate are True, set truncate to False
        if drop and truncate:
            truncate = False

        item_table = table if table else "items"
        # Determine attributes table based on item table (if not explicitly provided)
        if attributes_table is None:
            attributes_table = TABLE2STR[BackingTable.MOBILE_ITEM_ATTRIBUTES]

        statements = []

        if drop:
            statements.append(f"DROP TABLE IF EXISTS {database}.{attributes_table};")
            statements.append(f"DROP TABLE IF EXISTS {database}.{item_table};")

        if truncate:
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
                f"(item_id, mobile_id, internal_name, max_stack_size, item_type, blueprint_id) "
                f"VALUES ({obj.item_id}, {obj.mobile_id}, '{obj.internal_name}', {max_stack}, '{item_type_name}', {blueprint_val});"
            )
        else:
            statements.append(
                f"INSERT INTO {database}.{item_table} "
                f"(id, item_id, mobile_id, internal_name, max_stack_size, item_type, blueprint_id) "
                f"VALUES ({obj.id}, {obj.item_id}, {obj.mobile_id}, '{obj.internal_name}', {max_stack}, '{item_type_name}', {blueprint_val});"
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
                    # Handle AttributeValue union
                    from game.ttypes import AttributeValue

                    if isinstance(attribute.value, AttributeValue):
                        if attribute.value.bool_value is not None:
                            bool_val = str(attribute.value.bool_value)
                        elif attribute.value.double_value is not None:
                            double_val = str(attribute.value.double_value)
                        elif attribute.value.vector3 is not None:
                            vec3_x = str(attribute.value.vector3.x)
                            vec3_y = str(attribute.value.vector3.y)
                            vec3_z = str(attribute.value.vector3.z)
                        elif attribute.value.asset_id is not None:
                            asset_val = str(attribute.value.asset_id)
                    # Handle primitive values for backwards compatibility
                    elif isinstance(attribute.value, bool):
                        bool_val = str(attribute.value)
                    elif isinstance(attribute.value, (int, float)) and not isinstance(
                        attribute.value, bool
                    ):
                        double_val = str(attribute.value)
                    elif isinstance(attribute.value, ItemVector3):
                        vec3_x = str(attribute.value.x)
                        vec3_y = str(attribute.value.y)
                        vec3_z = str(attribute.value.z)
                    elif isinstance(attribute.value, int):
                        asset_val = str(attribute.value)

                # Insert attribute
                from game.ttypes import AttributeType as AttrTypeEnum2

                attr_type_name2 = AttrTypeEnum2._VALUES_TO_NAMES[
                    attribute.attribute_type
                ]

                statements.append(
                    f"INSERT INTO {database}.{attributes_table} "
                    f"(mobile_item_id, internal_name, visible, attribute_type, bool_value, double_value, "
                    f"vector3_x, vector3_y, vector3_z, asset_id) "
                    f"VALUES ({{item_id}},'{attribute.internal_name}', {attribute.visible}, "
                    f"'{attr_type_name2}', {bool_val}, {double_val}, "
                    f"{vec3_x}, {vec3_y}, {vec3_z}, {asset_val});"
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
                from common import is_ok

                if not is_ok(blueprint_results):
                    self.connection.rollback()
                    return blueprint_results

            # Get SQL statements
            statements = self.get_mobile_item_sql(database, obj, table)

            # Execute each statement and track last_insert_id
            last_id = None
            item_id_set = False
            for stmt in statements:
                # Replace placeholder with actual last_insert_id
                if "{last_insert_id}" in stmt:
                    if last_id is None:
                        raise Exception(
                            "Attempted to use last_insert_id but no previous insert occurred"
                        )
                    stmt = stmt.replace("{last_insert_id}", str(last_id))

                # Replace placeholder with actual item_id
                if "{item_id}" in stmt:
                    current_item_id = obj.id if obj.id is not None else last_id
                    if current_item_id is None:
                        raise Exception(
                            "Attempted to use item_id but no item insert occurred"
                        )
                    stmt = stmt.replace("{item_id}", str(current_item_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith("INSERT"):
                    last_id = cursor.lastrowid
                    # If this was the item insert and obj.id was None, set it now
                    if not item_id_set and obj.id is None and "items" in stmt:
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
                        message=f"Cannot update MobileItem with id=None",
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
                from common import is_ok

                if not is_ok(blueprint_results):
                    self.connection.rollback()
                    return blueprint_results

            item_table = table if table else "items"
            # Determine attributes table based on item table
            attributes_table = TABLE2STR[BackingTable.MOBILE_ATTRIBUTES]

            # Handle optional blueprint - reference by id
            blueprint_id = obj.blueprint.id if obj.blueprint else None

            from game.ttypes import ItemType as ItemTypeEnum

            item_type_name = ItemTypeEnum._VALUES_TO_NAMES[obj.item_type]

            max_stack = obj.max_stack_size if obj.max_stack_size else "NULL"
            blueprint_val = blueprint_id if blueprint_id else "NULL"

            # Update item
            kv_pairs = [
                f"item_id = '{obj.item_id}'",
                f"mobile_id = '{obj.mobile_id}'",
                f"internal_name = '{obj.internal_name}'",
                f"max_stack_size = {max_stack}",
                f"item_type = '{item_type_name}'",
                f"blueprint_id = {blueprint_val}",
            ]
            sql = (
                f"UPDATE {database}.{item_table} SET "
                + ",".join(kv_pairs)
                + f" WHERE id = {obj.id};"
            )
            print(sql)
            cursor.execute(sql)

            # Delete existing attributes
            cursor.execute(
                f"DELETE FROM {database}.{attributes_table} WHERE mobile_item_id = {obj.id};"
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
                        # Handle AttributeValue union
                        from game.ttypes import AttributeValue

                        if isinstance(attribute.value, AttributeValue):
                            if attribute.value.bool_value is not None:
                                bool_val = str(attribute.value.bool_value)
                            elif attribute.value.double_value is not None:
                                double_val = str(attribute.value.double_value)
                            elif attribute.value.vector3 is not None:
                                vec3_x = str(attribute.value.vector3.x)
                                vec3_y = str(attribute.value.vector3.y)
                                vec3_z = str(attribute.value.vector3.z)
                            elif attribute.value.asset_id is not None:
                                asset_val = str(attribute.value.asset_id)
                        # Handle primitive values for backwards compatibility
                        elif isinstance(attribute.value, bool):
                            bool_val = str(attribute.value)
                        elif isinstance(
                            attribute.value, (int, float)
                        ) and not isinstance(attribute.value, bool):
                            double_val = str(attribute.value)
                        elif isinstance(attribute.value, ItemVector3):
                            vec3_x = str(attribute.value.x)
                            vec3_y = str(attribute.value.y)
                            vec3_z = str(attribute.value.z)
                        elif isinstance(attribute.value, int):
                            asset_val = str(attribute.value)

                    from game.ttypes import AttributeType as AttrTypeEnum2

                    attr_type_name2 = AttrTypeEnum2._VALUES_TO_NAMES[
                        attribute.attribute_type
                    ]
                    cursor.execute(
                        f"INSERT INTO {database}.{attributes_table} "
                        f"(mobile_item_id, internal_name, visible, attribute_type, bool_value, double_value, "
                        f"vector3_x, vector3_y, vector3_z, asset_id) "
                        f"VALUES ({{item_id}}, '{attribute.internal_name}', {attribute.visible}, "
                        f"'{attr_type_name2}', {bool_val}, {double_val}, "
                        f"{vec3_x}, {vec3_y}, {vec3_z}, {asset_val});"
                    )

            # Commit transaction
            self.connection.commit()
            cursor.close()

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated MobileItem id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update MobileItem id={obj.id} in database={database}: {str(e)}",
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

            item_table = table if table else TABLE2STR[BackingTable.MOBILE_ITEMS]
            attributes_table = TABLE2STR[BackingTable.MOBILE_ITEM_ATTRIBUTES]

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
                        message=f"MobileItem id={item_id} not found in database={database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load blueprint if it exists
            blueprint = None
            if item_row["blueprint_id"]:
                from common import is_true

                blueprint_result, blueprint = self.load_item_blueprint(
                    database,
                    item_row["blueprint_id"],
                )
                if not is_true(blueprint_result):
                    cursor.close()
                    return (blueprint_result, None)

            # Load attributes through attribute_owners
            attribute_rows = []

            cursor.execute(
                f"SELECT a.* FROM {database}.{attributes_table} a "
                f"WHERE a.mobile_item_id = %s;",
                (item_id,),
            )

            attribute_rows = cursor.fetchall()

            # Build attributes map
            attributes = {}
            for row in attribute_rows:
                # Reconstruct AttributeValue union
                value = None
                if row["bool_value"] is not None:
                    value = row["bool_value"]
                elif row["double_value"] is not None:
                    value = row["double_value"]
                elif row["vector3_x"] is not None:
                    value = ItemVector3(
                        x=row["vector3_x"],
                        y=row["vector3_y"],
                        z=row["vector3_z"],
                    )
                elif row["asset_id"] is not None:
                    value = row["asset_id"]

                owner = None
                # The Owner is always a Mobile in this case
                owner = Owner(mobile_id=item_row["mobile_id"])

                # Import AttributeType enum
                from game.ttypes import AttributeType, Attribute

                attr_type = AttributeType._NAMES_TO_VALUES[row["attribute_type"]]

                attribute = Attribute(
                    id=row["id"],
                    internal_name=row["internal_name"],
                    visible=row["visible"],
                    value=value,
                    attribute_type=attr_type,
                    owner=owner,
                )
                attributes[attr_type] = attribute

            # Import ItemType enum
            from game.ttypes import ItemType
            from common import STR2TABLE

            item_type = ItemType._NAMES_TO_VALUES[item_row["item_type"]]

            # Determine backing_table based on the table used
            backing_table_value = BackingTable.MOBILE_ITEMS

            # Create Item object
            item = MobileItem(
                id=item_row["id"],
                mobile_id=item_row["mobile_id"],
                item_id=item_row["item_id"],
                internal_name=item_row["internal_name"],
                attributes=attributes,
                max_stack_size=item_row["max_stack_size"],
                item_type=item_type,
                blueprint=blueprint,
                backing_table=backing_table_value,
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded MobileItem id={item_id}",
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
        components_table: Optional[str] = None,
    ) -> list[str]:
        # If both drop and truncate are True, set truncate to False
        if drop and truncate:
            truncate = False

        blueprint_table = BackingTable.MOBILE_ITEM_BLUEPRINTS
        components_table = BackingTable.MOBILE_ITEM_BLUEPRINT_COMPONENTS

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
                if "{blueprint_id}" in stmt:
                    blueprint_id = (
                        obj.id if obj.id is not None else blueprint_id_for_components
                    )
                    if blueprint_id is None:
                        raise Exception(
                            "Attempted to use blueprint_id but no blueprint insert occurred"
                        )
                    stmt = stmt.replace("{blueprint_id}", str(blueprint_id))

                cursor.execute(stmt)

                # Get last insert id if this was an INSERT
                if stmt.strip().upper().startswith("INSERT"):
                    last_id = cursor.lastrowid
                    # If this was the blueprint insert and obj.id was None, store it for components
                    if (
                        blueprint_id_for_components is None
                        and obj.id is None
                        and "item_blueprints" in stmt
                    ):
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

            blueprint_table = (
                table if table else TABLE2STR[BackingTable.MOBILE_ITEM_BLUEPRINTS]
            )
            components_table = TABLE2STR[BackingTable.MOBILE_ITEM_BLUEPRINT_COMPONENTS]

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

            blueprint_table = (
                table if table else TABLE2STR[BackingTable.MOBILE_ITEM_BLUEPRINTS]
            )
            components_table = TABLE2STR[
                BackingTableBackingTable.MOBILE_ITEM_BLUEPRINT_COMPONENTS
            ]

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
                    ratio=row["ratio"],
                    item_id=row["component_item_id"],
                )
                components[row["component_item_id"]] = component

            # Create ItemBlueprint object
            blueprint = ItemBlueprint(
                id=blueprint_row["id"],
                components=components,
                bake_time_ms=blueprint_row["bake_time_ms"],
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
        if table is None:
            table = TABLE2STR[BackingTable.MOBILE_ITEMS]

        if obj.id is None:
            return self.create_item(database, obj, table)
        else:
            return self.update_item(database, obj, table)

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

            blueprint_table = (
                table if table else TABLE2STR[BackingTable.MOBILE_ITEM_BLUEPRINTS]
            )
            components_table = TABLE2STR[BackingTable.MOBILE_ITEM_BLUEPRINT_COMPONENTS]

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

            item_table = table if table else TABLE2STR[BackingTable.MOBILE_ITEMS]
            attributes_table = TABLE2STR[BackingTable.MOBILE_ITEM_ATTRIBUTES]

            cursor.execute(
                f"DELETE FROM {database}.{attributes_table} WHERE mobile_item_id = {item_id}"
            )

            # Delete the item
            cursor.execute(f"DELETE FROM {database}.{item_table} WHERE id = {item_id};")

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

    def list_item(
        self,
        database: str,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[Item]], int]:
        """
        List items with pagination and optional search.

        Args:
            database: Database name
            page: Page number (0-indexed)
            results_per_page: Number of results per page
            search_string: Optional search string (searches internal_name)
            table: Optional table name override

        Returns:
            Tuple of (GameResult, list of Item objects, total count)
        """
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            item_table = table if table else TABLE2STR[BackingTable.MOBILE_ITEMS]

            # Calculate offset (page is 1-indexed from API)
            page = max(0, page)
            offset = page * results_per_page

            # Build WHERE clause for search
            where_clause = ""
            params = []
            if search_string:
                where_clause = "WHERE internal_name LIKE %s"
                search_pattern = f"%{search_string}%"
                params = [search_pattern]

            # Get total count
            count_query = (
                f"SELECT COUNT(*) as total FROM {database}.{item_table} {where_clause};"
            )
            cursor.execute(count_query, tuple(params))
            count_row = cursor.fetchone()
            total_count = count_row["total"] if count_row else 0

            # Get paginated results
            query = f"SELECT * FROM {database}.{item_table} {where_clause} ORDER BY id LIMIT %s OFFSET %s;"
            cursor.execute(query, tuple(params + [results_per_page, offset]))
            item_rows = cursor.fetchall()

            # Convert rows to Item objects
            items = []
            for row in item_rows:
                # Load blueprint if it exists
                blueprint = None
                if row["blueprint_id"]:
                    from common import is_true

                    blueprint_result, blueprint = self.load_item_blueprint(
                        database,
                        row["blueprint_id"],
                    )

                # Load attributes through attribute_owners
                # Determine attributes table based on item table
                attributes_table = TABLE2STR[BackingTable.MOBILE_ITEM_ATTRIBUTES]

                cursor.execute(
                    f"SELECT a.* FROM {database}.{attributes_table} a "
                    f"WHERE a.mobile_item_id = %s;",
                    (row["id"],),
                )
                attribute_rows = cursor.fetchall()

                # Build attributes map
                attributes = {}
                for attr_row in attribute_rows:
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

                    owner = Owner(mobile_id=row["id"])

                    # Import AttributeType enum
                    from game.ttypes import AttributeType, Attribute

                    attr_type = AttributeType._NAMES_TO_VALUES[
                        attr_row["attribute_type"]
                    ]

                    attribute = Attribute(
                        id=attr_row["id"],
                        internal_name=attr_row["internal_name"],
                        visible=attr_row["visible"],
                        value=value,
                        attribute_type=attr_type,
                        owner=owner,
                    )
                    attributes[attr_type] = attribute

                # Import ItemType enum
                from game.ttypes import ItemType
                from common import STR2TABLE

                item_type = ItemType._NAMES_TO_VALUES[row["item_type"]]

                # Determine backing_table based on the table used
                backing_table_value = (
                    STR2TABLE.get(item_table) if item_table in STR2TABLE else None
                )

                # Create Item object
                item = Item(
                    id=row["id"],
                    internal_name=row["internal_name"],
                    attributes=attributes,
                    max_stack_size=row["max_stack_size"],
                    item_type=item_type,
                    blueprint=blueprint,
                    backing_table=backing_table_value,
                )
                items.append(item)

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully listed {len(items)} items (total: {total_count})",
                ),
                items,
                total_count,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to list items from database={database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
        finally:
            if cursor:
                cursor.close()
