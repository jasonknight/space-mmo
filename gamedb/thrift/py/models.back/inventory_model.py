"""Inventory database model."""

import sys
from typing import Optional, Tuple

sys.path.append("../../gen-py")
sys.path.append("../")

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    Inventory,
    InventoryEntry,
    Owner,
)
from base_model import BaseModel


class InventoryModel(BaseModel):
    """Model for Inventory database operations."""

    # Table constants - single source of truth for table names
    INVENTORY_TABLE = "inventories"
    INVENTORY_ENTRIES_TABLE = "inventory_entries"
    INVENTORY_OWNERS_TABLE = "inventory_owners"

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        inventory_table: Optional[str] = None,
        inventory_entries_table: Optional[str] = None,
        inventory_owners_table: Optional[str] = None,
    ):
        super().__init__(host, user, password, database)
        # Allow table override
        self.inventory_table = (
            inventory_table if inventory_table else self.INVENTORY_TABLE
        )
        self.inventory_entries_table = (
            inventory_entries_table
            if inventory_entries_table
            else self.INVENTORY_ENTRIES_TABLE
        )
        self.inventory_owners_table = (
            inventory_owners_table
            if inventory_owners_table
            else self.INVENTORY_OWNERS_TABLE
        )

    def create(
        self,
        obj: Inventory,
    ) -> list[GameResult]:
        """Create a new Inventory in the database."""
        try:
            with self.transaction() as cursor:
                # Extract owner information
                mobile_id = None
                item_id = None
                asset_id = None
                player_id = None
                owner_type = None
                owner_id = None

                if obj.owner is not None:
                    if isinstance(obj.owner, Owner):
                        if (
                            hasattr(obj.owner, "mobile_id")
                            and obj.owner.mobile_id is not None
                        ):
                            mobile_id = obj.owner.mobile_id
                            owner_id = mobile_id
                            owner_type = "MOBILE"
                        elif (
                            hasattr(obj.owner, "item_id")
                            and obj.owner.item_id is not None
                        ):
                            item_id = obj.owner.item_id
                            owner_id = item_id
                            owner_type = "ITEM"
                        elif (
                            hasattr(obj.owner, "asset_id")
                            and obj.owner.asset_id is not None
                        ):
                            asset_id = obj.owner.asset_id
                            owner_id = asset_id
                            owner_type = "ASSET"
                        elif (
                            hasattr(obj.owner, "player_id")
                            and obj.owner.player_id is not None
                        ):
                            player_id = obj.owner.player_id
                            owner_id = player_id
                            owner_type = "PLAYER"
                    elif isinstance(obj.owner, int):
                        mobile_id = obj.owner
                        owner_id = mobile_id
                        owner_type = "MOBILE"

                # Insert inventory
                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.inventory_table} "
                        f"(owner_id, owner_type, max_entries, max_volume, last_calculated_volume) "
                        f"VALUES (%s, %s, %s, %s, %s);",
                        (
                            owner_id,
                            owner_type,
                            obj.max_entries,
                            obj.max_volume,
                            obj.last_calculated_volume,
                        ),
                    )
                    obj.id = cursor.lastrowid
                else:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.inventory_table} "
                        f"(id, owner_id, owner_type, max_entries, max_volume, last_calculated_volume) "
                        f"VALUES (%s, %s, %s, %s, %s, %s);",
                        (
                            obj.id,
                            owner_id,
                            owner_type,
                            obj.max_entries,
                            obj.max_volume,
                            obj.last_calculated_volume,
                        ),
                    )

                # Insert inventory entries
                if obj.entries:
                    for entry in obj.entries:
                        mobile_item_id_val = (
                            entry.mobile_item_id
                            if hasattr(entry, "mobile_item_id") and entry.mobile_item_id
                            else None
                        )
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.inventory_entries_table} "
                            f"(inventory_id, item_id, quantity, is_max_stacked, mobile_item_id) "
                            f"VALUES (%s, %s, %s, %s, %s);",
                            (
                                obj.id,
                                entry.item_id,
                                entry.quantity,
                                entry.is_max_stacked,
                                mobile_item_id_val,
                            ),
                        )

                # Insert inventory owner
                cursor.execute(
                    f"INSERT INTO {self.database}.{self.inventory_owners_table} "
                    f"(inventory_id, mobile_id, item_id, asset_id, player_id) "
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
                    message=f"Successfully created Inventory id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to create Inventory id={obj.id}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def load(
        self,
        obj_id: int,
    ) -> Tuple[GameResult, Optional[Inventory]]:
        """Load an Inventory from the database by ID."""
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Load the inventory
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.inventory_table} WHERE id = %s;",
                (obj_id,),
            )
            inv_row = cursor.fetchone()

            if not inv_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Inventory id={obj_id} not found in database={self.database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load inventory entries
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.inventory_entries_table} WHERE inventory_id = %s;",
                (obj_id,),
            )
            entry_rows = cursor.fetchall()

            # Build entries list
            entries = []
            for row in entry_rows:
                entry = InventoryEntry(
                    item_id=row["item_id"],
                    quantity=row["quantity"],
                    is_max_stacked=row["is_max_stacked"],
                    mobile_item_id=row.get("mobile_item_id"),
                )
                entries.append(entry)

            # Load owner
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.inventory_owners_table} WHERE inventory_id = %s;",
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

            # Create Inventory object
            inventory = Inventory(
                id=inv_row["id"],
                max_entries=inv_row["max_entries"],
                max_volume=inv_row["max_volume"],
                entries=entries,
                last_calculated_volume=inv_row["last_calculated_volume"],
                owner=owner,
            )

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded Inventory id={obj_id}",
                ),
                inventory,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Inventory id={obj_id}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def update(
        self,
        obj: Inventory,
    ) -> list[GameResult]:
        """Update an existing Inventory in the database."""
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Inventory with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            with self.transaction() as cursor:
                # Extract owner information
                mobile_id = None
                item_id = None
                asset_id = None
                player_id = None
                owner_type = None
                owner_id = None

                if obj.owner is not None:
                    if isinstance(obj.owner, Owner):
                        if (
                            hasattr(obj.owner, "mobile_id")
                            and obj.owner.mobile_id is not None
                        ):
                            mobile_id = obj.owner.mobile_id
                            owner_id = mobile_id
                            owner_type = "MOBILE"
                        elif (
                            hasattr(obj.owner, "item_id")
                            and obj.owner.item_id is not None
                        ):
                            item_id = obj.owner.item_id
                            owner_id = item_id
                            owner_type = "ITEM"
                        elif (
                            hasattr(obj.owner, "asset_id")
                            and obj.owner.asset_id is not None
                        ):
                            asset_id = obj.owner.asset_id
                            owner_id = asset_id
                            owner_type = "ASSET"
                        elif (
                            hasattr(obj.owner, "player_id")
                            and obj.owner.player_id is not None
                        ):
                            player_id = obj.owner.player_id
                            owner_id = player_id
                            owner_type = "PLAYER"
                    elif isinstance(obj.owner, int):
                        mobile_id = obj.owner
                        owner_id = mobile_id
                        owner_type = "MOBILE"

                # Update inventory
                cursor.execute(
                    f"UPDATE {self.database}.{self.inventory_table} SET "
                    f"owner_id = %s, "
                    f"owner_type = %s, "
                    f"max_entries = %s, "
                    f"max_volume = %s, "
                    f"last_calculated_volume = %s "
                    f"WHERE id = %s;",
                    (
                        owner_id,
                        owner_type,
                        obj.max_entries,
                        obj.max_volume,
                        obj.last_calculated_volume,
                        obj.id,
                    ),
                )

                # Delete existing entries
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.inventory_entries_table} WHERE inventory_id = %s;",
                    (obj.id,),
                )

                # Insert new entries
                if obj.entries:
                    for entry in obj.entries:
                        mobile_item_id_val = (
                            entry.mobile_item_id
                            if hasattr(entry, "mobile_item_id") and entry.mobile_item_id
                            else None
                        )
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.inventory_entries_table} "
                            f"(inventory_id, item_id, quantity, is_max_stacked, mobile_item_id) "
                            f"VALUES (%s, %s, %s, %s, %s);",
                            (
                                obj.id,
                                entry.item_id,
                                entry.quantity,
                                entry.is_max_stacked,
                                mobile_item_id_val,
                            ),
                        )

                # Update owner (delete and re-insert)
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.inventory_owners_table} WHERE inventory_id = %s;",
                    (obj.id,),
                )

                cursor.execute(
                    f"INSERT INTO {self.database}.{self.inventory_owners_table} "
                    f"(inventory_id, mobile_id, item_id, asset_id, player_id) "
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
                    message=f"Successfully updated Inventory id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Inventory id={obj.id}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def destroy(
        self,
        obj_id: int,
    ) -> list[GameResult]:
        """Delete an Inventory from the database by ID."""
        try:
            with self.transaction() as cursor:
                # Delete inventory entries first (foreign key)
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.inventory_entries_table} WHERE inventory_id = %s;",
                    (obj_id,),
                )

                # Delete inventory owner
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.inventory_owners_table} WHERE inventory_id = %s;",
                    (obj_id,),
                )

                # Delete the inventory
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.inventory_table} WHERE id = %s;",
                    (obj_id,),
                )

                # Check if any rows were affected
                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Inventory id={obj_id} not found in database={self.database}",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Inventory id={obj_id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Inventory id={obj_id}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    def search(
        self,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[Inventory]], int]:
        """
        Search for Inventories with pagination.
        Note: Inventory doesn't have searchable text fields, so search_string is ignored.

        Args:
            page: Page number (0-indexed)
            results_per_page: Number of results per page
            search_string: Optional search string (ignored for Inventory)

        Returns:
            Tuple of (GameResult, list of Inventory objects, total count)
        """
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Calculate offset
            page = max(0, page)
            offset = page * results_per_page

            # Get total count
            count_query = (
                f"SELECT COUNT(*) as total FROM {self.database}.{self.inventory_table};"
            )
            cursor.execute(count_query)
            count_row = cursor.fetchone()
            total_count = count_row["total"] if count_row else 0

            # Get paginated results
            query = f"SELECT * FROM {self.database}.{self.inventory_table} ORDER BY id LIMIT %s OFFSET %s;"
            cursor.execute(
                query,
                (
                    results_per_page,
                    offset,
                ),
            )
            inventory_rows = cursor.fetchall()

            # Convert rows to Inventory objects
            inventories = []
            for row in inventory_rows:
                # Load inventory entries
                cursor.execute(
                    f"SELECT * FROM {self.database}.{self.inventory_entries_table} WHERE inventory_id = %s;",
                    (row["id"],),
                )
                entry_rows = cursor.fetchall()

                entries = []
                for entry_row in entry_rows:
                    entry = InventoryEntry(
                        item_id=entry_row["item_id"],
                        quantity=entry_row["quantity"],
                        is_max_stacked=entry_row["is_max_stacked"],
                        mobile_item_id=entry_row.get("mobile_item_id"),
                    )
                    entries.append(entry)

                # Load owner information
                cursor.execute(
                    f"SELECT * FROM {self.database}.{self.inventory_owners_table} WHERE inventory_id = %s;",
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

                # Create Inventory object
                inventory = Inventory(
                    id=row["id"],
                    max_entries=row["max_entries"],
                    max_volume=row["max_volume"],
                    entries=entries,
                    last_calculated_volume=row["last_calculated_volume"],
                    owner=owner,
                )
                inventories.append(inventory)

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully listed {len(inventories)} inventories (total: {total_count})",
                ),
                inventories,
                total_count,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to search inventories: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
        finally:
            if cursor:
                cursor.close()
