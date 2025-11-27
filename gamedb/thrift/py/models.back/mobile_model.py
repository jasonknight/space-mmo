"""Mobile database model."""

import sys
from typing import Optional, Tuple

sys.path.append("../../gen-py")
sys.path.append("../")

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    ItemVector3,
    Mobile,
    MobileType,
    Attribute,
    AttributeType,
    Owner,
)
from base_model import BaseModel
from common import is_ok


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


class MobileModel(BaseModel):
    """Model for Mobile database operations."""

    # Table constants - single source of truth for table names
    MOBILE_TABLE = "mobiles"
    ATTRIBUTES_TABLE = "attributes"
    ATTRIBUTE_OWNERS_TABLE = "attribute_owners"

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        mobile_table: Optional[str] = None,
        attributes_table: Optional[str] = None,
        attribute_owners_table: Optional[str] = None,
    ):
        super().__init__(host, user, password, database)
        # Allow table override
        self.mobile_table = mobile_table if mobile_table else self.MOBILE_TABLE
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
        obj: Mobile,
    ) -> list[GameResult]:
        """Create a new Mobile in the database."""
        try:
            with self.transaction() as cursor:
                # Get mobile type name
                mobile_type_name = MobileType._VALUES_TO_NAMES[obj.mobile_type]

                # Extract owner information
                owner_mobile_id = None
                owner_item_id = None
                owner_asset_id = None
                owner_player_id = None

                if obj.owner is not None:
                    if isinstance(obj.owner, Owner):
                        if (
                            hasattr(obj.owner, "mobile_id")
                            and obj.owner.mobile_id is not None
                        ):
                            owner_mobile_id = obj.owner.mobile_id
                        elif (
                            hasattr(obj.owner, "item_id")
                            and obj.owner.item_id is not None
                        ):
                            owner_item_id = obj.owner.item_id
                        elif (
                            hasattr(obj.owner, "asset_id")
                            and obj.owner.asset_id is not None
                        ):
                            owner_asset_id = obj.owner.asset_id
                        elif (
                            hasattr(obj.owner, "player_id")
                            and obj.owner.player_id is not None
                        ):
                            owner_player_id = obj.owner.player_id
                    elif isinstance(obj.owner, int):
                        owner_mobile_id = obj.owner

                what_we_call_you = (
                    obj.what_we_call_you
                    if hasattr(obj, "what_we_call_you") and obj.what_we_call_you
                    else ""
                )

                # Insert the mobile
                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.mobile_table} "
                        f"(mobile_type, owner_mobile_id, owner_item_id, owner_asset_id, owner_player_id, what_we_call_you) "
                        f"VALUES (%s, %s, %s, %s, %s, %s);",
                        (
                            mobile_type_name,
                            owner_mobile_id,
                            owner_item_id,
                            owner_asset_id,
                            owner_player_id,
                            what_we_call_you,
                        ),
                    )
                    obj.id = cursor.lastrowid
                else:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.mobile_table} "
                        f"(id, mobile_type, owner_mobile_id, owner_item_id, owner_asset_id, owner_player_id, what_we_call_you) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s);",
                        (
                            obj.id,
                            mobile_type_name,
                            owner_mobile_id,
                            owner_item_id,
                            owner_asset_id,
                            owner_player_id,
                            what_we_call_you,
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
                            f"(attribute_id, mobile_id) "
                            f"VALUES (%s, %s);",
                            (
                                attr_id,
                                obj.id,
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created Mobile id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to create Mobile id={obj.id}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def load(
        self,
        obj_id: int,
    ) -> Tuple[GameResult, Optional[Mobile]]:
        """Load a Mobile from the database by ID."""
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Load the mobile
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.mobile_table} WHERE id = %s;",
                (obj_id,),
            )
            mobile_row = cursor.fetchone()

            if not mobile_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Mobile id={obj_id} not found in database={self.database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load attributes through attribute_owners
            cursor.execute(
                f"SELECT a.* FROM {self.database}.{self.attributes_table} a "
                f"INNER JOIN {self.database}.{self.attribute_owners_table} ao ON a.id = ao.attribute_id "
                f"WHERE ao.mobile_id = %s;",
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

            # Get mobile type
            mobile_type = MobileType._NAMES_TO_VALUES[mobile_row["mobile_type"]]

            # Reconstruct owner for the mobile
            mobile_owner = None
            if mobile_row["owner_mobile_id"]:
                mobile_owner = Owner(mobile_id=mobile_row["owner_mobile_id"])
            elif mobile_row["owner_item_id"]:
                mobile_owner = Owner(item_id=mobile_row["owner_item_id"])
            elif mobile_row["owner_asset_id"]:
                mobile_owner = Owner(asset_id=mobile_row["owner_asset_id"])
            elif mobile_row["owner_player_id"]:
                mobile_owner = Owner(player_id=mobile_row["owner_player_id"])

            # Create Mobile object
            what_we_call_you = mobile_row.get("what_we_call_you", "")
            mobile = Mobile(
                id=mobile_row["id"],
                mobile_type=mobile_type,
                attributes=attributes,
                owner=mobile_owner,
                what_we_call_you=what_we_call_you,
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded Mobile id={obj_id}",
                ),
                mobile,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Mobile id={obj_id}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def update(
        self,
        obj: Mobile,
    ) -> list[GameResult]:
        """Update an existing Mobile in the database."""
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Mobile with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            with self.transaction() as cursor:
                # Get mobile type name
                mobile_type_name = MobileType._VALUES_TO_NAMES[obj.mobile_type]

                # Extract owner information
                owner_mobile_id = None
                owner_item_id = None
                owner_asset_id = None
                owner_player_id = None

                if obj.owner is not None:
                    if isinstance(obj.owner, Owner):
                        if (
                            hasattr(obj.owner, "mobile_id")
                            and obj.owner.mobile_id is not None
                        ):
                            owner_mobile_id = obj.owner.mobile_id
                        elif (
                            hasattr(obj.owner, "item_id")
                            and obj.owner.item_id is not None
                        ):
                            owner_item_id = obj.owner.item_id
                        elif (
                            hasattr(obj.owner, "asset_id")
                            and obj.owner.asset_id is not None
                        ):
                            owner_asset_id = obj.owner.asset_id
                        elif (
                            hasattr(obj.owner, "player_id")
                            and obj.owner.player_id is not None
                        ):
                            owner_player_id = obj.owner.player_id
                    elif isinstance(obj.owner, int):
                        owner_mobile_id = obj.owner

                what_we_call_you = (
                    obj.what_we_call_you
                    if hasattr(obj, "what_we_call_you") and obj.what_we_call_you
                    else ""
                )

                # Update mobile
                cursor.execute(
                    f"UPDATE {self.database}.{self.mobile_table} SET "
                    f"mobile_type = %s, "
                    f"owner_mobile_id = %s, "
                    f"owner_item_id = %s, "
                    f"owner_asset_id = %s, "
                    f"owner_player_id = %s, "
                    f"what_we_call_you = %s "
                    f"WHERE id = %s;",
                    (
                        mobile_type_name,
                        owner_mobile_id,
                        owner_item_id,
                        owner_asset_id,
                        owner_player_id,
                        what_we_call_you,
                        obj.id,
                    ),
                )

                # Delete existing attributes
                # First get the attribute IDs
                cursor.execute(
                    f"SELECT attribute_id FROM {self.database}.{self.attribute_owners_table} WHERE mobile_id = %s;",
                    (obj.id,),
                )
                attr_ids = [row[0] for row in cursor.fetchall()]

                # Delete from attribute_owners
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.attribute_owners_table} WHERE mobile_id = %s;",
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
                            f"(attribute_id, mobile_id) "
                            f"VALUES (%s, %s);",
                            (
                                attr_id,
                                obj.id,
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated Mobile id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Mobile id={obj.id}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def destroy(
        self,
        obj_id: int,
    ) -> list[GameResult]:
        """Delete a Mobile from the database by ID."""
        try:
            with self.transaction() as cursor:
                # Get attribute IDs first
                cursor.execute(
                    f"SELECT attribute_id FROM {self.database}.{self.attribute_owners_table} WHERE mobile_id = %s;",
                    (obj_id,),
                )
                attr_ids = [row[0] for row in cursor.fetchall()]

                # Delete attribute owners
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.attribute_owners_table} WHERE mobile_id = %s;",
                    (obj_id,),
                )

                # Delete attributes
                if attr_ids:
                    placeholders = ",".join(["%s"] * len(attr_ids))
                    cursor.execute(
                        f"DELETE FROM {self.database}.{self.attributes_table} WHERE id IN ({placeholders});",
                        tuple(attr_ids),
                    )

                # Delete the mobile
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.mobile_table} WHERE id = %s;",
                    (obj_id,),
                )

                # Check if any rows were affected
                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Mobile id={obj_id} not found in database={self.database}",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Mobile id={obj_id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Mobile id={obj_id}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    def search(
        self,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[Mobile]], int]:
        """
        Search for Mobiles with pagination and optional search.

        Args:
            page: Page number (0-indexed)
            results_per_page: Number of results per page
            search_string: Optional search string (searches what_we_call_you)

        Returns:
            Tuple of (GameResult, list of Mobile objects, total count)
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
                where_clause = "WHERE what_we_call_you LIKE %s"
                search_pattern = f"%{search_string}%"
                params = [search_pattern]

            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM {self.database}.{self.mobile_table} {where_clause};"
            cursor.execute(count_query, tuple(params))
            count_row = cursor.fetchone()
            total_count = count_row["total"] if count_row else 0

            # Get paginated results
            query = f"SELECT * FROM {self.database}.{self.mobile_table} {where_clause} ORDER BY id LIMIT %s OFFSET %s;"
            cursor.execute(query, tuple(params + [results_per_page, offset]))
            mobile_rows = cursor.fetchall()

            # Convert rows to Mobile objects
            mobiles = []
            for row in mobile_rows:
                # Load attributes through attribute_owners
                cursor.execute(
                    f"SELECT a.* FROM {self.database}.{self.attributes_table} a "
                    f"INNER JOIN {self.database}.{self.attribute_owners_table} ao ON a.id = ao.attribute_id "
                    f"WHERE ao.mobile_id = %s;",
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

                # Get mobile type
                mobile_type = MobileType._NAMES_TO_VALUES[row["mobile_type"]]

                # Reconstruct owner for the mobile
                mobile_owner = None
                if row["owner_mobile_id"]:
                    mobile_owner = Owner(mobile_id=row["owner_mobile_id"])
                elif row["owner_item_id"]:
                    mobile_owner = Owner(item_id=row["owner_item_id"])
                elif row["owner_asset_id"]:
                    mobile_owner = Owner(asset_id=row["owner_asset_id"])
                elif row["owner_player_id"]:
                    mobile_owner = Owner(player_id=row["owner_player_id"])

                # Create Mobile object
                what_we_call_you = row.get("what_we_call_you", "")
                mobile = Mobile(
                    id=row["id"],
                    mobile_type=mobile_type,
                    attributes=attributes,
                    owner=mobile_owner,
                    what_we_call_you=what_we_call_you,
                )
                mobiles.append(mobile)

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully listed {len(mobiles)} mobiles (total: {total_count})",
                ),
                mobiles,
                total_count,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to search mobiles: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
        finally:
            if cursor:
                cursor.close()
