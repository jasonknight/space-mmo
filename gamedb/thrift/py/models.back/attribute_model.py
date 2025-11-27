"""Attribute database model."""

import sys
from typing import Optional, Tuple

sys.path.append("../../gen-py")
sys.path.append("../")

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    ItemVector3,
    Attribute,
    AttributeType,
    Owner,
)
from base_model import BaseModel


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


class AttributeModel(BaseModel):
    """Model for Attribute database operations."""

    # Table constants - single source of truth for table names
    ATTRIBUTES_TABLE = "attributes"
    ATTRIBUTE_OWNERS_TABLE = "attribute_owners"

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        attributes_table: Optional[str] = None,
        attribute_owners_table: Optional[str] = None,
    ):
        super().__init__(host, user, password, database)
        # Allow table override for mobile attributes, etc.
        self.attributes_table = (
            attributes_table if attributes_table else self.ATTRIBUTES_TABLE
        )
        self.attribute_owners_table = (
            attribute_owners_table
            if attribute_owners_table
            else self.ATTRIBUTE_OWNERS_TABLE
        )

    def create(
        self,
        obj: Attribute,
    ) -> list[GameResult]:
        """Create a new Attribute in the database."""
        try:
            with self.transaction() as cursor:
                # Convert attribute value to SQL fields
                value_fields = attribute_value_to_sql_fields(obj)

                # Get attribute type name
                attr_type_name = AttributeType._VALUES_TO_NAMES[obj.attribute_type]

                # Insert attribute with parameterized query
                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.attributes_table} "
                        f"(internal_name, visible, attribute_type, bool_value, double_value, "
                        f"vector3_x, vector3_y, vector3_z, asset_id) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
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
                        f"INSERT INTO {self.database}.{self.attributes_table} "
                        f"(id, internal_name, visible, attribute_type, bool_value, double_value, "
                        f"vector3_x, vector3_y, vector3_z, asset_id) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
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
                        f"INSERT INTO {self.database}.{self.attribute_owners_table} "
                        f"(attribute_id, mobile_id, item_id, asset_id, player_id) "
                        f"VALUES (%s, %s, %s, %s, %s);",
                        (
                            obj.id,
                            mobile_id,
                            item_id,
                            asset_id,
                            player_id,
                        ),
                    )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created Attribute id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to create Attribute to database={self.database}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def load(
        self,
        obj_id: int,
    ) -> Tuple[GameResult, Optional[Attribute]]:
        """Load an Attribute from the database by ID."""
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Load the attribute
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.attributes_table} WHERE id = %s;",
                (obj_id,),
            )
            attr_row = cursor.fetchone()

            if not attr_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Attribute id={obj_id} not found in database={self.database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

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

            # Load owner
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.attribute_owners_table} WHERE attribute_id = %s;",
                (obj_id,),
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
                    message=f"Successfully loaded Attribute id={obj_id}",
                ),
                attribute,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Attribute id={obj_id} from database={self.database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def update(
        self,
        obj: Attribute,
    ) -> list[GameResult]:
        """Update an existing Attribute in the database."""
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Attribute with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            with self.transaction() as cursor:
                # Convert attribute value to SQL fields
                value_fields = attribute_value_to_sql_fields(obj)

                # Get attribute type name
                attr_type_name = AttributeType._VALUES_TO_NAMES[obj.attribute_type]

                # Update attribute
                cursor.execute(
                    f"UPDATE {self.database}.{self.attributes_table} SET "
                    f"internal_name = %s, "
                    f"visible = %s, "
                    f"attribute_type = %s, "
                    f"bool_value = %s, "
                    f"double_value = %s, "
                    f"vector3_x = %s, "
                    f"vector3_y = %s, "
                    f"vector3_z = %s, "
                    f"asset_id = %s "
                    f"WHERE id = %s;",
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
                        obj.id,
                    ),
                )

                # Update owner (delete and re-insert)
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.attribute_owners_table} WHERE attribute_id = %s;",
                    (obj.id,),
                )

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
                        f"INSERT INTO {self.database}.{self.attribute_owners_table} "
                        f"(attribute_id, mobile_id, item_id, asset_id, player_id) "
                        f"VALUES (%s, %s, %s, %s, %s);",
                        (
                            obj.id,
                            mobile_id,
                            item_id,
                            asset_id,
                            player_id,
                        ),
                    )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated Attribute id={obj.id}, internal_name={obj.internal_name}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Attribute id={obj.id} in database={self.database}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def destroy(
        self,
        obj_id: int,
    ) -> list[GameResult]:
        """Delete an Attribute from the database by ID."""
        try:
            with self.transaction() as cursor:
                # Delete attribute owner first (foreign key)
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.attribute_owners_table} WHERE attribute_id = %s;",
                    (obj_id,),
                )

                # Delete the attribute
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.attributes_table} WHERE id = %s;",
                    (obj_id,),
                )

                # Check if any rows were affected
                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Attribute id={obj_id} not found in database={self.database}",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Attribute id={obj_id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Attribute id={obj_id} in database={self.database}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    def search(
        self,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[Attribute]], int]:
        """
        Search for Attributes with pagination and optional search.

        Args:
            page: Page number (0-indexed)
            results_per_page: Number of results per page
            search_string: Optional search string (searches internal_name)

        Returns:
            Tuple of (GameResult, list of Attribute objects, total count)
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
            count_query = f"SELECT COUNT(*) as total FROM {self.database}.{self.attributes_table} {where_clause};"
            cursor.execute(count_query, tuple(params))
            count_row = cursor.fetchone()
            total_count = count_row["total"] if count_row else 0

            # Get paginated results
            query = f"SELECT * FROM {self.database}.{self.attributes_table} {where_clause} ORDER BY id LIMIT %s OFFSET %s;"
            cursor.execute(query, tuple(params + [results_per_page, offset]))
            attr_rows = cursor.fetchall()

            # Convert rows to Attribute objects
            attributes = []
            for row in attr_rows:
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

                # Load owner for this attribute
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
                attributes.append(attribute)

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully listed {len(attributes)} attributes (total: {total_count})",
                ),
                attributes,
                total_count,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to search attributes from database={self.database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
        finally:
            if cursor:
                cursor.close()
