# Database Models Component Exploration

**Exploration Date:** 2025-11-27
**Git Commit:** a803046747bf543d1649097e62aa2f9d038936ba
**Git Branch:** main
**Component Path:** /vagrant/gamedb/thrift/py/db_models/

## Update History
- **2025-11-27 (Commit: a803046)**: Enhanced with domain model clarifications, design decisions, and implementation guidance based on deep architectural review
- **2025-11-26 (Commit: a803046)**: Initial exploration

## Environment
> Reference `/vagrant/current-cycle/tasks/env.md` for complete environment details

- **Language/Runtime:** Python 3.12.3
- **Key Dependencies:**
  - Apache Thrift (code generation and RPC)
  - mysql-connector-python (database connectivity)
  - Jinja2 (template engine for code generation)
- **Build Tools:** Apache Thrift compiler
- **Testing Framework:** Python unittest (mix of library and adhoc approaches)
- **Database:** MySQL (localhost, credentials: admin/minda)

## Overview

The db_models component is a code generator that introspects MySQL database schemas and generates ActiveRecord-style Python model classes with Thrift integration. It reads database table structures and creates Python classes with getters, setters, CRUD operations, relationship methods (belongs_to, has_many), and bidirectional Thrift conversion methods. The generator handles complex patterns including Owner union types (flattened to multiple nullable FK columns), pivot tables for many-to-many relationships, and AttributeValue union conversion.

This is the **new approach** replacing the legacy hand-written models in `/vagrant/gamedb/thrift/py/dbinc/`. The generator creates a single monolithic `models.py` file with all model classes, plus a corresponding `tests.py` file with comprehensive test coverage.

**CRITICAL NOTE:** The generated code currently has Python import path issues. Tests fail because generated models import from `game.ttypes` without proper PYTHONPATH configuration. Run with: `PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 tests.py`

## Important Files

- `/vagrant/gamedb/thrift/game.thrift:1-683` - Thrift service definitions including Player, Mobile, Item, Inventory, Attribute structs and Owner/AttributeValue unions
- `/vagrant/gamedb/thrift/gen-py/game/ttypes.py:1-6334` - Thrift-generated Python types (auto-generated, do not edit)
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py:1-2663` - Main generator script that introspects database and generates models
- `/vagrant/gamedb/thrift/py/db_models/models.py:1-7201` - Generated ActiveRecord models (all tables in one monolithic file)
- `/vagrant/gamedb/thrift/py/db_models/tests.py:1-3301` - Generated comprehensive test suite
- `/vagrant/gamedb/thrift/py/db_models/templates/model_template.py.tmpl:1-150` - Jinja2 template for model generation
- `/vagrant/gamedb/thrift/py/db_models/generator/naming.py:1-100` - Table/column name conversion utilities (snake_case ↔ PascalCase, pluralization)
- `/vagrant/gamedb/thrift/py/db_models/generator/type_mapping.py:1-50` - MySQL to Python type conversions
- `/vagrant/gamedb/thrift/py/db_models/generator/database.py:1-200` - Database introspection queries
- `/vagrant/gamedb/thrift/py/db_models/generator/config.py:1-184` - Thrift struct to table name mappings and union field configuration

## Related Documents

- **Plans using this exploration:** None yet
- **Related explorations:** None yet
- **Supersedes:** None (initial exploration)
- **Superseded by:** N/A

## Architecture Summary

The generator follows a three-phase process: (1) Database introspection - connects to MySQL and extracts table schemas, foreign key constraints, and unique constraints; (2) Code generation - uses Jinja2 templates to generate Python classes with all methods; (3) File output - writes a single models.py file containing all model classes and a corresponding tests.py file. Each generated model is a self-contained class with its own CREATE TABLE statement for test isolation, database connection management, and full CRUD operations. The generator understands foreign key relationships and generates belongs_to (many-to-one) and has_many (one-to-many) relationship methods with lazy loading and caching support.

## Domain Model: Understanding Game Entity Relationships

This section describes the game domain model that drives the database design and code generation.

### Players and Mobiles: The Avatar Pattern

**Player** is a user account record. To appear in the game world, a player must "own" a **Mobile** (their avatar).

**Critical constraint:** Player→Mobile is strictly **1-to-1**. A player can own exactly one mobile at any time. This mobile is the player's avatar in the game world.

**Why 1-to-1:** Network efficiency. When serializing a Player Thrift object for transmission, the mobile is embedded inline to avoid a second round-trip. The Thrift definition has `Player.mobile` (singular, optional).

**Current code issue:** Generated code creates `player.get_mobiles()` (plural, returns list) instead of `player.get_mobile()` (singular, returns one Mobile). This needs to be fixed.

**Thrift conversion behavior:**
- `Player.from_thrift(thrift_obj)`: If thrift_obj has a mobile, update the existing mobile (if player already owns one) or create new mobile
- `Player.into_thrift()`: Load the single mobile and embed it in the Player Thrift object

### Mobiles: NPCs and Ownership Hierarchies

**Mobile** is a general-purpose NPC/game unit. Mobiles can own other mobiles, creating ownership hierarchies.

**Use case:** A wizard mobile spawns minion mobiles to attack the player. The wizard owns multiple minions.

**Relationships:**
- Mobile→Mobile is **1-to-many**: A mobile can own multiple "child" mobiles (minions)
- Method naming: `mobile.get_minions()` returns child mobiles, `mobile.get_owner_mobile()` returns parent mobile

**Ownership tree example:**
```
Player (id=1)
  └─ Mobile (id=10, owner_player_id=1)  [player's avatar]
       ├─ Mobile (id=20, owner_mobile_id=10)  [minion 1]
       └─ Mobile (id=21, owner_mobile_id=10)  [minion 2]
```

**Future expansion:** Eventually Mobile Thrift struct will add `optional Mobile mobile` (singular) and `bool has_mobiles` flag for efficient serialization. For now, minions are NOT recursively embedded in parent Mobile Thrift objects.

### Items vs MobileItems: Templates and Instances

**Item** (items table): Platonic ideal/template of an item. Shared by all instances. Used in world containers like treasure chests. Immutable from player perspective.

**MobileItem** (mobile_items table): Player-specific instance copy of an item. Created when item transfers from world→player possession. Can be modified (enchantments, durability, custom properties). References original Item via FK for base stats.

**Transfer trigger:** When an item moves from a world container inventory to a mobile's inventory, the system copies Item→MobileItem. This is called "transfer" logic.

**InventoryEntry pattern:**
```
InventoryEntry
  ├─ item_id (FK to items) - the template
  └─ mobile_item_id (FK to mobile_items) - the personalized instance
```

If `mobile_item_id IS NOT NULL`, use that (personalized). Otherwise use `item_id` (world/template item).

**Examples:**
- Treasure chest inventory: InventoryEntry references Item (shared template)
- Player picks up sword from chest: System creates MobileItem copy, updates InventoryEntry to reference MobileItem
- Player enchants sword (+2 strength): Changes only affect MobileItem, not Item template
- Another player finds same chest: Gets Item template (unenchanted)

### Inventories and Ownership

**Inventory** is a container for items. Owned by exactly one entity (Player, Mobile, Item, or Asset via Owner union).

**Current implementation:** Uses `inventory_owners` pivot table, which is legacy/overly-generic from a previous developer. Real relationships should be direct FK columns: `owner_player_id`, `owner_mobile_id`, `owner_item_id`.

**Future addition:** `owner_mobile_item_id` column will be added when MobileItem ownership is implemented.

**Inventory structure:**
```
Inventory
  └─ InventoryEntries (many)
       ├─ item_id → Item (template, for world items)
       └─ mobile_item_id → MobileItem (instance, for player items)
```

## Owner Union Pattern: Polymorphic Ownership

Thrift defines an Owner union with four variants: player_id, mobile_id, item_id, asset_id. This represents polymorphic ownership - "this entity is owned by one of these types."

**Database representation:** The union is flattened into four nullable FK columns where exactly one should be non-NULL:
```sql
owner_player_id BIGINT NULL
owner_mobile_id BIGINT NULL
owner_item_id BIGINT NULL
owner_asset_id BIGINT NULL
```

**Critical constraint (not enforced by DB):** For mobiles table, only `owner_player_id` OR `owner_mobile_id` can be set. `owner_item_id` and `owner_asset_id` are **never valid** - items and assets cannot own mobiles. These columns exist only because a previous developer flattened the entire Owner union generically without considering domain constraints.

**Validation needed:** Code-level validation should enforce:
- Mobiles: only player_id XOR mobile_id (never item/asset)
- Exactly one owner FK set (never zero, never multiple)
- Different tables may have different valid owner types

**Thrift conversion:**
- `from_thrift(thrift_obj)`: Checks which union field is set, populates corresponding column, sets others to NULL
- `into_thrift()`: Checks which column is non-NULL, creates Owner union with that field

**Tables using Owner pattern:**
- mobiles (valid: player, mobile; invalid: item, asset)
- items (valid: player, mobile, item, asset)
- inventory_owners pivot table (valid: player, mobile, item, asset)
- attribute_owners pivot table (valid: player, mobile, item, asset)

## AttributeValue Union Pattern: Typed Values

Thrift defines an AttributeValue union for storing different typed values: bool, double, Vector3 (x/y/z), or asset_id. The attributes table flattens this into multiple nullable columns.

**Database representation:**
```sql
bool_value TINYINT(1) NULL
double_value DOUBLE NULL
vector3_x DOUBLE NULL
vector3_y DOUBLE NULL
vector3_z DOUBLE NULL
asset_id BIGINT NULL
```

**Variant detection (priority order):**
1. If any of (vector3_x, vector3_y, vector3_z) IS NOT NULL → Vector3 type (all three must be set)
2. Else if asset_id IS NOT NULL → asset type
3. Else if double_value IS NOT NULL → double type (can be 0.0, negative, positive)
4. Else → bool type (default fallback; NULL = false, 0 = false, 1 = true)

**Note:** `bool_value` is the fallback type when all other columns are NULL. This means every Attribute must have a value - there's no "empty" Attribute state.

**Thrift conversion:**
- `from_thrift(thrift_obj)`: Checks AttributeValue union variant, populates appropriate column(s)
- `into_thrift()`: Uses priority order to determine variant, creates AttributeValue union

## Pivot Tables and Attribute Maps

Some tables use pivot tables for many-to-many relationships. The generator creates special helper methods for these.

### attribute_owners Pivot Table

Links attributes to owners (player, mobile, item, or asset via Owner union).

**Purpose:** Implements Thrift's `map<AttributeType, Attribute>` on Item and Mobile.

**Generated methods:**
- `get_attributes()` - Returns all attributes for this owner
- `add_attribute(attr)` - Links attribute to owner
- `remove_attribute(attr)` - Deletes attribute record AND removes association (cascade delete)
- `set_attributes(attrs)` - Replaces all attributes

**Map conversion:** When converting Item or Mobile to Thrift, the generator loads all related Attribute records through the pivot table and builds a `map<AttributeType, Attribute>` using the attribute's `attribute_type` field as the map key.

**Duplicate handling:** If database has multiple Attributes with same `attribute_type` for one owner, `into_thrift()` uses last-write-wins (last one overwrites previous in map). This is self-healing - duplicates are normalized when saving back to DB.

**Save behavior:** `from_thrift(thrift_obj)` with attribute map should delete all existing attributes for this owner, then recreate from map (clean slate approach). This prevents orphaned attributes and handles map key removals correctly.

### inventory_owners Pivot Table

Links inventories to owners (player, mobile, item, or asset via Owner union).

**Note:** This table is legacy/overly-generic from a previous developer. In reality, each inventory should be owned by exactly one entity (not many-to-many). The pivot table is superfluous - direct FK columns would be clearer.

## Generator Main Script (generate_models.py)

The main entry point that orchestrates the entire generation process. Connects to MySQL using credentials from .env file, introspects all tables in the database, analyzes foreign key and unique constraints to build relationship metadata, and generates a single models.py file containing all model classes plus a tests.py file with comprehensive relationship tests.

Key functions:
- `main()` - Entry point that orchestrates database connection, introspection, and code generation
- `generate_model()` - Generates a complete model class from table metadata using the template
- `generate_tests()` - Generates comprehensive unittest test cases for all models
- `generate_from_thrift_method()` - Creates method to populate model from Thrift object
- `generate_into_thrift_method()` - Creates method to convert model to Thrift object
- `generate_belongs_to_methods()` - Creates getter/setter methods for belongs-to relationships
- `generate_has_many_methods()` - Creates methods to query related records
- `generate_pivot_helper_methods()` - Creates add/remove/set methods for pivot table relationships
- `generate_owner_union_to_db_code()` - Converts Thrift Owner union to flattened owner_*_id columns
- `generate_db_to_owner_union_code()` - Converts flattened owner_*_id columns back to Thrift Owner union
- `generate_attribute_value_to_db_code()` - Converts Thrift AttributeValue union to flattened attribute columns
- `generate_db_to_attribute_value_code()` - Converts flattened attribute columns back to Thrift AttributeValue union

## Database Introspection (generator/database.py)

Queries MySQL INFORMATION_SCHEMA to extract table structures, column definitions, foreign keys, and unique constraints. Returns structured metadata that drives code generation.

Key functions:
- `get_all_tables()` - Queries INFORMATION_SCHEMA.TABLES to list all tables
- `get_table_columns()` - Extracts column definitions with types, nullability, defaults
- `get_foreign_key_constraints()` - Reads FK relationships from INFORMATION_SCHEMA.KEY_COLUMN_USAGE
- `get_unique_constraints()` - Identifies unique indexes for validation
- `get_create_table_statement()` - Retrieves exact CREATE TABLE DDL for embedding in model classes

## Naming Conventions (generator/naming.py)

Handles conversion between database naming (snake_case, plural table names) and Python naming (PascalCase classes, snake_case methods). Implements basic pluralization/singularization rules.

Key functions:
- `singularize()` - Converts plural table names to singular (e.g., "players" → "player")
- `pluralize()` - Converts singular to plural for method names
- `to_pascal_case()` - Converts snake_case to PascalCase for class names
- `to_snake_case()` - Converts PascalCase to snake_case for file/method names
- `column_to_relationship_name()` - Converts FK column name to relationship method name (e.g., "owner_player_id" → "owner_player")

**Special case:** Player→Mobile relationship should generate `get_mobile()` (singular) not `get_mobiles()` (plural). This requires custom logic for 1-to-1 relationships.

## Type Mapping (generator/type_mapping.py)

Maps MySQL data types to Python types for type hints and value handling.

Key mappings:
- `VARCHAR/TEXT → str`
- `BIGINT/INT → int`
- `TINYINT(1) → bool`
- `DOUBLE/FLOAT → float`
- `DATETIME/TIMESTAMP → datetime`

## Configuration (generator/config.py)

Defines which database tables correspond to which Thrift structs for conversion method generation. Only tables with Thrift equivalents get `from_thrift()` and `into_thrift()` methods.

**Current implementation:** Hardcoded `TABLE_TO_THRIFT_MAPPING` dictionary.

**Desired implementation:** Parse `game.thrift` for annotations like `//@mysql_table(players)` to auto-discover mappings. This eliminates manual configuration and keeps Thrift definition as single source of truth.

Key mappings (current):
- `players → Player`
- `mobiles → Mobile`
- `items → Item`
- `mobile_items → MobileItem`
- `inventories → Inventory`
- `inventory_entries → InventoryEntry`
- `attributes → Attribute`
- `item_blueprints → ItemBlueprint`
- `item_blueprint_components → ItemBlueprintComponent`

**Union field configuration:**
- `OWNER_COLUMNS`: List of owner union FK columns
- `ATTRIBUTE_VALUE_COLUMNS`: List of AttributeValue union columns
- `PIVOT_TABLES`: List of pivot/junction tables
- `THRIFT_CONVERSION_CONFIG`: Special handling flags for tables (has_attribute_map, has_attribute_value_union, etc.)

## Generated Model Structure (models.py)

A single Python file containing all generated model classes. Each model class includes:

### Core Infrastructure

- Class-level `CREATE_TABLE_STATEMENT` constant with exact DDL
- `__init__()` - Initializes empty `_data` dict, connection, and marks as dirty
- `_connect()` / `_disconnect()` - Database connection management
- `_create_connection()` - Static factory for new connections

### CRUD Operations

- `save(connection, cascade)` - INSERT or UPDATE with transaction support and cascade saves
- `find(id)` - Static method to load record by primary key
- `find_by_*()` - Static methods for each foreign key column
- Dirty tracking - `_dirty` flag prevents unnecessary saves

**ID-based save logic:**
- `id == None` → INSERT (new record)
- `id != None` → UPDATE (existing record)
- Caller sets ID from Thrift object or leaves None for new records

### Getters/Setters

- `get_<column>()` - Returns value from `_data` dict
- `set_<column>(value)` - Sets value and marks dirty

### Relationship Methods

- `get_<related>()` - Loads related record(s) with caching
- `set_<related>()` - Updates FK and caches related object
- Lazy loading support with `lazy=True` parameter (returns iterator)
- Cache invalidation with `reload=True` parameter

**Special naming:**
- `player.get_mobile()` - Singular for 1-to-1 relationship
- `mobile.get_minions()` - Returns child mobiles owned by this mobile
- `mobile.get_owner_mobile()` - Returns parent mobile (if owned by mobile)
- `mobile.get_owner_player()` - Returns player owner (if this is player avatar)

### Pivot Table Methods (for many-to-many)

- `get_<related_plural>()` - Queries through pivot table
- `add_<related>()` - Creates pivot record
- `remove_<related>()` - Deletes pivot record and related record (cascade delete)
- `set_<related_plural>()` - Replaces all related records

### Thrift Conversion Methods

- `from_thrift(thrift_obj)` - Populates model from Thrift object (data only, no DB queries, returns model instance)
- `into_thrift()` - Converts model to Thrift object (loads relationships as needed, returns Thrift object)

**Conversion behavior:**
- `from_thrift()`: Sets fields from Thrift object, does NOT save to database (caller must call `save()`)
- `into_thrift()`: Loads related objects as needed to populate Thrift struct (e.g., Player loads mobile)
- For attributes: `from_thrift()` should delete all existing attributes then recreate (clean slate)
- For 1-to-1 relationships: Update existing record if ID is set, create new if ID is None

## Relationships

The generator analyzes foreign keys to create relationship methods:

### Belongs-to (many-to-one)

Generated when table has FK column pointing to another table.

- Creates `get_<relation>()` method that loads single related record
- Creates `set_<relation>()` method that updates FK and caches object
- Example: `mobile.get_owner_player()` loads the Player that owns this Mobile

### Has-many (one-to-many)

Generated when another table has FK pointing to this table.

- Creates `get_<relations>()` method that queries related records
- Supports lazy loading (returns iterator) and eager loading (returns list)
- Example: `mobile.get_minions()` finds all Mobiles where owner_mobile_id = mobile.id

**Special case:** Player→Mobile should be 1-to-1, so `player.get_mobile()` returns single Mobile, not list.

### Pivot relationships (many-to-many through junction table)

Detected when table has two FKs and limited other columns.

- Generates full CRUD methods: get, add, remove, set
- Example: `player.add_inventory(inv)` creates record in inventory_owners pivot table
- `remove_*()` performs cascade delete of related record, not just pivot entry

## Cascade Saves

The `save(cascade=True)` method walks relationships and saves related objects.

### Belongs-to cascade

Before saving parent, saves any cached belongs-to related objects that are dirty. Updates FK with newly assigned IDs. Ensures related objects exist before creating parent.

### Has-many cascade

After saving parent, saves any cached has-many related objects that are dirty. Ensures parent exists with valid ID before creating children.

### Attributes are special

Attributes are NOT cascaded. Instead, `save()` should:
1. Delete all existing attributes for this owner
2. INSERT new attribute records from attribute map
3. This is simpler than matching/updating and handles removals correctly

### Transaction support

Accepts optional `connection` parameter for transaction management. If no connection provided, creates and commits own transaction. If connection provided, participates in caller's transaction.

## Dirty Tracking

Models use `_dirty` flag to track whether database save is needed:
- New models start with `_dirty = True`
- After successful `save()`, `_dirty` set to False
- Any `set_*()` call sets `_dirty = True`
- `save()` returns immediately if `_dirty = False` (optimization)

## Caching

**Current implementation:** Relationship getters cache loaded objects in instance variables.

**Design decision:** Caching should be **removed** - it's premature optimization. Issues:
- Cache goes stale if another thread/process updates DB
- Adds complexity without clear benefit
- `reload=True` parameter needed to bypass cache

**Recommendation:** Remove caching entirely until performance profiling shows it's actually needed.

## Lazy Loading Use Case

Lazy loading is for nested traversal where you can short-circuit early.

**Example:** Check if player (via any controlled mobile) has a quest item:
```python
# Without lazy: loads ALL mobiles, ALL inventories into memory before checking any
# With lazy: iterates one at a time, stops when found
for mobile in player.get_all_mobiles(lazy=True):  # lazy iterator
    for inventory in mobile.get_inventories(lazy=True):  # lazy iterator
        if is_virtual_item_in_inventory(inventory, quest_item_id):
            return True  # Found it! Short-circuit, stop loading more
```

**Use cases:**
- Searching for specific item across ownership tree
- Admin tools querying large collections
- Any operation that can terminate early

**Not for:** Situations where you need all records anyway (eager loading is simpler).

## Edge Cases & Error Handling

### Missing related records

- `get_<relation>()` methods return None if FK points to non-existent record
- `find()` returns None if record not found

### Unsaved models

- `get_id()` returns None for new unsaved models
- Relationship getters return empty list/None if parent ID is None
- Pivot methods raise ValueError if trying to add related objects to unsaved parent

### Owner union validation

**Current:** Generated code doesn't enforce "exactly one owner FK set" rule.

**Issues:**
- Multiple owner FKs could be set simultaneously (data corruption)
- Zero owner FKs could be set (orphaned records)
- No database constraints enforce single-owner rule
- No validation that only valid owner types are used (e.g., mobiles can only be owned by player or mobile, never item/asset)

**Needed:** Code-level validation in setters and `from_thrift()` method.

### Transaction failures

- `save()` rolls back transaction on exception
- Connection closed in finally block to prevent leaks

## Testing Notes

**Test file:** `/vagrant/gamedb/thrift/py/db_models/tests.py` (3301 lines)
**Status:** Generated but cannot run due to import path issues

**Workaround:** `PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 tests.py`

### Test Structure

- Module-level `setUpModule()` creates unique test database per run
- Each model gets a test class `Test<ModelName>Relationships`
- Tests cover: belongs-to getters/setters, has-many lazy/eager loading, dirty tracking, cascade saves
- Module-level `tearDownModule()` drops test database after all tests complete

### Test Database

- Unique name per run: `gamedb_test_<8-char-hex>`
- Tables created from model CREATE_TABLE_STATEMENT constants
- Foreign key constraint handling: Either disable with `SET FOREIGN_KEY_CHECKS=0` or create tables in dependency order
- Complete cleanup after tests

**Design decision:** Foreign key constraints are avoided in development - they're "futzy" and can change over time. Better to express constraints in code. A previous developer added them to the schema, but they're not essential.

### Missing Test Coverage

- Thrift conversion methods (from_thrift/into_thrift) not tested
- Owner union conversion not tested
- AttributeValue union conversion not tested
- Pivot table attribute map conversion not tested
- Pass-through relationships not tested (e.g., player → mobile → inventories)
- 1-to-1 Player→Mobile constraint not tested

## Dependencies

### External

- `mysql-connector-python` - Database connectivity and cursor operations
- `python-dotenv` - Loading .env file for database credentials
- `jinja2` - Template engine for code generation
- Apache Thrift compiler - Generates ttypes.py from game.thrift

### Internal

- `base_model.py` - NOT USED (old approach, replaced by generator)
- `db_tables.py` - NOT USED (old approach, replaced by generator)
- `/vagrant/gamedb/thrift/py/dbinc/*` - NOT USED (old hand-written models, replaced by generator)
- `game.ttypes` - Thrift-generated types imported by models.py

## Configuration

### Environment Variables (.env file)

```
DB_HOST=localhost
DB_USER=admin
DB_PASSWORD=minda
DB_DATABASE=gamedb
```

### Generator Execution

```bash
cd /vagrant/gamedb/thrift/py/db_models
python3 generate_models.py
```

No command-line arguments needed - everything comes from .env file.

### Running Tests

```bash
cd /vagrant/gamedb/thrift/py/db_models
PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 tests.py
```

## Design Decisions & Implementation Guidance

This section documents key design decisions that affect code generation and usage.

### Foreign Key Constraints: Code Over Database

**Decision:** Avoid using MySQL foreign key constraints. Express constraints in application code instead.

**Rationale:**
- FK constraints are "futzy" during development
- Constraints can change frequently while evolving the schema
- Easier to temporarily relax constraints for testing/debugging
- More explicit control over cascade behavior
- Previous developer added FK constraints, but they're not essential

**Implementation:** Generator should either create tables in dependency order or wrap CREATE TABLE in `SET FOREIGN_KEY_CHECKS=0`.

### ID-Based Save Logic: Trust the Caller

**Decision:** Use ID presence to determine INSERT vs UPDATE. Trust that IDs in Thrift objects are correct.

**Logic:**
- `model.id == None` → INSERT new record
- `model.id != None` → UPDATE existing record with that ID

**Implications:**
- `from_thrift(thrift_obj)` sets model.id from thrift_obj.id
- Caller is responsible for providing correct IDs
- No validation that ID exists in DB before UPDATE
- No checking for conflicts or stale data

**Future:** Add sanitization/validation layer - don't trust user input (could be attacker). But for now, trust the data.

### Attribute Map: Delete-Then-Recreate

**Decision:** When saving attributes from Thrift map, delete all existing attributes for the owner, then INSERT new ones.

**Rationale:**
- Simpler than matching existing records and updating
- Handles map key removals correctly (deleted keys = no record)
- Handles map key changes correctly (type change = delete old, insert new)
- Self-healing for duplicate AttributeTypes

**Implementation:** `save()` or `from_thrift()` should execute DELETE then INSERT, not cascade save.

### Thrift Struct Mapping: Annotations Over Configuration

**Current:** Hardcoded mapping dictionary in `generator/config.py`.

**Desired:** Parse annotations in `game.thrift` like `//@mysql_table(players)`.

**Benefits:**
- Single source of truth (Thrift file)
- No manual configuration updates when adding tables
- Explicit documentation in Thrift definition
- Generator auto-discovers mappings

**Example:**
```thrift
//@mysql_table(players)
struct Player {
    1: optional i64 id,
    2: optional string name,
    3: optional Mobile mobile,
}

// No annotation = no DB mapping (network-only struct)
struct NetworkMessage {
    1: string type,
    2: binary payload,
}
```

### Caching: Premature Optimization

**Decision:** Remove relationship caching entirely.

**Issues with current caching:**
- Stale data if DB updated by another process
- Added complexity (cache invalidation, reload parameter)
- No evidence it's actually needed
- Encourages holding models in memory longer than necessary

**Recommendation:** Remove `_<relation>_cache` instance variables and `reload=True` parameters. Load fresh on every call until profiling shows caching is needed.

### Player→Mobile: Enforce 1-to-1 in Code

**Decision:** Player owns exactly one mobile (the avatar). Enforce in generated methods, not DB constraints.

**Implementation:**
- `player.get_mobile()` - Singular method name, returns one Mobile
- `player.set_mobile(mob)` - Sets/replaces the avatar mobile
- `Player.from_thrift(thrift_obj)`: If thrift_obj.mobile present, update existing mobile or create new
- `Player.into_thrift()`: Load mobile and embed in Player Thrift object
- No validation preventing multiple mobiles per player at DB level (yet)

**Future:** May add validation or unique constraint when design stabilizes.

### Owner Union: Valid Types Per Table

**Decision:** Different tables have different valid owner types. Express as code-level validation, not DB constraints.

**Valid owner types:**
- **mobiles:** player_id OR mobile_id (never item/asset)
- **items:** player_id, mobile_id, item_id, or asset_id (all valid)
- **inventories:** player_id, mobile_id, item_id, or asset_id (all valid)

**Why item_id/asset_id exist on mobiles table:** Previous developer flattened Owner union generically without considering domain constraints. These columns should never be populated for mobiles.

**Implementation needed:** Validation in `set_owner_*()` methods and `from_thrift()` to enforce valid owner types per table.

## Known Issues / Technical Debt

### CRITICAL: Import Path Broken

**Issue:** Generated models.py imports `from game.ttypes import ...` but Python path doesn't include `/vagrant/gamedb/thrift/gen-py`. Tests fail immediately with ModuleNotFoundError.

**Impact:** Cannot run any generated code. All tests fail on import.

**Workaround:** `PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 tests.py`

**Fixes to consider:**
1. Set PYTHONPATH in test runner or documentation
2. Modify generated imports to use relative path
3. Add path manipulation in generated code header
4. Create __init__.py with path setup

### CRITICAL: Player-Mobile Relationship Generates Wrong Method Name

**Issue:** Thrift defines `Player.mobile` (singular, optional) for 1-to-1 relationship, but generator creates `player.get_mobiles()` (plural, returns list) treating it as 1-to-many.

**Impact:**
- API doesn't reflect intended 1-to-1 relationship
- Confusing method name (sounds like player owns multiple mobiles)
- No enforcement of singular mobile per player
- `from_thrift()` doesn't update existing mobile, may create duplicates
- `into_thrift()` doesn't embed mobile in Player object

**Design intent:** Player should have exactly one active mobile for network serialization efficiency. When Player Thrift object is sent over network, mobile is embedded inline to avoid second round-trip.

**Fix needed:**
1. Generate `player.get_mobile()` (singular) instead of `player.get_mobiles()`
2. Modify `from_thrift()` to update existing mobile or create new (not create duplicates)
3. Modify `into_thrift()` to load mobile and embed in Player Thrift object
4. Consider adding validation to prevent multiple mobiles per player

### HIGH: Owner Union Validation Missing

**Issue:** Owner union pattern uses four nullable FKs (owner_player_id, owner_mobile_id, owner_item_id, owner_asset_id) but no validation ensures exactly one is set or that only valid types are used.

**Impact:**
- Could set multiple owner FKs simultaneously (data corruption)
- Could set zero owner FKs (orphaned records)
- Could set invalid owner types (e.g., item_id on mobiles table)
- No database constraints enforce single-owner rule
- No validation of domain-specific constraints

**Fix needed:**
1. Add validation in `set_owner_*()` methods to clear other owner FKs
2. Add validation in `from_thrift()` method to ensure exactly one owner
3. Add per-table validation of valid owner types (e.g., mobiles only allow player/mobile)
4. Consider CHECK constraint: `(owner_player_id IS NOT NULL)::int + (owner_mobile_id IS NOT NULL)::int + ... = 1`

### HIGH: Thrift Struct Mapping Hardcoded

**Issue:** Table-to-Thrift mappings are hardcoded in `generator/config.py`. Must manually update when adding new tables.

**Impact:**
- Manual synchronization between game.thrift and config.py
- Easy to forget updating config when adding tables
- Thrift definition is not single source of truth

**Fix needed:** Implement annotation parsing from game.thrift (`//@mysql_table(table_name)`) to auto-discover mappings.

### MEDIUM: Thrift Conversion Not Tested

**Issue:** Generated `from_thrift()` and `into_thrift()` methods exist but have no test coverage.

**Impact:** Unknown if conversions work correctly. Owner union and AttributeValue union conversions particularly complex and error-prone.

**Fix needed:** Generate test cases that round-trip objects through Thrift conversion, including:
- Owner union variants
- AttributeValue union variants
- Attribute maps
- Embedded relationships (Player.mobile)
- Null handling

### MEDIUM: Attribute Map Conversion Incomplete

**Issue:** Code exists to convert pivot table attributes to `map<AttributeType, Attribute>` but unclear if fully implemented and working, especially the delete-then-recreate logic.

**Impact:** May not be able to serialize Item/Mobile attributes correctly to Thrift. Orphaned attributes may accumulate.

**Fix needed:**
1. Implement delete-all-then-recreate in `from_thrift()` or `save()`
2. Test attribute map conversion in both directions
3. Verify duplicate AttributeType handling (last-write-wins in into_thrift)

### MEDIUM: Caching Adds Complexity Without Clear Benefit

**Issue:** Relationship methods cache loaded objects, requiring `reload=True` parameter and cache invalidation logic.

**Impact:**
- Stale data if database updated elsewhere
- Added complexity in generated code
- No evidence caching provides meaningful performance benefit
- Encourages anti-pattern of holding models too long

**Fix needed:** Remove caching entirely. Simplify generated code. Add back only if profiling shows it's needed.

### LOW: inventory_owners Pivot Table Superfluous

**Issue:** `inventory_owners` uses pivot table for inventory ownership, but inventories should be owned by exactly one entity (not many-to-many).

**Impact:** Overcomplicated schema. Direct FK columns would be clearer.

**Design decision:** Legacy from previous developer who didn't understand the domain. Works but suboptimal.

**Fix:** Refactor to direct FK columns when time permits. Not urgent.

### LOW: Cascade Delete Behavior May Be Surprising

**Issue:** `remove_<relation>()` methods on pivot tables perform cascade delete of related records (e.g., `player.remove_inventory(inv)` deletes the Inventory record itself, not just the pivot entry).

**Impact:** Potentially surprising behavior. May not want to delete Inventory just because removing from player.

**Design decision needed:** Document whether pivot remove should cascade delete or just remove association. Current behavior may be correct for some tables (attributes) but wrong for others (inventories).

### LOW: Pass-Through Relationships Not Generated

**Issue:** Generator doesn't create methods to traverse multi-hop relationships. Example: Player owns Mobile, Mobile owns Inventories, but no `player.get_inventories()` helper.

**Impact:** Must manually traverse relationships in application code. No convenience methods for common patterns.

**Design decision:** Nice-to-have for admin functions, not critical path. Admin tools can manually traverse. Don't add complexity to generator until proven needed.

**Fix if needed:** Generator should detect transitive relationships and create helper methods like `player.get_all_inventories(include_mobile_inventories=True)`.

## Questions & Assumptions

### Assumptions Made During Exploration

1. **One mobile per player intended:** Assumed Thrift's singular `Player.mobile` means one-to-one relationship, not one-to-many. ✓ Confirmed correct.

2. **Import path issue is configuration:** Assumed tests are meant to run but PYTHONPATH needs configuration, not a fundamental design flaw. ✓ Correct - just needs workaround or documentation.

3. **Pivot cascade delete intentional:** Assumed `remove_<relation>()` cascade delete is intended behavior, not a bug. ⚠️ Needs case-by-case review.

4. **AttributeValue conversion complete:** Assumed attribute value union conversion is fully implemented. ⚠️ Needs testing to verify, especially delete-then-recreate logic.

5. **No soft deletes:** Assumed hard deletes are correct approach. No deleted_at timestamp or soft delete pattern. ✓ Correct for now.

6. **FK constraints not essential:** Assumed foreign key constraints can be avoided/disabled without issue. ✓ Confirmed - design decision to use code-level constraints.

7. **Caching is premature:** Assumed caching adds complexity without proven benefit. ✓ Confirmed - should be removed.

8. **ID-based save is sufficient:** Assumed trusting IDs from Thrift objects is acceptable for now. ✓ Confirmed - sanitization is future work.

### Unclear Areas Requiring Future Clarification

1. **Cascade delete semantics:** For each pivot table, should `remove_*()` delete the related record or just the association? May differ per table.

2. **Attribute map uniqueness enforcement:** Should code prevent duplicate AttributeTypes per owner, or just handle gracefully via self-healing?

3. **Inventory ownership exclusivity:** Should inventory_owners enforce exclusive ownership (one owner at a time)?

4. **Mobile ownership recursion depth:** Mobile can own mobile (which owns mobile...). Are there depth limits? Cycle detection needed?

5. **When to add validation:** Balance between "trust the data" (current) and "sanitize all input" (future). What's the trigger for adding validation?

## Helper Functions

Brief coverage of utility functions in the generator:

### Relationship Builders

- `build_relationship_metadata()` - Analyzes all FK constraints to build belongs-to and has-many relationships for all tables
- `get_pivot_table_info()` - Detects pivot tables (2+ FKs, minimal other columns)
- `get_pivot_owner_relationships()` - Finds tables that are targets of pivot table FKs
- `is_pivot_table()` - Heuristic to identify junction tables (checks PIVOT_TABLES config and FK count)

### Code Generation Helpers

- `generate_imports()` - Builds import statements based on column types and features used
- `generate_getters()` / `generate_setters()` - Creates accessor methods for all columns
- `generate_find_by_methods()` - Creates static finders for each FK column
- `generate_cascade_save_code()` - Generates code to walk and save relationships (excluding attributes)

### Naming Helpers

- `needs_owner_conversion()` - Checks if table has owner_*_id columns
- `needs_attribute_value_conversion()` - Checks if table has attribute value union columns
- `has_thrift_mapping()` - Checks if table has corresponding Thrift struct
- `get_thrift_struct_name()` - Returns Thrift struct name for table (from config)

### Template Helpers

- `format_sql()` - Indents and escapes SQL for embedding in Python strings
- `escape_quotes()` - Escapes triple quotes in SQL statements for Python multi-line strings
