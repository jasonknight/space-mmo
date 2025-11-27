# Services Layer Exploration

**Exploration Date:** 2025-11-27
**Git Commit:** 9942f614554744b62c16a3fbfbde9a958de98c81
**Git Branch:** main
**Component Path:** /vagrant/gamedb/thrift/py/services/

## Update History
- **2025-11-27 (Commit: 9942f61)**: Updated with architectural evolution context, refactoring history, corrected line numbers, verified snippets directory, added db_models conversion flow guidance, and clarified that broken state is intentional "fix forward" strategy

## Environment
> Reference `/vagrant/current-cycle/tasks/env.md` for complete environment details

- **Language/Runtime:** Python 3.12.3
- **Key Dependencies:**
  - Apache Thrift (RPC framework and code generation)
  - mysql-connector-python (database connectivity)
  - game.ttypes (Thrift-generated types)
- **Build Tools:** Apache Thrift compiler
- **Testing Framework:** Python unittest (tests currently have broken imports)
- **Database:** MySQL (localhost, credentials: admin/minda)

## Overview

The services component provides a Thrift RPC service layer that exposes game operations over the network. It implements three main services (PlayerService, ItemService, InventoryService) that handle CRUD operations and game-specific logic like inventory transfers and stack splitting. Each service follows a handler pattern that receives Thrift request objects, performs operations, and returns Thrift response objects with status results.

**CRITICAL STATUS: This code is currently non-functional (by design).** The services layer underwent multiple failed refactoring attempts that revealed fundamental flaws in the original architecture. Rather than maintain a complex uncommitted changeset, the team decided to "fix forward": commit the broken state while building the new `db_models` layer from scratch with a proper API. Services will be refactored once `db_models` is complete. Nothing depends on this code in production. This exploration documents the intended post-refactor architecture and stable Thrift service definitions.

## Important Files

- `/vagrant/gamedb/thrift/game.thrift:1-708` - Thrift service definitions, request/response structures, and service discovery metadata
- `/vagrant/gamedb/thrift/gen-py/game/PlayerService.py:1-400` - Thrift-generated PlayerService interface (auto-generated, do not edit)
- `/vagrant/gamedb/thrift/gen-py/game/ItemService.py:1-500` - Thrift-generated ItemService interface (auto-generated, do not edit)
- `/vagrant/gamedb/thrift/gen-py/game/InventoryService.py:1-450` - Thrift-generated InventoryService interface (auto-generated, do not edit)
- `/vagrant/gamedb/thrift/py/services/base_service.py:1-332` - Base service handler providing describe() metadata for service discovery
- `/vagrant/gamedb/thrift/py/services/player_service.py:1-391` - PlayerService handler implementation (currently broken)
- `/vagrant/gamedb/thrift/py/services/item_service.py:1-630` - ItemService handler implementation (currently broken)
- `/vagrant/gamedb/thrift/py/services/inventory_service.py:1-648` - InventoryService handler implementation (currently broken)
- `/vagrant/gamedb/thrift/py/services/lru_cache.py:1-74` - LRU cache implementation for service handlers
- `/vagrant/gamedb/thrift/py/inventory.py:1-537` - Core inventory logic functions (add, transfer, split stack operations)
- `/vagrant/gamedb/thrift/py/common.py:1-34` - Utility functions for result checking and table name mapping

## Related Documents

- **Plans using this exploration:** None yet
- **Related explorations:**
  - `/vagrant/current-cycle/tasks/explore-db-models.md` - Database models that services will use after refactoring
- **Supersedes:** None (initial exploration)
- **Superseded by:** N/A

## Architecture Summary

The services layer sits between Thrift RPC endpoints and the data access layer. Each service handler receives typed Thrift request objects, extracts the operation-specific data from discriminated unions, performs business logic, and returns typed Thrift response objects with operation results. The architecture includes a base service providing service discovery metadata, LRU caching for frequently accessed entities, and separation between service coordination logic and pure business logic functions (inventory operations).

Services follow a consistent pattern: validate request structure, perform operation via model layer, construct response with GameResult status objects. The BaseServiceHandler provides a describe() method that returns ServiceMetadata for client service discovery (method signatures, example JSON, enum definitions).

**Current broken state:** Services import from a deleted model layer (`models.player_model`, `models.item_model`, `models.inventory_model`). These need to be replaced with the new ActiveRecord models from `db_models/models.py`.

## Architectural Evolution

The services layer has undergone significant architectural changes:

**Phase 1 (Original):** Singleton `self.db` instance with methods for all model types (`self.db.load_inventory()`, `self.db.load_player()`, etc.)
- **Problem:** Inflexible, tight coupling to database implementation, difficult to test

**Phase 2 (Failed refactor):** Separate `PlayerModel`, `ItemModel`, `InventoryModel` classes
- **Attempt:** Break up singleton into individual model classes
- **Problem:** Still too coupled to database implementation, awkward API, unclear responsibilities
- **Result:** Partially migrated InventoryService (mix of `self.db` and `self.model` calls)

**Phase 3 (Multiple attempts):** Various approaches to fix Phase 2
- **Problem:** Realized the model pattern itself was fundamentally flawed
- **Result:** Multiple broken states across different files

**Phase 4 (Current - "fix forward"):** Build new `db_models` from scratch
- **Decision:** Commit broken code rather than maintain large uncommitted changeset
- **Strategy:** Build new ActiveRecord-style models with proper database abstraction in `/vagrant/gamedb/thrift/py/db_models/`
- **Status:** `db_models` generation complete with 129 passing tests, services await refactoring
- **Risk:** None - no production dependencies yet, this is early development

**Key insight:** The service layer is the **security and abstraction boundary** for the MMO. Client game applications connect via Thrift services, never directly to the database. Services will contain game business logic and coordinate between the database layer and reusable logic libraries (like `inventory.py`). The current "thin proxy" state is temporary while `db_models` API stabilizes.

## Refactoring History Context

**Why the broken imports exist:**

The broken imports and `self.db` references are artifacts from Phases 1-3 above. Each service file reflects a different point in the failed refactoring attempts:

- **PlayerService/ItemService:** Import deleted `models.*_model` classes (Phase 2 artifacts)
- **InventoryService:** Mix of Phase 2 (`self.inventory_model`, `self.item_model`) and Phase 1 (`self.db.*`) calls
- **inventory.py:** Currently operates on Thrift structs directly; may be refactored to use db_models in the future

**Important:** Don't try to fix these incrementally. They should be completely replaced with Phase 4's `db_models` patterns. The Thrift service definitions (in `game.thrift`) and GameResult return patterns are correct and stable - only the internal implementation needs updating.

## Service Layer Architecture

### Three-Tier Design

The service layer implements a three-tier architecture:

1. **Thrift Interface Layer** (gen-py/game/*Service.py) - Auto-generated from game.thrift, defines RPC method signatures
2. **Service Handler Layer** (services/*_service.py) - Implements business logic, validates requests, coordinates operations
3. **Data Access Layer** (MISSING - was models/*.py, will be db_models/models.py) - Manages database persistence

**Current issue:** Tier 3 was deleted, services are broken. After refactoring, services will call ActiveRecord models directly (e.g., `Player.find(id)` instead of `player_model.load(id)`).

### Request/Response Pattern

All service methods follow a consistent pattern using Thrift union types for extensibility:

**Request Structure:**
```
Request
  └─ RequestData (union)
       ├─ load_* (operation 1 data)
       ├─ create_* (operation 2 data)
       ├─ save_* (operation 3 data)
       └─ ... (future operations)
```

**Response Structure:**
```
Response
  ├─ results: list[GameResult] (status, message, optional error_code)
  └─ response_data: ResponseData (union, optional)
       ├─ load_* (operation 1 result)
       ├─ create_* (operation 2 result)
       └─ ... (matches request data variants)
```

**Benefits:**
- Single request/response type per service (extensible via unions)
- Future fields can be added without breaking existing clients (request_id, auth_token, trace_context, etc.)
- Multiple operations can share common error handling
- Supports operation batching (future enhancement)

### Service Discovery via describe()

All services inherit from BaseService which provides a `describe()` method for runtime service introspection.

**Purpose:** Allows dynamic client generation, API documentation, and tools like Fiddler to discover service capabilities without hardcoding.

**Metadata includes:**
- Service name and version
- Method descriptions with human-readable explanations
- Example request/response JSON (with enums as strings for readability)
- Enum definitions with string-to-int mappings
- Field-to-enum type mappings for validation

**Implementation:** BaseServiceHandler (services/base_service.py:40-332) determines which concrete service class is being used and returns appropriate metadata. Example JSON snippets are loaded from services/snippets/ directory.

## PlayerService

Handles player account operations: create, load, save, delete, and paginated listing with search.

**Status:** Currently broken - imports missing `models.player_model.PlayerModel`

**Key Methods:**
- `load(request)` - Loads player by ID, checks LRU cache first (services/player_service.py:66-142)
- `create(request)` - Creates new player account, populates cache after success (services/player_service.py:144-202)
- `save(request)` - Updates existing player or creates new, updates cache (services/player_service.py:204-263)
- `delete(request)` - Deletes player account, invalidates cache entry (services/player_service.py:265-322)
- `list_records(request)` - Returns paginated player list with optional search on name fields (services/player_service.py:324-390)

**Cache Strategy:**
- LRU cache with configurable size (default 1000 entries)
- Cache checked on load(), populated on create()/save(), invalidated on delete()
- Deep copies on get/put to prevent external modifications affecting cached data
- Cache hit avoids database query entirely

**Expected Model API (old, deleted):**
```python
player_model.load(id) -> (GameResult, Player)
player_model.create(player) -> list[GameResult]
player_model.save(player) -> list[GameResult]
player_model.destroy(id) -> list[GameResult]
player_model.search(page, per_page, search_string) -> (GameResult, list[Player], total_count)
```

**Future Model API (ActiveRecord):**
```python
Player.find(id) -> Player or None
player.save() -> None (raises on error)
# Service layer will need to wrap these to return GameResult objects
```

## ItemService

Handles item template operations: CRUD operations, paginated listing with search, autocomplete, and blueprint tree loading.

**Status:** Currently broken - imports missing `models.item_model.ItemModel`

**Key Methods:**
- `create(request)` - Creates new item template (services/item_service.py:69-124)
- `load(request)` - Loads item by ID (services/item_service.py:126-178)
- `save(request)` - Updates existing item or creates new (services/item_service.py:180-234)
- `destroy(request)` - Deletes item template (services/item_service.py:236-290)
- `list_records(request)` - Returns paginated items with search on internal_name (services/item_service.py:292-358)
- `autocomplete(request)` - Lightweight search returning only id and internal_name for UI autocomplete (services/item_service.py:360-450)
- `load_with_blueprint_tree(request)` - Recursively loads item with full component blueprint tree (services/item_service.py:452-532)

**Notable Implementation:**
- No LRU cache (items are templates, assumed to be read through other caches or infrequently accessed)
- Autocomplete uses raw SQL query for performance (services/item_service.py:390-410)
- Blueprint tree builder handles cycles, max depth, and calculates total bake time (services/item_service.py:534-629)

**Blueprint Tree Logic:**
- Recursively loads component items
- Tracks visited items for cycle detection
- Respects max_depth parameter (default 10)
- Calculates cumulative bake_time_ms for entire tree
- Returns BlueprintTreeNode with metadata flags (max_depth_reached, cycle_detected)

## InventoryService

Handles inventory container operations: CRUD, stack splitting, item transfers between inventories, and paginated listing.

**Status:** Currently broken - imports missing `models.inventory_model.InventoryModel` and `models.item_model.ItemModel`, plus invalid `self.db` references

**Key Methods:**
- `load(request)` - Loads inventory by ID, checks LRU cache first (services/inventory_service.py:72-154)
- `create(request)` - Creates new inventory, populates cache (services/inventory_service.py:156-221)
- `save(request)` - Updates inventory, updates cache (services/inventory_service.py:223-285)
- `split_stack(request)` - Splits item stack within inventory, saves result (services/inventory_service.py:287-428)
- `transfer_item(request)` - Moves items between two inventories, saves both (services/inventory_service.py:430-576)
- `list_records(request)` - Returns paginated inventory list (services/inventory_service.py:578-647)

**Cache Strategy:**
- LRU cache for inventories (same pattern as PlayerService)
- Cache invalidation on both source and destination inventories after transfer

**Inventory Business Logic:**
- Delegates to pure functions in inventory.py (split_stack, transfer_item)
- Service layer handles loading, validation, saving, and cache management
- Business logic handles volume calculations, max entries, stack limits, virtual items

**Critical Issues:**
- Lines 179, 245, 320, 386, 456, 474, 491, 531, 535, 606: References to `self.db` methods (load_inventory, save_inventory, load_item, list_inventory)
- `self.db` is never defined in `__init__` (services/inventory_service.py:58-70)
- **Historical context:** `self.db` was a singleton database instance from Phase 1 architecture (see Architectural Evolution above). InventoryService was only partially migrated during Phase 2 refactor - `__init__` creates `self.inventory_model` and `self.item_model` instances, but the method bodies still call the old Phase 1 `self.db` singleton that no longer exists.
- Should use model layer instead (after refactoring: `Inventory.find(id)`, `inventory.save()`)

## BaseServiceHandler

Provides service discovery metadata for all concrete services. Uses class introspection to determine which service is executing and returns appropriate metadata.

**Key Method:**
- `describe()` - Returns ServiceMetadata with methods, enums, examples (services/base_service.py:56-74)

**Private Methods:**
- `_describe_inventory_service()` - Builds InventoryService metadata (services/base_service.py:131-190)
- `_describe_item_service()` - Builds ItemService metadata (services/base_service.py:192-278)
- `_describe_player_service()` - Builds PlayerService metadata (services/base_service.py:280-331)
- `_get_common_enums()` - Returns StatusType and GameError definitions used by all services (services/base_service.py:76-116)
- `_get_common_response_enum_fields()` - Maps response fields to enum types (services/base_service.py:118-129)
- `_load_snippet(filename)` - Loads example JSON from services/snippets/ (services/base_service.py:16-24)

**Usage Pattern:**
```python
class PlayerServiceHandler(BaseServiceHandler, PlayerServiceIface):
    def __init__(self, ...):
        BaseServiceHandler.__init__(self, PlayerServiceHandler)
```

BaseServiceHandler checks `isinstance()` to determine concrete service and returns appropriate metadata.

## LRU Cache Implementation

Simple least-recently-used cache using OrderedDict for service handlers.

**Key Features:**
- Fixed maximum size (configurable, default 1000)
- Deep copy on get/put to prevent cache pollution
- Automatic eviction of oldest entry when full
- Debug logging for hits, misses, evictions

**Methods:**
- `get(key)` - Returns deep copy or None, moves to end (most recent) (services/lru_cache.py:27-41)
- `put(key, value)` - Stores deep copy, evicts LRU if over capacity (services/lru_cache.py:43-59)
- `invalidate(key)` - Removes entry from cache (services/lru_cache.py:61-65)
- `clear()` - Removes all entries (services/lru_cache.py:67-69)
- `size()` - Returns current cache entry count (services/lru_cache.py:71-73)

**Design Decision:** Deep copy prevents external code from modifying cached objects, but has performance cost. Consider removing if profiling shows unnecessary overhead.

## Inventory Business Logic (inventory.py)

Pure functions implementing inventory operations without database dependencies. Service layer calls these functions, handles persistence.

**Core Operations:**

### add_item_to_inventory()
Adds items to inventory considering stacking, volume limits, max entries (inventory.py:143-276).

**Logic:**
1. Calculate item volume if not provided
2. Check if item can be added (volume, max entries, virtual item exemptions)
3. Try to add to existing stacks with free capacity
4. Create new entries if quantity remains
5. Returns list of GameResult objects describing each step

**Handles:**
- Partial adds when inventory has limited capacity
- Multiple stacks of same item (up to max_stack_size each)
- Virtual items bypass volume/count limits
- Max stack detection (sets is_max_stacked flag)

### transfer_item()
Moves items from one inventory to another (inventory.py:350-425).

**Logic:**
1. Validate transfer is possible via can_transfer_item()
2. Add items to destination inventory
3. Subtract quantity from source inventory
4. Remove source entries with zero quantity
5. Returns list of GameResult objects

**Delegates to:** add_item_to_inventory() for destination, handles source cleanup directly

### split_stack()
Splits an inventory entry into two separate entries (inventory.py:466-536).

**Logic:**
1. Validate entry_index exists
2. Validate new_quantity < current quantity
3. Validate inventory not at max_entries
4. Deep copy entry, adjust quantities
5. Append new entry to inventory

**Use case:** Player wants to split stack of 100 ore into two stacks of 60 and 40 for separate storage/trading

### Helper Functions

- `get_item_volume(item, quantity)` - Calculates volume from VOLUME attribute and quantity (inventory.py:56-66)
- `get_item_quantity(item)` - Extracts quantity from QUANTITY attribute (inventory.py:38-42)
- `set_item_quantity(item, quantity)` - Updates QUANTITY attribute (inventory.py:30-35)
- `get_entry_free_quantity(entry, item)` - Calculates remaining stack capacity (inventory.py:45-53)
- `is_item_in_inventory(inventory, item_id, quantity)` - Checks if item exists with sufficient quantity (inventory.py:69-97)
- `can_transfer_item(from, to, item, quantity)` - Validates transfer without executing (inventory.py:279-347)
- `transfer_item_to_first_available_inventory(from, to_list, item, quantity)` - Tries transfer to first accepting inventory (inventory.py:428-463)

## Common Utilities (common.py)

Shared utility functions for result checking and type mapping.

**Functions:**
- `is_true(result)` - Checks if result/list has no FAILURE status (common.py:5-19)
- `is_ok(results)` - Checks if result list has no FAILURE status (common.py:21-26)
- `STR2TABLE` - Reverse map from table name strings to BackingTable enum values (common.py:28-32)

**Usage:**
```python
if is_ok(results):
    # All operations succeeded
else:
    # At least one failure occurred
```

## Thrift Request/Response Structures

All three services use discriminated union patterns for extensibility. Each service defines:
- Request wrapper with union of operation-specific data types
- Response wrapper with results list + optional union of response data types

**Complete structure definitions:** See `/vagrant/gamedb/thrift/game.thrift` (auto-generated code in `gen-py/game/ttypes.py`):
- **PlayerService:** game.thrift:516-590 (operations: Create, Load, Save, Delete, List)
- **ItemService:** game.thrift:408-510 (operations: Create, Load, Save, Destroy, List, Autocomplete, LoadWithBlueprintTree)
- **InventoryService:** game.thrift:312-402 (operations: Load, Create, Save, SplitStack, TransferItem, List)

**Key pattern:** Request/response variants match operation names (e.g., `LoadPlayerRequestData` → `LoadPlayerResponseData`). Services extract the appropriate union field based on which operation was invoked.

## Error Handling and Results

### GameResult Structure

Every operation returns one or more GameResult objects with:
- `status` - StatusType enum (SUCCESS, FAILURE, SKIP)
- `message` - Human-readable description
- `error_code` - Optional GameError enum for programmatic handling

### StatusType Enum (game.thrift:238-242)

- `SUCCESS = 1` - Operation completed successfully
- `FAILURE = 2` - Operation failed (check error_code and message)
- `SKIP = 3` - Operation skipped (not an error, but didn't execute)

### GameError Enum (game.thrift:244-267)

**Inventory Errors:**
- `INV_MAX_ITEMS_REACHED` - Inventory at max_entries
- `INV_ALL_ENTRIES_MAX_STACKED` - All stacks full
- `INV_NEW_VOLUME_TOO_HIGH` - Would exceed max_volume
- `INV_CANNOT_ADD_ITEM` - Cannot add for multiple reasons
- `INV_FAILED_TO_ADD` - Add operation failed
- `INV_FAILED_TO_TRANSFER` - Transfer operation failed
- `INV_COULD_NOT_FIND_ENTRY` - Entry index invalid
- `INV_NEW_QUANTITY_INVALID` - Split quantity invalid
- `INV_FULL_CANNOT_SPLIT` - No room for split
- `INV_ITEM_NOT_FOUND` - Item not in inventory
- `INV_INSUFFICIENT_QUANTITY` - Not enough quantity available
- `INV_OPERATION_FAILED` - Generic inventory operation failure

**Database Errors:**
- `DB_CONNECTION_FAILED` - Cannot connect to database
- `DB_TRANSACTION_FAILED` - Transaction rolled back
- `DB_INSERT_FAILED` - INSERT failed
- `DB_UPDATE_FAILED` - UPDATE failed
- `DB_DELETE_FAILED` - DELETE failed
- `DB_QUERY_FAILED` - SELECT failed
- `DB_RECORD_NOT_FOUND` - Record doesn't exist
- `DB_INVALID_DATA` - Invalid request data
- `DB_FOREIGN_KEY_VIOLATION` - FK constraint violation
- `DB_UNIQUE_CONSTRAINT_VIOLATION` - Unique constraint violation

**Error Message Mapping:**
Constant `INVERR2STRING` maps each error code to user-friendly message (game.thrift:274-297)

## Testing Notes

**Test Location:** `/vagrant/gamedb/thrift/py/services/tests/` (3 test files)

**Status:** Tests have broken imports - they were moved to tests/ subdirectory but imports weren't updated to reflect new location.

**Test Files:**
- `services/tests/player_service_test.py` - Tests PlayerService CRUD operations
- `services/tests/item_service_test.py` - Tests ItemService operations
- `services/tests/inventory_service_test.py` - Tests InventoryService operations

**Test Pattern:**
- Each test creates unique test database
- Sets up tables using SQL from old model layer (also broken)
- Creates service handler with test database credentials
- Executes service methods with Thrift request objects
- Validates response structure and status codes
- Drops test database at end

**Fix Required:** Update imports to use new db_models and correct paths after service refactoring.

## Dependencies

### External
- `mysql-connector-python` - Database connectivity (will be abstracted by model layer)
- Apache Thrift runtime - RPC framework and serialization
- `python-dotenv` - NOT USED (old model layer used it)

### Internal (Thrift-Generated)
- `game.ttypes` - All Thrift struct definitions, enums, constants
- `game.PlayerService.Iface` - PlayerService interface
- `game.ItemService.Iface` - ItemService interface
- `game.InventoryService.Iface` - InventoryService interface
- `game.BaseService.Iface` - BaseService interface

### Internal (Hand-Written)
- `inventory.py` - Pure business logic functions for inventory operations
- `common.py` - Utility functions for result checking
- `services.lru_cache` - LRU cache implementation
- `services.base_service` - Base service handler with describe()

### Internal (MISSING - Need Refactoring)
- `models.player_model.PlayerModel` - DELETED, need to use db_models.models.Player
- `models.item_model.ItemModel` - DELETED, need to use db_models.models.Item
- `models.inventory_model.InventoryModel` - DELETED, need to use db_models.models.Inventory

## Configuration

Services have no configuration files. Database credentials come from:
- **Old approach (deleted):** Constructor parameters from caller
- **New approach (after refactoring):** db_models loads from .env file, services don't need to know

**Service Initialization (current, broken):**
```python
player_service = PlayerServiceHandler(
    host='localhost',
    user='admin',
    password='minda',
    database='gamedb',
    cache_size=1000,
)
```

**Future Initialization:**
```python
# Services won't need database credentials
player_service = PlayerServiceHandler(cache_size=1000)
```

## Known Issues / Technical Debt

> **Note:** Most "issues" below are expected artifacts from the refactoring history described in "Architectural Evolution" above. They are not bugs to fix piecemeal, but rather markers showing which code needs complete replacement with db_models patterns. The Thrift service definitions and GameResult patterns are correct and stable.

### EXPECTED: Services Are Non-Functional (By Design)

**Issue:** Services import from deleted model layer (`models.player_model`, `models.item_model`, `models.inventory_model`).

**Impact:** Services cannot be instantiated or used. All service methods will fail with ImportError.

**Root Cause:** Old hand-written model layer was deleted when switching to generated ActiveRecord models, but services weren't refactored.

**Fix Required:**
1. Remove imports of deleted model classes
2. Import new models from `db_models.models` (Player, Item, Inventory, etc.)
3. Refactor all model calls to use ActiveRecord pattern:
   - `Player.find(id)` instead of `player_model.load(id)`
   - `player.save()` instead of `player_model.save(player)`
   - Wrap model operations to return GameResult objects
4. Remove database credential parameters from service constructors
5. Handle None returns from find() methods (model not found)

**Example Refactoring:**
```python
# OLD (broken):
from models.player_model import PlayerModel
self.player_model = PlayerModel(host, user, password, database)
result, player = self.player_model.load(player_id)

# NEW (after refactoring):
from db_models.models import Player
player = Player.find(player_id)
if player:
    result = GameResult(status=StatusType.SUCCESS, message="Loaded")
else:
    result = GameResult(status=StatusType.FAILURE, error_code=GameError.DB_RECORD_NOT_FOUND)
```

### EXPECTED: InventoryService Has Invalid self.db References

**Issue:** InventoryService references `self.db` methods but `self.db` is never defined.

**Locations:** Lines 179, 245, 320, 386, 456, 474, 491, 531, 535, 606 in services/inventory_service.py

**Impact:** All inventory operations will fail with AttributeError.

**Root Cause:** Phase 1 singleton architecture artifacts (see Architectural Evolution above). InventoryService was only partially migrated during Phase 2.

**Fix Required:** Replace all `self.db.*` calls with:
- `Inventory.find(id)` for loading
- `inventory.save()` for saving
- `Item.find(id)` for item loading

### HIGH: Test Imports Are Broken

**Issue:** Tests in `services/tests/` were moved but imports weren't updated.

**Impact:** Tests cannot run, will fail with ImportError.

**Fix Required:**
1. Update imports to use new db_models
2. Update imports to reflect new file locations
3. Refactor test database setup to use generated model CREATE_TABLE_STATEMENT

### MEDIUM: API Mismatch Between Old and New Model Layer

**Issue:** Services expect tuple/list returns (`result, player = model.load(id)`), but ActiveRecord models return objects or None.

**Impact:** Cannot simply replace imports - need to rewrite method bodies.

**Fix Required:** Wrap ActiveRecord operations in try/catch, construct GameResult objects, handle None returns.

### MEDIUM: Service Constructors Need Database Credentials

**Issue:** Services require host, user, password, database in constructor, but new model layer loads from .env.

**Impact:** Services are not database-agnostic as intended.

**Design Goal:** Services should not know about or care about database implementation.

**Fix Required:** Remove database credential parameters from service constructors. Models handle persistence internally using .env configuration.

### LOW: LRU Cache Uses Deep Copy

**Issue:** LRU cache deep copies all objects on get/put to prevent cache pollution.

**Impact:** Performance cost for large objects (Inventory with many entries, Item with many attributes).

**Design Decision:** May be premature optimization. Consider removing deep copy and trusting callers not to modify cached objects, or removing cache entirely until proven needed by profiling.

### LOW: No Logging Configuration

**Issue:** Services configure logging with `logging.basicConfig()` at module level.

**Impact:** Multiple services configuring logging can interfere with each other. Not configurable by application.

**Fix:** Remove module-level logging configuration, expect application to configure logging before importing services.

### LOW: Example JSON Snippets Exist But May Be Stale

**Issue:** BaseServiceHandler loads example JSON from services/snippets/ directory. The directory exists with all 32 JSON files, but they may be out of date with current Thrift definitions.

**Impact:** describe() method returns potentially stale examples.

**Verification:** Directory `/vagrant/gamedb/thrift/py/services/snippets/` contains all required JSON files for all three services. ✓ Confirmed present.

**Fix:** Verify snippet content matches current request/response structures. Consider generating examples from Thrift definitions instead of maintaining separate files.

### LOW: Code Style Violation in inventory.py

**Issue:** inventory.py:12 uses `from game.ttypes import *` which violates project coding standards.

**Impact:** Makes it unclear which types are imported, can cause namespace pollution.

**Standard:** /vagrant/CLAUDE.md specifies: "Never use import *. Always use `from <library> import ()`"

**Fix:** Replace wildcard import with explicit imports listing all required types from game.ttypes.

## Refactoring Plan

### Phase 1: Fix Imports and Core CRUD

1. Remove imports of deleted model classes (`models.player_model`, etc.)
2. Import ActiveRecord models from `db_models.models` (Player, Item, Inventory, etc.)
3. Remove database credential parameters from service constructors
4. Refactor CRUD methods to use db_models pattern:
   - Use `Model.find(id)` static method to load records
   - Use `model.save()` instance method to persist
   - Use `model.from_thrift(thrift_obj)` to populate from Thrift request data
   - Use `model.into_thrift()` to convert for Thrift response data
   - Wrap db_models operations to return GameResult objects
5. Add proper error handling for None returns from `find()`

**Key conversion flow:**
```python
# Load: Database → Model → Thrift
player = Player.find(player_id)  # Returns model instance or None
if player:
    thrift_player = player.into_thrift()  # Convert to Thrift struct
    # Return in PlayerResponse with GameResult

# Save: Thrift → Model → Database
player = Player.from_thrift(thrift_player)  # Populate model from Thrift
player.save()  # Persist to database
# Return GameResult
```

### Phase 2: Fix Inventory Service

1. Replace all `self.db.*` calls (lines 179, 245, 320, 386, 456, 474, 491, 531, 535, 606) with db_models methods
2. Evaluate whether inventory.py should continue using Thrift structs or be refactored to use db_models
3. Test split_stack and transfer_item operations with new model layer
4. Verify cache invalidation on multi-inventory operations

### Phase 3: Update Tests

1. Fix test imports to use db_models
2. Update database setup to use model CREATE_TABLE_STATEMENT constants
3. Add PYTHONPATH configuration to test runner: `PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH"`
4. Verify all tests pass with new model layer

### Phase 4: Service Discovery and Polish

1. Verify example JSON snippets match current Thrift definitions
2. Test describe() method returns valid metadata
3. Remove module-level logging configuration from service files
4. Fix wildcard import in inventory.py (use explicit imports)
5. Document service initialization and usage patterns

## Design Decisions

### Services Are the Security and Abstraction Boundary

**Decision:** Services are the **only** interface between game clients and the backend. Clients never access the database directly.

**Rationale:**
- **Security:** Client game applications (installed on player computers) connect via Thrift RPC. Services validate all requests, enforce game rules, prevent cheating.
- **Flexibility:** Database technology can change (MySQL → MongoDB → SpacetimeDB) without affecting clients. Only service internals need updating.
- **Scalability:** Services can be deployed as middleware layer, scaled horizontally, run on different machines from database.
- **Business logic:** Services coordinate game operations, enforcing rules that can't be expressed in database constraints.

**Current state:** Services are "thin proxies" during early development while the db_models layer stabilizes. Once refactoring is complete, services will contain rich game logic beyond simple CRUD operations.

**Implementation:** After refactoring, services will only interact with db_models (never direct SQL). Services translate between Thrift types (network format) and database models (persistence format).

### Inventory Logic Separated from Service Layer

**Decision:** Pure inventory business logic lives in inventory.py as stateless, reusable functions. Service layer handles orchestration, persistence, and caching.

**Rationale:**
- Business logic can be tested without service/database overhead
- Logic can be reused by other components (CLI tools, admin panels, test scripts)
- Easier to reason about and modify game rules
- Clear separation of concerns

**Current implementation:** Service layer loads data (from db_models), calls inventory.py functions (which currently operate on Thrift structs), saves results (via db_models).

**Future consideration:** inventory.py may be refactored to accept db_model instances instead of Thrift structs, or services may convert between the two. This will be decided once db_models API is stable and service refactoring begins.

### LRU Cache for Frequently Accessed Entities

**Decision:** PlayerService and InventoryService use LRU cache, ItemService does not.

**Rationale:**
- Players accessed frequently (every request has associated player)
- Inventories accessed frequently (gameplay involves constant inventory checks)
- Items are templates, accessed less frequently, likely cached elsewhere

**Implementation:** Cache size configurable per service instance. Deep copy on get/put prevents cache pollution.

**Reconsideration:** May be premature optimization. Consider removing until profiling shows actual benefit.

### Union-Based Request/Response for Extensibility

**Decision:** Use Thrift unions for request/response data instead of separate methods.

**Rationale:**
- Single RPC method per operation type (not one per CRUD operation)
- Future fields can be added to request/response wrappers (auth, tracing, etc.)
- Supports operation batching (future enhancement)
- Consistent pattern across all services

**Trade-off:** More verbose than separate methods, requires union handling in service code.

### Service Discovery for Dynamic Tooling

**Decision:** All services provide describe() method returning structured metadata.

**Rationale:** Enables tools like Fiddler to dynamically discover and call services without hardcoded knowledge. Supports API documentation generation, client stub generation.

**Implementation:** BaseServiceHandler provides common describe() logic. JSON examples loaded from separate files for maintainability.

### GameResult List Pattern

**Decision:** Operations return list[GameResult] even for single results.

**Rationale:**
- Multi-step operations can report each step (inventory operations have multiple phases)
- Consistent return type across all operations
- Allows partial success reporting (e.g., added 50 of 100 items)

**Usage:** Clients check `is_ok(results)` for overall success, iterate results for details.

## Questions & Assumptions

### Assumptions Made During Exploration

1. **Services should use ActiveRecord directly:** Assumed no wrapper/adapter layer needed between services and db_models. ✓ Confirmed correct.

2. **self.db references are mistakes:** Assumed `self.db` calls should use model layer instead. ✓ Confirmed - old architecture artifact.

3. **Deep copy in cache is intentional:** Assumed deep copy prevents cache pollution. ⚠️ May be premature optimization.

4. **Example JSON snippets exist:** Assumed services/snippets/ directory has JSON files. ✓ Verified - directory contains all 32 required JSON files.

5. **Tests will work after fixing imports:** Assumed tests are well-written and just need import updates. ⚠️ Need verification.

6. **inventory.py will evolve:** Assumed inventory.py may be refactored to use db_models instead of Thrift structs. ⚠️ Design decision pending.

7. **No authentication/authorization yet:** Assumed services trust all requests. ✓ Correct - future enhancement.

8. **Single-threaded operation:** Assumed services handle one request at a time, no concurrency concerns. ⚠️ May need thread-safe cache.

### Unclear Areas Requiring Future Clarification

1. **Cache thread safety:** If services run in multi-threaded server, is LRU cache thread-safe? OrderedDict operations are not atomic.

2. **Transaction boundaries:** Where should database transactions begin/end after refactoring? Service level or model level?

3. **Cascade saves:** When saving Player with embedded Mobile, should service cascade save or expect caller to save separately?

4. **Error detail exposure:** How much database error detail should be exposed in GameResult messages? Security vs debugging trade-off.

5. **Service deployment:** Will services run as separate processes, in single server, or as library? Affects cache sharing and database connection pooling.

6. **Thrift server framework:** Which Thrift server type (TSimpleServer, TThreadedServer, TNonblockingServer)? Affects concurrency model.

7. **db_models conversion strategy:** Should services convert between Thrift and db_models at the service boundary, or should inventory.py and other logic libraries work directly with db_models? Trade-offs between decoupling and conversion overhead.

## Helper Functions

For detailed coverage of utility functions, see the main sections above:
- **Result Checking:** See "Common Utilities (common.py)" section
- **Inventory Helpers:** See "Inventory Business Logic (inventory.py)" section
- **Cache Operations:** See "LRU Cache Implementation" section
