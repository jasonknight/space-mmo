"""Mobile database operations."""
import sys
from typing import Optional, Tuple

sys.path.append('../gen-py')

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    ItemVector3,
    Attribute,
    Mobile,
)


class MobileMixin:
    """Mixin class for Mobile database operations."""

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
                elif hasattr(obj.owner, 'item_id') and obj.owner.item_id is not None:
                    owner_item_id = str(obj.owner.item_id)
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
                    elif hasattr(obj.owner, 'item_id') and obj.owner.item_id is not None:
                        owner_item_id = str(obj.owner.item_id)
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
                owner.item_id = mobile_row['owner_item_id']
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
