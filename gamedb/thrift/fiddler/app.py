#!/usr/bin/env python3
"""
Fiddler - A generic Thrift service explorer and testing tool.

This webapp provides a web UI to discover and interact with any Thrift service
that implements the describe() method.
"""

import sys
import json
import re
from bottle import Bottle, request, response, static_file, TEMPLATE_PATH
from bottle import jinja2_template as template

# Add paths for Thrift imports
sys.path.append('../gen-py')
sys.path.append('../py')

# Thrift imports
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from game.InventoryService import Client as InventoryServiceClient

app = Bottle()

# Store service metadata and connection info
service_metadata = None
enum_lookup = {}  # enum_name -> {string_value -> int_value}
enum_reverse_lookup = {}  # enum_name -> {int_value -> string_value}
current_host = None
current_port = None


def connect_to_service(host, port):
    """Create and return a Thrift client connection."""
    transport = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = InventoryServiceClient(protocol)
    transport.open()
    return client, transport


def load_service_metadata(host, port):
    """Load service metadata by calling describe()."""
    global service_metadata, enum_lookup, enum_reverse_lookup, current_host, current_port

    try:
        client, transport = connect_to_service(host, port)
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
        data = request.json
        server_address = data.get('server')

        if not server_address:
            response.status = 400
            return {'error': 'Missing server address'}

        # Parse host:port
        if ':' in server_address:
            host, port_str = server_address.split(':', 1)
            try:
                port = int(port_str)
            except ValueError:
                response.status = 400
                return {'error': 'Invalid port number'}
        else:
            host = server_address
            port = 9090  # Default port

        # Try to connect and load metadata
        load_service_metadata(host, port)

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
        response.status = 500
        return {'error': str(e)}


@app.route('/api/invoke', method='POST')
def invoke_method():
    """Invoke a service method with the provided request JSON."""
    try:
        method_name = request.json.get('method')
        request_json = request.json.get('request')

        if not method_name or not request_json:
            response.status = 400
            return {'error': 'Missing method or request'}

        # Find the method description
        method_desc = None
        for m in service_metadata.methods:
            if m.method_name == method_name:
                method_desc = m
                break

        if not method_desc:
            response.status = 404
            return {'error': f'Method {method_name} not found'}

        # Parse the JSON request
        try:
            request_obj = json.loads(request_json)
        except json.JSONDecodeError as e:
            response.status = 400
            return {'error': f'Invalid JSON: {str(e)}'}

        # Check if we have a connection
        if not current_host or not current_port:
            response.status = 400
            return {'error': 'Not connected to any service. Please connect first.'}

        # Convert enum strings to ints
        request_obj = convert_enums_to_ints(request_obj, method_desc.request_enum_fields)

        # Connect and invoke
        client, transport = connect_to_service(current_host, current_port)

        # Call the appropriate method
        method_func = getattr(client, method_name)

        # Serialize request to thrift Request object
        from thrift.protocol import TJSONProtocol
        from thrift.TSerialization import deserialize
        from game.ttypes import Request as ThriftRequest

        json_str = json.dumps(request_obj)
        thrift_request = deserialize(ThriftRequest(), json_str.encode('utf-8'),
                                     protocol_factory=TJSONProtocol.TSimpleJSONProtocolFactory())

        # Invoke method
        thrift_response = method_func(thrift_request)

        transport.close()

        # Serialize response back to JSON
        from thrift.TSerialization import serialize
        response_json_bytes = serialize(thrift_response, TJSONProtocol.TSimpleJSONProtocolFactory())
        response_obj = json.loads(response_json_bytes)

        # Convert enum ints to strings
        response_obj = convert_enums_to_strings(response_obj, method_desc.response_enum_fields)

        return {
            'success': True,
            'response': response_obj,
        }

    except Exception as e:
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
