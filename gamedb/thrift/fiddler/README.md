# Fiddler - Thrift Service Explorer

Fiddler is a lightweight web application for discovering and interacting with Thrift services that implement the `describe()` method.

## Features

- **Dynamic Service Discovery**: Automatically discovers service methods, parameters, and enums via the `describe()` method
- **Interactive Testing**: Web UI for invoking service methods with JSON requests
- **Enum Support**: Automatically converts between user-friendly enum strings and integer values
- **Real-time Responses**: Displays service responses in formatted JSON
- **Enum Reference Panel**: Shows all available enums and their values alongside the request editor

## Prerequisites

### System Dependencies
```bash
sudo apt-get install python3-bottle
```

### Python Dependencies
The following are included in the system Python installation:
- bottle (web framework)
- thrift (Apache Thrift Python library)

## Directory Structure

```
fiddler/
├── app.py              # Main Bottle web application
├── templates/
│   ├── index.html      # Main UI template
│   └── error.html      # Error page template
├── static/
│   └── style.css       # Application styling
└── README.md           # This file
```

## Setup

### 1. Start the InventoryService

Before running Fiddler, you need to start the Thrift service:

```bash
cd /vagrant/gamedb/thrift/py
python3 run_server.py
```

The service will listen on `localhost:9090` by default.

### 2. Bootstrap the Database (First Time Only)

If this is your first time running the service, create the database:

```bash
cd /vagrant/gamedb/thrift/py
python3 bootstrap.py
```

This creates the `gamedb` database and all necessary tables.

## Running Fiddler

Start the Fiddler web application:

```bash
cd /vagrant/gamedb/thrift/fiddler
python3 app.py
```

The application will:
1. Connect to the InventoryService at `localhost:9090`
2. Call `describe()` to load service metadata
3. Start the web server on `http://0.0.0.0:8080`

## Using Fiddler

1. **Open your browser** to `http://localhost:8080`

2. **Select a method** from the dropdown menu

3. **Edit the request JSON** in the left panel
   - Example JSON is automatically loaded for each method
   - Enum fields should use string values (e.g., `"SUCCESS"` not `1`)

4. **Reference enums** in the right panel
   - View all available enum values
   - See which fields use which enums

5. **Click "Invoke Method"** to execute the request

6. **View the response** below the request editor
   - Enum integers are automatically converted back to strings for readability

## Example Request

For the `create` method:

```json
{
  "data": {
    "create_inventory": {
      "inventory": {
        "max_entries": 10,
        "max_volume": 1000.0,
        "entries": [],
        "owner": {
          "mobile_id": 100
        }
      }
    }
  }
}
```

## Configuration

### Service Connection

Edit `app.py` to change the service connection settings:

```python
def connect_to_service(host='localhost', port=9090):
```

### Web Server Port

Edit the `app.run()` call at the bottom of `app.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=True, reloader=True)
```

## Architecture

### Request Flow

1. User submits JSON request through the web UI
2. Fiddler converts enum strings to integers using metadata from `describe()`
3. JSON is deserialized to a Thrift `Request` object
4. Service method is invoked via Thrift RPC
5. Thrift `Response` is serialized back to JSON
6. Enum integers are converted to strings for display
7. Response is shown in the UI

### Enum Conversion

Fiddler uses `FieldEnumMapping` from the service metadata to know which fields contain enums:

- **Request**: Strings → Integers before sending to service
- **Response**: Integers → Strings before displaying to user

Example mapping:
```python
FieldEnumMapping(
    field_path="results[].status",
    enum_name="StatusType"
)
```

## Troubleshooting

### "Service metadata not loaded" Error

**Problem**: Can't connect to the Thrift service

**Solutions**:
- Ensure the InventoryService is running on `localhost:9090`
- Check that the service implements the `describe()` method
- Verify network connectivity

### "Invalid JSON" Error

**Problem**: Malformed JSON in the request editor

**Solutions**:
- Click "Format JSON" to validate and format your JSON
- Check for missing commas, quotes, or brackets
- Reset to the example JSON by changing methods

### Enum Conversion Errors

**Problem**: Enums not converting properly

**Solutions**:
- Use string values in your JSON (e.g., `"SUCCESS"`)
- Check the Enum Reference panel for valid values
- Verify field paths in the Field Mappings section

## Extending Fiddler

### Supporting Additional Services

Fiddler works with any Thrift service that:

1. Implements a `describe()` method returning `ServiceMetadata`
2. Uses the `Request`/`Response` pattern (or update the serialization code)
3. Provides enum definitions and field mappings in metadata

To add a new service:

1. Update the import in `app.py`:
   ```python
   from game.YourService import Client as YourServiceClient
   ```

2. Update `connect_to_service()` to create the appropriate client

3. Optionally add a service selector dropdown in the UI

## Technical Details

- **Framework**: Bottle (minimal Python web framework)
- **RPC Protocol**: Apache Thrift with TBinaryProtocol
- **Serialization**: TJSONProtocol for JSON↔Thrift conversion
- **Transport**: TBufferedTransport over TSocket
- **Template Engine**: Jinja2 (via Bottle)

## License

This tool is part of the gamedb Thrift service project.
