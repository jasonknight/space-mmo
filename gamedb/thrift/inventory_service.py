import sys
sys.path.append('gen-py')

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
)
from game.InventoryService import Iface as InventoryServiceIface
from db import DB
from inventory import split_stack, transfer_item
from common import is_ok


class InventoryServiceHandler(InventoryServiceIface):
    """
    Implementation of the InventoryService thrift interface.
    Handles inventory operations using the DB layer and inventory.py functions.
    """

    def __init__(self, db: DB, database: str):
        self.db = db
        self.database = database

    def load(self, request: Request) -> Response:
        """Load an inventory by ID."""
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
            result, inventory = self.db.load_inventory(
                self.database,
                load_data.inventory_id,
            )

            if inventory:
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
        """Create a new inventory."""
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
        """Save (create or update) an inventory."""
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
        """Split a stack of items within an inventory."""
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

            # Load the inventory
            result, inventory = self.db.load_inventory(
                self.database,
                split_data.inventory_id,
            )

            if not inventory:
                return Response(
                    results=[result],
                    response_data=None,
                )

            # Perform the split
            split_result = split_stack(
                inventory,
                split_data.item_id,
                split_data.quantity_to_split,
            )

            if not is_ok([split_result]):
                return Response(
                    results=[split_result],
                    response_data=None,
                )

            # Save the updated inventory
            save_results = self.db.save_inventory(
                self.database,
                inventory,
            )

            if is_ok(save_results):
                response_data = ResponseData(
                    split_stack=SplitStackResponseData(
                        inventory=inventory,
                    ),
                )
                return Response(
                    results=[split_result] + save_results,
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
                        error_code=GameError.INVENTORY_OPERATION_FAILED,
                    ),
                ],
                response_data=None,
            )

    def transfer_item(self, request: Request) -> Response:
        """Transfer items between inventories."""
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

            # Load both inventories
            result1, source_inv = self.db.load_inventory(
                self.database,
                transfer_data.source_inventory_id,
            )
            if not source_inv:
                return Response(
                    results=[result1],
                    response_data=None,
                )

            result2, dest_inv = self.db.load_inventory(
                self.database,
                transfer_data.destination_inventory_id,
            )
            if not dest_inv:
                return Response(
                    results=[result2],
                    response_data=None,
                )

            # Perform the transfer
            transfer_result = transfer_item(
                source_inv,
                dest_inv,
                transfer_data.item_id,
                transfer_data.quantity,
            )

            if not is_ok([transfer_result]):
                return Response(
                    results=[transfer_result],
                    response_data=None,
                )

            # Save both inventories
            save_results1 = self.db.save_inventory(
                self.database,
                source_inv,
            )
            save_results2 = self.db.save_inventory(
                self.database,
                dest_inv,
            )

            if is_ok(save_results1) and is_ok(save_results2):
                response_data = ResponseData(
                    transfer_item=TransferItemResponseData(
                        source_inventory=source_inv,
                        destination_inventory=dest_inv,
                    ),
                )
                return Response(
                    results=[transfer_result] + save_results1 + save_results2,
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
                        error_code=GameError.INVENTORY_OPERATION_FAILED,
                    ),
                ],
                response_data=None,
            )
