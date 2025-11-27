"""Item database model."""

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
    ItemType,
    Attribute,
    AttributeType,
    Owner,
    BackingTable,
)
from game.constants import TABLE2STR
from base_model import BaseModel
from models.blueprint_model import BlueprintModel
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


class ItemModel(BaseModel):
    """Model for Item database operations."""

    # Table constants - single source of truth for table names
    ITEM_TABLE = "items"
    ATTRIBUTES_TABLE = "attributes"
    ATTRIBUTE_OWNERS_TABLE = "attribute_owners"

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        item_table: Optional[str] = None,
        attributes_table: Optional[str] = None,
        attribute_owners_table: Optional[str] = None,
    ):
        super().__init__(host, user, password, database)
        # Allow table override for mobile items, etc.
        self.item_table = item_table if item_table else self.ITEM_TABLE
        self.attributes_table = (
            attributes_table if attributes_table else self.ATTRIBUTES_TABLE
        )
        self.attribute_owners_table = (
            attribute_owners_table
            if attribute_owners_table
            else self.ATTRIBUTE_OWNERS_TABLE
        )

    def _get_blueprint_model(self) -> BlueprintModel:
        """Get a BlueprintModel instance for blueprint operations."""
        return BlueprintModel(
            self.host,
            self.user,
            self.password,
            self.database,
        )

    def create(
        self,
        obj: Item,
    ) -> list[GameResult]:
        """Create a new Item in the database."""
        try:
            with self.transaction() as cursor:
                # If blueprint exists, save it first
                if obj.blueprint:
                    blueprint_model = self._get_blueprint_model()
                    blueprint_results = blueprint_model.save(obj.blueprint)
                    if not is_ok(blueprint_results):
                        return blueprint_results

                # Insert the item
                blueprint_id = obj.blueprint.id if obj.blueprint else None

                # Get item type name
                item_type_name = ItemType._VALUES_TO_NAMES[obj.item_type]

                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.item_table} "
                        f"(internal_name, max_stack_size, item_type, blueprint_id) "
                        f"VALUES (%s, %s, %s, %s);",
                        (
                            obj.internal_name,
                            obj.max_stack_size,
                            item_type_name,
                            blueprint_id,
                        ),
                    )
                    obj.id = cursor.lastrowid
                else:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.item_table} "
                        f"(id, internal_name, max_stack_size, item_type, blueprint_id) "
                        f"VALUES (%s, %s, %s, %s, %s);",
                        (
                            obj.id,
                            obj.internal_name,
                            obj.max_stack_size,
                            item_type_name,
                            blueprint_id,
                        ),
                    )

                # Insert attributes
                if obj.attributes:
                    for attr_type, attribute in obj.attributes.items():
                        # Convert attribute value to SQL fields
                        value_fields = attribute_value_to_sql_fields(attribute)

                        # Get attribute type name
                        attr_type_name = AttributeType._VALUES_TO_NAMES[
                            attribute.attribute_type
                        ]

                        # Insert attribute
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.attributes_table} "
                            f"(internal_name, visible, attribute_type, bool_value, double_value, "
                            f"vector3_x, vector3_y, vector3_z, asset_id) "
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                            (
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

                        attr_id = cursor.lastrowid

                        # Insert attribute owner relationship
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.attribute_owners_table} "
                            f"(attribute_id, item_id) "
                            f"VALUES (%s, %s);",
                            (
                                attr_id,
                                obj.id,
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created Item id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to create Item id={obj.id}, internal_name={obj.internal_name} to database={self.database}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def load(
        self,
        obj_id: int,
    ) -> Tuple[GameResult, Optional[Item]]:
        """Load an Item from the database by ID."""
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Load the item
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.item_table} WHERE id = %s;",
                (obj_id,),
            )
            item_row = cursor.fetchone()

            if not item_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Item id={obj_id} not found in database={self.database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load blueprint if it exists
            blueprint = None
            if item_row["blueprint_id"]:
                blueprint_model = self._get_blueprint_model()
                blueprint_result, blueprint = blueprint_model.load(
                    item_row["blueprint_id"],
                )
                if blueprint_result.status == StatusType.FAILURE:
                    cursor.close()
                    return (
                        blueprint_result,
                        None,
                    )

            # Load attributes through attribute_owners
            cursor.execute(
                f"SELECT a.* FROM {self.database}.{self.attributes_table} a "
                f"INNER JOIN {self.database}.{self.attribute_owners_table} ao ON a.id = ao.attribute_id "
                f"WHERE ao.item_id = %s;",
                (obj_id,),
            )
            attribute_rows = cursor.fetchall()

            # Build attributes map
            attributes = {}
            for row in attribute_rows:
                # Reconstruct AttributeValue
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

                # Reconstruct Owner
                cursor.execute(
                    f"SELECT * FROM {self.database}.{self.attribute_owners_table} WHERE attribute_id = %s;",
                    (row["id"],),
                )
                owner_row = cursor.fetchone()

                owner = None
                if owner_row:
                    if owner_row["mobile_id"]:
                        owner = Owner(mobile_id=owner_row["mobile_id"])
                    elif owner_row["item_id"]:
                        owner = Owner(item_id=owner_row["item_id"])
                    elif owner_row["asset_id"]:
                        owner = Owner(asset_id=owner_row["asset_id"])
                    elif owner_row["player_id"]:
                        owner = Owner(player_id=owner_row["player_id"])

                # Get attribute type
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

            # Determine backing_table based on the table used
            backing_table_value = (
                STR2TABLE.get(self.item_table) if self.item_table in STR2TABLE else None
            )

            # Create Item object
            item = Item(
                id=item_row["id"],
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
                    message=f"Successfully loaded Item id={obj_id}",
                ),
                item,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Item id={obj_id} from database={self.database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def update(
        self,
        obj: Item,
    ) -> list[GameResult]:
        """Update an existing Item in the database."""
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Item with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            with self.transaction() as cursor:
                # If blueprint exists, save it first (will create or update as needed)
                if obj.blueprint:
                    blueprint_model = self._get_blueprint_model()
                    blueprint_results = blueprint_model.save(obj.blueprint)
                    if not is_ok(blueprint_results):
                        return blueprint_results

                # Update item
                blueprint_id = obj.blueprint.id if obj.blueprint else None
                item_type_name = ItemType._VALUES_TO_NAMES[obj.item_type]

                cursor.execute(
                    f"UPDATE {self.database}.{self.item_table} SET "
                    f"internal_name = %s, "
                    f"max_stack_size = %s, "
                    f"item_type = %s, "
                    f"blueprint_id = %s "
                    f"WHERE id = %s;",
                    (
                        obj.internal_name,
                        obj.max_stack_size,
                        item_type_name,
                        blueprint_id,
                        obj.id,
                    ),
                )

                # Delete existing attributes
                # First get the attribute IDs
                cursor.execute(
                    f"SELECT attribute_id FROM {self.database}.{self.attribute_owners_table} WHERE item_id = %s;",
                    (obj.id,),
                )
                attr_ids = [row[0] for row in cursor.fetchall()]

                # Delete from attribute_owners
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.attribute_owners_table} WHERE item_id = %s;",
                    (obj.id,),
                )

                # Delete the attributes themselves
                if attr_ids:
                    placeholders = ",".join(["%s"] * len(attr_ids))
                    cursor.execute(
                        f"DELETE FROM {self.database}.{self.attributes_table} WHERE id IN ({placeholders});",
                        tuple(attr_ids),
                    )

                # Insert new attributes
                if obj.attributes:
                    for attr_type, attribute in obj.attributes.items():
                        # Convert attribute value to SQL fields
                        value_fields = attribute_value_to_sql_fields(attribute)

                        # Get attribute type name
                        attr_type_name = AttributeType._VALUES_TO_NAMES[
                            attribute.attribute_type
                        ]

                        # Insert attribute
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.attributes_table} "
                            f"(internal_name, visible, attribute_type, bool_value, double_value, "
                            f"vector3_x, vector3_y, vector3_z, asset_id) "
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                            (
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

                        attr_id = cursor.lastrowid

                        # Insert attribute owner relationship
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.attribute_owners_table} "
                            f"(attribute_id, item_id) "
                            f"VALUES (%s, %s);",
                            (
                                attr_id,
                                obj.id,
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated Item id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Item id={obj.id} in database={self.database}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def destroy(
        self,
        obj_id: int,
    ) -> list[GameResult]:
        """Delete an Item from the database by ID."""
        try:
            with self.transaction() as cursor:
                # Get attribute IDs first
                cursor.execute(
                    f"SELECT attribute_id FROM {self.database}.{self.attribute_owners_table} WHERE item_id = %s;",
                    (obj_id,),
                )
                attr_ids = [row[0] for row in cursor.fetchall()]

                # Delete attribute owners
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.attribute_owners_table} WHERE item_id = %s;",
                    (obj_id,),
                )

                # Delete attributes
                if attr_ids:
                    placeholders = ",".join(["%s"] * len(attr_ids))
                    cursor.execute(
                        f"DELETE FROM {self.database}.{self.attributes_table} WHERE id IN ({placeholders});",
                        tuple(attr_ids),
                    )

                # Delete the item
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.item_table} WHERE id = %s;",
                    (obj_id,),
                )

                # Check if any rows were affected
                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Item id={obj_id} not found in database={self.database}",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Item id={obj_id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Item id={obj_id} in database={self.database}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    def search(
        self,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[Item]], int]:
        """
        Search for Items with pagination and optional search.

        Args:
            page: Page number (0-indexed)
            results_per_page: Number of results per page
            search_string: Optional search string (searches internal_name)

        Returns:
            Tuple of (GameResult, list of Item objects, total count)
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
            count_query = f"SELECT COUNT(*) as total FROM {self.database}.{self.item_table} {where_clause};"
            cursor.execute(count_query, tuple(params))
            count_row = cursor.fetchone()
            total_count = count_row["total"] if count_row else 0

            # Get paginated results
            query = f"SELECT * FROM {self.database}.{self.item_table} {where_clause} ORDER BY id LIMIT %s OFFSET %s;"
            cursor.execute(query, tuple(params + [results_per_page, offset]))
            item_rows = cursor.fetchall()

            # Convert rows to Item objects
            items = []
            blueprint_model = self._get_blueprint_model()
            for row in item_rows:
                # Load blueprint if it exists
                blueprint = None
                if row["blueprint_id"]:
                    blueprint_result, blueprint = blueprint_model.load(
                        row["blueprint_id"],
                    )

                # Load attributes through attribute_owners
                cursor.execute(
                    f"SELECT a.* FROM {self.database}.{self.attributes_table} a "
                    f"INNER JOIN {self.database}.{self.attribute_owners_table} ao ON a.id = ao.attribute_id "
                    f"WHERE ao.item_id = %s;",
                    (row["id"],),
                )
                attribute_rows = cursor.fetchall()

                # Build attributes map
                attributes = {}
                for attr_row in attribute_rows:
                    # Reconstruct AttributeValue
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

                    # Reconstruct Owner
                    cursor.execute(
                        f"SELECT * FROM {self.database}.{self.attribute_owners_table} WHERE attribute_id = %s;",
                        (attr_row["id"],),
                    )
                    owner_row = cursor.fetchone()

                    owner = None
                    if owner_row:
                        if owner_row["mobile_id"]:
                            owner = Owner(mobile_id=owner_row["mobile_id"])
                        elif owner_row["item_id"]:
                            owner = Owner(item_id=owner_row["item_id"])
                        elif owner_row["asset_id"]:
                            owner = Owner(asset_id=owner_row["asset_id"])
                        elif owner_row["player_id"]:
                            owner = Owner(player_id=owner_row["player_id"])

                    # Get attribute type
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

                # Determine backing_table based on the table used
                backing_table_value = (
                    STR2TABLE.get(self.item_table)
                    if self.item_table in STR2TABLE
                    else None
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
                    message=f"Failed to search items from database={self.database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
        finally:
            if cursor:
                cursor.close()
