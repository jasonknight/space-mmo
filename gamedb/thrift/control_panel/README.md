# Control Panel - Game Database Admin

A professional web-based admin interface for managing game database entities (Items, Inventories, and Players) using a single-page application architecture.

## Overview

The Control Panel provides an intuitive interface for creating, reading, updating, and deleting (CRUD) game database entities. It communicates with Thrift services over HTTP and provides:

- **Item Management**: Full CRUD operations for game items including attributes and blueprints
- **Inventory Management**: (Coming soon)
- **Player Management**: (Coming soon)

## Architecture

### Technology Stack

- **Backend**: Python 3 with Bottle web framework
- **Frontend**: jQuery + Bootstrap 5
- **Services**: Apache Thrift (ItemService, InventoryService, PlayerService)
- **Database**: MySQL

### Project Structure

```
control_panel/
├── app.py                    # Bottle web server with REST API
├── templates/
│   └── index.html           # Single-page application template
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       ├── app.js           # Core app logic and utilities
│       ├── item.js          # Item CRUD module
│       ├── inventory.js     # (Future) Inventory CRUD module
│       └── player.js        # (Future) Player CRUD module
└── README.md
```

## Prerequisites

1. **Python 3.7+** with the following packages:
   - bottle
   - thrift
   - mysql-connector-python

2. **MySQL Server** running with the `gamedb` database

3. **Thrift Services** must be running:
   - ItemService (default: localhost:9090)

## Installation

### 1. Install Python Dependencies

From the thrift directory:

```bash
pip install bottle thrift mysql-connector-python
```

### 2. Compile Thrift Definitions

Make sure the Thrift files are compiled:

```bash
cd /vagrant/gamedb/thrift
thrift --gen py game.thrift
```

### 3. Set up the Database

Ensure the MySQL database is running and the `gamedb` database exists with all tables:

```bash
# Test database connection
mysql -uadmin -pminda -e "USE gamedb; SHOW TABLES;"
```

## Running the Application

### Step 1: Start the ItemService

Open a terminal and start the ItemService Thrift server:

```bash
cd /vagrant/gamedb/thrift/py
python3 item_server.py --host localhost --port 9090 --database gamedb
```

You should see:
```
INFO - ItemService starting on localhost:9090
INFO - Using database: gamedb
INFO - Press Ctrl+C to stop
```

### Step 2: Start the Control Panel

In another terminal, start the Control Panel web application:

```bash
cd /vagrant/gamedb/thrift/control_panel
python3 app.py --host localhost --port 8080
```

You should see:
```
INFO - Starting Control Panel on localhost:8080
INFO - Connecting to ItemService at localhost:9090
Bottle v0.12.x server starting up...
```

### Step 3: Access the Web Interface

Open your web browser and navigate to:

```
http://localhost:8080
```

## Usage

### Item Management

#### Listing Items

1. Click on **Items** in the navigation bar (active by default)
2. Use the search box to filter items by internal name
3. View paginated results with item details
4. Items per page: 20 (configurable)

#### Creating a New Item

1. Click the **Create Item** button
2. Fill in the basic information:
   - **Internal Name** (required): Non-localized identifier
   - **Item Type** (required): Select from dropdown (VIRTUAL, CONTAINER, WEAPON, etc.)
   - **Max Stack Size** (optional): Maximum stackable quantity
   - **Backing Table** (optional): Database table identifier

3. **Add Attributes** (optional):
   - Click **Add Attribute**
   - Select attribute type from dropdown
   - Enter internal name
   - Choose visibility (Yes/No)
   - Select value type (Bool, Double, Vector3, Asset ID)
   - Enter the value
   - Click **Save**
   - Repeat to add more attributes

4. **Add Blueprint** (optional):
   - Check **This item has a blueprint**
   - Enter bake time in milliseconds
   - Click **Add Component** to add blueprint components:
     - Type to search for items
     - Select an item from the search results
     - Set the ratio (0.1 - 1.0)
     - Click **Add Component**
   - Repeat to add more components

5. Click **Create Item** to save

#### Editing an Item

1. Find the item in the list
2. Click the **Edit** button
3. Modify fields as needed
4. Add or remove attributes
5. Add or remove blueprint components
6. Click **Update Item** to save changes

#### Deleting an Item

1. Find the item in the list
2. Click the **Delete** button
3. Confirm the deletion in the dialog

#### Searching Items

Use the search box to filter items by internal name. Press Enter or click the search icon to search.

### Attributes

Attributes are key-value pairs associated with items. They support:

- **14 Attribute Types**: Including TRANSLATED_NAME, QUANTITY, SIZE, GALACTIC_POSITION, etc.
- **4 Value Types**: Bool, Double, Vector3, Asset ID
- **Owner References**: Link attributes to specific entities
- **Visibility Control**: Show or hide attributes

### Blueprints

Blueprints define crafting/recycling recipes:

- **Components**: Map of ItemID → (ratio, item_id)
- **Ratio**: How much each component contributes (0.1 to 1.0)
- **Bake Time**: Crafting time in milliseconds
- **Search Integration**: Find items via autocomplete

## API Endpoints

The Control Panel exposes the following REST API endpoints:

### Items

- `GET /api/items` - List items with pagination
  - Query params: `page`, `per_page`, `search`
- `GET /api/items/:id` - Get a single item
- `POST /api/items` - Create a new item
- `PUT /api/items/:id` - Update an item
- `DELETE /api/items/:id` - Delete an item
- `GET /api/items/autocomplete` - Search items for autocomplete
  - Query params: `search`, `max_results`

### Enums

- `GET /api/enums` - Get all enum definitions

## Configuration

### Control Panel Options

```bash
python3 app.py --help

Options:
  --host HOST               Host to bind to (default: localhost)
  --port PORT               Port to bind to (default: 8080)
  --item-service-host HOST  ItemService host (default: localhost)
  --item-service-port PORT  ItemService port (default: 9090)
```

### ItemService Options

```bash
python3 item_server.py --help

Options:
  --host HOST           Host to bind to (default: localhost)
  --port PORT           Port to bind to (default: 9090)
  --db-host HOST        Database host (default: localhost)
  --db-user USER        Database user (default: admin)
  --db-password PASS    Database password (default: minda)
  --database DB         Database name (default: gamedb)
```

## Development

### Adding New Features

The modular JavaScript architecture makes it easy to extend:

1. **New Entity Type**: Create a new `<entity>.js` module following the pattern in `item.js`
2. **New Fields**: Update the form rendering in the module
3. **New API Endpoints**: Add routes in `app.py`
4. **Styling**: Customize `static/css/style.css`

### Testing

Test the API endpoints directly:

```bash
# List items
curl "http://localhost:8080/api/items?page=1&per_page=5"

# Get item
curl "http://localhost:8080/api/items/1"

# Create item
curl -X POST http://localhost:8080/api/items \
  -H "Content-Type: application/json" \
  -d '{"internal_name": "test_item", "item_type": 4, "max_stack_size": 100}'

# Update item
curl -X PUT http://localhost:8080/api/items/1 \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "internal_name": "updated_item", "item_type": 4}'

# Delete item
curl -X DELETE http://localhost:8080/api/items/1

# Autocomplete
curl "http://localhost:8080/api/items/autocomplete?search=copper"
```

## Troubleshooting

### Control Panel Can't Connect to ItemService

**Error**: `Could not connect to any of [('127.0.0.1', 9090)]`

**Solution**:
1. Verify ItemService is running: `netstat -tlnp | grep 9090`
2. Check ItemService logs
3. Ensure correct host/port configuration

### Database Connection Failed

**Error**: `Database connection failed`

**Solution**:
1. Verify MySQL is running: `sudo systemctl status mysql`
2. Check credentials: `mysql -uadmin -pminda gamedb`
3. Ensure database exists: `SHOW DATABASES;`

### Items Not Loading

**Solution**:
1. Check browser console for JavaScript errors (F12)
2. Verify API endpoint returns data: `curl http://localhost:8080/api/items`
3. Check ItemService logs for errors

### Autocomplete Not Working

**Solution**:
1. Verify the autocomplete endpoint works: `curl "http://localhost:8080/api/items/autocomplete?search=test"`
2. Check that items table has data: `mysql -uadmin -pminda -e "SELECT COUNT(*) FROM gamedb.items;"`

## Future Enhancements

- [ ] Inventory CRUD interface
- [ ] Player CRUD interface
- [ ] Mobile entity management
- [ ] Bulk operations (import/export CSV)
- [ ] Advanced search with filters
- [ ] Real-time updates via WebSockets
- [ ] User authentication and authorization
- [ ] Audit logging
- [ ] Data validation with better error messages
- [ ] Undo/redo functionality

## Contributing

When adding new features:

1. Follow the existing code structure
2. Use Bootstrap 5 components for consistency
3. Keep JavaScript modular (one file per entity type)
4. Add proper error handling
5. Update this README with new features

## License

This project is part of the game database system. Internal use only.

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the Thrift service logs
- Inspect browser console for errors
- Verify database schema is up to date
