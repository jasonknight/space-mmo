"""Player database model."""

import sys
from typing import Optional, Tuple
from datetime import datetime

sys.path.append("../../gen-py")
sys.path.append("../")

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    Player,
    Mobile,
    MobileType,
    Owner,
)
from base_model import BaseModel
from models.mobile_model import MobileModel
from common import is_ok, is_true


class PlayerModel(BaseModel):
    """Model for Player database operations."""

    # Table constants - single source of truth for table names
    PLAYERS_TABLE = "players"

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        players_table: Optional[str] = None,
    ):
        super().__init__(host, user, password, database)
        # Allow table override
        self.players_table = players_table if players_table else self.PLAYERS_TABLE

    def _get_mobile_model(self) -> MobileModel:
        """Get a MobileModel instance for mobile operations."""
        return MobileModel(
            self.host,
            self.user,
            self.password,
            self.database,
        )

    def create(
        self,
        obj: Player,
    ) -> list[GameResult]:
        """Create a new Player in the database."""
        try:
            # Automatically set over_13 based on birth year
            current_year = datetime.now().year
            obj.over_13 = (current_year - obj.year_of_birth) >= 13

            with self.transaction() as cursor:
                # Insert the player
                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.players_table} "
                        f"(full_name, what_we_call_you, security_token, over_13, year_of_birth, email) "
                        f"VALUES (%s, %s, %s, %s, %s, %s);",
                        (
                            obj.full_name,
                            obj.what_we_call_you,
                            obj.security_token,
                            obj.over_13,
                            obj.year_of_birth,
                            obj.email,
                        ),
                    )
                    obj.id = cursor.lastrowid
                else:
                    cursor.execute(
                        f"INSERT INTO {self.database}.{self.players_table} "
                        f"(id, full_name, what_we_call_you, security_token, over_13, year_of_birth, email) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s);",
                        (
                            obj.id,
                            obj.full_name,
                            obj.what_we_call_you,
                            obj.security_token,
                            obj.over_13,
                            obj.year_of_birth,
                            obj.email,
                        ),
                    )

            # Create the associated mobile for this player (in separate transaction)
            mobile_owner = Owner(player_id=obj.id)

            # If the player already has a mobile defined, use it
            # Otherwise create a new empty one
            if hasattr(obj, "mobile") and obj.mobile is not None:
                mobile = obj.mobile
                mobile.owner = mobile_owner
                if mobile.id is None:
                    mobile.id = None  # Ensure it gets a new ID
            else:
                mobile = Mobile(
                    id=None,
                    mobile_type=MobileType.PLAYER,
                    attributes={},
                    owner=mobile_owner,
                    what_we_call_you=obj.what_we_call_you,
                )

            # Create the mobile using mobile model
            mobile_model = self._get_mobile_model()
            mobile_results = mobile_model.save(mobile)
            if not is_ok(mobile_results):
                # If mobile creation fails, we need to roll back the player too
                # But the player transaction already committed, so we delete it
                self.destroy(obj.id)
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to create mobile for player: {mobile_results[0].message}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully created Player id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to create Player: {str(e)}",
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def load(
        self,
        obj_id: int,
    ) -> Tuple[GameResult, Optional[Player]]:
        """Load a Player from the database by ID."""
        try:
            with self.transaction_dict() as cursor:
                # Load the player
                cursor.execute(
                    f"SELECT * FROM {self.database}.{self.players_table} WHERE id = %s;",
                    (obj_id,),
                )
                player_row = cursor.fetchone()

                if not player_row:
                    return (
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Player id={obj_id} not found in database={self.database}",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                        None,
                    )

                # Create Player object
                player = Player(
                    id=player_row["id"],
                    full_name=player_row["full_name"],
                    what_we_call_you=player_row["what_we_call_you"],
                    security_token=player_row["security_token"],
                    over_13=player_row["over_13"],
                    year_of_birth=player_row["year_of_birth"],
                    email=player_row["email"],
                )

                # Load the associated mobile if it exists
                cursor.execute(
                    f"SELECT id FROM {self.database}.mobiles WHERE owner_player_id = %s;",
                    (obj_id,),
                )
                mobile_row = cursor.fetchone()

                if mobile_row:
                    mobile_id = mobile_row["id"]
                    mobile_model = self._get_mobile_model()
                    mobile_result, mobile = mobile_model.load(mobile_id)
                    if is_true(mobile_result):
                        player.mobile = mobile

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded Player id={obj_id}",
                ),
                player,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to load Player id={obj_id}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )

    def update(
        self,
        obj: Player,
    ) -> list[GameResult]:
        """Update an existing Player in the database."""
        try:
            if obj.id is None:
                return [
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Cannot update Player with id=None",
                        error_code=GameError.DB_INVALID_DATA,
                    ),
                ]

            # Automatically set over_13 based on birth year
            current_year = datetime.now().year
            obj.over_13 = (current_year - obj.year_of_birth) >= 13

            with self.transaction() as cursor:
                # Update player
                cursor.execute(
                    f"UPDATE {self.database}.{self.players_table} SET "
                    f"full_name = %s, "
                    f"what_we_call_you = %s, "
                    f"security_token = %s, "
                    f"over_13 = %s, "
                    f"year_of_birth = %s, "
                    f"email = %s "
                    f"WHERE id = %s;",
                    (
                        obj.full_name,
                        obj.what_we_call_you,
                        obj.security_token,
                        obj.over_13,
                        obj.year_of_birth,
                        obj.email,
                        obj.id,
                    ),
                )

            # If mobile is present, save it
            if hasattr(obj, "mobile") and obj.mobile is not None:
                mobile_model = self._get_mobile_model()
                mobile_results = mobile_model.save(obj.mobile)
                if not is_ok(mobile_results):
                    return mobile_results

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully updated Player id={obj.id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to update Player id={obj.id}: {str(e)}",
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def destroy(
        self,
        obj_id: int,
    ) -> list[GameResult]:
        """Delete a Player from the database by ID."""
        try:
            with self.transaction() as cursor:
                # First, find and delete the associated mobile
                cursor.execute(
                    f"SELECT id FROM {self.database}.mobiles WHERE owner_player_id = %s;",
                    (obj_id,),
                )
                mobile_row = cursor.fetchone()

                if mobile_row:
                    mobile_id = mobile_row[0]

                    # Get attribute IDs for this mobile
                    cursor.execute(
                        f"SELECT attribute_id FROM {self.database}.attribute_owners WHERE mobile_id = %s;",
                        (mobile_id,),
                    )
                    attr_ids = [row[0] for row in cursor.fetchall()]

                    # Delete attribute owners
                    cursor.execute(
                        f"DELETE FROM {self.database}.attribute_owners WHERE mobile_id = %s;",
                        (mobile_id,),
                    )

                    # Delete attributes
                    if attr_ids:
                        placeholders = ",".join(["%s"] * len(attr_ids))
                        cursor.execute(
                            f"DELETE FROM {self.database}.attributes WHERE id IN ({placeholders});",
                            tuple(attr_ids),
                        )

                    # Delete the mobile
                    cursor.execute(
                        f"DELETE FROM {self.database}.mobiles WHERE id = %s;",
                        (mobile_id,),
                    )

                # Now delete the player
                cursor.execute(
                    f"DELETE FROM {self.database}.{self.players_table} WHERE id = %s;",
                    (obj_id,),
                )

                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Player id={obj_id} not found in database={self.database}",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully destroyed Player id={obj_id}",
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to destroy Player id={obj_id}: {str(e)}",
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    def search(
        self,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[Player]], int]:
        """
        Search for Players with pagination and optional search.

        Args:
            page: Page number (0-indexed)
            results_per_page: Number of results per page
            search_string: Optional search string (searches full_name, what_we_call_you, and email)

        Returns:
            Tuple of (GameResult, list of Player objects, total count)
        """
        try:
            with self.transaction_dict() as cursor:
                # Calculate offset
                page = max(0, page)
                offset = page * results_per_page

                # Build WHERE clause for search
                where_clause = ""
                params = []
                if search_string:
                    where_clause = "WHERE (full_name LIKE %s OR what_we_call_you LIKE %s OR email LIKE %s)"
                    search_pattern = f"%{search_string}%"
                    params = [
                        search_pattern,
                        search_pattern,
                        search_pattern,
                    ]

                # Get total count
                count_query = f"SELECT COUNT(*) as total FROM {self.database}.{self.players_table} {where_clause};"
                cursor.execute(count_query, tuple(params))
                count_row = cursor.fetchone()
                total_count = count_row["total"] if count_row else 0

                # Get paginated results
                query = f"SELECT * FROM {self.database}.{self.players_table} {where_clause} ORDER BY id LIMIT %s OFFSET %s;"
                cursor.execute(query, tuple(params + [results_per_page, offset]))
                player_rows = cursor.fetchall()

                # Convert rows to Player objects
                players = []
                player_ids = []
                for row in player_rows:
                    player = Player(
                        id=row["id"],
                        full_name=row["full_name"],
                        what_we_call_you=row["what_we_call_you"],
                        security_token=row["security_token"],
                        over_13=row["over_13"],
                        year_of_birth=row["year_of_birth"],
                        email=row["email"],
                    )
                    players.append(player)
                    player_ids.append(row["id"])

                # Load mobiles for all players in one query
                if player_ids:
                    placeholders = ",".join(["%s"] * len(player_ids))
                    mobile_query = f"""
                        SELECT id, what_we_call_you, owner_player_id 
                        FROM {self.database}.mobiles 
                        WHERE owner_player_id IN ({placeholders});
                    """
                    cursor.execute(mobile_query, tuple(player_ids))
                    mobile_rows = cursor.fetchall()

                    # Create a map of player_id -> mobile data
                    mobile_map = {}
                    for mobile_row in mobile_rows:
                        mobile = Mobile(
                            id=mobile_row["id"],
                            what_we_call_you=mobile_row["what_we_call_you"],
                            mobile_type=MobileType.PLAYER,
                            attributes={},
                        )

                        mobile_owner = Owner(player_id=mobile_row["owner_player_id"])
                        mobile.owner = mobile_owner

                        mobile_map[mobile_row["owner_player_id"]] = mobile

                    # Attach mobiles to players
                    for player in players:
                        if player.id in mobile_map:
                            player.mobile = mobile_map[player.id]

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully listed {len(players)} players (total: {total_count})",
                ),
                players,
                total_count,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=f"Failed to search players: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
