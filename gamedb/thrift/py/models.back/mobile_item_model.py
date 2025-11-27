"""MobileItem database model."""

import sys
from typing import Optional, Tuple

sys.path.append("../../gen-py")
sys.path.append("../")

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    ItemVector3,
    MobileItem,
    ItemType,
    Attribute,
    AttributeType,
    Owner,
    BackingTable,
    ItemBlueprint,
)
from game.constants import TABLE2STR
from base_model import BaseModel
from common import is_ok, STR2TABLE


# Helper function to convert attribute value to SQL fields
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
            attribute.value,
            bool,
        ):
            fields["double_value"] = attribute.value
        elif isinstance(attribute.value, ItemVector3):
            fields["vector3_x"] = attribute.value.x
            fields["vector3_y"] = attribute.value.y
            fields["vector3_z"] = attribute.value.z
        elif isinstance(attribute.value, int):
            fields["asset_id"] = attribute.value

    return fields


class MobileItemModel(BaseModel):
    """Model for MobileItem database operations."""

    # Table constants - single source of truth for table names
    MOBILE_ITEM_TABLE = "mobile_items"
    MOBILE_ITEM_ATTRIBUTES_TABLE = "mobile_item_attributes"
    MOBILE_ITEM_BLUEPRINTS_TABLE = "mobile_item_blueprints"
    MOBILE_ITEM_BLUEPRINT_COMPONENTS_TABLE = "mobile_item_blueprint_components"

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        mobile_item_table: Optional[str] = None,
        mobile_item_attributes_table: Optional[str] = None,
        mobile_item_blueprints_table: Optional[str] = None,
        mobile_item_blueprint_components_table: Optional[str] = None,
    ):
        super().__init__(host, user, password, database)
        # Allow table override
        self.mobile_item_table = (
            mobile_item_table if mobile_item_table else self.MOBILE_ITEM_TABLE
        )
        self.mobile_item_attributes_table = (
            mobile_item_attributes_table
            if mobile_item_attributes_table
            else self.MOBILE_ITEM_ATTRIBUTES_TABLE
        )
        self.mobile_item_blueprints_table = (
            mobile_item_blueprints_table
            if mobile_item_blueprints_table
            else self.MOBILE_ITEM_BLUEPRINTS_TABLE
        )
        self.mobile_item_blueprint_components_table = (
            mobile_item_blueprint_components_table
            if mobile_item_blueprint_components_table
            else self.MOBILE_ITEM_BLUEPRINT_COMPONENTS_TABLE
        )

    def _save_blueprint(
        self,
        blueprint: ItemBlueprint,
    ) -> list[GameResult]:
        """Save a blueprint for mobile items."""
        try:
            with self.transaction() as cursor:
                # Insert or update the blueprint
                if blueprint.id is None:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.mobile_item_blueprints_table} "
                        f"(bake_time_ms) VALUES (%s);",
                        (blueprint.bake_time_ms,),
                    )
                    blueprint.id = cursor.lastrowid
                else:
                    # Update existing blueprint
                    cursor.execute(
                        f"UPDATE {self.database}.{self.mobile_item_blueprints_table} "
                        f"SET bake_time_ms = %s WHERE id = %s;",
                        (
                            blueprint.bake_time_ms,
                            blueprint.id,
                        ),
                    )

                    # Delete existing components
                    cursor.execute(
                        f"DELETE FROM {self.database}.{self.mobile_item_blueprint_components_table} "
                        f"WHERE mobile_item_blueprint_id = %s;",
                        (blueprint.id,),
                    )

                # Insert components
                if blueprint.components:
                    for item_id, component in blueprint.components.items():
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.mobile_item_blueprint_components_table} "
                            f"(mobile_item_blueprint_id, component_item_id, ratio) "
                            f"VALUES (%s, %s, %s);",
                            (
                                blueprint.id,
                                component.item_id,
                                component.ratio,
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully saved mobile item blueprint id={blueprint.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to save mobile item blueprint: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def _load_blueprint(
        self,
        blueprint_id: int,
    ) -> Tuple[GameResult, Optional[ItemBlueprint]]:
        """Load a blueprint for mobile items."""
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Load the blueprint
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.mobile_item_blueprints_table} WHERE id = %s;",
                (blueprint_id,),
            )
            blueprint_row = cursor.fetchone()

            if not blueprint_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Mobile item blueprint id={blueprint_id} not found",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load components
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.mobile_item_blueprint_components_table} "
                f"WHERE mobile_item_blueprint_id = %s;",
                (blueprint_id,),
            )
            component_rows = cursor.fetchall()

            # Build components map
            from game.ttypes import ItemBlueprintComponent

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
                    message=f"Successfully loaded mobile item blueprint id={blueprint_id}",
                ),
                blueprint,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load mobile item blueprint id={blueprint_id}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def create(
        self,
        obj: MobileItem,
    ) -> list[GameResult]:
        """Create a new MobileItem in the database."""
        try:
            with self.transaction() as cursor:
                # If blueprint exists, save it first
                if obj.blueprint:
                    blueprint_results = self._save_blueprint(obj.blueprint)
                    if not is_ok(blueprint_results):
                        return blueprint_results

                # Insert the mobile item
                blueprint_id = obj.blueprint.id if obj.blueprint else None
                item_type_name = ItemType._VALUES_TO_NAMES[obj.item_type]

                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.mobile_item_table} "
                        f"(item_id, mobile_id, internal_name, max_stack_size, item_type, blueprint_id) "
                        f"VALUES (%s, %s, %s, %s, %s, %s);",
                        (
                            obj.item_id,
                            obj.mobile_id,
                            obj.internal_name,
                            obj.max_stack_size,
                            item_type_name,
                            blueprint_id,
                        ),
                    )
                    obj.id = cursor.lastrowid
                else:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.mobile_item_table} "
                        f"(id, item_id, mobile_id, internal_name, max_stack_size, item_type, blueprint_id) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s);",
                        (
                            obj.id,
                            obj.item_id,
                            obj.mobile_id,
                            obj.internal_name,
                            obj.max_stack_size,
                            item_type_name,
                            blueprint_id,
                        ),
                    )

                # Insert attributes directly (mobile_items use mobile_item_attributes table)
                if obj.attributes:
                    for attr_type, attribute in obj.attributes.items():
                        value_fields = attribute_value_to_sql_fields(attribute)
                        attr_type_name = AttributeType._VALUES_TO_NAMES[
                            attribute.attribute_type
                        ]

                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.mobile_item_attributes_table} "
                            f"(mobile_item_id, internal_name, visible, attribute_type, bool_value, "
                            f"double_value, vector3_x, vector3_y, vector3_z, asset_id) "
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                            (
                                obj.id,
                                attribute.internal_name,
                                attribute.visible,
                                attr_type_name,
                                value_fields["bool_value"],
                                value_fields["double_value"],
                                value_fields["vector3_x"],
                                value_fields["vector3_y"],
                                value_fields["vector3_z"],
                                value_fields["asset_id"],
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created MobileItem id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to create MobileItem id={obj.id}, internal_name={obj.internal_name}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def load(
        self,
        obj_id: int,
    ) -> Tuple[GameResult, Optional[MobileItem]]:
        """Load a MobileItem from the database by ID."""
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Load the mobile item
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.mobile_item_table} WHERE id = %s;",
                (obj_id,),
            )
            item_row = cursor.fetchone()

            if not item_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"MobileItem id={obj_id} not found in database={self.database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load blueprint if it exists
            blueprint = None
            if item_row["blueprint_id"]:
                blueprint_result, blueprint = self._load_blueprint(
                    item_row["blueprint_id"],
                )
                if blueprint_result.status == StatusType.FAILURE:
                    cursor.close()
                    return (
                        blueprint_result,
                        None,
                    )

            # Load attributes (stored directly in mobile_item_attributes)
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.mobile_item_attributes_table} "
                f"WHERE mobile_item_id = %s;",
                (obj_id,),
            )
            attribute_rows = cursor.fetchall()

            # Build attributes map
            attributes = {}
            for row in attribute_rows:
                # Reconstruct attribute value
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

                # Owner is always the mobile for mobile items
                owner = Owner(mobile_id=item_row["mobile_id"])

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

            # Get item type
            item_type = ItemType._NAMES_TO_VALUES[item_row["item_type"]]

            # Create MobileItem object
            mobile_item = MobileItem(
                id=item_row["id"],
                item_id=item_row["item_id"],
                mobile_id=item_row["mobile_id"],
                internal_name=item_row["internal_name"],
                attributes=attributes,
                max_stack_size=item_row["max_stack_size"],
                item_type=item_type,
                blueprint=blueprint,
                backing_table=BackingTable.MOBILE_ITEMS,
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded MobileItem id={obj_id}",
                ),
                mobile_item,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load MobileItem id={obj_id}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def update(
        self,
        obj: MobileItem,
    ) -> list[GameResult]:
        """Update an existing MobileItem in the database."""
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update MobileItem with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            with self.transaction() as cursor:
                # If blueprint exists, save it first
                if obj.blueprint:
                    blueprint_results = self._save_blueprint(obj.blueprint)
                    if not is_ok(blueprint_results):
                        return blueprint_results

                # Update mobile item
                blueprint_id = obj.blueprint.id if obj.blueprint else None
                item_type_name = ItemType._VALUES_TO_NAMES[obj.item_type]

                cursor.execute(
                    f"UPDATE {self.database}.{self.mobile_item_table} SET "
                    f"item_id = %s, "
                    f"mobile_id = %s, "
                    f"internal_name = %s, "
                    f"max_stack_size = %s, "
                    f"item_type = %s, "
                    f"blueprint_id = %s "
                    f"WHERE id = %s;",
                    (
                        obj.item_id,
                        obj.mobile_id,
                        obj.internal_name,
                        obj.max_stack_size,
                        item_type_name,
                        blueprint_id,
                        obj.id,
                    ),
                )

                # Delete existing attributes
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.mobile_item_attributes_table} "
                    f"WHERE mobile_item_id = %s;",
                    (obj.id,),
                )

                # Insert new attributes
                if obj.attributes:
                    for attr_type, attribute in obj.attributes.items():
                        value_fields = attribute_value_to_sql_fields(attribute)
                        attr_type_name = AttributeType._VALUES_TO_NAMES[
                            attribute.attribute_type
                        ]

                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.mobile_item_attributes_table} "
                            f"(mobile_item_id, internal_name, visible, attribute_type, bool_value, "
                            f"double_value, vector3_x, vector3_y, vector3_z, asset_id) "
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                            (
                                obj.id,
                                attribute.internal_name,
                                attribute.visible,
                                attr_type_name,
                                value_fields["bool_value"],
                                value_fields["double_value"],
                                value_fields["vector3_x"],
                                value_fields["vector3_y"],
                                value_fields["vector3_z"],
                                value_fields["asset_id"],
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated MobileItem id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update MobileItem id={obj.id}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def destroy(
        self,
        obj_id: int,
    ) -> list[GameResult]:
        """Delete a MobileItem from the database by ID."""
        try:
            with self.transaction() as cursor:
                # Delete attributes
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.mobile_item_attributes_table} "
                    f"WHERE mobile_item_id = %s;",
                    (obj_id,),
                )

                # Delete the mobile item
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.mobile_item_table} WHERE id = %s;",
                    (obj_id,),
                )

                # Check if any rows were affected
                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"MobileItem id={obj_id} not found in database={self.database}",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed MobileItem id={obj_id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy MobileItem id={obj_id}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    def search(
        self,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[MobileItem]], int]:
        """
        Search for MobileItems with pagination and optional search.

        Args:
            page: Page number (0-indexed)
            results_per_page: Number of results per page
            search_string: Optional search string (searches internal_name)

        Returns:
            Tuple of (GameResult, list of MobileItem objects, total count)
        """
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Calculate offset (page is 0-indexed)
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
            count_query = f"SELECT COUNT(*) as total FROM {self.database}.{self.mobile_item_table} {where_clause};"
            cursor.execute(count_query, tuple(params))
            count_row = cursor.fetchone()
            total_count = count_row["total"] if count_row else 0

            # Get paginated results
            query = f"SELECT * FROM {self.database}.{self.mobile_item_table} {where_clause} ORDER BY id LIMIT %s OFFSET %s;"
            cursor.execute(query, tuple(params + [results_per_page, offset]))
            item_rows = cursor.fetchall()

            # Convert rows to MobileItem objects
            mobile_items = []
            for row in item_rows:
                # Load blueprint if it exists
                blueprint = None
                if row["blueprint_id"]:
                    blueprint_result, blueprint = self._load_blueprint(
                        row["blueprint_id"],
                    )

                # Load attributes
                cursor.execute(
                    f"SELECT * FROM {self.database}.{self.mobile_item_attributes_table} "
                    f"WHERE mobile_item_id = %s;",
                    (row["id"],),
                )
                attribute_rows = cursor.fetchall()

                # Build attributes map
                attributes = {}
                for attr_row in attribute_rows:
                    # Reconstruct attribute value
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

                    owner = Owner(mobile_id=row["mobile_id"])
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

                # Get item type
                item_type = ItemType._NAMES_TO_VALUES[row["item_type"]]

                # Create MobileItem object
                mobile_item = MobileItem(
                    id=row["id"],
                    item_id=row["item_id"],
                    mobile_id=row["mobile_id"],
                    internal_name=row["internal_name"],
                    attributes=attributes,
                    max_stack_size=row["max_stack_size"],
                    item_type=item_type,
                    blueprint=blueprint,
                    backing_table=BackingTable.MOBILE_ITEMS,
                )
                mobile_items.append(mobile_item)

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully listed {len(mobile_items)} mobile items (total: {total_count})",
                ),
                mobile_items,
                total_count,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to search mobile items: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
        finally:
            if cursor:
                cursor.close()
