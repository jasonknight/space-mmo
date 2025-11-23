#!/usr/bin/env python3
"""
Control Panel - Admin webapp for game database management
"""

import sys
sys.path.append('../gen-py')
sys.path.append('../py')

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
)
from game.ItemService import Client as ItemServiceClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create Bottle app
app = Bottle()

# Configuration
ITEM_SERVICE_HOST = 'localhost'
ITEM_SERVICE_PORT = 9090


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
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if value is not None:
                result[key] = thrift_to_dict(value)
        return result

    return obj


def dict_to_item(data):
    """Convert a dictionary to an Item thrift object."""
    item = Item()

    if 'id' in data and data['id']:
        item.id = int(data['id'])

    item.internal_name = data.get('internal_name', '')

    if 'max_stack_size' in data and data['max_stack_size']:
        item.max_stack_size = int(data['max_stack_size'])

    # ItemType enum
    if 'item_type' in data:
        item.item_type = ItemType._NAMES_TO_VALUES.get(
            data['item_type'],
            data['item_type'] if isinstance(data['item_type'], int) else ItemType.VIRTUAL,
        )

    # BackingTable enum
    if 'backing_table' in data:
        item.backing_table = BackingTable._NAMES_TO_VALUES.get(
            data['backing_table'],
            data['backing_table'] if isinstance(data['backing_table'], int) else BackingTable.ITEMS,
        )

    # Attributes map
    if 'attributes' in data and data['attributes']:
        item.attributes = {}
        for attr_type_key, attr_data in data['attributes'].items():
            # Convert attribute type
            if isinstance(attr_type_key, str):
                attr_type = AttributeType._NAMES_TO_VALUES.get(attr_type_key, int(attr_type_key))
            else:
                attr_type = int(attr_type_key)

            # Build Attribute object
            attr = Attribute()
            if 'id' in attr_data and attr_data['id']:
                attr.id = int(attr_data['id'])
            attr.internal_name = attr_data.get('internal_name', '')
            attr.visible = attr_data.get('visible', True)

            # AttributeType enum
            if 'attribute_type' in attr_data:
                attr.attribute_type = AttributeType._NAMES_TO_VALUES.get(
                    attr_data['attribute_type'],
                    attr_data['attribute_type'] if isinstance(attr_data['attribute_type'], int) else AttributeType.TRANSLATED_NAME,
                )

            # AttributeValue union
            if 'value' in attr_data:
                value_data = attr_data['value']
                attr_value = AttributeValue()

                if 'bool_value' in value_data:
                    attr_value.bool_value = value_data['bool_value']
                elif 'double_value' in value_data:
                    attr_value.double_value = float(value_data['double_value'])
                elif 'vector3' in value_data:
                    v = value_data['vector3']
                    attr_value.vector3 = ItemVector3(
                        x=float(v.get('x', 0)),
                        y=float(v.get('y', 0)),
                        z=float(v.get('z', 0)),
                    )
                elif 'asset_id' in value_data:
                    attr_value.asset_id = int(value_data['asset_id'])

                attr.value = attr_value

            # Owner union
            if 'owner' in attr_data:
                owner_data = attr_data['owner']
                owner = Owner()

                if 'mobile_id' in owner_data:
                    owner.mobile_id = int(owner_data['mobile_id'])
                elif 'item_id' in owner_data:
                    owner.item_id = int(owner_data['item_id'])
                elif 'asset_id' in owner_data:
                    owner.asset_id = int(owner_data['asset_id'])
                elif 'player_id' in owner_data:
                    owner.player_id = int(owner_data['player_id'])

                attr.owner = owner

            item.attributes[attr_type] = attr

    # Blueprint
    if 'blueprint' in data and data['blueprint']:
        bp_data = data['blueprint']
        blueprint = ItemBlueprint()

        if 'id' in bp_data and bp_data['id']:
            blueprint.id = int(bp_data['id'])

        blueprint.bake_time_ms = int(bp_data.get('bake_time_ms', 0))

        # Components map
        if 'components' in bp_data and bp_data['components']:
            blueprint.components = {}
            for item_id_key, comp_data in bp_data['components'].items():
                item_id = int(item_id_key)
                component = ItemBlueprintComponent(
                    ratio=float(comp_data.get('ratio', 1.0)),
                    item_id=int(comp_data.get('item_id', item_id)),
                )
                blueprint.components[item_id] = component

        item.blueprint = blueprint

    return item


# ============================================================================
# API Routes - Items
# ============================================================================

@app.route('/api/items', method='GET')
def list_items():
    """List items with pagination and search."""
    try:
        page = int(request.params.get('page', 1))
        per_page = int(request.params.get('per_page', 20))
        search = request.params.get('search', '')

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
                    items = [thrift_to_dict(item) for item in resp.response_data.list_item.items]
                    total_count = resp.response_data.list_item.total_count
                else:
                    total_count = 0

                response.content_type = 'application/json'
                return json.dumps({
                    'success': True,
                    'items': items,
                    'total_count': total_count,
                    'page': page,
                    'per_page': per_page,
                })
            else:
                error_msg = resp.results[0].message if resp.results else 'Unknown error'
                response.status = 500
                return json.dumps({
                    'success': False,
                    'error': error_msg,
                })
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error listing items: {e}", exc_info=True)
        response.status = 500
        return json.dumps({
            'success': False,
            'error': str(e),
        })


@app.route('/api/items/<item_id:int>', method='GET')
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

                response.content_type = 'application/json'
                return json.dumps({
                    'success': True,
                    'item': item,
                })
            else:
                error_msg = resp.results[0].message if resp.results else 'Unknown error'
                response.status = 404
                return json.dumps({
                    'success': False,
                    'error': error_msg,
                })
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps({
            'success': False,
            'error': str(e),
        })


@app.route('/api/items', method='POST')
def create_item():
    """Create a new item."""
    try:
        data = request.json

        if not data:
            response.status = 400
            return json.dumps({
                'success': False,
                'error': 'No data provided',
            })

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

                response.content_type = 'application/json'
                return json.dumps({
                    'success': True,
                    'item': created_item,
                })
            else:
                error_msg = resp.results[0].message if resp.results else 'Unknown error'
                response.status = 500
                return json.dumps({
                    'success': False,
                    'error': error_msg,
                })
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error creating item: {e}", exc_info=True)
        response.status = 500
        return json.dumps({
            'success': False,
            'error': str(e),
        })


@app.route('/api/items/<item_id:int>', method='PUT')
def update_item(item_id):
    """Update an existing item."""
    try:
        data = request.json

        if not data:
            response.status = 400
            return json.dumps({
                'success': False,
                'error': 'No data provided',
            })

        # Ensure the ID is set
        data['id'] = item_id
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

                response.content_type = 'application/json'
                return json.dumps({
                    'success': True,
                    'item': updated_item,
                })
            else:
                error_msg = resp.results[0].message if resp.results else 'Unknown error'
                response.status = 500
                return json.dumps({
                    'success': False,
                    'error': error_msg,
                })
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps({
            'success': False,
            'error': str(e),
        })


@app.route('/api/items/<item_id:int>', method='DELETE')
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
                response.content_type = 'application/json'
                return json.dumps({
                    'success': True,
                    'message': f'Item {item_id} deleted successfully',
                })
            else:
                error_msg = resp.results[0].message if resp.results else 'Unknown error'
                response.status = 500
                return json.dumps({
                    'success': False,
                    'error': error_msg,
                })
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps({
            'success': False,
            'error': str(e),
        })


@app.route('/api/items/autocomplete', method='GET')
def autocomplete_items():
    """Autocomplete search for items."""
    try:
        search = request.params.get('search', '')
        max_results = int(request.params.get('max_results', 10))

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
                    results = [thrift_to_dict(r) for r in resp.response_data.autocomplete_item.results]

                response.content_type = 'application/json'
                return json.dumps({
                    'success': True,
                    'results': results,
                })
            else:
                error_msg = resp.results[0].message if resp.results else 'Unknown error'
                response.status = 500
                return json.dumps({
                    'success': False,
                    'error': error_msg,
                })
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error autocompleting items: {e}", exc_info=True)
        response.status = 500
        return json.dumps({
            'success': False,
            'error': str(e),
        })


@app.route('/api/items/<item_id:int>/blueprint_tree', method='GET')
def get_item_blueprint_tree(item_id):
    """Get an item with its complete blueprint tree (recursive)."""
    try:
        max_depth = int(request.params.get('max_depth', 10))

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
                    tree = thrift_to_dict(resp.response_data.load_with_blueprint_tree.tree)

                response.content_type = 'application/json'
                return json.dumps({
                    'success': True,
                    'tree': tree,
                })
            else:
                error_msg = resp.results[0].message if resp.results else 'Unknown error'
                response.status = 404
                return json.dumps({
                    'success': False,
                    'error': error_msg,
                })
        finally:
            transport.close()

    except Exception as e:
        logger.error(f"Error getting blueprint tree for item {item_id}: {e}", exc_info=True)
        response.status = 500
        return json.dumps({
            'success': False,
            'error': str(e),
        })


# ============================================================================
# API Routes - Enums (for dropdowns)
# ============================================================================

@app.route('/api/enums', method='GET')
def get_enums():
    """Get all enum definitions for the frontend."""
    response.content_type = 'application/json'
    return json.dumps({
        'success': True,
        'enums': {
            'ItemType': {name: value for name, value in ItemType._NAMES_TO_VALUES.items()},
            'BackingTable': {name: value for name, value in BackingTable._NAMES_TO_VALUES.items()},
            'AttributeType': {name: value for name, value in AttributeType._NAMES_TO_VALUES.items()},
        },
    })


# ============================================================================
# Web Routes
# ============================================================================

@app.route('/')
def index():
    """Serve the main SPA page."""
    return static_file('index.html', root='./templates')


@app.route('/static/<filepath:path>')
def serve_static(filepath):
    """Serve static files (CSS, JS, images)."""
    return static_file(filepath, root='./static')


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Control Panel - Admin webapp')
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port to bind to (default: 8080)',
    )
    parser.add_argument(
        '--item-service-host',
        default='localhost',
        help='ItemService host (default: localhost)',
    )
    parser.add_argument(
        '--item-service-port',
        type=int,
        default=9090,
        help='ItemService port (default: 9090)',
    )

    args = parser.parse_args()

    ITEM_SERVICE_HOST = args.item_service_host
    ITEM_SERVICE_PORT = args.item_service_port

    logger.info(f"Starting Control Panel on {args.host}:{args.port}")
    logger.info(f"Connecting to ItemService at {ITEM_SERVICE_HOST}:{ITEM_SERVICE_PORT}")

    app.run(
        host=args.host,
        port=args.port,
        debug=True,
        reloader=True,
    )
