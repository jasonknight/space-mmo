"""Player database operations."""

import sys
from typing import Optional, Tuple
from datetime import datetime
import logging

sys.path.append("../../gen-py")

from game.ttypes import (
    GameResult,
    StatusType,
    GameError,
    Player,
    Mobile,
    MobileType,
    Owner,
)
logger = logging.getLogger(__name__)
# Table names
TABLE_PLAYERS = "players"

# Error message templates
MSG_CREATED = "Successfully created {type} id={id}"
MSG_UPDATED = "Successfully updated {type} id={id}"
MSG_DESTROYED = "Successfully destroyed {type} id={id}"
MSG_LOADED = "Successfully loaded {type} id={id}"
MSG_CREATE_FAILED = "Failed to create {type} in database={database}: {error}"
MSG_UPDATE_FAILED = "Failed to update {type} id={id} in database={database}: {error}"
MSG_DESTROY_FAILED = "Failed to destroy {type} id={id} in database={database}: {error}"
MSG_LOAD_FAILED = "Failed to load {type} id={id} from database={database}: {error}"
MSG_NOT_FOUND = "{type} id={id} not found in database={database}"


class PlayerMixin:
    """Mixin class for Player database operations."""

    def get_players_table_sql(
        self,
        database: str,
    ) -> list[str]:
        return [
            f"CREATE DATABASE IF NOT EXISTS {database};",
            f"""CREATE TABLE IF NOT EXISTS {database}.players (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                what_we_call_you VARCHAR(255) NOT NULL,
                security_token VARCHAR(255) NOT NULL,
                over_13 BOOLEAN NOT NULL,
                year_of_birth BIGINT NOT NULL,
                email VARCHAR(255) NOT NULL
            );""",
        ]

    def create_player(
        self,
        database: str,
        obj: Player,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            # Automatically set over_13 based on birth year
            current_year = datetime.now().year
            obj.over_13 = (current_year - obj.year_of_birth) >= 13

            with self.transaction() as cursor:
                players_table = table if table else TABLE_PLAYERS

                if obj.id is None:
                    cursor.execute(
                        f"INSERT INTO {database}.{players_table} "
                        f"(full_name, what_we_call_you, security_token, over_13, year_of_birth, email) "
                        f"VALUES (%s, %s, %s, %s, %s, %s)",
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
                        f"INSERT INTO {database}.{players_table} "
                        f"(id, full_name, what_we_call_you, security_token, over_13, year_of_birth, email) "
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s)",
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

                # Create the associated mobile for this player
                from game.ttypes import Mobile, MobileType, Owner

                mobile_owner = Owner()
                mobile_owner.player_id = obj.id

                mobile = Mobile(
                    id=None,
                    mobile_type=MobileType.PLAYER,
                    attributes={},
                    owner=mobile_owner,
                )

                # Get SQL for mobile creation
                mobile_statements = self.get_mobile_sql(
                    database,
                    mobile,
                )

                # Execute mobile creation statements
                for stmt in mobile_statements:
                    cursor.execute(stmt)

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_CREATED.format(type="Player", id=obj.id),
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_CREATE_FAILED.format(
                        type="Player", database=database, error=str(e)
                    ),
                    error_code=GameError.DB_INSERT_FAILED,
                ),
            ]

    def update_player(
        self,
        database: str,
        obj: Player,
        table: Optional[str] = None,
    ) -> list[GameResult]:
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
                players_table = table if table else TABLE_PLAYERS

                cursor.execute(
                    f"UPDATE {database}.{players_table} SET "
                    f"full_name = %s, "
                    f"what_we_call_you = %s, "
                    f"security_token = %s, "
                    f"over_13 = %s, "
                    f"year_of_birth = %s, "
                    f"email = %s "
                    f"WHERE id = %s",
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
                    mobile_results = self.save_mobile(database, obj.mobile)
                    from common import is_ok

                    if not is_ok(mobile_results):
                        return mobile_results

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_UPDATED.format(type="Player", id=obj.id),
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_UPDATE_FAILED.format(
                        type="Player", id=obj.id, database=database, error=str(e)
                    ),
                    error_code=GameError.DB_UPDATE_FAILED,
                ),
            ]

    def load_player(
        self,
        database: str,
        player_id: int,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[Player]]:
        try:
            with self.transaction_dict() as cursor:
                players_table = table if table else TABLE_PLAYERS

                cursor.execute(
                    f"SELECT * FROM {database}.{players_table} WHERE id = %s;",
                    (player_id,),
                )
                player_row = cursor.fetchone()

                if not player_row:
                    return (
                        GameResult(
                            status=StatusType.FAILURE,
                            message=MSG_NOT_FOUND.format(
                                type="Player", id=player_id, database=database
                            ),
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                        None,
                    )

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
                    f"SELECT id FROM {database}.mobiles WHERE owner_player_id = %s;",
                    (player_id,),
                )
                mobile_row = cursor.fetchone()

                if mobile_row:
                    mobile_id = mobile_row["id"]
                    mobile_result, mobile = self.load_mobile(database, mobile_id)
                    from common import is_true

                    if is_true(mobile_result):
                        player.mobile = mobile

            return (
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_LOADED.format(type="Player", id=player_id),
                ),
                player,
            )
        except Exception as e:
            return (
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_LOAD_FAILED.format(
                        type="Player", id=player_id, database=database, error=str(e)
                    ),
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
            )

    def save_player(
        self,
        database: str,
        obj: Player,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        if obj.id is None:
            return self.create_player(database, obj, table)
        else:
            return self.update_player(database, obj, table)

    def destroy_player(
        self,
        database: str,
        player_id: int,
        table: Optional[str] = None,
    ) -> list[GameResult]:
        try:
            with self.transaction() as cursor:
                players_table = table if table else TABLE_PLAYERS

                # First, find and delete the associated mobile
                cursor.execute(
                    f"SELECT id FROM {database}.mobiles WHERE owner_player_id = %s;",
                    (player_id,),
                )
                mobile_row = cursor.fetchone()

                if mobile_row:
                    mobile_id = mobile_row[0]

                    # Get attribute IDs for this mobile
                    cursor.execute(
                        f"SELECT attribute_id FROM {database}.attribute_owners WHERE mobile_id = %s;",
                        (mobile_id,),
                    )
                    attr_ids = [row[0] for row in cursor.fetchall()]

                    # Delete attribute owners
                    cursor.execute(
                        f"DELETE FROM {database}.attribute_owners WHERE mobile_id = %s;",
                        (mobile_id,),
                    )

                    # Delete attributes
                    if attr_ids:
                        placeholders = ",".join(["%s"] * len(attr_ids))
                        cursor.execute(
                            f"DELETE FROM {database}.attributes WHERE id IN ({placeholders});",
                            tuple(attr_ids),
                        )

                    # Delete the mobile
                    cursor.execute(
                        f"DELETE FROM {database}.mobiles WHERE id = %s;",
                        (mobile_id,),
                    )

                # Now delete the player
                cursor.execute(
                    f"DELETE FROM {database}.{players_table} WHERE id = %s;",
                    (player_id,),
                )

                if cursor.rowcount == 0:
                    return [
                        GameResult(
                            status=StatusType.FAILURE,
                            message=MSG_NOT_FOUND.format(
                                type="Player", id=player_id, database=database
                            ),
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ]

            return [
                GameResult(
                    status=StatusType.SUCCESS,
                    message=MSG_DESTROYED.format(type="Player", id=player_id),
                ),
            ]
        except Exception as e:
            return [
                GameResult(
                    status=StatusType.FAILURE,
                    message=MSG_DESTROY_FAILED.format(
                        type="Player", id=player_id, database=database, error=str(e)
                    ),
                    error_code=GameError.DB_DELETE_FAILED,
                ),
            ]

    def list_player(
        self,
        database: str,
        page: int,
        results_per_page: int,
        search_string: Optional[str] = None,
        table: Optional[str] = None,
    ) -> Tuple[GameResult, Optional[list[Player]], int]:
        """
        List players with pagination and optional search.

        Args:
            database: Database name
            page: Page number (0-indexed)
            results_per_page: Number of results per page
            search_string: Optional search string (searches full_name, what_we_call_you, and email)
            table: Optional table name override

        Returns:
            Tuple of (GameResult, list of Player objects, total count)
        """
        try:
            with self.transaction_dict() as cursor:
                players_table = table if table else TABLE_PLAYERS

                # Calculate offset
                offset = page * results_per_page

                # Build WHERE clause for search
                where_clause = ""
                params = []
                if search_string:
                    where_clause = "WHERE (full_name LIKE %s OR what_we_call_you LIKE %s OR email LIKE %s)"
                    search_pattern = f"%{search_string}%"
                    params = [search_pattern, search_pattern, search_pattern]

                # Get total count
                count_query = f"SELECT COUNT(*) as total FROM {database}.{players_table} {where_clause};"
                logger.debug(count_query)
                cursor.execute(count_query, tuple(params))
                count_row = cursor.fetchone()
                total_count = count_row["total"] if count_row else 0

                # Get paginated results
                if not search_string:
                    query = f"SELECT * FROM {database}.{players_table} {where_clause} ORDER BY id LIMIT %s OFFSET %s;"
                    logger.debug(query)
                    args_to_query = tuple(params + [results_per_page, offset])
                    logger.debug(args_to_query)
                    cursor.execute(query, args_to_query)
                else:
                    query = f"SELECT * FROM {database}.{players_table} {where_clause} ORDER BY id LIMIT 100;"
                    logger.debug(query)
                    args_to_query = tuple(params)
                    logger.debug(args_to_query)
                    cursor.execute(query, args_to_query)
                
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
                        FROM {database}.mobiles 
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

                        mobile_owner = Owner()
                        mobile_owner.player_id = mobile_row["owner_player_id"]
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
                    message=f"Failed to list players from database={database}: {str(e)}",
                    error_code=GameError.DB_QUERY_FAILED,
                ),
                None,
                0,
            )
