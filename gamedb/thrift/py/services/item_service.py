import sys
sys.path.append('../../gen-py')
sys.path.append('..')

from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

from game.ttypes import (
    ItemRequest,
    ItemResponse,
    ItemRequestData,
    ItemResponseData,
    CreateItemRequestData,
    CreateItemResponseData,
    LoadItemRequestData,
    LoadItemResponseData,
    SaveItemRequestData,
    SaveItemResponseData,
    DestroyItemRequestData,
    DestroyItemResponseData,
    ListItemRequestData,
    ListItemResponseData,
    Item,
    GameResult,
    StatusType,
    GameError,
    ServiceMetadata,
    MethodDescription,
    EnumDefinition,
    FieldEnumMapping,
)
from game.ItemService import Iface as ItemServiceIface
from db import DB
from common import is_ok
from services.base_service import BaseServiceHandler


class ItemServiceHandler(BaseServiceHandler, ItemServiceIface):
    """
    Implementation of the ItemService thrift interface.
    Handles item CRUD operations using the DB layer.
    """

    def __init__(self, db: DB, database: str):
        BaseServiceHandler.__init__(self, ItemServiceHandler)
        self.db = db
        self.database = database

    def create(self, request: ItemRequest) -> ItemResponse:
        """Create a new item."""
        logger.info("=== CREATE item request ===")
        try:
            if not request.data.create_item:
                logger.error("Request data missing create_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain create_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            create_data = request.data.create_item
            logger.info(f"Creating item with internal_name={create_data.item.internal_name}")

            results = self.db.create_item(
                self.database,
                create_data.item,
            )

            if is_ok(results):
                logger.info(f"SUCCESS: Created item with id={create_data.item.id}")
                response_data = ItemResponseData(
                    create_item=CreateItemResponseData(
                        item=create_data.item,
                    ),
                )
                return ItemResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not create item - {results[0].message if results else 'unknown error'}")
                return ItemResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in create: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to create item: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def load(self, request: ItemRequest) -> ItemResponse:
        """Load an item by ID."""
        logger.info("=== LOAD item request ===")
        try:
            if not request.data.load_item:
                logger.error("Request data missing load_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain load_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            load_data = request.data.load_item
            item_id = load_data.item_id
            logger.info(f"Loading item_id={item_id}")

            # Determine table to use based on backing_table if provided
            table = None
            if hasattr(load_data, 'backing_table') and load_data.backing_table is not None:
                from game.ttypes import TABLE2STR
                table = TABLE2STR.get(load_data.backing_table)
                logger.info(f"Using table={table} from backing_table={load_data.backing_table}")

            result, item = self.db.load_item(
                self.database,
                item_id,
                table,
            )

            if item:
                logger.info(f"SUCCESS: Loaded item_id={item_id}")
                response_data = ItemResponseData(
                    load_item=LoadItemResponseData(
                        item=item,
                    ),
                )
                return ItemResponse(
                    results=[result],
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Item_id={item_id} not found in database")
                return ItemResponse(
                    results=[result],
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in load: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to load item: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )

    def save(self, request: ItemRequest) -> ItemResponse:
        """Save (create or update) an item."""
        logger.info("=== SAVE item request ===")
        try:
            if not request.data.save_item:
                logger.error("Request data missing save_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain save_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            save_data = request.data.save_item
            item_id = save_data.item.id if save_data.item.id else "NEW"
            logger.info(f"Saving item_id={item_id}")

            results = self.db.save_item(
                self.database,
                save_data.item,
            )

            if is_ok(results):
                logger.info(f"SUCCESS: Saved item_id={save_data.item.id}")
                response_data = ItemResponseData(
                    save_item=SaveItemResponseData(
                        item=save_data.item,
                    ),
                )
                return ItemResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not save item - {results[0].message if results else 'unknown error'}")
                return ItemResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in save: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to save item: {str(e)}",
                        error_code=GameError.DB_INSERT_FAILED,
                    ),
                ],
                response_data=None,
            )

    def destroy(self, request: ItemRequest) -> ItemResponse:
        """Destroy (delete) an item by ID."""
        logger.info("=== DESTROY item request ===")
        try:
            if not request.data.destroy_item:
                logger.error("Request data missing destroy_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain destroy_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            destroy_data = request.data.destroy_item
            item_id = destroy_data.item_id
            logger.info(f"Destroying item_id={item_id}")

            results = self.db.destroy_item(
                self.database,
                item_id,
            )

            if is_ok(results):
                logger.info(f"SUCCESS: Destroyed item_id={item_id}")
                response_data = ItemResponseData(
                    destroy_item=DestroyItemResponseData(
                        item_id=item_id,
                    ),
                )
                return ItemResponse(
                    results=results,
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not destroy item - {results[0].message if results else 'unknown error'}")
                return ItemResponse(
                    results=results,
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in destroy: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to destroy item: {str(e)}",
                        error_code=GameError.DB_DELETE_FAILED,
                    ),
                ],
                response_data=None,
            )

    def list_records(self, request: ItemRequest) -> ItemResponse:
        """List items with pagination and optional search."""
        logger.info("=== LIST item records request ===")
        try:
            if not request.data.list_item:
                logger.error("Request data missing list_item field")
                return ItemResponse(
                    results=[
                        GameResult(
                            status=StatusType.FAILURE,
                            message="Request data must contain list_item",
                            error_code=GameError.DB_INVALID_DATA,
                        ),
                    ],
                    response_data=None,
                )

            list_data = request.data.list_item
            page = list_data.page
            results_per_page = list_data.results_per_page
            search_string = list_data.search_string if hasattr(list_data, 'search_string') else None

            logger.info(f"Listing items: page={page}, results_per_page={results_per_page}, search_string={search_string}")

            result, items, total_count = self.db.list_item(
                self.database,
                page,
                results_per_page,
                search_string=search_string,
            )

            if items is not None:
                logger.info(f"SUCCESS: Listed {len(items)} items (total: {total_count})")
                response_data = ItemResponseData(
                    list_item=ListItemResponseData(
                        items=items,
                        total_count=total_count,
                    ),
                )
                return ItemResponse(
                    results=[result],
                    response_data=response_data,
                )
            else:
                logger.warning(f"FAILURE: Could not list items - {result.message}")
                return ItemResponse(
                    results=[result],
                    response_data=None,
                )

        except Exception as e:
            logger.error(f"EXCEPTION in list_records: {type(e).__name__}: {str(e)}")
            return ItemResponse(
                results=[
                    GameResult(
                        status=StatusType.FAILURE,
                        message=f"Failed to list items: {str(e)}",
                        error_code=GameError.DB_QUERY_FAILED,
                    ),
                ],
                response_data=None,
            )
