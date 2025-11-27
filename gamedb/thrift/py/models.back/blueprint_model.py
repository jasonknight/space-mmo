"""ItemBlueprint database model."""

import sys
from typing import Optional, Tuple

sys.path.append("../../gen-py")
sys.path.append("../")

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    ItemBlueprint,
    ItemBlueprintComponent,
)
from base_model import BaseModel


class BlueprintModel(BaseModel):
    """Model for ItemBlueprint database operations."""

    # Table constants - single source of truth for table names
    BLUEPRINT_TABLE = "item_blueprints"
    COMPONENTS_TABLE = "item_blueprint_components"

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        blueprint_table: Optional[str] = None,
        components_table: Optional[str] = None,
    ):
        super().__init__(host, user, password, database)
        # Allow table override for mobile blueprints, etc.
        self.blueprint_table = (
            blueprint_table if blueprint_table else self.BLUEPRINT_TABLE
        )
        self.components_table = (
            components_table if components_table else self.COMPONENTS_TABLE
        )

    def create(
        self,
        obj: ItemBlueprint,
    ) -> list[GameResult]:
        """Create a new ItemBlueprint in the database."""
        try:
            with self.transaction() as cursor:
                # Insert the blueprint
                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.blueprint_table} (bake_time_ms) "
                        f"VALUES (%s);",
                        (obj.bake_time_ms,),
                    )
                    obj.id = cursor.lastrowid
                else:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.blueprint_table} (id, bake_time_ms) "
                        f"VALUES (%s, %s);",
                        (
                            obj.id,
                            obj.bake_time_ms,
                        ),
                    )

                # Insert components
                if obj.components:
                    for item_id, component in obj.components.items():
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.components_table} "
                            f"(item_blueprint_id, component_item_id, ratio) "
                            f"VALUES (%s, %s, %s);",
                            (
                                obj.id,
                                component.item_id,
                                component.ratio,
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created ItemBlueprint id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to create ItemBlueprint to database={self.database}: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def load(
        self,
        obj_id: int,
    ) -> Tuple[GameResult, Optional[ItemBlueprint]]:
        """Load an ItemBlueprint from the database by ID."""
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Load the blueprint
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.blueprint_table} WHERE id = %s;",
                (obj_id,),
            )
            blueprint_row = cursor.fetchone()

            if not blueprint_row:
                cursor.close()
                return (
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"ItemBlueprint id={obj_id} not found in database={self.database}",
                        error_code=GameError.DB_RECORD_NOT_FOUND,
                    ),
                    None,
                )

            # Load components
            cursor.execute(
                f"SELECT * FROM {self.database}.{self.components_table} WHERE item_blueprint_id = %s;",
                (obj_id,),
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
                    message=f"Successfully loaded ItemBlueprint id={obj_id}",
                ),
                blueprint,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load ItemBlueprint id={obj_id} from database={self.database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )
        finally:
            if cursor:
                cursor.close()

    def update(
        self,
        obj: ItemBlueprint,
    ) -> list[GameResult]:
        """Update an existing ItemBlueprint in the database."""
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update ItemBlueprint with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            with self.transaction() as cursor:
                # Update blueprint
                cursor.execute(
                    f"UPDATE {self.database}.{self.blueprint_table} SET "
                    f"bake_time_ms = %s "
                    f"WHERE id = %s;",
                    (
                        obj.bake_time_ms,
                        obj.id,
                    ),
                )

                # Delete existing components
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.components_table} WHERE item_blueprint_id = %s;",
                    (obj.id,),
                )

                # Insert new components
                if obj.components:
                    for item_id, component in obj.components.items():
                        cursor.execute(
                            f"INSERT INTO {self.database}.{self.components_table} "
                            f"(item_blueprint_id, component_item_id, ratio) "
                            f"VALUES (%s, %s, %s);",
                            (
                                obj.id,
                                component.item_id,
                                component.ratio,
                            ),
                        )

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated ItemBlueprint id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update ItemBlueprint id={obj.id} in database={self.database}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def destroy(
        self,
        obj_id: int,
    ) -> list[GameResult]:
        """Delete an ItemBlueprint from the database by ID."""
        try:
            with self.transaction() as cursor:
                # Delete components first (foreign key)
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.components_table} WHERE item_blueprint_id = %s;",
                    (obj_id,),
                )

                # Delete the blueprint
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.blueprint_table} WHERE id = %s;",
                    (obj_id,),
                )

                # Check if any rows were affected
                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"ItemBlueprint id={obj_id} not found in database={self.database}",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed ItemBlueprint id={obj_id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy ItemBlueprint id={obj_id} in database={self.database}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    def search(
        self,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[ItemBlueprint]], int]:
        """
        Search for ItemBlueprints with pagination.
        Note: ItemBlueprint doesn't have searchable text fields, so search_string is ignored.

        Returns:
            Tuple of (GameResult, list of ItemBlueprint objects, total count)
        """
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)

            # Calculate offset (page is 0-indexed)
            page = max(0, page)
            offset = page * results_per_page

            # Get total count
            count_query = (
                f"SELECT COUNT(*) as total FROM {self.database}.{self.blueprint_table};"
            )
            cursor.execute(count_query)
            count_row = cursor.fetchone()
            total_count = count_row["total"] if count_row else 0

            # Get paginated results
            query = f"SELECT * FROM {self.database}.{self.blueprint_table} ORDER BY id LIMIT %s OFFSET %s;"
            cursor.execute(
                query,
                (
                    results_per_page,
                    offset,
                ),
            )
            blueprint_rows = cursor.fetchall()

            # Convert rows to ItemBlueprint objects
            blueprints = []
            for row in blueprint_rows:
                # Load components for this blueprint
                cursor.execute(
                    f"SELECT * FROM {self.database}.{self.components_table} WHERE item_blueprint_id = %s;",
                    (row["id"],),
                )
                component_rows = cursor.fetchall()

                # Build components map
                components = {}
                for comp_row in component_rows:
                    component = ItemBlueprintComponent(
                        ratio=comp_row["ratio"],
                        item_id=comp_row["component_item_id"],
                    )
                    components[comp_row["component_item_id"]] = component

                # Create ItemBlueprint object
                blueprint = ItemBlueprint(
                    id=row["id"],
                    components=components,
                    bake_time_ms=row["bake_time_ms"],
                )
                blueprints.append(blueprint)

            cursor.close()

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully listed {len(blueprints)} blueprints (total: {total_count})",
                ),
                blueprints,
                total_count,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to search blueprints from database={self.database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
        finally:
            if cursor:
                cursor.close()
