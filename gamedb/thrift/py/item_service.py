import sys
sys.path.append('../gen-py')

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


class ItemServiceHandler(ItemServiceIface):
    """
    Implementation of the ItemService thrift interface.
    Handles item CRUD operations using the DB layer.
    """

    def __init__(self, db: DB, database: str):
        self.db = db
        self.database = database

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
            EnumDefinition(
                enum_name="ItemType",
                values={
                    "VIRTUAL": 1,
                    "CONTAINER": 2,
                    "WEAPON": 3,
                    "RAWMATERIAL": 4,
                    "REFINEDMATERIAL": 5,
                },
                description="Item type classification",
            ),
            EnumDefinition(
                enum_name="AttributeType",
                values={
                    "TRANSLATED_NAME": 1,
                    "TRANSLATED_SHORT_DESCRIPTION": 2,
                    "TRANSLATED_LONG_DESCRIPTION": 3,
                    "TRANSLATED_ASSET": 4,
                    "UNTRANSLATED_ASSET": 5,
                    "QUANTITY": 6,
                    "GALACTIC_POSITION": 7,
                    "SOLAR_POSITION": 8,
                    "GLOBAL_POSITION": 9,
                    "LOCAL_POSITION": 10,
                    "SIZE": 11,
                    "ITEM": 12,
                    "PURITY": 13,
                    "VOLUME": 14,
                },
                description="Attribute types for items",
            ),
        ]

        # Define methods with examples
        methods = [
            MethodDescription(
                method_name="create",
                description="Create a new item in the database",
                example_request_json='''{
    "data": {
        "create_item": {
            "item": {
                "internal_name": "iron_ore",
                "attributes": {},
                "max_stack_size": 1000,
                "item_type": "RAWMATERIAL"
            }
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully created Item id=1, internal_name=iron_ore"
    }],
    "response_data": {
        "create_item": {
            "item": {
                "id": 1,
                "internal_name": "iron_ore",
                "attributes": {},
                "max_stack_size": 1000,
                "item_type": "RAWMATERIAL"
            }
        }
    }
}''',
                request_enum_fields=[
                    FieldEnumMapping(field_path="data.create_item.item.item_type", enum_name="ItemType"),
                ],
                response_enum_fields=[
                    FieldEnumMapping(field_path="results[].status", enum_name="StatusType"),
                    FieldEnumMapping(field_path="results[].error_code", enum_name="GameError"),
                    FieldEnumMapping(field_path="response_data.create_item.item.item_type", enum_name="ItemType"),
                ],
            ),
            MethodDescription(
                method_name="load",
                description="Load an item from the database by ID",
                example_request_json='''{
    "data": {
        "load_item": {
            "item_id": 1
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully loaded Item id=1"
    }],
    "response_data": {
        "load_item": {
            "item": {
                "id": 1,
                "internal_name": "iron_ore",
                "attributes": {},
                "max_stack_size": 1000,
                "item_type": "RAWMATERIAL"
            }
        }
    }
}''',
                request_enum_fields=[],
                response_enum_fields=[
                    FieldEnumMapping(field_path="results[].status", enum_name="StatusType"),
                    FieldEnumMapping(field_path="results[].error_code", enum_name="GameError"),
                    FieldEnumMapping(field_path="response_data.load_item.item.item_type", enum_name="ItemType"),
                ],
            ),
            MethodDescription(
                method_name="save",
                description="Save (create or update) an item in the database",
                example_request_json='''{
    "data": {
        "save_item": {
            "item": {
                "id": 1,
                "internal_name": "iron_ore_refined",
                "attributes": {},
                "max_stack_size": 500,
                "item_type": "REFINEDMATERIAL"
            }
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully updated Item id=1, internal_name=iron_ore_refined"
    }],
    "response_data": {
        "save_item": {
            "item": {
                "id": 1,
                "internal_name": "iron_ore_refined",
                "attributes": {},
                "max_stack_size": 500,
                "item_type": "REFINEDMATERIAL"
            }
        }
    }
}''',
                request_enum_fields=[
                    FieldEnumMapping(field_path="data.save_item.item.item_type", enum_name="ItemType"),
                ],
                response_enum_fields=[
                    FieldEnumMapping(field_path="results[].status", enum_name="StatusType"),
                    FieldEnumMapping(field_path="results[].error_code", enum_name="GameError"),
                    FieldEnumMapping(field_path="response_data.save_item.item.item_type", enum_name="ItemType"),
                ],
            ),
            MethodDescription(
                method_name="destroy",
                description="Destroy (delete) an item from the database",
                example_request_json='''{
    "data": {
        "destroy_item": {
            "item_id": 1
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully destroyed Item id=1"
    }],
    "response_data": {
        "destroy_item": {
            "item_id": 1
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
            service_name="ItemService",
            version="1.0",
            description="Service for managing game items with create, load, save, and destroy operations",
            methods=methods,
            enums=enums,
        )

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

            result, item = self.db.load_item(
                self.database,
                item_id,
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
