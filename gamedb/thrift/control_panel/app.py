#!/usr/bin/env python3
"""
Control Panel - Admin webapp for game database management
"""

import sys

sys.path.append("../gen-py")
sys.path.append("../py")

import json
import logging
from bottle import (
    Bottle,
    request,
    response,
    static_file,
    template,
    HTTPError,
)
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from game.ttypes import (
    ItemRequest,
    ItemRequestData,
    CreateItemRequestData,
    LoadItemRequestData,
    SaveItemRequestData,
    DestroyItemRequestData,
    ListItemRequestData,
    AutocompleteItemRequestData,
    LoadItemWithBlueprintTreeRequestData,
    Item,
    ItemBlueprint,
    ItemBlueprintComponent,
    Attribute,
    AttributeValue,
    ItemVector3,
    Owner,
    ItemType,
    BackingTable,
    AttributeType,
    StatusType,
    InventoryRequest,
    InventoryRequestData,
    CreateInventoryRequestData,
    LoadInventoryRequestData,
    SaveInventoryRequestData,
    ListInventoryRequestData,
    Inventory,
    InventoryEntry,
    PlayerRequest,
    PlayerRequestData,
    ListPlayerRequestData,
    CreatePlayerRequestData,
    LoadPlayerRequestData,
    SavePlayerRequestData,
    DeletePlayerRequestData,
    Player,
    Mobile,
    MobileType,
)
from game.constants import TABLE2STR
from game.ItemService import Client as ItemServiceClient
from game.InventoryService import Client as InventoryServiceClient
from game.PlayerService import Client as PlayerServiceClient

# Import DB adapter
from db import DB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create Bottle app
app = Bottle()

# Configuration
ITEM_SERVICE_HOST = "localhost"
ITEM_SERVICE_PORT = 9091
INVENTORY_SERVICE_HOST = "localhost"
INVENTORY_SERVICE_PORT = 9090
PLAYER_SERVICE_HOST = "localhost"
PLAYER_SERVICE_PORT = 9092

# Database configuration
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASSWORD = "minda"
DB_NAME = "gamedb"

# Database instance (will be initialized after arg parsing)
db_instance = None


# ============================================================================
# Thrift Client Helpers
# ============================================================================


def get_item_service_client():
    """Create and return an ItemService client."""
    transport = TSocket.TSocket(ITEM_SERVICE_HOST, ITEM_SERVICE_PORT)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ItemServiceClient(protocol)
    transport.open()
    return client, transport


def get_inventory_service_client():
    """Create and return an InventoryService client."""
    transport = TSocket.TSocket(INVENTORY_SERVICE_HOST, INVENTORY_SERVICE_PORT)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = InventoryServiceClient(protocol)
    transport.open()
    return client, transport


def get_player_service_client():
    """Create and return a PlayerService client."""
    transport = TSocket.TSocket(PLAYER_SERVICE_HOST, PLAYER_SERVICE_PORT)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = PlayerServiceClient(protocol)
    transport.open()
    return client, transport


# ============================================================================
# JSON Serialization Helpers
# ============================================================================


def thrift_to_dict(obj):
    """Convert a Thrift object to a dictionary for JSON serialization."""
    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, list):
        return [thrift_to_dict(item) for item in obj]

    if isinstance(obj, dict):
        return {k: thrift_to_dict(v) for k, v in obj.items()}

    # Handle Thrift structs
    if hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            if value is not None:
                result[key] = thrift_to_dict(value)
        return result

    return obj


def dict_to_item(data):
    """Convert a dictionary to an Item thrift object."""
    item = Item()

    if "id" in data and data["id"]:
        item.id = int(data["id"])

    item.internal_name = data.get("internal_name", "")

    if "max_stack_size" in data and data["max_stack_size"]:
        item.max_stack_size = int(data["max_stack_size"])

    # ItemType enum
    if "item_type" in data:
        item.item_type = ItemType._NAMES_TO_VALUES.get(
            data["item_type"],
            data["item_type"]
            if isinstance(data["item_type"], int)
            else ItemType.VIRTUAL,
        )

    # BackingTable enum
    if "backing_table" in data:
        item.backing_table = BackingTable._NAMES_TO_VALUES.get(
            data["backing_table"],
            data["backing_table"]
            if isinstance(data["backing_table"], int)
            else BackingTable.ITEMS,
        )

    # Attributes map
    if "attributes" in data and data["attributes"]:
        item.attributes = {}
        for attr_type_key, attr_data in data["attributes"].items():
            # Convert attribute type
            if isinstance(attr_type_key, str):
                attr_type = AttributeType._NAMES_TO_VALUES.get(
                    attr_type_key, int(attr_type_key)
                )
            else:
                attr_type = int(attr_type_key)

            # Build Attribute object
            attr = Attribute()
            if "id" in attr_data and attr_data["id"]:
                attr.id = int(attr_data["id"])
            attr.internal_name = attr_data.get("internal_name", "")
            attr.visible = attr_data.get("visible", True)

            # AttributeType enum
            if "attribute_type" in attr_data:
                attr.attribute_type = AttributeType._NAMES_TO_VALUES.get(
                    attr_data["attribute_type"],
                    attr_data["attribute_type"]
                    if isinstance(attr_data["attribute_type"], int)
                    else AttributeType.TRANSLATED_NAME,
                )

            # AttributeValue union
            if "value" in attr_data:
                value_data = attr_data["value"]
                attr_value = AttributeValue()

                if "bool_value" in value_data:
                    attr_value.bool_value = value_data["bool_value"]
                elif "double_value" in value_data:
                    attr_value.double_value = float(value_data["double_value"])
                elif "vector3" in value_data:
                    v = value_data["vector3"]
                    attr_value.vector3 = ItemVector3(
                        x=float(v.get("x", 0)),
                        y=float(v.get("y", 0)),
                        z=float(v.get("z", 0)),
                    )
                elif "asset_id" in value_data:
                    attr_value.asset_id = int(value_data["asset_id"])

                attr.value = attr_value

            # Owner union
            if "owner" in attr_data:
                owner_data = attr_data["owner"]
                owner = Owner()

                if "mobile_id" in owner_data:
                    owner.mobile_id = int(owner_data["mobile_id"])
                elif "item_id" in owner_data:
                    owner.item_id = int(owner_data["item_id"])
                elif "asset_id" in owner_data:
                    owner.asset_id = int(owner_data["asset_id"])
                elif "player_id" in owner_data:
                    owner.player_id = int(owner_data["player_id"])

                attr.owner = owner

            item.attributes[attr_type] = attr

    # Blueprint
    if "blueprint" in data and data["blueprint"]:
        bp_data = data["blueprint"]
        blueprint = ItemBlueprint()

        if "id" in bp_data and bp_data["id"]:
            blueprint.id = int(bp_data["id"])

        blueprint.bake_time_ms = int(bp_data.get("bake_time_ms", 0))

        # Components map
        if "components" in bp_data and bp_data["components"]:
            blueprint.components = {}
            for item_id_key, comp_data in bp_data["components"].items():
                item_id = int(item_id_key)
                component = ItemBlueprintComponent(
                    ratio=float(comp_data.get("ratio", 1.0)),
                    item_id=int(comp_data.get("item_id", item_id)),
                )
                blueprint.components[item_id] = component

        item.blueprint = blueprint

    return item


def dict_to_inventory(data):
    """Convert a dictionary to an Inventory thrift object."""
    inventory = Inventory()

    if "id" in data and data["id"]:
        inventory.id = int(data["id"])

    inventory.max_entries = int(data.get("max_entries", 0))
    inventory.max_volume = float(data.get("max_volume", 0.0))

    if "last_calculated_volume" in data:
        inventory.last_calculated_volume = float(data["last_calculated_volume"])
    else:
        inventory.last_calculated_volume = 0.0

    # Entries list
    if "entries" in data and data["entries"]:
        inventory.entries = []
        for entry_data in data["entries"]:
            entry = InventoryEntry(
                item_id=int(entry_data.get("item_id", 0)),
                quantity=float(entry_data.get("quantity", 0.0)),
                is_max_stacked=entry_data.get("is_max_stacked", False),
            )
            inventory.entries.append(entry)
    else:
        inventory.entries = []

    # Owner union
    if "owner" in data and data["owner"]:
        owner_data = data["owner"]
        owner = Owner()

        if "mobile_id" in owner_data and owner_data["mobile_id"]:
            owner.mobile_id = int(owner_data["mobile_id"])
        elif "item_id" in owner_data and owner_data["item_id"]:
            owner.item_id = int(owner_data["item_id"])
        elif "asset_id" in owner_data and owner_data["asset_id"]:
            owner.asset_id = int(owner_data["asset_id"])
        elif "player_id" in owner_data and owner_data["player_id"]:
            owner.player_id = int(owner_data["player_id"])

        inventory.owner = owner

    return inventory


def dict_to_player(data):
    """Convert a dictionary to a Player thrift object with Mobile."""
    player = Player()

    if "id" in data and data["id"]:
        player.id = int(data["id"])

    player.full_name = data.get("full_name", "")
    player.what_we_call_you = data.get("what_we_call_you", "")
    player.security_token = data.get("security_token", "")
    player.year_of_birth = int(data.get("year_of_birth", 0))
    player.email = data.get("email", "")

    # Calculate over_13 based on year_of_birth
    from datetime import datetime

    current_year = datetime.now().year
    player.over_13 = (current_year - player.year_of_birth) >= 13

    # Handle Mobile sub-object
    if "mobile" in data and data["mobile"]:
        mobile_data = data["mobile"]
        mobile = Mobile()

        if "id" in mobile_data and mobile_data["id"]:
            mobile.id = int(mobile_data["id"])

        # Hardcode mobile_type to PLAYER (value 1)
        mobile.mobile_type = MobileType.PLAYER

        mobile.what_we_call_you = mobile_data.get("what_we_call_you", "")

        # Owner points back to player
        owner = Owner()
        if player.id:
            owner.player_id = player.id
        mobile.owner = owner

        # Attributes map (similar to Item attributes)
        if "attributes" in mobile_data and mobile_data["attributes"]:
            mobile.attributes = {}
            for attr_type_key, attr_data in mobile_data["attributes"].items():
                # Convert attribute type
                if isinstance(attr_type_key, str):
                    attr_type = AttributeType._NAMES_TO_VALUES.get(
                        attr_type_key,
                        int(attr_type_key),
                    )
                else:
                    attr_type = int(attr_type_key)

                # Build Attribute object
                attr = Attribute()
                if "id" in attr_data and attr_data["id"]:
                    attr.id = int(attr_data["id"])
                attr.internal_name = attr_data.get("internal_name", "")
                attr.visible = attr_data.get("visible", True)

                # AttributeType enum
                if "attribute_type" in attr_data:
                    attr.attribute_type = AttributeType._NAMES_TO_VALUES.get(
                        attr_data["attribute_type"],
                        attr_data["attribute_type"]
                        if isinstance(
                            attr_data["attribute_type"],
                            int,
                        )
                        else AttributeType.TRANSLATED_NAME,
                    )

                # AttributeValue union
                if "value" in attr_data:
                    value_data = attr_data["value"]
                    attr_value = AttributeValue()

                    if "bool_value" in value_data:
                        attr_value.bool_value = value_data["bool_value"]
                    elif "double_value" in value_data:
                        attr_value.double_value = float(value_data["double_value"])
                    elif "vector3" in value_data:
                        v = value_data["vector3"]
                        attr_value.vector3 = ItemVector3(
                            x=float(v.get("x", 0)),
                            y=float(v.get("y", 0)),
                            z=float(v.get("z", 0)),
                        )
                    elif "asset_id" in value_data:
                        attr_value.asset_id = int(value_data["asset_id"])

                    attr.value = attr_value

                # Owner for attribute (points to mobile)
                attr_owner = Owner()
                if mobile.id:
                    attr_owner.mobile_id = mobile.id
                attr.owner = attr_owner

                mobile.attributes[attr_type] = attr
        else:
            mobile.attributes = {}

        player.mobile = mobile

    return player


# ============================================================================
# API Routes - Items
# ============================================================================


@app.route("/api/items", method="GET")
def list_items():
    """List items with pagination and search."""
    try:
        page = int(request.params.get("page", 0))
        per_page = int(request.params.get("per_page", 10))
        search = request.params.get("search", "")

        client, transport = get_item_service_client()

        try:
            req = ItemRequest(
                data=ItemRequestData(
                    list_item=ListItemRequestData(
                        page=page,
                        results_per_page=per_page,
                        search_string=search if search else None,
                    ),
                ),
            )

            resp = client.list_records(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                items = []
                if resp.response_data and resp.response_data.list_item:
                    items = [
                        thrift_to_dict(item)
                        for item in resp.response_data.list_item.items
                    ]
                    total_count = resp.response_data.list_item.total_count
                else:
                    total_count = 0

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "items": items,
                        "total_count": total_count,
                        "page": page,
                        "per_page": per_page,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error listing items: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/items/<item_id:int>", method="GET")
def get_item(item_id):
    """Get a single item by ID."""
    try:
        client, transport = get_item_service_client()

        try:
            req = ItemRequest(
                data=ItemRequestData(
                    load_item=LoadItemRequestData(
                        item_id=item_id,
                    ),
                ),
            )

            resp = client.load(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                item = None
                if resp.response_data and resp.response_data.load_item:
                    item = thrift_to_dict(resp.response_data.load_item.item)

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "item": item,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 404
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/items", method="POST")
def create_item():
    """Create a new item."""
    try:
        data = request.json

        if not data:
            response.status = 400
            return json.dumps(
                {
                    "success": False,
                    "error": "No data provided",
                }
            )

        item = dict_to_item(data)

        client, transport = get_item_service_client()

        try:
            req = ItemRequest(
                data=ItemRequestData(
                    create_item=CreateItemRequestData(
                        item=item,
                    ),
                ),
            )

            resp = client.create(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                created_item = None
                if resp.response_data and resp.response_data.create_item:
                    created_item = thrift_to_dict(resp.response_data.create_item.item)

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "item": created_item,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error creating item: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/items/<item_id:int>", method="PUT")
def update_item(item_id):
    """Update an existing item."""
    try:
        data = request.json

        if not data:
            response.status = 400
            return json.dumps(
                {
                    "success": False,
                    "error": "No data provided",
                }
            )

        # Ensure the ID is set
        data["id"] = item_id
        item = dict_to_item(data)

        client, transport = get_item_service_client()

        try:
            req = ItemRequest(
                data=ItemRequestData(
                    save_item=SaveItemRequestData(
                        item=item,
                    ),
                ),
            )

            resp = client.save(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                updated_item = None
                if resp.response_data and resp.response_data.save_item:
                    updated_item = thrift_to_dict(resp.response_data.save_item.item)

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "item": updated_item,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/items/<item_id:int>", method="DELETE")
def delete_item(item_id):
    """Delete an item."""
    try:
        client, transport = get_item_service_client()

        try:
            req = ItemRequest(
                data=ItemRequestData(
                    destroy_item=DestroyItemRequestData(
                        item_id=item_id,
                    ),
                ),
            )

            resp = client.destroy(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "message": f"Item {item_id} deleted successfully",
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/items/autocomplete", method="GET")
def autocomplete_items():
    """Autocomplete search for items."""
    try:
        search = request.params.get("search", "")
        max_results = int(request.params.get("max_results", 10))

        client, transport = get_item_service_client()

        try:
            req = ItemRequest(
                data=ItemRequestData(
                    autocomplete_item=AutocompleteItemRequestData(
                        search_string=search,
                        max_results=max_results,
                    ),
                ),
            )

            resp = client.autocomplete(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                results = []
                if resp.response_data and resp.response_data.autocomplete_item:
                    results = [
                        thrift_to_dict(r)
                        for r in resp.response_data.autocomplete_item.results
                    ]

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "results": results,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error autocompleting items: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/items/<item_id:int>/blueprint_tree", method="GET")
def get_item_blueprint_tree(item_id):
    """Get an item with its complete blueprint tree (recursive)."""
    try:
        max_depth = int(request.params.get("max_depth", 10))

        client, transport = get_item_service_client()

        try:
            req = ItemRequest(
                data=ItemRequestData(
                    load_with_blueprint_tree=LoadItemWithBlueprintTreeRequestData(
                        item_id=item_id,
                        max_depth=max_depth,
                    ),
                ),
            )

            resp = client.load_with_blueprint_tree(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                tree = None
                if resp.response_data and resp.response_data.load_with_blueprint_tree:
                    tree = thrift_to_dict(
                        resp.response_data.load_with_blueprint_tree.tree
                    )

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "tree": tree,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 404
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(
            f"Error getting blueprint tree for item {item_id}: {e}", exc_info=True
        )
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


# ============================================================================
# API Routes - Inventories
# ============================================================================


@app.route("/api/inventories", method="GET")
def list_inventories():
    """List inventories with pagination and search."""
    try:
        page = int(request.params.get("page", 0))
        per_page = int(request.params.get("per_page", 10))
        search = request.params.get("search", "")

        client, transport = get_inventory_service_client()

        try:
            req = InventoryRequest(
                data=InventoryRequestData(
                    list_inventory=ListInventoryRequestData(
                        page=page,
                        results_per_page=per_page,
                        search_string=search if search else None,
                    ),
                ),
            )

            resp = client.list_records(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                inventories = []
                if resp.response_data and resp.response_data.list_inventory:
                    inventories = [
                        thrift_to_dict(inv)
                        for inv in resp.response_data.list_inventory.inventories
                    ]
                    total_count = resp.response_data.list_inventory.total_count
                else:
                    total_count = 0

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "inventories": inventories,
                        "total_count": total_count,
                        "page": page,
                        "per_page": per_page,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error listing inventories: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/inventories/<inventory_id:int>", method="GET")
def get_inventory(inventory_id):
    """Get a single inventory by ID."""
    try:
        client, transport = get_inventory_service_client()

        try:
            req = InventoryRequest(
                data=InventoryRequestData(
                    load_inventory=LoadInventoryRequestData(
                        inventory_id=inventory_id,
                    ),
                ),
            )

            resp = client.load(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                inventory = None
                if resp.response_data and resp.response_data.load_inventory:
                    inventory = thrift_to_dict(
                        resp.response_data.load_inventory.inventory
                    )

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "inventory": inventory,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 404
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error getting inventory {inventory_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/inventories", method="POST")
def create_inventory():
    """Create a new inventory."""
    try:
        data = request.json

        if not data:
            response.status = 400
            return json.dumps(
                {
                    "success": False,
                    "error": "No data provided",
                }
            )

        inventory = dict_to_inventory(data)

        client, transport = get_inventory_service_client()

        try:
            req = InventoryRequest(
                data=InventoryRequestData(
                    create_inventory=CreateInventoryRequestData(
                        inventory=inventory,
                    ),
                ),
            )

            resp = client.create(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                created_inventory = None
                if resp.response_data and resp.response_data.create_inventory:
                    created_inventory = thrift_to_dict(
                        resp.response_data.create_inventory.inventory
                    )

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "inventory": created_inventory,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error creating inventory: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/inventories/<inventory_id:int>", method="PUT")
def update_inventory(inventory_id):
    """Update an existing inventory."""
    try:
        data = request.json

        if not data:
            response.status = 400
            return json.dumps(
                {
                    "success": False,
                    "error": "No data provided",
                }
            )

        # Ensure the ID is set
        data["id"] = inventory_id
        inventory = dict_to_inventory(data)

        client, transport = get_inventory_service_client()

        try:
            req = InventoryRequest(
                data=InventoryRequestData(
                    save_inventory=SaveInventoryRequestData(
                        inventory=inventory,
                    ),
                ),
            )

            resp = client.save(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                updated_inventory = None
                if resp.response_data and resp.response_data.save_inventory:
                    updated_inventory = thrift_to_dict(
                        resp.response_data.save_inventory.inventory
                    )

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "inventory": updated_inventory,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error updating inventory {inventory_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


# ============================================================================
# API Routes - Players (for owner search)
# ============================================================================


@app.route("/api/players/search", method="GET")
def search_players():
    """Search players by name."""
    response.content_type = "application/json"

    try:
        # Get query parameters
        search_query = request.query.get("search", "")
        max_results = int(request.query.get("max_results", 10))

        if not search_query or len(search_query) < 2:
            return json.dumps(
                {
                    "success": True,
                    "results": [],
                }
            )

        # Create request
        list_data = ListPlayerRequestData(
            page=1,
            results_per_page=max_results,
            search_string=search_query,
        )
        req = PlayerRequest(
            data=PlayerRequestData(
                list_player=list_data,
            ),
        )

        # Call service
        client, transport = get_player_service_client()
        try:
            resp = client.list_records(req)

            if resp.results[0].status == StatusType.SUCCESS and resp.response_data:
                players = resp.response_data.list_player.players
                result_list = [
                    {
                        "id": player.id,
                        "what_we_call_you": player.what_we_call_you,
                        "full_name": player.full_name,
                        "email": player.email,
                    }
                    for player in players
                ]
                return json.dumps(
                    {
                        "success": True,
                        "results": result_list,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error searching players: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/players", method="GET")
def list_players():
    """List players with pagination and search."""
    try:
        page = int(request.params.get("page", 0))
        per_page = int(request.params.get("per_page", 10))
        search = request.params.get("search", "")

        client, transport = get_player_service_client()

        try:
            req = PlayerRequest(
                data=PlayerRequestData(
                    list_player=ListPlayerRequestData(
                        page=page,
                        results_per_page=per_page,
                        search_string=search if search else None,
                    ),
                ),
            )

            resp = client.list_records(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                players = []
                if resp.response_data and resp.response_data.list_player:
                    players = [
                        thrift_to_dict(player)
                        for player in resp.response_data.list_player.players
                    ]
                    total_count = resp.response_data.list_player.total_count
                else:
                    total_count = 0

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "players": players,
                        "total_count": total_count,
                        "page": page,
                        "per_page": per_page,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error listing players: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/players/<player_id:int>", method="GET")
def get_player(player_id):
    """Get a single player by ID."""
    try:
        client, transport = get_player_service_client()

        try:
            req = PlayerRequest(
                data=PlayerRequestData(
                    load_player=LoadPlayerRequestData(
                        player_id=player_id,
                    ),
                ),
            )

            resp = client.load(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                player = None
                if resp.response_data and resp.response_data.load_player:
                    player = thrift_to_dict(resp.response_data.load_player.player)

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "player": player,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 404
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error getting player {player_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/players", method="POST")
def create_player():
    """Create a new player."""
    try:
        data = request.json

        if not data:
            response.status = 400
            return json.dumps(
                {
                    "success": False,
                    "error": "No data provided",
                }
            )

        player = dict_to_player(data)

        client, transport = get_player_service_client()

        try:
            req = PlayerRequest(
                data=PlayerRequestData(
                    create_player=CreatePlayerRequestData(
                        player=player,
                    ),
                ),
            )

            resp = client.create(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                created_player = None
                if resp.response_data and resp.response_data.create_player:
                    created_player = thrift_to_dict(
                        resp.response_data.create_player.player,
                    )

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "player": created_player,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error creating player: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/players/<player_id:int>", method="PUT")
def update_player(player_id):
    """Update an existing player."""
    try:
        data = request.json

        if not data:
            response.status = 400
            return json.dumps(
                {
                    "success": False,
                    "error": "No data provided",
                }
            )

        # Ensure the ID is set
        data["id"] = player_id
        player = dict_to_player(data)

        client, transport = get_player_service_client()

        try:
            req = PlayerRequest(
                data=PlayerRequestData(
                    save_player=SavePlayerRequestData(
                        player=player,
                    ),
                ),
            )

            resp = client.save(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                updated_player = None
                if resp.response_data and resp.response_data.save_player:
                    updated_player = thrift_to_dict(
                        resp.response_data.save_player.player,
                    )

                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "player": updated_player,
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error updating player {player_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


@app.route("/api/players/<player_id:int>", method="DELETE")
def delete_player(player_id):
    """Delete a player."""
    try:
        client, transport = get_player_service_client()

        try:
            req = PlayerRequest(
                data=PlayerRequestData(
                    delete_player=DeletePlayerRequestData(
                        player_id=player_id,
                    ),
                ),
            )

            resp = client.delete(req)

            if resp.results and resp.results[0].status == StatusType.SUCCESS:
                response.content_type = "application/json"
                return json.dumps(
                    {
                        "success": True,
                        "message": f"Player {player_id} deleted successfully",
                    }
                )
            else:
                error_msg = resp.results[0].message if resp.results else "Unknown error"
                response.status = 500
                return json.dumps(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                )
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error deleting player {player_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


# ============================================================================
# API Routes - Mobiles (for owner search)
# ============================================================================


@app.route("/api/mobiles/search", method="GET")
def search_mobiles():
    """Search mobiles by what_we_call_you field."""
    response.content_type = "application/json"

    try:
        # Get query parameters
        search_query = request.query.get("search", "")
        max_results = int(request.query.get("max_results", 10))

        if not search_query or len(search_query) < 2:
            return json.dumps(
                {
                    "success": True,
                    "results": [],
                }
            )

        # Get mobiles table name from TABLE2STR
        mobiles_table = TABLE2STR[BackingTable.MOBILES]

        # Query database directly
        db_instance.connect()
        cursor = db_instance.connection.cursor(dictionary=True)

        try:
            query = f"""
                SELECT id, what_we_call_you, mobile_type
                FROM {DB_NAME}.{mobiles_table}
                WHERE what_we_call_you LIKE %s
                ORDER BY what_we_call_you
                LIMIT %s
            """
            cursor.execute(query, (f"%{search_query}%", max_results))
            rows = cursor.fetchall()

            result_list = [
                {
                    "id": row["id"],
                    "what_we_call_you": row["what_we_call_you"],
                    "mobile_type": row["mobile_type"],
                }
                for row in rows
            ]

            return json.dumps(
                {
                    "success": True,
                    "results": result_list,
                }
            )
        finally:
            cursor.close()

    except Exception as e:
        logger.error(f"Error searching mobiles: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


# ============================================================================
# API Routes - Owner Info (for display)
# ============================================================================


@app.route("/api/owners/<owner_type>/<owner_id:int>", method="GET")
def get_owner_info(owner_type, owner_id):
    """Get owner display information by type and ID."""
    response.content_type = "application/json"

    try:
        if owner_type == "item_id":
            # Get item info
            client, transport = get_item_service_client()
            try:
                req = ItemRequest(
                    data=ItemRequestData(
                        load_item=LoadItemRequestData(
                            item_id=owner_id,
                        ),
                    ),
                )
                resp = client.load(req)

                if resp.results and resp.results[0].status == StatusType.SUCCESS:
                    item = resp.response_data.load_item.item
                    return json.dumps(
                        {
                            "success": True,
                            "owner": {
                                "id": item.id,
                                "name": item.internal_name,
                                "type": "Item",
                            },
                        }
                    )
                else:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Item not found",
                        }
                    )
            finally:
                transport.close()

        elif owner_type == "player_id":
            # Get player info
            client, transport = get_player_service_client()
            try:
                req = PlayerRequest(
                    data=PlayerRequestData(
                        list_player=ListPlayerRequestData(
                            page=1,
                            results_per_page=1,
                            search_string=str(owner_id),
                        ),
                    ),
                )
                resp = client.list_records(req)

                if resp.results[0].status == StatusType.SUCCESS and resp.response_data:
                    players = resp.response_data.list_player.players
                    if players:
                        player = players[0]
                        return json.dumps(
                            {
                                "success": True,
                                "owner": {
                                    "id": player.id,
                                    "name": player.what_we_call_you,
                                    "type": "Player",
                                },
                            }
                        )

                return json.dumps(
                    {
                        "success": False,
                        "error": "Player not found",
                    }
                )
            finally:
                transport.close()

        elif owner_type == "mobile_id":
            # Get mobile info from database
            mobiles_table = TABLE2STR[BackingTable.MOBILES]

            db_instance.connect()
            cursor = db_instance.connection.cursor(dictionary=True)

            try:
                query = f"""
                    SELECT id, what_we_call_you, mobile_type
                    FROM {DB_NAME}.{mobiles_table}
                    WHERE id = %s
                """
                cursor.execute(query, (owner_id,))
                row = cursor.fetchone()

                if row:
                    return json.dumps(
                        {
                            "success": True,
                            "owner": {
                                "id": row["id"],
                                "name": row["what_we_call_you"],
                                "type": "Mobile",
                            },
                        }
                    )
                else:
                    return json.dumps(
                        {
                            "success": False,
                            "error": "Mobile not found",
                        }
                    )
            finally:
                cursor.close()

        elif owner_type == "asset_id":
            # Assets don't have a service, so just return the ID
            return json.dumps(
                {
                    "success": True,
                    "owner": {
                        "id": owner_id,
                        "name": f"Asset #{owner_id}",
                        "type": "Asset",
                    },
                }
            )

        else:
            response.status = 400
            return json.dumps(
                {
                    "success": False,
                    "error": f"Unknown owner type: {owner_type}",
                }
            )

    except Exception as e:
        logger.error(f"Error getting owner info: {e}", exc_info=True)
        response.status = 500
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )


# ============================================================================
# API Routes - Enums (for dropdowns)
# ============================================================================


@app.route("/api/enums", method="GET")
def get_enums():
    """Get all enum definitions for the frontend."""
    response.content_type = "application/json"
    return json.dumps(
        {
            "success": True,
            "enums": {
                "ItemType": {
                    name: value for name, value in ItemType._NAMES_TO_VALUES.items()
                },
                "BackingTable": {
                    name: value for name, value in BackingTable._NAMES_TO_VALUES.items()
                },
                "AttributeType": {
                    name: value
                    for name, value in AttributeType._NAMES_TO_VALUES.items()
                },
            },
        }
    )


# ============================================================================
# Web Routes
# ============================================================================


@app.route("/")
def index():
    """Serve the main SPA page."""
    return static_file("index.html", root="./templates")


@app.route("/static/<filepath:path>")
def serve_static(filepath):
    """Serve static files (CSS, JS, images)."""
    return static_file(filepath, root="./static")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Control Panel - Admin webapp")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to (default: 8080)",
    )
    parser.add_argument(
        "--item-service-host",
        default="localhost",
        help="ItemService host (default: localhost)",
    )
    parser.add_argument(
        "--item-service-port",
        type=int,
        default=9091,
        help="ItemService port (default: 9091)",
    )
    parser.add_argument(
        "--inventory-service-host",
        default="localhost",
        help="InventoryService host (default: localhost)",
    )
    parser.add_argument(
        "--inventory-service-port",
        type=int,
        default=9090,
        help="InventoryService port (default: 9090)",
    )
    parser.add_argument(
        "--player-service-host",
        default="localhost",
        help="PlayerService host (default: localhost)",
    )
    parser.add_argument(
        "--player-service-port",
        type=int,
        default=9092,
        help="PlayerService port (default: 9092)",
    )
    parser.add_argument(
        "--db-host",
        default="localhost",
        help="Database host (default: localhost)",
    )
    parser.add_argument(
        "--db-user",
        default="admin",
        help="Database user (default: admin)",
    )
    parser.add_argument(
        "--db-password",
        default="minda",
        help="Database password (default: minda)",
    )
    parser.add_argument(
        "--db-name",
        default="gamedb",
        help="Database name (default: gamedb)",
    )

    args = parser.parse_args()

    ITEM_SERVICE_HOST = args.item_service_host
    ITEM_SERVICE_PORT = args.item_service_port
    INVENTORY_SERVICE_HOST = args.inventory_service_host
    INVENTORY_SERVICE_PORT = args.inventory_service_port
    PLAYER_SERVICE_HOST = args.player_service_host
    PLAYER_SERVICE_PORT = args.player_service_port
    DB_HOST = args.db_host
    DB_USER = args.db_user
    DB_PASSWORD = args.db_password
    DB_NAME = args.db_name

    # Initialize database instance
    db_instance = DB(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
    )

    logger.info(f"Starting Control Panel on {args.host}:{args.port}")
    logger.info(f"Connecting to ItemService at {ITEM_SERVICE_HOST}:{ITEM_SERVICE_PORT}")
    logger.info(
        f"Connecting to InventoryService at {INVENTORY_SERVICE_HOST}:{INVENTORY_SERVICE_PORT}"
    )
    logger.info(
        f"Connecting to PlayerService at {PLAYER_SERVICE_HOST}:{PLAYER_SERVICE_PORT}"
    )
    logger.info(f"Connecting to Database at {DB_HOST} (database: {DB_NAME})")

    app.run(
        host=args.host,
        port=args.port,
        debug=True,
        reloader=True,
    )
