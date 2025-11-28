# Control Panel Exploration

**Exploration Date:** 2025-11-28
**Git Commit:** 25290a97e0442d6c9b68602d4ca5c93f495ef642
**Git Branch:** main
**Component Path:** /vagrant/gamedb/thrift/control_panel

## Environment
> Reference `./tasks/env.md` for complete environment details

- **Language/Runtime:** Python 3.12.3
- **Key Dependencies:**
  - Bottle (web framework)
  - Apache Thrift (RPC communication)
  - jQuery + Bootstrap 5 (frontend)
  - mysql-connector-python (database access)
- **Build Tools:** thrift compiler
- **Testing Framework:** None (webapp has no tests)

## Overview

The Control Panel is a single-page web application that provides a visual admin interface for managing game database entities (Items, Inventories, Players, Mobiles). Built with Python Bottle on the backend and jQuery + Bootstrap 5 on the frontend, it acts as a bridge between web browsers and Thrift services.

**IMPORTANT: This application is currently broken** - it imports an old `db.py` singleton module that no longer exists (app.py:71). See "Known Issues" section below.

## Important Files

- `app.py:1-2265` - Bottle web server with REST API endpoints and Thrift client creation
- `templates/index.html:1-191` - Single-page application HTML template with Bootstrap UI
- `static/js/app.js:1-200+` - Core JavaScript module handling routing and notifications
- `static/js/item.js` - Item management UI module
- `static/js/inventory.js` - Inventory management UI module
- `static/js/player.js` - Player management UI module
- `static/js/mobile.js` - Mobile management UI module

## Related Documents

- **Plans using this exploration:** None yet
- **Related explorations:** (Need to explore db_models/ and services/ for full context)
- **Supersedes:** None (initial exploration)
- **Superseded by:** N/A

## Architecture Summary

The Control Panel uses a three-tier architecture: a jQuery frontend makes AJAX requests to Bottle REST endpoints, which communicate with Thrift services over TCP. The frontend is organized as a single-page app with modular JavaScript files for each entity type. The backend provides JSON REST APIs that translate between JSON and Thrift protocols.

**Hybrid database access:** The app connects to both Thrift services (for Items, Inventories, Players) and directly to MySQL (for Mobiles), though the direct database access is currently broken.

## Backend - Bottle Web Server (app.py)

The Bottle app provides REST endpoints that proxy requests to Thrift services and serve static files.

**Thrift Client Management:**
- `get_item_service_client()` - Creates ItemService client (port 9091)
- `get_inventory_service_client()` - Creates InventoryService client (port 9090)
- `get_player_service_client()` - Creates PlayerService client (port 9092)

**Serialization Helpers:**
- `thrift_to_dict()` - Converts Thrift objects to JSON-serializable dicts
- `dict_to_item()` - Builds Thrift Item objects from JSON
- `dict_to_inventory()` - Builds Thrift Inventory objects from JSON
- `dict_to_player()` - Builds Thrift Player objects from JSON
- `dict_to_mobile()` - Builds Thrift Mobile objects from JSON

## REST API Endpoints

All endpoints return JSON with `{"success": true/false, ...}` format.

**Items API (lines 556-971):**
- `GET /api/items` - List items with pagination (page, per_page, search params)
- `GET /api/items/<id>` - Get single item by ID
- `POST /api/items` - Create new item
- `PUT /api/items/<id>` - Update existing item
- `DELETE /api/items/<id>` - Delete item
- `GET /api/items/autocomplete` - Search items for autocomplete (search, max_results params)
- `GET /api/items/<id>/blueprint_tree` - Get item with recursive blueprint tree

**Inventories API (lines 978-1233):**
- `GET /api/inventories` - List inventories with pagination
- `GET /api/inventories/<id>` - Get single inventory
- `POST /api/inventories` - Create inventory
- `PUT /api/inventories/<id>` - Update inventory

**Players API (lines 1240-1614):**
- `GET /api/players` - List players with pagination
- `GET /api/players/<id>` - Get single player
- `POST /api/players` - Create player
- `PUT /api/players/<id>` - Update player
- `DELETE /api/players/<id>` - Delete player
- `GET /api/players/search` - Search players by name

**Mobiles API (lines 1622-1954):**
- `GET /api/mobiles` - List NPC mobiles with pagination (uses direct DB queries)
- `GET /api/mobiles/<id>` - Get single mobile (uses db_instance.load_mobile)
- `POST /api/mobiles` - Create mobile (uses db_instance.create_mobile)
- `PUT /api/mobiles/<id>` - Update mobile (uses db_instance.update_mobile)
- `DELETE /api/mobiles/<id>` - Delete mobile (uses db_instance.destroy_mobile)
- `GET /api/mobiles/search` - Search mobiles by name

**Utility Endpoints:**
- `GET /api/enums` - Returns all enum definitions (ItemType, BackingTable, AttributeType)
- `GET /api/owners/<type>/<id>` - Get owner display info (item_id, player_id, mobile_id, asset_id)

## Frontend - Single Page Application

The frontend uses jQuery and Bootstrap 5 to create a tabbed interface with CRUD operations for each entity type.

**Navigation:** Tab-based navigation switches between Items, Inventories, Players, and Mobiles views.

**Modules (static/js/):**
- `app.js` - Core module that handles routing, enum loading, notifications, and view switching
- `item.js` - Item management with support for attributes and blueprints
- `inventory.js` - Inventory management with entries
- `player.js` - Player management with mobile sub-objects
- `mobile.js` - NPC mobile management

**Shared UI Components:**
- Loading overlay spinner
- Toast notifications for success/error messages
- Search modals for selecting components and owners
- Form builders for complex nested objects (attributes, blueprint components)

## Edge Cases & Error Handling

- Missing request data returns 400 Bad Request with error message
- Not found records return 404 with error message
- Thrift service exceptions caught and returned as 500 with error details
- Transport connections closed in finally blocks to prevent leaks
- Frontend displays user-friendly error toasts for failed operations

## Testing Notes

No tests exist for the Control Panel. The README.md file (lines 261-285) documents manual testing with curl commands for API endpoints.

## Dependencies

**External:**
- bottle - Web framework for routing and request handling
- thrift - Apache Thrift RPC library
- mysql-connector-python - Direct database access for mobiles
- jQuery 3.7.0 - Frontend DOM manipulation and AJAX
- Bootstrap 5.3.0 - UI components and styling

**Internal:**
- game.thrift (generated code in gen-py/) - Thrift type definitions and service interfaces
- game.constants - TABLE2STR enum mapping
- db module - Database adapter (CURRENTLY MISSING - see Known Issues)

## Configuration

The app accepts command-line arguments for service connection details:

- `--host` / `--port` - Web server bind address (default: 0.0.0.0:8080)
- `--item-service-host` / `--item-service-port` - ItemService location (default: localhost:9091)
- `--inventory-service-host` / `--inventory-service-port` - InventoryService location (default: localhost:9090)
- `--player-service-host` / `--player-service-port` - PlayerService location (default: localhost:9092)
- `--db-host` / `--db-user` / `--db-password` / `--db-name` - MySQL connection (default: localhost, admin, minda, gamedb)

## Known Issues / Technical Debt

**CRITICAL - Application is currently broken:**

The app imports `from db import DB` at line 71, expecting an old singleton-pattern database module that no longer exists. This causes an ImportError on startup.

**What changed:**
- Old pattern: Singleton `DB` class with methods like `db_instance.load_mobile()`, `db_instance.create_mobile()`
- New pattern: ActiveRecord models in `/vagrant/gamedb/thrift/py/db_models/models.py`

**Where the new database layer lives:**
- **Models:** `/vagrant/gamedb/thrift/py/db_models/models.py` - ActiveRecord classes (Item, Mobile, Player, etc.)
- **Services:** `/vagrant/gamedb/thrift/py/services/*_service.py` - Service handlers using ActiveRecord pattern
- **Example usage:** `item = Item.find(item_id)`, `item.save()`, `item.from_thrift(thrift_obj)`, `results, thrift_obj = item.into_thrift()`

**Affected functionality:**
- All mobile endpoints (GET/POST/PUT/DELETE /api/mobiles/*)
- Owner info lookups for mobiles (GET /api/owners/mobile_id/*)
- Mobile search (GET /api/mobiles/search)

**To fix:**
1. Remove the `from db import DB` import (line 71)
2. Replace all `db_instance.*` calls with direct ActiveRecord model usage from `db_models.models`
3. Alternatively, create a MobileService using Thrift like the other entities (recommended for consistency)
4. Update database connection initialization (lines 2242-2247) to work with ActiveRecord pattern

**Other issues:**
- No automated tests for any functionality
- Error messages could be more specific for validation failures
- Direct SQL queries mixed with Thrift service calls (inconsistent architecture)
- Hardcoded database credentials in defaults (should use environment variables)

## Questions & Assumptions

- **Why hybrid architecture?** Unclear why Mobiles bypass Thrift services while other entities use them
- **Is Mobile special?** Mobile management seems incomplete compared to other entities
- **Test strategy?** Should this webapp have integration tests, or rely on service layer tests?
- **Authentication?** No user authentication exists - is this admin-only tool expected to be behind firewall?

## Helper Functions

- `showLoading()` / `hideLoading()` - Toggle loading spinner overlay
- `showSuccess(message)` / `showError(message)` - Display toast notifications
- `getEnumName(enumType, value)` - Convert enum values to display names
- Various `render*Form()` functions in JS modules - Generate HTML forms for entity types
