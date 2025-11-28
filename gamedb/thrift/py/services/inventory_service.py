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
from db_models.models import Inventory, InventoryEntry, Item, MobileItem
from inventory import split_stack, transfer_item
from common import is_ok
from services.base_service import BaseServiceHandler


class InventoryServiceHandler(BaseServiceHandler, InventoryServiceIface):
    """
    Implementation of the InventoryService thrift interface.
    Handles inventory operations using db_models and inventory.py functions.
    """

    def __init__(self):
        BaseServiceHandler.__init__(self, InventoryServiceHandler)

    def load(self, request: InventoryRequest) -> InventoryResponse:
        """Load an inventory by ID."""
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

            # Load from database using ActiveRecord
            inventory = Inventory.find(inventory_id)

            if inventory:
                logger.info(
                    f"SUCCESS: Loaded inventory_id={inventory_id} from DATABASE"
                )

                # Convert to Thrift
                results, thrift_inventory = inventory.into_thrift()

                if thrift_inventory:
                    response_data = InventoryResponseData(
                        load_inventory=LoadInventoryResponseData(
                            inventory=thrift_inventory,
                        ),
                    )
                    return InventoryResponse(
                        results=results,
                        response_data=response_data,
                    )
                else:
                    # Conversion failed
                    return InventoryResponse(
                        results=results,
                        response_data=None,
                    )
            else:
                logger.warning(
                    f"FAILURE: Inventory_id={inventory_id} not found in database"
                )
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Inventory {inventory_id} not found",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ],
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
        """Create a new inventory."""
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
            entry_count = len(create_data.inventory.entries) if create_data.inventory.entries else 0
            logger.debug(f"Inventory has {entry_count} entries")

            # Create model and populate from Thrift
            inventory = Inventory()
            inventory.from_thrift(create_data.inventory)

            # Save to database
            inventory.save()

            logger.info(
                f"SUCCESS: Created inventory with id={inventory.get_id()}"
            )

            # Convert back to Thrift
            results, thrift_inventory = inventory.into_thrift()

            if thrift_inventory:
                response_data = InventoryResponseData(
                    create_inventory=CreateInventoryResponseData(
                        inventory=thrift_inventory,
                    ),
                )
                return InventoryResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                # Conversion failed
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
        """Save (create or update) an inventory."""
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
            entry_count = len(save_data.inventory.entries) if save_data.inventory.entries else 0
            logger.debug(f"Inventory has {entry_count} entries")

            # Create model and populate from Thrift
            inventory = Inventory()
            inventory.from_thrift(save_data.inventory)

            # Save to database
            inventory.save()

            logger.info(f"SUCCESS: Saved inventory_id={inventory.get_id()}")

            # Convert back to Thrift
            results, thrift_inventory = inventory.into_thrift()

            if thrift_inventory:
                response_data = InventoryResponseData(
                    save_inventory=SaveInventoryResponseData(
                        inventory=thrift_inventory,
                    ),
                )
                return InventoryResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                # Conversion failed
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
        """Split a stack of items within an inventory."""
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

            # Load from database using ActiveRecord
            logger.debug(f"Loading from DATABASE for inventory_id={inventory_id}")
            inventory_model = Inventory.find(inventory_id)

            if not inventory_model:
                logger.error(f"Inventory_id={inventory_id} not found")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Inventory {inventory_id} not found",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ],
                    response_data=None,
                )

            # Convert to Thrift for inventory.py function
            _, thrift_inventory = inventory_model.into_thrift()

            # Find the entry index that matches the item_id
            # inventory.split_stack expects entry_index, not item_id
            logger.debug(
                f"Searching for item_id={split_data.item_id} in {len(thrift_inventory.entries)} entries"
            )
            entry_index = None
            for idx, entry in enumerate(thrift_inventory.entries):
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
            # Note: split_stack() from inventory.py mutates the thrift_inventory object
            logger.debug(
                f"Calling split_stack() with entry_index={entry_index}, quantity={split_data.quantity_to_split}"
            )
            split_results = split_stack(
                thrift_inventory,
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
                f"Split successful, now inventory has {len(thrift_inventory.entries)} entries"
            )

            # Convert modified Thrift back to model and save
            logger.debug("Saving updated inventory to database...")
            inventory_model.from_thrift(thrift_inventory)
            inventory_model.save()

            logger.info(
                f"SUCCESS: Split stack completed for inventory_id={inventory_id}"
            )

            # Convert final state back to Thrift for response
            save_results, final_thrift_inventory = inventory_model.into_thrift()

            response_data = InventoryResponseData(
                split_stack=SplitStackResponseData(
                    inventory=final_thrift_inventory,
                ),
            )
            results = split_results + save_results
            return InventoryResponse(
                results=results,
                response_data=response_data,
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
        """Transfer items between inventories."""
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

            # Load the item from database using ActiveRecord
            logger.debug(f"Loading item_id={transfer_data.item_id} from database...")
            item_model = Item.find(transfer_data.item_id)
            if not item_model:
                logger.error(f"Item_id={transfer_data.item_id} not found in database")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Item {transfer_data.item_id} not found",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ],
                    response_data=None,
                )

            # Convert item to Thrift for inventory.py function
            _, thrift_item = item_model.into_thrift()
            logger.debug(f"Loaded item: {thrift_item.internal_name}")

            # Load source inventory using ActiveRecord
            logger.debug(f"Loading source inventory_id={source_id}...")
            source_model = Inventory.find(source_id)
            if not source_model:
                logger.error(f"Source inventory_id={source_id} not found")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Source inventory {source_id} not found",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ],
                    response_data=None,
                )

            # Convert source to Thrift
            _, thrift_source_inv = source_model.into_thrift()

            # Load destination inventory using ActiveRecord
            logger.debug(f"Loading destination inventory_id={dest_id}...")
            dest_model = Inventory.find(dest_id)
            if not dest_model:
                logger.error(f"Destination inventory_id={dest_id} not found")
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message=f"Destination inventory {dest_id} not found",
                            error_code=GameError.DB_RECORD_NOT_FOUND,
                        ),
                    ],
                    response_data=None,
                )

            # Convert destination to Thrift
            _, thrift_dest_inv = dest_model.into_thrift()

            # Perform the transfer - inventory.py function mutates both Thrift inventories
            logger.debug(
                f"Calling transfer_item() with quantity={transfer_data.quantity}"
            )
            logger.debug(
                f"Source has {len(thrift_source_inv.entries)} entries, destination has {len(thrift_dest_inv.entries)} entries"
            )
            transfer_results = transfer_item(
                thrift_source_inv,
                thrift_dest_inv,
                thrift_item,
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
                f"Transfer successful. Source now has {len(thrift_source_inv.entries)} entries, destination has {len(thrift_dest_inv.entries)} entries"
            )

            # Convert modified Thrift objects back to models and save both
            logger.debug("Saving both inventories to database...")
            source_model.from_thrift(thrift_source_inv)
            dest_model.from_thrift(thrift_dest_inv)

            source_model.save()
            dest_model.save()

            logger.info(
                f"SUCCESS: Transfer completed from inventory_id={source_id} to inventory_id={dest_id}"
            )

            # Convert final state back to Thrift for response
            save_results1, final_source = source_model.into_thrift()
            save_results2, final_dest = dest_model.into_thrift()

            response_data = InventoryResponseData(
                transfer_item=TransferItemResponseData(
                    source_inventory=final_source,
                    destination_inventory=final_dest,
                ),
            )
            return InventoryResponse(
                results=transfer_results + save_results1 + save_results2,
                response_data=response_data,
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

            logger.info(
                f"Listing inventories: page={page}, results_per_page={results_per_page}"
            )

            # Query with pagination
            connection = Inventory._create_connection()
            cursor = connection.cursor(dictionary=True)

            try:
                # Get total count
                cursor.execute("SELECT COUNT(*) as count FROM inventories")
                total_count = cursor.fetchone()['count']

                # Get paginated results
                offset = page * results_per_page
                cursor.execute(
                    "SELECT * FROM inventories ORDER BY id LIMIT %s OFFSET %s",
                    (results_per_page, offset),
                )
                rows = cursor.fetchall()

                # Convert to models then to Thrift
                thrift_inventories = []
                for row in rows:
                    inventory = Inventory()
                    inventory._data = row
                    _, thrift_inv = inventory.into_thrift()
                    if thrift_inv:
                        thrift_inventories.append(thrift_inv)

                logger.info(
                    f"SUCCESS: Listed {len(thrift_inventories)} inventories (total: {total_count})"
                )

                response_data = InventoryResponseData(
                    list_inventory=ListInventoryResponseData(
                        inventories=thrift_inventories,
                        total_count=total_count,
                    ),
                )
                return InventoryResponse(
                    results=[
                        GameResult(
                            status=StatusType.SUCCESS,
                            message=f"Successfully listed inventories",
                        ),
                    ],
                    response_data=response_data,
                )

            finally:
                cursor.close()
                connection.close()

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
