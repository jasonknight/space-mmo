import sys
sys.path.append('../gen-py')

from collections import OrderedDict
from typing import Optional
from copy import deepcopy
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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
from db import DB
from common import is_ok


class LRUCache:
    """
    Simple LRU (Least Recently Used) cache implementation using OrderedDict.
    When the cache reaches max_size, the least recently used item is evicted.
    """

    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key: int) -> Optional[Player]:
        """
        Get a player from the cache by ID.
        Returns a deep copy to prevent modifications affecting the cached version.
        Moves the item to the end (most recently used).
        """
        if key not in self.cache:
            logger.debug(f"Cache MISS for player_id={key}")
            return None

        logger.debug(f"Cache HIT for player_id={key}")
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        # Return a deep copy to prevent external modifications
        return deepcopy(self.cache[key])

    def put(self, key: int, value: Player) -> None:
        """
        Add or update a player in the cache.
        Stores a deep copy to prevent external modifications affecting the cache.
        If cache is full, removes the least recently used item.
        """
        # Store a deep copy to prevent external modifications
        self.cache[key] = deepcopy(value)
        self.cache.move_to_end(key)

        # Evict least recently used if over capacity
        if len(self.cache) > self.max_size:
            evicted_key = next(iter(self.cache))
            self.cache.popitem(last=False)
            logger.debug(f"Cache EVICTED player_id={evicted_key} (cache full, size={self.max_size})")

        logger.debug(f"Cache PUT player_id={key} (cache size now {len(self.cache)})")

    def invalidate(self, key: int) -> None:
        """Remove a player from the cache."""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache INVALIDATED player_id={key}")

    def clear(self) -> None:
        """Clear all entries from the cache."""
        self.cache.clear()

    def size(self) -> int:
        """Return the current size of the cache."""
        return len(self.cache)


class PlayerServiceHandler(PlayerServiceIface):
    """
    Implementation of the PlayerService thrift interface.
    Handles player operations using the DB layer.
    Includes an LRU cache to reduce database queries for frequently accessed players.
    """

    def __init__(self, db: DB, database: str, cache_size: int = 1000):
        self.db = db
        self.database = database
        self.cache = LRUCache(max_size=cache_size)

    def describe(self) -> ServiceMetadata:
        """Return service metadata for discovery (used by Fiddler)."""

        # Define all enums used by this service
        enums = [
            EnumDefinition(
                enum_name="StatusType",
                values={
                    "SUCCESS": int(StatusType.SUCCESS),
                    "FAILURE": int(StatusType.FAILURE),
                    "SKIP": int(StatusType.SKIP),
                },
                description="Status of an operation result",
            ),
            EnumDefinition(
                enum_name="GameError",
                values={
                    "DB_CONNECTION_FAILED": int(GameError.DB_CONNECTION_FAILED),
                    "DB_TRANSACTION_FAILED": int(GameError.DB_TRANSACTION_FAILED),
                    "DB_INSERT_FAILED": int(GameError.DB_INSERT_FAILED),
                    "DB_UPDATE_FAILED": int(GameError.DB_UPDATE_FAILED),
                    "DB_DELETE_FAILED": int(GameError.DB_DELETE_FAILED),
                    "DB_QUERY_FAILED": int(GameError.DB_QUERY_FAILED),
                    "DB_RECORD_NOT_FOUND": int(GameError.DB_RECORD_NOT_FOUND),
                    "DB_INVALID_DATA": int(GameError.DB_INVALID_DATA),
                    "DB_FOREIGN_KEY_VIOLATION": int(GameError.DB_FOREIGN_KEY_VIOLATION),
                    "DB_UNIQUE_CONSTRAINT_VIOLATION": int(GameError.DB_UNIQUE_CONSTRAINT_VIOLATION),
                },
                description="Error codes for operations",
            ),
        ]

        # Define methods with examples
        methods = [
            MethodDescription(
                method_name="load",
                description="Load a player from the database by ID",
                example_request_json='''{
    "data": {
        "load_player": {
            "player_id": 1
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully loaded Player id=1"
    }],
    "response_data": {
        "load_player": {
            "player": {
                "id": 1,
                "full_name": "John Doe",
                "what_we_call_you": "JohnD",
                "security_token": "hashed_token",
                "over_13": true,
                "year_of_birth": 1990
            }
        }
    }
}''',
                request_enum_fields=[],
                response_enum_fields=[
                    FieldEnumMapping(field_path="results[].status", enum_name="StatusType"),
                    FieldEnumMapping(field_path="results[].error_code", enum_name="GameError"),
                ],
            ),
            MethodDescription(
                method_name="create",
                description="Create a new player in the database",
                example_request_json='''{
    "data": {
        "create_player": {
            "player": {
                "full_name": "John Doe",
                "what_we_call_you": "JohnD",
                "security_token": "hashed_token",
                "over_13": true,
                "year_of_birth": 1990
            }
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully created Player id=1"
    }],
    "response_data": {
        "create_player": {
            "player": {
                "id": 1,
                "full_name": "John Doe",
                "what_we_call_you": "JohnD",
                "security_token": "hashed_token",
                "over_13": true,
                "year_of_birth": 1990
            }
        }
    }
}''',
                request_enum_fields=[],
                response_enum_fields=[
                    FieldEnumMapping(field_path="results[].status", enum_name="StatusType"),
                    FieldEnumMapping(field_path="results[].error_code", enum_name="GameError"),
                ],
            ),
            MethodDescription(
                method_name="save",
                description="Save (create or update) a player in the database",
                example_request_json='''{
    "data": {
        "save_player": {
            "player": {
                "id": 1,
                "full_name": "John Doe Updated",
                "what_we_call_you": "JohnD",
                "security_token": "new_hashed_token",
                "over_13": true,
                "year_of_birth": 1990
            }
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully updated Player id=1"
    }],
    "response_data": {
        "save_player": {
            "player": {
                "id": 1,
                "full_name": "John Doe Updated",
                "what_we_call_you": "JohnD",
                "security_token": "new_hashed_token",
                "over_13": true,
                "year_of_birth": 1990
            }
        }
    }
}''',
                request_enum_fields=[],
                response_enum_fields=[
                    FieldEnumMapping(field_path="results[].status", enum_name="StatusType"),
                    FieldEnumMapping(field_path="results[].error_code", enum_name="GameError"),
                ],
            ),
            MethodDescription(
                method_name="delete",
                description="Delete a player from the database",
                example_request_json='''{
    "data": {
        "delete_player": {
            "player_id": 1
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully destroyed Player id=1"
    }],
    "response_data": {
        "delete_player": {
            "player_id": 1
        }
    }
}''',
                request_enum_fields=[],
                response_enum_fields=[
                    FieldEnumMapping(field_path="results[].status", enum_name="StatusType"),
                    FieldEnumMapping(field_path="results[].error_code", enum_name="GameError"),
                ],
            ),
            MethodDescription(
                method_name="list_records",
                description="List players with pagination and optional search on full_name or what_we_call_you",
                example_request_json='''{
    "data": {
        "list_player": {
            "page": 0,
            "results_per_page": 10,
            "search_string": "John"
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully listed 10 players (total: 100)"
    }],
    "response_data": {
        "list_player": {
            "players": [
                {
                    "id": 1,
                    "full_name": "John Doe",
                    "what_we_call_you": "JohnD",
                    "security_token": "hashed_token",
                    "over_13": true,
                    "year_of_birth": 1990
                }
            ],
            "total_count": 100
        }
    }
}''',
                request_enum_fields=[],
                response_enum_fields=[
                    FieldEnumMapping(field_path="results[].status", enum_name="StatusType"),
                    FieldEnumMapping(field_path="results[].error_code", enum_name="GameError"),
                ],
            ),
        ]

        return ServiceMetadata(
            service_name="PlayerService",
            version="1.0",
            description="Service for managing game players with create, load, save, and delete operations",
            methods=methods,
            enums=enums,
        )

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
            result, player = self.db.load_player(
                self.database,
                player_id,
            )

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

            results = self.db.create_player(
                self.database,
                create_data.player,
            )

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
                logger.warning(f"FAILURE: Could not create player - {results[0].message if results else 'unknown error'}")
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

            results = self.db.save_player(
                self.database,
                save_data.player,
            )

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
                logger.warning(f"FAILURE: Could not save player - {results[0].message if results else 'unknown error'}")
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

            results = self.db.destroy_player(
                self.database,
                player_id,
            )

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
                logger.warning(f"FAILURE: Could not delete player - {results[0].message if results else 'unknown error'}")
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
            page = list_data.page
            results_per_page = list_data.results_per_page
            search_string = list_data.search_string if hasattr(list_data, 'search_string') else None

            logger.info(f"Listing players: page={page}, results_per_page={results_per_page}, search_string={search_string}")

            result, players, total_count = self.db.list_player(
                self.database,
                page,
                results_per_page,
                search_string=search_string,
            )

            if players is not None:
                logger.info(f"SUCCESS: Listed {len(players)} players (total: {total_count})")
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
