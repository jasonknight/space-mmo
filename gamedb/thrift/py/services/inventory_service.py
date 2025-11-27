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
from models.inventory_model import InventoryModel
from models.item_model import ItemModel
from inventory import split_stack, transfer_item
from common import is_ok
from services.lru_cache import LRUCache
from services.base_service import BaseServiceHandler


class InventoryServiceHandler(BaseServiceHandler, InventoryServiceIface):
    """
    Implementation of the InventoryService thrift interface.
    Handles inventory operations using the InventoryModel layer and inventory.py functions.
    Includes an LRU cache to reduce database queries for frequently accessed inventories.
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        cache_size: int = 1000,
    ):
        BaseServiceHandler.__init__(self, InventoryServiceHandler)
        self.inventory_model = InventoryModel(host, user, password, database)
        self.item_model = ItemModel(host, user, password, database)
        self.database = database
        self.cache = LRUCache(max_size=cache_size)

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
            logger.debug(
                f"Cache miss, loading from DATABASE for inventory_id={inventory_id}"
            )
            result, inventory = self.inventory_model.load(inventory_id)

            if inventory:
                logger.info(
                    f"SUCCESS: Loaded inventory_id={inventory_id} from DATABASE"
                )
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
                logger.warning(
                    f"FAILURE: Inventory_id={inventory_id} not found in database"
                )
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
            logger.info(
                f"Creating inventory with max_entries={create_data.inventory.max_entries}, max_volume={create_data.inventory.max_volume}"
            )
            logger.debug(f"Inventory has {len(create_data.inventory.entries)} entries")

            results = self.db.create_inventory(
                self.database,
                create_data.inventory,
            )

            if is_ok(results):
                logger.info(
                    f"SUCCESS: Created inventory with id={create_data.inventory.id}"
                )
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
                logger.warning(
                    f"FAILURE: Could not create inventory - {results[0].message if results else 'unknown error'}"
                )
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
                logger.warning(
                    f"FAILURE: Could not save inventory - {results[0].message if results else 'unknown error'}"
                )
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
            logger.info(
                f"Splitting stack in inventory_id={inventory_id}, item_id={split_data.item_id}, quantity={split_data.quantity_to_split}"
            )

            # Check cache first
            logger.debug("Checking cache...")
            inventory = self.cache.get(inventory_id)
            result = None

            if not inventory:
                # Cache miss - load from database
                logger.debug(
                    f"Cache miss, loading from DATABASE for inventory_id={inventory_id}"
                )
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
            logger.debug(
                f"Searching for item_id={split_data.item_id} in {len(inventory.entries)} entries"
            )
            entry_index = None
            for idx, entry in enumerate(inventory.entries):
                if entry.item_id == split_data.item_id:
                    entry_index = idx
                    logger.debug(
                        f"Found item at entry_index={idx}, current quantity={entry.quantity}"
                    )
                    break

            if entry_index is None:
                logger.warning(
                    f"Item_id={split_data.item_id} not found in inventory_id={inventory_id}"
                )
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
            logger.debug(
                f"Calling split_stack() with entry_index={entry_index}, quantity={split_data.quantity_to_split}"
            )
            split_results = split_stack(
                inventory,
                entry_index,
                split_data.quantity_to_split,
            )

            if not is_ok(split_results):
                logger.warning(
                    f"Split operation failed: {split_results[0].message if split_results else 'unknown'}"
                )
                return InventoryResponse(
                    results=split_results,
                    response_data=None,
                )

            logger.debug(
                f"Split successful, now inventory has {len(inventory.entries)} entries"
            )

            # Save the updated inventory to database
            logger.debug("Saving updated inventory to database...")
            save_results = self.db.save_inventory(
                self.database,
                inventory,
            )

            if is_ok(save_results):
                logger.info(
                    f"SUCCESS: Split stack completed for inventory_id={inventory_id}"
                )
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
                logger.error(
                    f"Failed to save inventory after split: {save_results[0].message if save_results else 'unknown'}"
                )
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
            logger.info(
                f"Transferring item_id={transfer_data.item_id}, quantity={transfer_data.quantity} from inventory_id={source_id} to inventory_id={dest_id}"
            )

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
            logger.debug(
                f"Calling transfer_item() with quantity={transfer_data.quantity}"
            )
            logger.debug(
                f"Source has {len(source_inv.entries)} entries, destination has {len(dest_inv.entries)} entries"
            )
            transfer_results = transfer_item(
                source_inv,
                dest_inv,
                item,
                transfer_data.quantity,
            )

            if not is_ok(transfer_results):
                logger.warning(
                    f"Transfer failed: {transfer_results[0].message if transfer_results else 'unknown'}"
                )
                return InventoryResponse(
                    results=transfer_results,
                    response_data=None,
                )

            logger.debug(
                f"Transfer successful. Source now has {len(source_inv.entries)} entries, destination has {len(dest_inv.entries)} entries"
            )

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
                logger.info(
                    f"SUCCESS: Transfer completed from inventory_id={source_id} to inventory_id={dest_id}"
                )
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
            page = max(0, list_data.page)
            results_per_page = list_data.results_per_page
            search_string = (
                list_data.search_string if hasattr(list_data, "search_string") else None
            )

            logger.info(
                f"Listing inventories: page={page}, results_per_page={results_per_page}, search_string={search_string}"
            )

            result, inventories, total_count = self.db.list_inventory(
                self.database,
                page,
                results_per_page,
                search_string=search_string,
            )

            if inventories is not None:
                logger.info(
                    f"SUCCESS: Listed {len(inventories)} inventories (total: {total_count})"
                )
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
                logger.warning(
                    f"FAILURE: Could not list inventories - {result.message}"
                )
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
