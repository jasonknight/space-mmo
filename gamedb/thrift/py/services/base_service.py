"""
BaseService implementation that provides common describe() functionality for all services.
"""

import sys
sys.path.append('../../gen-py')
sys.path.append('..')

import logging
from typing import Any

logger = logging.getLogger(__name__)

from game.ttypes import (
    ServiceMetadata,
    MethodDescription,
    EnumDefinition,
    FieldEnumMapping,
    StatusType,
    GameError,
    ItemType,
    AttributeType,
)
from game.BaseService import Iface as BaseServiceIface


class BaseServiceHandler(BaseServiceIface):
    """
    Base implementation that provides describe() functionality.
    Concrete services inherit from this to get the describe() method.
    """

    def __init__(self, klass: Any):
        """
        Initialize BaseService with the concrete service class.

        Args:
            klass: The concrete service class (e.g., InventoryServiceHandler,
                   ItemServiceHandler, PlayerServiceHandler)
        """
        self.klass = klass

    def describe(self) -> ServiceMetadata:
        """
        Return service metadata for discovery.
        This method determines which concrete service is being used
        and returns the appropriate metadata.
        """
        # Import here to avoid circular dependencies
        from services.inventory_service import InventoryServiceHandler
        from services.item_service import ItemServiceHandler
        from services.player_service import PlayerServiceHandler

        if self.klass == InventoryServiceHandler or isinstance(self, InventoryServiceHandler):
            return self._describe_inventory_service()
        elif self.klass == ItemServiceHandler or isinstance(self, ItemServiceHandler):
            return self._describe_item_service()
        elif self.klass == PlayerServiceHandler or isinstance(self, PlayerServiceHandler):
            return self._describe_player_service()
        else:
            raise ValueError(f"Unknown service class: {self.klass}")

    def _get_common_enums(self) -> list:
        """Get common enums used by all services."""
        return [
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
                    "INV_OPERATION_FAILED": int(GameError.INV_OPERATION_FAILED),
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

    def _get_common_response_enum_fields(self) -> list:
        """Get common response enum field mappings."""
        return [
            FieldEnumMapping(
                field_path="results[].status",
                enum_name="StatusType",
            ),
            FieldEnumMapping(
                field_path="results[].error_code",
                enum_name="GameError",
            ),
        ]

    def _describe_inventory_service(self) -> ServiceMetadata:
        """Generate metadata for InventoryService."""
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
            ),
        ]

        return ServiceMetadata(
            service_name="InventoryService",
            version="1.0",
            description="Service for managing game inventories with create, load, save, split, transfer, and list operations",
            methods=methods,
            enums=self._get_common_enums(),
        )

    def _describe_item_service(self) -> ServiceMetadata:
        """Generate metadata for ItemService."""
        enums = self._get_common_enums()
        enums.extend([
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
        ])

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
                request_enum_fields=[],
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
        "message": "Successfully updated Item id=1"
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
                request_enum_fields=[],
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
            ),
            MethodDescription(
                method_name="list_records",
                description="List items with pagination and optional search on internal_name",
                example_request_json='''{
    "data": {
        "list_item": {
            "page": 0,
            "results_per_page": 10,
            "search_string": "iron"
        }
    }
}''',
                example_response_json='''{
    "results": [{
        "status": "SUCCESS",
        "message": "Successfully listed 10 items (total: 100)"
    }],
    "response_data": {
        "list_item": {
            "items": [
                {
                    "id": 1,
                    "internal_name": "iron_ore",
                    "attributes": {},
                    "max_stack_size": 1000,
                    "item_type": "RAWMATERIAL"
                }
            ],
            "total_count": 100
        }
    }
}''',
                request_enum_fields=[],
                response_enum_fields=self._get_common_response_enum_fields(),
            ),
        ]

        return ServiceMetadata(
            service_name="ItemService",
            version="1.0",
            description="Service for managing game items with create, load, save, destroy, and list operations",
            methods=methods,
            enums=enums,
        )

    def _describe_player_service(self) -> ServiceMetadata:
        """Generate metadata for PlayerService."""
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
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
                response_enum_fields=self._get_common_response_enum_fields(),
            ),
        ]

        return ServiceMetadata(
            service_name="PlayerService",
            version="1.0",
            description="Service for managing game players with create, load, save, and delete operations",
            methods=methods,
            enums=self._get_common_enums(),
        )
