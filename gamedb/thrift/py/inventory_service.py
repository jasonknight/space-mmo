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
    InventoryRequest,
    InventoryResponse,
    InventoryRequestData,
    InventoryResponseData,
    LoadInventoryRequestData,
    LoadInventoryResponseData,
    CreateInventoryRequestData,
    CreateInventoryResponseData,
    SaveInventoryRequestData,
    SaveInventoryResponseData,
    SplitStackRequestData,
    SplitStackResponseData,
    TransferItemRequestData,
    TransferItemResponseData,
    ListInventoryRequestData,
    ListInventoryResponseData,
    Inventory,
    InventoryEntry,
    GameResult,
    StatusType,
    GameError,
    ServiceMetadata,
    MethodDescription,
    EnumDefinition,
    FieldEnumMapping,
)
from game.InventoryService import Iface as InventoryServiceIface
from db import DB
from inventory import split_stack, transfer_item
from common import is_ok


class LRUCache:
    """
    Simple LRU (Least Recently Used) cache implementation using OrderedDict.
    When the cache reaches max_size, the least recently used item is evicted.
    """

    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key: int) -> Optional[Inventory]:
        """
        Get an inventory from the cache by ID.
        Returns a deep copy to prevent modifications affecting the cached version.
        Moves the item to the end (most recently used).
        """
        if key not in self.cache:
            logger.debug(f"Cache MISS for inventory_id={key}")
            return None

        logger.debug(f"Cache HIT for inventory_id={key}")
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        # Return a deep copy to prevent external modifications
        return deepcopy(self.cache[key])

    def put(self, key: int, value: Inventory) -> None:
        """
        Add or update an inventory in the cache.
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
            logger.debug(f"Cache EVICTED inventory_id={evicted_key} (cache full, size={self.max_size})")

        logger.debug(f"Cache PUT inventory_id={key} (cache size now {len(self.cache)})")

    def invalidate(self, key: int) -> None:
        """Remove an inventory from the cache."""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache INVALIDATED inventory_id={key}")

    def clear(self) -> None:
        """Clear all entries from the cache."""
        self.cache.clear()

    def size(self) -> int:
        """Return the current size of the cache."""
        return len(self.cache)


class InventoryServiceHandler(InventoryServiceIface):
    """
    Implementation of the InventoryService thrift interface.
    Handles inventory operations using the DB layer and inventory.py functions.
    Includes an LRU cache to reduce database queries for frequently accessed inventories.
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
                    "INV_MAX_ITEMS_REACHED": int(GameError.INV_MAX_ITEMS_REACHED),
                    "INV_ALL_ENTRIES_MAX_STACKED": int(GameError.INV_ALL_ENTRIES_MAX_STACKED),
                    "INV_NEW_VOLUME_TOO_HIGH": int(GameError.INV_NEW_VOLUME_TOO_HIGH),
                    "INV_CANNOT_ADD_ITEM": int(GameError.INV_CANNOT_ADD_ITEM),
                    "INV_FAILED_TO_ADD": int(GameError.INV_FAILED_TO_ADD),
                    "INV_FAILED_TO_TRANSFER": int(GameError.INV_FAILED_TO_TRANSFER),
                    "INV_COULD_NOT_FIND_ENTRY": int(GameError.INV_COULD_NOT_FIND_ENTRY),
                    "INV_NEW_QUANTITY_INVALID": int(GameError.INV_NEW_QUANTITY_INVALID),
                    "INV_FULL_CANNOT_SPLIT": int(GameError.INV_FULL_CANNOT_SPLIT),
                    "INV_ITEM_NOT_FOUND": int(GameError.INV_ITEM_NOT_FOUND),
                    "INV_INSUFFICIENT_QUANTITY": int(GameError.INV_INSUFFICIENT_QUANTITY),
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
                    "INV_OPERATION_FAILED": int(GameError.INV_OPERATION_FAILED),
                },
                description="Error codes for operations",
            ),
        ]

        # Define methods with examples
        methods = [
            MethodDescription(
                method_name="load",
                description="Load an inventory from the database by ID",
                example_request_json='''{
    "data": {
        "load_inventory": {
            "inventory_id": 1
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully loaded Inventory id=1"
    }],
    "response_data": {
        "load_inventory": {
            "inventory": {
                "id": 1,
                "max_entries": 10,
                "max_volume": 500.0,
                "entries": [],
                "last_calculated_volume": 0.0,
                "owner": {"mobile_id": 100}
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
                description="Create a new inventory in the database",
                example_request_json='''{
    "data": {
        "create_inventory": {
            "inventory": {
                "max_entries": 10,
                "max_volume": 500.0,
                "entries": [],
                "last_calculated_volume": 0.0,
                "owner": {"mobile_id": 100}
            }
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully created Inventory id=1"
    }],
    "response_data": {
        "create_inventory": {
            "inventory": {
                "id": 1,
                "max_entries": 10,
                "max_volume": 500.0,
                "entries": [],
                "last_calculated_volume": 0.0,
                "owner": {"mobile_id": 100}
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
                description="Save (create or update) an inventory in the database",
                example_request_json='''{
    "data": {
        "save_inventory": {
            "inventory": {
                "id": 1,
                "max_entries": 20,
                "max_volume": 1000.0,
                "entries": [],
                "last_calculated_volume": 0.0,
                "owner": {"mobile_id": 100}
            }
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully updated Inventory id=1"
    }],
    "response_data": {
        "save_inventory": {
            "inventory": {
                "id": 1,
                "max_entries": 20,
                "max_volume": 1000.0,
                "entries": [],
                "last_calculated_volume": 0.0,
                "owner": {"mobile_id": 100}
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
                method_name="split_stack",
                description="Split a stack of items within an inventory",
                example_request_json='''{
    "data": {
        "split_stack": {
            "inventory_id": 1,
            "item_id": 5,
            "quantity_to_split": 50.0
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "split entry"
    }],
    "response_data": {
        "split_stack": {
            "inventory": {
                "id": 1,
                "max_entries": 10,
                "max_volume": 500.0,
                "entries": [
                    {"item_id": 5, "quantity": 50.0, "is_max_stacked": false},
                    {"item_id": 5, "quantity": 50.0, "is_max_stacked": false}
                ],
                "last_calculated_volume": 0.0,
                "owner": {"mobile_id": 100}
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
                method_name="transfer_item",
                description="Transfer items between two inventories",
                example_request_json='''{
    "data": {
        "transfer_item": {
            "source_inventory_id": 1,
            "destination_inventory_id": 2,
            "item_id": 5,
            "quantity": 30.0
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "transferred 30.0 of 5 to 2"
    }],
    "response_data": {
        "transfer_item": {
            "source_inventory": {
                "id": 1,
                "max_entries": 10,
                "max_volume": 500.0,
                "entries": [{"item_id": 5, "quantity": 20.0, "is_max_stacked": false}],
                "last_calculated_volume": 0.0,
                "owner": {"mobile_id": 100}
            },
            "destination_inventory": {
                "id": 2,
                "max_entries": 10,
                "max_volume": 500.0,
                "entries": [{"item_id": 5, "quantity": 30.0, "is_max_stacked": false}],
                "last_calculated_volume": 0.0,
                "owner": {"mobile_id": 200}
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
                method_name="list_records",
                description="List inventories with pagination (no search - inventories have no searchable text fields)",
                example_request_json='''{
    "data": {
        "list_inventory": {
            "page": 0,
            "results_per_page": 10
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully listed 10 inventories (total: 100)"
    }],
    "response_data": {
        "list_inventory": {
            "inventories": [
                {
                    "id": 1,
                    "max_entries": 10,
                    "max_volume": 500.0,
                    "entries": [],
                    "last_calculated_volume": 0.0,
                    "owner": {"mobile_id": 100}
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
            service_name="InventoryService",
            version="1.0",
            description="Service for managing game inventories with create, load, save, split, transfer, and list operations",
            methods=methods,
            enums=enums,
        )

    def load(self, request: InventoryRequest) -> InventoryResponse:
        """Load an inventory by ID. Checks cache first before querying database."""
        logger.info("=== LOAD inventory request ===")
        try:
            if not request.data.load_inventory:
                logger.error("Request data missing load_inventory field")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain load_inventory",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            load_data = request.data.load_inventory
            inventory_id = load_data.inventory_id
            logger.info(f"Loading inventory_id={inventory_id}")

            # Check cache first
            logger.debug("Checking cache...")
            cached_inventory = self.cache.get(inventory_id)
            if cached_inventory:
                logger.info(f"SUCCESS: Loaded inventory_id={inventory_id} from CACHE")
                result = GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded inventory id={inventory_id} from cache",
                )
                response_data = InventoryResponseData(
                    load_inventory=LoadInventoryResponseData(
                        inventory=cached_inventory,
                    ),
                )
                return InventoryResponse(
                    results=[result],
                    response_data=response_data,
                )

            # Cache miss - load from database
            logger.debug(f"Cache miss, loading from DATABASE for inventory_id={inventory_id}")
            result, inventory = self.db.load_inventory(
                self.database,
                inventory_id,
            )

            if inventory:
                logger.info(f"SUCCESS: Loaded inventory_id={inventory_id} from DATABASE")
                # Store in cache for future requests
                self.cache.put(inventory_id, inventory)

                response_data = InventoryResponseData(
                    load_inventory=LoadInventoryResponseData(
                        inventory=inventory,
                    ),
                )
                return InventoryResponse(
                    results=[result],
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Inventory_id={inventory_id} not found in database")
                return InventoryResponse(
                    results=[result],
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in load: {type(e).__name__}: {str(e)}")
            return InventoryResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to load inventory: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )

    def create(self, request: InventoryRequest) -> InventoryResponse:
        """Create a new inventory. Populates cache after successful creation."""
        logger.info("=== CREATE inventory request ===")
        try:
            if not request.data.create_inventory:
                logger.error("Request data missing create_inventory field")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain create_inventory",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            create_data = request.data.create_inventory
            logger.info(f"Creating inventory with max_entries={create_data.inventory.max_entries}, max_volume={create_data.inventory.max_volume}")
            logger.debug(f"Inventory has {len(create_data.inventory.entries)} entries")

            results = self.db.create_inventory(
                self.database,
                create_data.inventory,
            )

            if is_ok(results):
                logger.info(f"SUCCESS: Created inventory with id={create_data.inventory.id}")
                # Add to cache after successful creation
                if create_data.inventory.id is not None:
                    self.cache.put(create_data.inventory.id, create_data.inventory)

                response_data = InventoryResponseData(
                    create_inventory=CreateInventoryResponseData(
                        inventory=create_data.inventory,
                    ),
                )
                return InventoryResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not create inventory - {results[0].message if results else 'unknown error'}")
                return InventoryResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in create: {type(e).__name__}: {str(e)}")
            return InventoryResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to create inventory: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def save(self, request: InventoryRequest) -> InventoryResponse:
        """Save (create or update) an inventory. Updates cache after successful save."""
        logger.info("=== SAVE inventory request ===")
        try:
            if not request.data.save_inventory:
                logger.error("Request data missing save_inventory field")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain save_inventory",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            save_data = request.data.save_inventory
            inventory_id = save_data.inventory.id if save_data.inventory.id else "NEW"
            logger.info(f"Saving inventory_id={inventory_id}")
            logger.debug(f"Inventory has {len(save_data.inventory.entries)} entries")

            results = self.db.save_inventory(
                self.database,
                save_data.inventory,
            )

            if is_ok(results):
                logger.info(f"SUCCESS: Saved inventory_id={save_data.inventory.id}")
                # Update cache after successful save
                if save_data.inventory.id is not None:
                    self.cache.put(save_data.inventory.id, save_data.inventory)

                response_data = InventoryResponseData(
                    save_inventory=SaveInventoryResponseData(
                        inventory=save_data.inventory,
                    ),
                )
                return InventoryResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not save inventory - {results[0].message if results else 'unknown error'}")
                return InventoryResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in save: {type(e).__name__}: {str(e)}")
            return InventoryResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to save inventory: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def split_stack(self, request: InventoryRequest) -> InventoryResponse:
        """Split a stack of items within an inventory. Checks cache and updates it."""
        logger.info("=== SPLIT_STACK request ===")
        try:
            if not request.data.split_stack:
                logger.error("Request data missing split_stack field")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain split_stack",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            split_data = request.data.split_stack
            inventory_id = split_data.inventory_id
            logger.info(f"Splitting stack in inventory_id={inventory_id}, item_id={split_data.item_id}, quantity={split_data.quantity_to_split}")

            # Check cache first
            logger.debug("Checking cache...")
            inventory = self.cache.get(inventory_id)
            result = None

            if not inventory:
                # Cache miss - load from database
                logger.debug(f"Cache miss, loading from DATABASE for inventory_id={inventory_id}")
                result, inventory = self.db.load_inventory(
                    self.database,
                    inventory_id,
                )

                if not inventory:
                    logger.error(f"Inventory_id={inventory_id} not found")
                    return InventoryResponse(
                        results=[result],
                        response_data=None,
                    )

            # Find the entry index that matches the item_id
            # inventory.split_stack expects entry_index, not item_id
            logger.debug(f"Searching for item_id={split_data.item_id} in {len(inventory.entries)} entries")
            entry_index = None
            for idx, entry in enumerate(inventory.entries):
                if entry.item_id == split_data.item_id:
                    entry_index = idx
                    logger.debug(f"Found item at entry_index={idx}, current quantity={entry.quantity}")
                    break

            if entry_index is None:
                logger.warning(f"Item_id={split_data.item_id} not found in inventory_id={inventory_id}")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Item {split_data.item_id} not found in inventory {inventory_id}",
                            error_code=GameError.INV_ITEM_NOT_FOUND,
                        ),
                    ],
                    response_data=None,
                )

            # Perform the split - pass entry_index, not item_id
            logger.debug(f"Calling split_stack() with entry_index={entry_index}, quantity={split_data.quantity_to_split}")
            split_results = split_stack(
                inventory,
                entry_index,
                split_data.quantity_to_split,
            )

            if not is_ok(split_results):
                logger.warning(f"Split operation failed: {split_results[0].message if split_results else 'unknown'}")
                return InventoryResponse(
                    results=split_results,
                    response_data=None,
                )

            logger.debug(f"Split successful, now inventory has {len(inventory.entries)} entries")

            # Save the updated inventory to database
            logger.debug("Saving updated inventory to database...")
            save_results = self.db.save_inventory(
                self.database,
                inventory,
            )

            if is_ok(save_results):
                logger.info(f"SUCCESS: Split stack completed for inventory_id={inventory_id}")
                # Update cache with modified inventory
                self.cache.put(inventory_id, inventory)

                response_data = InventoryResponseData(
                    split_stack=SplitStackResponseData(
                        inventory=inventory,
                    ),
                )
                results = split_results + save_results
                return InventoryResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.error(f"Failed to save inventory after split: {save_results[0].message if save_results else 'unknown'}")
                return InventoryResponse(
                    results=save_results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in split_stack: {type(e).__name__}: {str(e)}")
            return InventoryResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to split stack: {str(e)}",
                        error_code=GameError.INV_OPERATION_FAILED,
                    ),
                ],
                response_data=None,
            )

    def transfer_item(self, request: InventoryRequest) -> InventoryResponse:
        """Transfer items between inventories. Checks cache and updates both inventories."""
        logger.info("=== TRANSFER_ITEM request ===")
        try:
            if not request.data.transfer_item:
                logger.error("Request data missing transfer_item field")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain transfer_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            transfer_data = request.data.transfer_item
            source_id = transfer_data.source_inventory_id
            dest_id = transfer_data.destination_inventory_id
            logger.info(f"Transferring item_id={transfer_data.item_id}, quantity={transfer_data.quantity} from inventory_id={source_id} to inventory_id={dest_id}")

            # Load the item from database - inventory.transfer_item needs Item object, not item_id
            logger.debug(f"Loading item_id={transfer_data.item_id} from database...")
            item_result, item = self.db.load_item(
                self.database,
                transfer_data.item_id,
            )
            if not item:
                logger.error(f"Item_id={transfer_data.item_id} not found in database")
                return InventoryResponse(
                    results=[item_result],
                    response_data=None,
                )
            logger.debug(f"Loaded item: {item.internal_name}")

            # Check cache for source inventory
            logger.debug(f"Loading source inventory_id={source_id}...")
            source_inv = self.cache.get(source_id)
            if not source_inv:
                # Cache miss - load from database
                logger.debug(f"Cache miss, loading source from DATABASE")
                result1, source_inv = self.db.load_inventory(
                    self.database,
                    source_id,
                )
                if not source_inv:
                    logger.error(f"Source inventory_id={source_id} not found")
                    return InventoryResponse(
                        results=[result1],
                        response_data=None,
                    )

            # Check cache for destination inventory
            logger.debug(f"Loading destination inventory_id={dest_id}...")
            dest_inv = self.cache.get(dest_id)
            if not dest_inv:
                # Cache miss - load from database
                logger.debug(f"Cache miss, loading destination from DATABASE")
                result2, dest_inv = self.db.load_inventory(
                    self.database,
                    dest_id,
                )
                if not dest_inv:
                    logger.error(f"Destination inventory_id={dest_id} not found")
                    return InventoryResponse(
                        results=[result2],
                        response_data=None,
                    )

            # Perform the transfer - pass Item object, not item_id
            logger.debug(f"Calling transfer_item() with quantity={transfer_data.quantity}")
            logger.debug(f"Source has {len(source_inv.entries)} entries, destination has {len(dest_inv.entries)} entries")
            transfer_results = transfer_item(
                source_inv,
                dest_inv,
                item,
                transfer_data.quantity,
            )

            if not is_ok(transfer_results):
                logger.warning(f"Transfer failed: {transfer_results[0].message if transfer_results else 'unknown'}")
                return InventoryResponse(
                    results=transfer_results,
                    response_data=None,
                )

            logger.debug(f"Transfer successful. Source now has {len(source_inv.entries)} entries, destination has {len(dest_inv.entries)} entries")

            # Save both inventories to database
            logger.debug("Saving both inventories to database...")
            save_results1 = self.db.save_inventory(
                self.database,
                source_inv,
            )
            save_results2 = self.db.save_inventory(
                self.database,
                dest_inv,
            )

            if is_ok(save_results1) and is_ok(save_results2):
                logger.info(f"SUCCESS: Transfer completed from inventory_id={source_id} to inventory_id={dest_id}")
                # Update both inventories in cache
                self.cache.put(source_id, source_inv)
                self.cache.put(dest_id, dest_inv)

                response_data = InventoryResponseData(
                    transfer_item=TransferItemResponseData(
                        source_inventory=source_inv,
                        destination_inventory=dest_inv,
                    ),
                )
                return InventoryResponse(
                    results=transfer_results + save_results1 + save_results2,
                    response_data=response_data,
                )
            else:
                logger.error(f"Failed to save inventories after transfer")
                return InventoryResponse(
                    results=save_results1 + save_results2,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in transfer_item: {type(e).__name__}: {str(e)}")
            return InventoryResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to transfer item: {str(e)}",
                        error_code=GameError.INV_OPERATION_FAILED,
                    ),
                ],
                response_data=None,
            )

    def list_records(self, request: InventoryRequest) -> InventoryResponse:
        """List inventories with pagination."""
        logger.info("=== LIST inventory records request ===")
        try:
            if not request.data.list_inventory:
                logger.error("Request data missing list_inventory field")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain list_inventory",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            list_data = request.data.list_inventory
            page = list_data.page
            results_per_page = list_data.results_per_page
            search_string = list_data.search_string if hasattr(list_data, 'search_string') else None

            logger.info(f"Listing inventories: page={page}, results_per_page={results_per_page}, search_string={search_string}")

            result, inventories, total_count = self.db.list_inventory(
                self.database,
                page,
                results_per_page,
                search_string=search_string,
            )

            if inventories is not None:
                logger.info(f"SUCCESS: Listed {len(inventories)} inventories (total: {total_count})")
                response_data = InventoryResponseData(
                    list_inventory=ListInventoryResponseData(
                        inventories=inventories,
                        total_count=total_count,
                    ),
                )
                return InventoryResponse(
                    results=[result],
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not list inventories - {result.message}")
                return InventoryResponse(
                    results=[result],
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in list_records: {type(e).__name__}: {str(e)}")
            return InventoryResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to list inventories: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )
