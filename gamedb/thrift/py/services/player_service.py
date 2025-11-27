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
from models.player_model import PlayerModel
from common import is_ok
from services.lru_cache import LRUCache
from services.base_service import BaseServiceHandler


class PlayerServiceHandler(BaseServiceHandler, PlayerServiceIface):
    """
    Implementation of the PlayerService thrift interface.
    Handles player operations using the PlayerModel layer.
    Includes an LRU cache to reduce database queries for frequently accessed players.
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        cache_size: int = 1000,
    ):
        BaseServiceHandler.__init__(self, PlayerServiceHandler)
        self.player_model = PlayerModel(host, user, password, database)
        self.database = database
        self.cache = LRUCache(max_size=cache_size)

    def load(self, request: PlayerRequest) -> PlayerResponse:
        """Load a player by ID. Checks cache first before querying database."""
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

            # Check cache first
            logger.debug("Checking cache...")
            cached_player = self.cache.get(player_id)
            if cached_player:
                logger.info(f"SUCCESS: Loaded player_id={player_id} from CACHE")
                result = GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded Player id={player_id} from cache",
                )
                response_data = PlayerResponseData(
                    load_player=LoadPlayerResponseData(
                        player=cached_player,
                    ),
                )
                return PlayerResponse(
                    results=[result],
                    response_data=response_data,
                )

            # Cache miss - load from database
            logger.debug(f"Cache miss, loading from DATABASE for player_id={player_id}")
            result, player = self.player_model.load(player_id)

            if player:
                logger.info(f"SUCCESS: Loaded player_id={player_id} from DATABASE")
                # Store in cache for future requests
                self.cache.put(player_id, player)

                response_data = PlayerResponseData(
                    load_player=LoadPlayerResponseData(
                        player=player,
                    ),
                )
                return PlayerResponse(
                    results=[result],
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Player_id={player_id} not found in database")
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
        """Create a new player. Populates cache after successful creation."""
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
            logger.info(f"Creating player: {create_data.player.what_we_call_you}")
            logger.debug(f"Full name: {create_data.player.full_name}")

            results = self.player_model.create(create_data.player)

            if is_ok(results):
                logger.info(f"SUCCESS: Created player with id={create_data.player.id}")
                # Add to cache after successful creation
                if create_data.player.id is not None:
                    self.cache.put(create_data.player.id, create_data.player)

                response_data = PlayerResponseData(
                    create_player=CreatePlayerResponseData(
                        player=create_data.player,
                    ),
                )
                return PlayerResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(
                    f"FAILURE: Could not create player - {results[0].message if results else 'unknown error'}"
                )
                return PlayerResponse(
                    results=results,
                    response_data=None,
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
        """Save (create or update) a player. Updates cache after successful save."""
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
            player_id = save_data.player.id if save_data.player.id else "NEW"
            logger.info(f"Saving player_id={player_id}")
            logger.debug(f"Player name: {save_data.player.what_we_call_you}")

            results = self.player_model.save(save_data.player)

            if is_ok(results):
                logger.info(f"SUCCESS: Saved player_id={save_data.player.id}")
                # Update cache after successful save
                if save_data.player.id is not None:
                    self.cache.put(save_data.player.id, save_data.player)

                response_data = PlayerResponseData(
                    save_player=SavePlayerResponseData(
                        player=save_data.player,
                    ),
                )
                return PlayerResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(
                    f"FAILURE: Could not save player - {results[0].message if results else 'unknown error'}"
                )
                return PlayerResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in save: {type(e).__name__}: {str(e)}")
            return PlayerResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to save player: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def delete(self, request: PlayerRequest) -> PlayerResponse:
        """Delete a player by ID. Invalidates cache after successful deletion."""
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

            results = self.player_model.destroy(player_id)

            if is_ok(results):
                logger.info(f"SUCCESS: Deleted player_id={player_id}")
                # Invalidate cache after successful deletion
                self.cache.invalidate(player_id)

                response_data = PlayerResponseData(
                    delete_player=DeletePlayerResponseData(
                        player_id=player_id,
                    ),
                )
                return PlayerResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(
                    f"FAILURE: Could not delete player - {results[0].message if results else 'unknown error'}"
                )
                return PlayerResponse(
                    results=results,
                    response_data=None,
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

            result, players, total_count = self.player_model.search(
                page,
                results_per_page,
                search_string=search_string,
            )

            if players is not None:
                logger.info(
                    f"SUCCESS: Listed {len(players)} players (total: {total_count})"
                )
                response_data = PlayerResponseData(
                    list_player=ListPlayerResponseData(
                        players=players,
                        total_count=total_count,
                    ),
                )
                return PlayerResponse(
                    results=[result],
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not list players - {result.message}")
                return PlayerResponse(
                    results=[result],
                    response_data=None,
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
