#!/usr/bin/env python3
"""
Fiddler - A generic Thrift service explorer and testing tool.

This webapp provides a web UI to discover and interact with any Thrift service
that implements the describe() method.
"""

import sys
import json
import re
import logging
import traceback
from bottle import Bottle, request, response, static_file, TEMPLATE_PATH
from bottle import jinja2_template as template

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Add paths for Thrift imports
sys.path.append('../gen-py')
sys.path.append('../py')

# Thrift imports
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol, TJSONProtocol
from game.InventoryService import Client as InventoryServiceClient
from game.PlayerService import Client as PlayerServiceClient
from game.ItemService import Client as ItemServiceClient

app = Bottle()

# Store service metadata and connection info
service_metadata = None
enum_lookup = {}  # enum_name -> {string_value -> int_value}
enum_reverse_lookup = {}  # enum_name -> {int_value -> string_value}
current_host = None
current_port = None
current_service_type = None  # 'inventory', 'player', or 'item'


def connect_to_service(host, port, service_type='inventory'):
    """Create and return a Thrift client connection."""
    transport = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    if service_type == 'inventory':
        client = InventoryServiceClient(protocol)
    elif service_type == 'player':
        client = PlayerServiceClient(protocol)
    elif service_type == 'item':
        client = ItemServiceClient(protocol)
    else:
        raise ValueError(f"Unknown service type: {service_type}")

    transport.open()
    return client, transport


def load_service_metadata(host, port, service_type='inventory'):
    """Load service metadata by calling describe()."""
    global service_metadata, enum_lookup, enum_reverse_lookup, current_host, current_port, current_service_type

    try:
        client, transport = connect_to_service(host, port, service_type)
        service_metadata = client.describe()
        transport.close()

        # Build enum lookup tables
        enum_lookup = {}
        enum_reverse_lookup = {}
        for enum_def in service_metadata.enums:
            enum_lookup[enum_def.enum_name] = enum_def.values
            enum_reverse_lookup[enum_def.enum_name] = {
                v: k for k, v in enum_def.values.items()
            }

        # Store current connection info
        current_host = host
        current_port = port
        current_service_type = service_type

        print(f"Loaded metadata for {service_metadata.service_name} v{service_metadata.version} from {host}:{port}")
        return True
    except Exception as e:
        print(f"Error loading service metadata: {e}")
        raise


def convert_enums_to_ints(obj, field_mappings):
    """
    Recursively convert enum string values to integers in a JSON object.
    Uses field_mappings to know which fields contain enums.
    """
    if obj is None:
        return obj

    # Build a map of field paths to enum names
    field_enum_map = {}
    for mapping in field_mappings:
        field_enum_map[mapping.field_path] = mapping.enum_name

    def convert_recursive(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                # Check if this field is an enum
                if current_path in field_enum_map:
                    enum_name = field_enum_map[current_path]
                    if isinstance(value, str) and enum_name in enum_lookup:
                        # Convert string to int
                        if value in enum_lookup[enum_name]:
                            data[key] = enum_lookup[enum_name][value]
                elif isinstance(value, (dict, list)):
                    convert_recursive(value, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                # Handle array notation like "results[]"
                array_path = f"{path}[]"
                if isinstance(item, (dict, list)):
                    convert_recursive(item, path)  # Use base path for array items

    convert_recursive(obj)
    return obj


def convert_enums_to_strings(obj, field_mappings):
    """
    Recursively convert enum integer values to strings in a JSON object.
    Uses field_mappings to know which fields contain enums.
    """
    if obj is None:
        return obj

    # Build a map of field paths to enum names
    field_enum_map = {}
    for mapping in field_mappings:
        field_enum_map[mapping.field_path] = mapping.enum_name

    def convert_recursive(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                # Check if this field is an enum
                if current_path in field_enum_map:
                    enum_name = field_enum_map[current_path]
                    if isinstance(value, int) and enum_name in enum_reverse_lookup:
                        # Convert int to string
                        if value in enum_reverse_lookup[enum_name]:
                            data[key] = enum_reverse_lookup[enum_name][value]
                elif isinstance(value, (dict, list)):
                    convert_recursive(value, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    convert_recursive(item, path)  # Use base path for array items

    convert_recursive(obj)
    return obj


@app.route('/')
def index():
    """Main page - service explorer UI."""
    return template('index.html')


@app.route('/api/connect', method='POST')
def connect():
    """Connect to a Thrift service and load its metadata."""
    try:
        logger.info("=== Connecting to Thrift service ===")
        data = request.json
        server_address = data.get('server')
        service_type = data.get('service_type', 'inventory')  # Default to inventory

        logger.info(f"Server address: {server_address}")
        logger.info(f"Service type: {service_type}")

        if not server_address:
            logger.error("No server address provided")
            response.status = 400
            return {'error': 'Missing server address'}

        # Parse host:port
        if ':' in server_address:
            host, port_str = server_address.split(':', 1)
            try:
                port = int(port_str)
            except ValueError:
                logger.error(f"Invalid port number: {port_str}")
                response.status = 400
                return {'error': 'Invalid port number'}
        else:
            host = server_address
            port = 9090  # Default port

        logger.info(f"Parsed connection: {host}:{port}")

        # Try to connect and load metadata
        logger.debug("Loading service metadata...")
        load_service_metadata(host, port, service_type)
        logger.info("Metadata loaded successfully")

        # Return the metadata
        return {
            'success': True,
            'metadata': {
                'service_name': service_metadata.service_name,
                'version': service_metadata.version,
                'description': service_metadata.description,
                'methods': [
                    {
                        'method_name': m.method_name,
                        'description': m.description,
                        'example_request_json': m.example_request_json,
                        'example_response_json': m.example_response_json,
                        'request_enum_fields': [
                            {'field_path': f.field_path, 'enum_name': f.enum_name}
                            for f in m.request_enum_fields
                        ],
                        'response_enum_fields': [
                            {'field_path': f.field_path, 'enum_name': f.enum_name}
                            for f in m.response_enum_fields
                        ],
                    }
                    for m in service_metadata.methods
                ],
                'enums': [
                    {
                        'enum_name': e.enum_name,
                        'description': e.description if hasattr(e, 'description') else None,
                        'values': e.values,
                    }
                    for e in service_metadata.enums
                ],
            },
            'enum_lookup': enum_lookup,
            'enum_reverse_lookup': enum_reverse_lookup,
        }

    except Exception as e:
        logger.error("=== Connection failed ===")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception message: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        response.status = 500
        return {'error': str(e)}


def build_inventory_request(request_obj):
    """Build an InventoryRequest from a JSON object."""
    from game.ttypes import (
        InventoryRequest,
        InventoryRequestData,
        LoadInventoryRequestData,
        CreateInventoryRequestData,
        SaveInventoryRequestData,
        SplitStackRequestData,
        TransferItemRequestData,
        ListInventoryRequestData,
        Inventory,
        InventoryEntry,
        Owner,
    )

    # Extract the data union field
    data_dict = request_obj.get('data', {})
    logger.debug(f"Data dict keys: {list(data_dict.keys())}")

    # Build InventoryRequestData based on which field is present
    request_data = InventoryRequestData()

    if 'load_inventory' in data_dict:
        load_data = LoadInventoryRequestData(
            inventory_id=data_dict['load_inventory']['inventory_id'],
        )
        request_data.load_inventory = load_data

    elif 'create_inventory' in data_dict:
        inv_data = data_dict['create_inventory']['inventory']

        # Build Owner
        owner_dict = inv_data.get('owner', {})
        owner = Owner()
        if 'mobile_id' in owner_dict:
            owner.mobile_id = owner_dict['mobile_id']
        elif 'item_id' in owner_dict:
            owner.item_id = owner_dict['item_id']
        elif 'asset_id' in owner_dict:
            owner.asset_id = owner_dict['asset_id']
        elif 'player_id' in owner_dict:
            owner.player_id = owner_dict['player_id']

        # Build Inventory
        inventory = Inventory(
            max_entries=inv_data['max_entries'],
            max_volume=inv_data['max_volume'],
            entries=[],
            last_calculated_volume=inv_data.get('last_calculated_volume', 0.0),
            owner=owner,
        )

        create_data = CreateInventoryRequestData(inventory=inventory)
        request_data.create_inventory = create_data

    elif 'save_inventory' in data_dict:
        inv_data = data_dict['save_inventory']['inventory']

        # Build Owner
        owner_dict = inv_data.get('owner', {})
        owner = Owner()
        if 'mobile_id' in owner_dict:
            owner.mobile_id = owner_dict['mobile_id']
        elif 'item_id' in owner_dict:
            owner.item_id = owner_dict['item_id']
        elif 'asset_id' in owner_dict:
            owner.asset_id = owner_dict['asset_id']
        elif 'player_id' in owner_dict:
            owner.player_id = owner_dict['player_id']

        # Build entries
        entries = []
        for entry_dict in inv_data.get('entries', []):
            entry = InventoryEntry(
                item_id=entry_dict['item_id'],
                quantity=entry_dict['quantity'],
                is_max_stacked=entry_dict.get('is_max_stacked', False),
            )
            entries.append(entry)

        # Build Inventory
        inventory = Inventory(
            id=inv_data.get('id'),
            max_entries=inv_data['max_entries'],
            max_volume=inv_data['max_volume'],
            entries=entries,
            last_calculated_volume=inv_data.get('last_calculated_volume', 0.0),
            owner=owner,
        )

        save_data = SaveInventoryRequestData(inventory=inventory)
        request_data.save_inventory = save_data

    elif 'split_stack' in data_dict:
        split_dict = data_dict['split_stack']
        split_data = SplitStackRequestData(
            inventory_id=split_dict['inventory_id'],
            item_id=split_dict['item_id'],
            quantity_to_split=split_dict['quantity_to_split'],
        )
        request_data.split_stack = split_data

    elif 'transfer_item' in data_dict:
        transfer_dict = data_dict['transfer_item']
        transfer_data = TransferItemRequestData(
            source_inventory_id=transfer_dict['source_inventory_id'],
            destination_inventory_id=transfer_dict['destination_inventory_id'],
            item_id=transfer_dict['item_id'],
            quantity=transfer_dict['quantity'],
        )
        request_data.transfer_item = transfer_data

    elif 'list_inventory' in data_dict:
        list_dict = data_dict['list_inventory']
        list_data = ListInventoryRequestData(
            page=list_dict['page'],
            results_per_page=list_dict['results_per_page'],
        )
        if 'search_string' in list_dict and list_dict['search_string']:
            list_data.search_string = list_dict['search_string']
        request_data.list_inventory = list_data

    else:
        raise ValueError(f"Unknown request type in data: {list(data_dict.keys())}")

    # Build the final InventoryRequest
    return InventoryRequest(data=request_data)


def build_item_request(request_obj):
    """Build an ItemRequest from a JSON object."""
    from game.ttypes import (
        ItemRequest,
        ItemRequestData,
        LoadItemRequestData,
        CreateItemRequestData,
        SaveItemRequestData,
        DestroyItemRequestData,
        ListItemRequestData,
        Item,
        ItemType,
        Attribute,
    )

    # Extract the data union field
    data_dict = request_obj.get('data', {})
    logger.debug(f"Data dict keys: {list(data_dict.keys())}")

    # Build ItemRequestData based on which field is present
    request_data = ItemRequestData()

    if 'load_item' in data_dict:
        load_data = LoadItemRequestData(
            item_id=data_dict['load_item']['item_id'],
        )
        request_data.load_item = load_data

    elif 'create_item' in data_dict:
        item_dict = data_dict['create_item']['item']

        # Build attributes dictionary
        attributes = {}
        if 'attributes' in item_dict:
            for attr_id, attr_val in item_dict['attributes'].items():
                if isinstance(attr_val, dict):
                    attributes[int(attr_id)] = Attribute(**attr_val)
                else:
                    attributes[int(attr_id)] = attr_val

        item = Item(
            internal_name=item_dict['internal_name'],
            attributes=attributes,
            max_stack_size=item_dict['max_stack_size'],
            item_type=item_dict['item_type'],
        )
        if 'id' in item_dict and item_dict['id'] is not None:
            item.id = item_dict['id']

        create_data = CreateItemRequestData(item=item)
        request_data.create_item = create_data

    elif 'save_item' in data_dict:
        item_dict = data_dict['save_item']['item']

        # Build attributes dictionary
        attributes = {}
        if 'attributes' in item_dict:
            for attr_id, attr_val in item_dict['attributes'].items():
                if isinstance(attr_val, dict):
                    attributes[int(attr_id)] = Attribute(**attr_val)
                else:
                    attributes[int(attr_id)] = attr_val

        item = Item(
            internal_name=item_dict['internal_name'],
            attributes=attributes,
            max_stack_size=item_dict['max_stack_size'],
            item_type=item_dict['item_type'],
        )
        if 'id' in item_dict and item_dict['id'] is not None:
            item.id = item_dict['id']

        save_data = SaveItemRequestData(item=item)
        request_data.save_item = save_data

    elif 'destroy_item' in data_dict:
        destroy_dict = data_dict['destroy_item']
        destroy_data = DestroyItemRequestData(
            item_id=destroy_dict['item_id'],
        )
        request_data.destroy_item = destroy_data

    elif 'list_item' in data_dict:
        list_dict = data_dict['list_item']
        list_data = ListItemRequestData(
            page=list_dict['page'],
            results_per_page=list_dict['results_per_page'],
        )
        if 'search_string' in list_dict and list_dict['search_string']:
            list_data.search_string = list_dict['search_string']
        request_data.list_item = list_data

    else:
        raise ValueError(f"Unknown request type in data: {list(data_dict.keys())}")

    # Build the final ItemRequest
    return ItemRequest(data=request_data)


def build_player_request(request_obj):
    """Build a PlayerRequest from a JSON object."""
    from game.ttypes import (
        PlayerRequest,
        PlayerRequestData,
        LoadPlayerRequestData,
        CreatePlayerRequestData,
        SavePlayerRequestData,
        DeletePlayerRequestData,
        ListPlayerRequestData,
        Player,
    )

    # Extract the data union field
    data_dict = request_obj.get('data', {})
    logger.debug(f"Data dict keys: {list(data_dict.keys())}")

    # Build PlayerRequestData based on which field is present
    request_data = PlayerRequestData()

    if 'load_player' in data_dict:
        load_data = LoadPlayerRequestData(
            player_id=data_dict['load_player']['player_id'],
        )
        request_data.load_player = load_data

    elif 'create_player' in data_dict:
        player_dict = data_dict['create_player']['player']
        player = Player(
            full_name=player_dict['full_name'],
            what_we_call_you=player_dict['what_we_call_you'],
            security_token=player_dict['security_token'],
            over_13=player_dict['over_13'],
            year_of_birth=player_dict['year_of_birth'],
        )
        if 'id' in player_dict and player_dict['id'] is not None:
            player.id = player_dict['id']

        create_data = CreatePlayerRequestData(player=player)
        request_data.create_player = create_data

    elif 'save_player' in data_dict:
        player_dict = data_dict['save_player']['player']
        player = Player(
            full_name=player_dict['full_name'],
            what_we_call_you=player_dict['what_we_call_you'],
            security_token=player_dict['security_token'],
            over_13=player_dict['over_13'],
            year_of_birth=player_dict['year_of_birth'],
        )
        if 'id' in player_dict and player_dict['id'] is not None:
            player.id = player_dict['id']

        save_data = SavePlayerRequestData(player=player)
        request_data.save_player = save_data

    elif 'delete_player' in data_dict:
        delete_dict = data_dict['delete_player']
        delete_data = DeletePlayerRequestData(
            player_id=delete_dict['player_id'],
        )
        request_data.delete_player = delete_data

    elif 'list_player' in data_dict:
        list_dict = data_dict['list_player']
        list_data = ListPlayerRequestData(
            page=list_dict['page'],
            results_per_page=list_dict['results_per_page'],
        )
        if 'search_string' in list_dict and list_dict['search_string']:
            list_data.search_string = list_dict['search_string']
        request_data.list_player = list_data

    else:
        raise ValueError(f"Unknown request type in data: {list(data_dict.keys())}")

    # Build the final PlayerRequest
    return PlayerRequest(data=request_data)


@app.route('/api/invoke', method='POST')
def invoke_method():
    """Invoke a service method with the provided request JSON."""
    try:
        logger.info("=== Starting method invocation ===")
        method_name = request.json.get('method')
        request_json = request.json.get('request')

        logger.info(f"Method: {method_name}")
        logger.debug(f"Request JSON: {request_json}")

        if not method_name or not request_json:
            logger.error("Missing method or request in payload")
            response.status = 400
            return {'error': 'Missing method or request'}

        # Find the method description
        logger.debug(f"Looking for method '{method_name}' in service metadata")
        method_desc = None
        for m in service_metadata.methods:
            if m.method_name == method_name:
                method_desc = m
                break

        if not method_desc:
            logger.error(f"Method '{method_name}' not found in metadata")
            response.status = 404
            return {'error': f'Method {method_name} not found'}

        logger.debug(f"Found method description: {method_desc.description}")

        # Parse the JSON request
        logger.debug("Parsing JSON request")
        try:
            request_obj = json.loads(request_json)
            logger.debug(f"Parsed request object: {request_obj}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            response.status = 400
            return {'error': f'Invalid JSON: {str(e)}'}

        # Check if we have a connection
        if not current_host or not current_port or not current_service_type:
            logger.error("No active connection to service")
            response.status = 400
            return {'error': 'Not connected to any service. Please connect first.'}

        logger.info(f"Using connection: {current_host}:{current_port} (service: {current_service_type})")

        # Convert enum strings to ints
        logger.debug(f"Converting enums to ints (field mappings: {len(method_desc.request_enum_fields)})")
        request_obj = convert_enums_to_ints(request_obj, method_desc.request_enum_fields)
        logger.debug(f"Request after enum conversion: {request_obj}")

        # Connect and invoke
        logger.debug(f"Connecting to service at {current_host}:{current_port}")
        client, transport = connect_to_service(current_host, current_port, current_service_type)
        logger.debug("Connected successfully")

        # Call the appropriate method
        logger.debug(f"Getting method function: {method_name}")
        method_func = getattr(client, method_name)

        # Build the Thrift Request object based on service type
        logger.debug(f"Building Thrift {current_service_type} Request object from JSON")
        if current_service_type == 'inventory':
            thrift_request = build_inventory_request(request_obj)
        elif current_service_type == 'player':
            thrift_request = build_player_request(request_obj)
        elif current_service_type == 'item':
            thrift_request = build_item_request(request_obj)
        else:
            raise ValueError(f"Unknown service type: {current_service_type}")

        logger.debug(f"Thrift {current_service_type} Request object built successfully")

        # Invoke method
        logger.info(f"Invoking method: {method_name}")
        thrift_response = method_func(thrift_request)
        logger.debug(f"Method invocation successful, response type: {type(thrift_response)}")

        transport.close()
        logger.debug("Transport closed")

        # Serialize response back to JSON
        logger.debug("Serializing Thrift response to JSON")
        from thrift.TSerialization import serialize
        response_json_bytes = serialize(thrift_response, TJSONProtocol.TSimpleJSONProtocolFactory())
        response_obj = json.loads(response_json_bytes)
        logger.debug(f"Response before enum conversion: {response_obj}")

        # Convert enum ints to strings
        logger.debug(f"Converting enums to strings (field mappings: {len(method_desc.response_enum_fields)})")
        response_obj = convert_enums_to_strings(response_obj, method_desc.response_enum_fields)
        logger.debug(f"Response after enum conversion: {response_obj}")

        logger.info("=== Method invocation completed successfully ===")
        return {
            'success': True,
            'response': response_obj,
        }

    except Exception as e:
        logger.error("=== Method invocation failed ===")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception message: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        response.status = 500
        return {'error': str(e)}


@app.route('/static/<filepath:path>')
def serve_static(filepath):
    """Serve static files."""
    return static_file(filepath, root='./static')


if __name__ == '__main__':
    print("Starting Fiddler - Thrift Service Explorer")
    print("=" * 60)
    print("Web UI: http://0.0.0.0:8080")
    print("Connect to a Thrift service via the web interface")
    print("=" * 60)

    # Add template path
    TEMPLATE_PATH.insert(0, './templates')

    # Start the server
    app.run(host='0.0.0.0', port=8080, debug=True, reloader=True)
