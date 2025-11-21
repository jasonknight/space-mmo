import sys
sys.path.append('../gen-py')

from collections import OrderedDict
from typing import Optional
from copy import deepcopy

from game.ttypes import (
    Request,
    Response,
    RequestData,
    ResponseData,
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
            return None

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
            self.cache.popitem(last=False)

    def invalidate(self, key: int) -> None:
        """Remove an inventory from the cache."""
        if key in self.cache:
            del self.cache[key]

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
        ]

        return ServiceMetadata(
            service_name="InventoryService",
            version="1.0",
            description="Service for managing game inventories with create, load, save, split, and transfer operations",
            methods=methods,
            enums=enums,
        )

    def load(self, request: Request) -> Response:
        """Load an inventory by ID. Checks cache first before querying database."""
        try:
            if not request.data.load_inventory:
                return Response(
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

            # Check cache first
            cached_inventory = self.cache.get(inventory_id)
            if cached_inventory:
                result = GameResult(
                    status=StatusType.SUCCESS,
                    message=f"Successfully loaded inventory id={inventory_id} from cache",
                )
                response_data = ResponseData(
                    load_inventory=LoadInventoryResponseData(
                        inventory=cached_inventory,
                    ),
                )
                return Response(
                    results=[result],
                    response_data=response_data,
                )

            # Cache miss - load from database
            result, inventory = self.db.load_inventory(
                self.database,
                inventory_id,
            )

            if inventory:
                # Store in cache for future requests
                self.cache.put(inventory_id, inventory)

                response_data = ResponseData(
                    load_inventory=LoadInventoryResponseData(
                        inventory=inventory,
                    ),
                )
                return Response(
                    results=[result],
                    response_data=response_data,
                )
            else:
                return Response(
                    results=[result],
                    response_data=None,
                )

        except Exception as e:
            return Response(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to load inventory: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )

    def create(self, request: Request) -> Response:
        """Create a new inventory. Populates cache after successful creation."""
        try:
            if not request.data.create_inventory:
                return Response(
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
            results = self.db.create_inventory(
                self.database,
                create_data.inventory,
            )

            if is_ok(results):
                # Add to cache after successful creation
                if create_data.inventory.id is not None:
                    self.cache.put(create_data.inventory.id, create_data.inventory)

                response_data = ResponseData(
                    create_inventory=CreateInventoryResponseData(
                        inventory=create_data.inventory,
                    ),
                )
                return Response(
                    results=results,
                    response_data=response_data,
                )
            else:
                return Response(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            return Response(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to create inventory: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def save(self, request: Request) -> Response:
        """Save (create or update) an inventory. Updates cache after successful save."""
        try:
            if not request.data.save_inventory:
                return Response(
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
            results = self.db.save_inventory(
                self.database,
                save_data.inventory,
            )

            if is_ok(results):
                # Update cache after successful save
                if save_data.inventory.id is not None:
                    self.cache.put(save_data.inventory.id, save_data.inventory)

                response_data = ResponseData(
                    save_inventory=SaveInventoryResponseData(
                        inventory=save_data.inventory,
                    ),
                )
                return Response(
                    results=results,
                    response_data=response_data,
                )
            else:
                return Response(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            return Response(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to save inventory: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def split_stack(self, request: Request) -> Response:
        """Split a stack of items within an inventory. Checks cache and updates it."""
        try:
            if not request.data.split_stack:
                return Response(
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

            # Check cache first
            inventory = self.cache.get(inventory_id)
            result = None

            if not inventory:
                # Cache miss - load from database
                result, inventory = self.db.load_inventory(
                    self.database,
                    inventory_id,
                )

                if not inventory:
                    return Response(
                        results=[result],
                        response_data=None,
                    )

            # Find the entry index that matches the item_id
            # inventory.split_stack expects entry_index, not item_id
            entry_index = None
            for idx, entry in enumerate(inventory.entries):
                if entry.item_id == split_data.item_id:
                    entry_index = idx
                    break

            if entry_index is None:
                return Response(
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
            split_results = split_stack(
                inventory,
                entry_index,
                split_data.quantity_to_split,
            )

            if not is_ok(split_results):
                return Response(
                    results=split_results,
                    response_data=None,
                )

            # Save the updated inventory to database
            save_results = self.db.save_inventory(
                self.database,
                inventory,
            )

            if is_ok(save_results):
                # Update cache with modified inventory
                self.cache.put(inventory_id, inventory)

                response_data = ResponseData(
                    split_stack=SplitStackResponseData(
                        inventory=inventory,
                    ),
                )
                results = split_results + save_results
                return Response(
                    results=results,
                    response_data=response_data,
                )
            else:
                return Response(
                    results=save_results,
                    response_data=None,
                )

        except Exception as e:
            return Response(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to split stack: {str(e)}",
                        error_code=GameError.INV_OPERATION_FAILED,
                    ),
                ],
                response_data=None,
            )

    def transfer_item(self, request: Request) -> Response:
        """Transfer items between inventories. Checks cache and updates both inventories."""
        try:
            if not request.data.transfer_item:
                return Response(
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

            # Load the item from database - inventory.transfer_item needs Item object, not item_id
            item_result, item = self.db.load_item(
                self.database,
                transfer_data.item_id,
            )
            if not item:
                return Response(
                    results=[item_result],
                    response_data=None,
                )

            # Check cache for source inventory
            source_inv = self.cache.get(source_id)
            if not source_inv:
                # Cache miss - load from database
                result1, source_inv = self.db.load_inventory(
                    self.database,
                    source_id,
                )
                if not source_inv:
                    return Response(
                        results=[result1],
                        response_data=None,
                    )

            # Check cache for destination inventory
            dest_inv = self.cache.get(dest_id)
            if not dest_inv:
                # Cache miss - load from database
                result2, dest_inv = self.db.load_inventory(
                    self.database,
                    dest_id,
                )
                if not dest_inv:
                    return Response(
                        results=[result2],
                        response_data=None,
                    )

            # Perform the transfer - pass Item object, not item_id
            transfer_results = transfer_item(
                source_inv,
                dest_inv,
                item,
                transfer_data.quantity,
            )

            if not is_ok(transfer_results):
                return Response(
                    results=transfer_results,
                    response_data=None,
                )

            # Save both inventories to database
            save_results1 = self.db.save_inventory(
                self.database,
                source_inv,
            )
            save_results2 = self.db.save_inventory(
                self.database,
                dest_inv,
            )

            if is_ok(save_results1) and is_ok(save_results2):
                # Update both inventories in cache
                self.cache.put(source_id, source_inv)
                self.cache.put(dest_id, dest_inv)

                response_data = ResponseData(
                    transfer_item=TransferItemResponseData(
                        source_inventory=source_inv,
                        destination_inventory=dest_inv,
                    ),
                )
                return Response(
                    results=transfer_results + save_results1 + save_results2,
                    response_data=response_data,
                )
            else:
                return Response(
                    results=save_results1 + save_results2,
                    response_data=None,
                )

        except Exception as e:
            return Response(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to transfer item: {str(e)}",
                        error_code=GameError.INV_OPERATION_FAILED,
                    ),
                ],
                response_data=None,
            )
