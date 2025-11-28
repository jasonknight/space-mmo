import sys

sys.path.append("../../gen-py")
sys.path.append("..")

import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from game.ttypes import (
    PlayerRequest,
    PlayerResponse,
    PlayerRequestData,
    PlayerResponseData,
    LoadPlayerRequestData,
    LoadPlayerResponseData,
    CreatePlayerRequestData,
    CreatePlayerResponseData,
    SavePlayerRequestData,
    SavePlayerResponseData,
    DeletePlayerRequestData,
    DeletePlayerResponseData,
    ListPlayerRequestData,
    ListPlayerResponseData,
    Player,
    GameResult,
    StatusType,
    GameError,
    ServiceMetadata,
    MethodDescription,
    EnumDefinition,
    FieldEnumMapping,
)
from game.PlayerService import Iface as PlayerServiceIface
from db_models.models import Player
from common import is_ok
from services.base_service import BaseServiceHandler


class PlayerServiceHandler(BaseServiceHandler, PlayerServiceIface):
    """
    Implementation of the PlayerService thrift interface.
    Handles player operations using the db_models layer.
    """

    def __init__(self):
        BaseServiceHandler.__init__(self, PlayerServiceHandler)

    def load(self, request: PlayerRequest) -> PlayerResponse:
        """Load a player by ID."""
        logger.info("=== LOAD player request ===")
        try:
            if not request.data.load_player:
                logger.error("Request data missing load_player field")
                return PlayerResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain load_player",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            load_data = request.data.load_player
            player_id = load_data.player_id
            logger.info(f"Loading player_id={player_id}")

            player = Player.find(player_id)

            if player:
                logger.info(f"SUCCESS: Loaded player_id={player_id}")
                results, thrift_player = player.into_thrift()
                response_data = PlayerResponseData(
                    load_player=LoadPlayerResponseData(
                        player=thrift_player,
                    ),
                )
                return PlayerResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Player_id={player_id} not found")
                result = GameResult(
                    status=StatusType.FAILURE,
                    message=f"Player id={player_id} not found",
                    error_code=GameError.DB_RECORD_NOT_FOUND,
                )
                return PlayerResponse(
                    results=[result],
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in load: {type(e).__name__}: {str(e)}")
            return PlayerResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to load player: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )

    def create(self, request: PlayerRequest) -> PlayerResponse:
        """Create a new player."""
        logger.info("=== CREATE player request ===")
        try:
            if not request.data.create_player:
                logger.error("Request data missing create_player field")
                return PlayerResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain create_player",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            create_data = request.data.create_player
            thrift_player = create_data.player
            logger.info(f"Creating player: {thrift_player.what_we_call_you}")
            logger.debug(f"Full name: {thrift_player.full_name}")

            player = Player()
            player.from_thrift(thrift_player)
            player.save()

            logger.info(f"SUCCESS: Created player with id={player.get_id()}")

            results, created_thrift_player = player.into_thrift()
            response_data = PlayerResponseData(
                create_player=CreatePlayerResponseData(
                    player=created_thrift_player,
                ),
            )
            return PlayerResponse(
                results=results,
                response_data=response_data,
            )

        except Exception as e:
            logger.error(f"EXCEPTION in create: {type(e).__name__}: {str(e)}")
            return PlayerResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to create player: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def save(self, request: PlayerRequest) -> PlayerResponse:
        """Save (create or update) a player."""
        logger.info("=== SAVE player request ===")
        try:
            if not request.data.save_player:
                logger.error("Request data missing save_player field")
                return PlayerResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain save_player",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            save_data = request.data.save_player
            thrift_player = save_data.player
            player_id = thrift_player.id if thrift_player.id else "NEW"
            logger.info(f"Saving player_id={player_id}")
            logger.debug(f"Player name: {thrift_player.what_we_call_you}")

            player = Player()
            player.from_thrift(thrift_player)
            player.save()

            logger.info(f"SUCCESS: Saved player_id={player.get_id()}")

            results, saved_thrift_player = player.into_thrift()
            response_data = PlayerResponseData(
                save_player=SavePlayerResponseData(
                    player=saved_thrift_player,
                ),
            )
            return PlayerResponse(
                results=results,
                response_data=response_data,
            )

        except Exception as e:
            logger.error(f"EXCEPTION in save: {type(e).__name__}: {str(e)}")
            return PlayerResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to save player: {str(e)}",
                        error_code=GameError.DB_UPDATE_FAILED,
                    ),
                ],
                response_data=None,
            )

    def delete(self, request: PlayerRequest) -> PlayerResponse:
        """Delete a player by ID."""
        logger.info("=== DELETE player request ===")
        try:
            if not request.data.delete_player:
                logger.error("Request data missing delete_player field")
                return PlayerResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain delete_player",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            delete_data = request.data.delete_player
            player_id = delete_data.player_id
            logger.info(f"Deleting player_id={player_id}")

            player = Player.find(player_id)

            if not player:
                logger.warning(f"FAILURE: Player_id={player_id} not found")
                result = GameResult(
                    status=StatusType.FAILURE,
                    message=f"Player id={player_id} not found",
                    error_code=GameError.DB_RECORD_NOT_FOUND,
                )
                return PlayerResponse(
                    results=[result],
                    response_data=None,
                )

            player._disconnect()
            player.destroy()
            logger.info(f"SUCCESS: Deleted player_id={player_id}")

            response_data = PlayerResponseData(
                delete_player=DeletePlayerResponseData(
                    player_id=player_id,
                ),
            )
            result = GameResult(
                status=StatusType.SUCCESS,
                message=f"Successfully deleted Player id={player_id}",
            )
            return PlayerResponse(
                results=[result],
                response_data=response_data,
            )

        except Exception as e:
            logger.error(f"EXCEPTION in delete: {type(e).__name__}: {str(e)}")
            return PlayerResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to delete player: {str(e)}",
                        error_code=GameError.DB_DELETE_FAILED,
                    ),
                ],
                response_data=None,
            )

    def list_records(self, request: PlayerRequest) -> PlayerResponse:
        """List players with pagination and optional search."""
        logger.info("=== LIST player records request ===")
        connection = None
        try:
            if not request.data.list_player:
                logger.error("Request data missing list_player field")
                return PlayerResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain list_player",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            list_data = request.data.list_player
            page = max(0, list_data.page)
            results_per_page = list_data.results_per_page
            search_string = (
                list_data.search_string if hasattr(list_data, "search_string") else None
            )

            logger.info(
                f"Listing players: page={page}, results_per_page={results_per_page}, search_string={search_string}"
            )

            connection = Player._create_connection()
            cursor = connection.cursor(dictionary=True)

            offset = page * results_per_page

            if search_string:
                count_query = """
                    SELECT COUNT(*) as total
                    FROM players
                    WHERE full_name LIKE %s OR what_we_call_you LIKE %s
                """
                search_param = f"%{search_string}%"
                cursor.execute(count_query, (search_param, search_param))
                total_count = cursor.fetchone()["total"]

                query = """
                    SELECT *
                    FROM players
                    WHERE full_name LIKE %s OR what_we_call_you LIKE %s
                    ORDER BY id
                    LIMIT %s OFFSET %s
                """
                cursor.execute(
                    query,
                    (search_param, search_param, results_per_page, offset),
                )
            else:
                count_query = "SELECT COUNT(*) as total FROM players"
                cursor.execute(count_query)
                total_count = cursor.fetchone()["total"]

                query = "SELECT * FROM players ORDER BY id LIMIT %s OFFSET %s"
                cursor.execute(query, (results_per_page, offset))

            rows = cursor.fetchall()

            players = []
            for row in rows:
                player = Player()
                player._data = row
                player._dirty = False
                results, thrift_player = player.into_thrift()
                if thrift_player:
                    players.append(thrift_player)

            logger.info(f"SUCCESS: Listed {len(players)} players (total: {total_count})")

            response_data = PlayerResponseData(
                list_player=ListPlayerResponseData(
                    players=players,
                    total_count=total_count,
                ),
            )
            result = GameResult(
                status=StatusType.SUCCESS,
                message=f"Successfully listed {len(players)} players",
            )
            return PlayerResponse(
                results=[result],
                response_data=response_data,
            )

        except Exception as e:
            logger.error(f"EXCEPTION in list_records: {type(e).__name__}: {str(e)}")
            return PlayerResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to list players: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )
        finally:
            if connection:
                connection.close()
