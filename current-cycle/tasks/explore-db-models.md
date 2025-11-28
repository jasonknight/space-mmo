# Database Models Exploration

**Exploration Date:** 2025-11-28
**Git Commit:** 51ef1a445fe8ac65ac4c970aa423c819e42b8b39
**Git Branch:** main
**Component Path:** /vagrant/gamedb/thrift/py/db_models/
**Test Status:** ✅ 157 tests passing

## Environment

> Reference `/vagrant/current-cycle/tasks/env.md` for complete environment details

- **Language:** Python 3.12.3
- **Database:** MySQL (localhost, admin/minda)
- **Dependencies:** mysql-connector-python, python-dotenv, Jinja2, Apache Thrift
- **PYTHONPATH Required:** `/vagrant/gamedb/thrift/gen-py` (for game.ttypes imports)

## Overview

The db_models component **generates** ActiveRecord-style Python model classes from MySQL database schemas. It introspects the database, reads table structures, and produces a single `models.py` file containing all model classes with:

- Getters/setters for all columns
- CRUD operations (save, find, find_by_*)
- Lazy-loaded relationship methods (belongs_to, has_many)
- Bidirectional Thrift conversion (from_thrift, into_thrift)
- Transaction-safe cascade saves
- Pivot table convenience methods

**This is code generation, not a runtime ORM.** You run the generator once to produce models.py, then import and use the generated classes.

## Important Files

- `generate_models.py:1-3488` - Main generator script (run this to regenerate models)
- `models.py:1-9339` - Generated models (14 classes, DO NOT EDIT MANUALLY)
- `tests/tests.py:1-5212` - Generated comprehensive tests
- `README.md:1-1200` - Detailed usage documentation with examples
- `generator/config.py:1-409` - Table-to-Thrift mappings and configuration
- `generator/naming.py:1-144` - Snake_case ↔ PascalCase conversions
- `generator/database.py` - MySQL introspection queries
- `generator/type_mapping.py` - MySQL → Python type mappings

## Generated Model Classes

14 ActiveRecord classes (singular PascalCase from plural snake_case tables):

```
AttributeOwner       ← attribute_owners (pivot)
Attribute            ← attributes
Inventory            ← inventories
InventoryEntry       ← inventory_entries
InventoryOwner       ← inventory_owners (pivot)
ItemBlueprintComponent ← item_blueprint_components
ItemBlueprint        ← item_blueprints
Item                 ← items
MobileItemAttribute  ← mobile_item_attributes
MobileItemBlueprintComponent ← mobile_item_blueprint_components
MobileItemBlueprint  ← mobile_item_blueprints
MobileItem           ← mobile_items
Mobile               ← mobiles
Player               ← players
```

## Quick Start

### Regenerate Models

```bash
cd /vagrant/gamedb/thrift/py/db_models
python3 generate_models.py
```

### Run Tests

```bash
cd /vagrant/gamedb/thrift/py/db_models
PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 tests/tests.py
```

### Use Models in Code

```python
from db_models.models import Player, Mobile, Item, Attribute

# Create and save
player = Player()
player.set_full_name('Alice')
player.set_email('alice@example.com')
player.set_security_token('token123')
player.set_over_13(True)
player.set_year_of_birth(1990)
player.set_what_we_call_you('Alice')
player.save()

# Find by ID
player = Player.find(1)

# Relationships
mobile = player.get_mobile()  # 1-to-1, returns single Mobile or None
attributes = player.get_attributes()  # Many-to-many via pivot, returns List[Attribute]

# Thrift conversion
thrift_player = player.into_thrift()  # Model → Thrift
player2 = Player().from_thrift(thrift_player)  # Thrift → Model (call save() to persist)
player2.save()
```

## Core Patterns

### 1. Owner Union Pattern

Thrift `Owner` union represents polymorphic ownership (player, mobile, item, or asset). **Flattened in DB** to 4 nullable FK columns:

```sql
owner_player_id BIGINT NULL
owner_mobile_id BIGINT NULL
owner_item_id BIGINT NULL
owner_asset_id BIGINT NULL
```

**Exactly one should be set.** Tables have domain-specific valid owner types:
- `mobiles`: only player OR mobile (never item/asset)
- `items`, `inventories`: any owner type valid

**Thrift conversion:**
- `from_thrift(thrift_obj)`: Checks union field, sets corresponding column, nulls others
- `into_thrift()`: Checks which column is non-NULL, creates Owner union

### 2. AttributeValue Union Pattern

Thrift `AttributeValue` union stores typed values. **Flattened in DB** to 6 columns:

```sql
bool_value TINYINT(1) NULL
double_value DOUBLE NULL
vector3_x DOUBLE NULL
vector3_y DOUBLE NULL
vector3_z DOUBLE NULL
asset_id BIGINT NULL
```

**Detection order (priority):**
1. Any of (vector3_x, vector3_y, vector3_z) NOT NULL → Vector3
2. asset_id NOT NULL → asset
3. double_value NOT NULL → double
4. Else → bool (default fallback)

### 3. Pivot Tables (Many-to-Many)

**attribute_owners** and **inventory_owners** implement many-to-many relationships.

**Convenience methods** (recommended):
```python
# Get all related objects
attributes = player.get_attributes()  # Returns List[Attribute]

# Add (creates pivot + saves related object)
player.add_attribute(strength_attr)

# Remove (CASCADE DELETE: deletes pivot AND related object)
player.remove_attribute(strength_attr)

# Replace all
player.set_attributes([attr1, attr2])  # Removes old, adds new
```

**Explicit pivot access** (advanced):
```python
pivots = player.get_attribute_owners()  # Returns List[AttributeOwner]
for pivot in pivots:
    if pivot.is_player():
        attr = pivot.get_attribute()
```

### 4. Player → Mobile (1-to-1)

**Special case:** Player owns exactly one Mobile (the avatar). Thrift embeds mobile inline.

```python
player = Player.find(1)
mobile = player.get_mobile()  # Singular, returns Mobile or None (NOT a list)

# Thrift conversion
thrift_player = player.into_thrift()  # Loads mobile, embeds in Player Thrift struct
player.from_thrift(thrift_player)  # If mobile present, updates/creates mobile
```

### 5. Dirty Tracking & Cascade Saves

Models track changes with `_dirty` flag:
- New models: `_dirty = True`
- After `save()`: `_dirty = False`
- Any `set_*()`: `_dirty = True`
- `save()` skips if not dirty (optimization)

**Cascade saves:**
```python
player.save(cascade=True)  # Saves player + related dirty objects
```

**Transaction support:**
```python
conn = Player._create_connection()
try:
    player.save(connection=conn)
    mobile.save(connection=conn)
    conn.commit()
except:
    conn.rollback()
finally:
    conn.close()
```

## Configuration (generator/config.py)

### Adding New Table Mappings

When adding a table that needs Thrift conversion:

```python
# 1. Add to TABLE_TO_THRIFT_MAPPING
TABLE_TO_THRIFT_MAPPING = {
    'your_table': 'YourThriftStruct',
}

# 2. If table uses Owner union, specify valid types
VALID_OWNER_TYPES = {
    'your_table': ['player', 'mobile'],  # or subset
}

# 3. If table has 1-to-1 relationship
ONE_TO_ONE_RELATIONSHIPS = {
    'parent_table': {
        'your_table': 'foreign_key_column',
    },
}

# 4. Special Thrift handling (optional)
THRIFT_CONVERSION_CONFIG = {
    'your_table': {
        'has_attribute_map': True,
        'has_embedded_relation': True,
    },
}
```

### Key Configuration Constants

- `OWNER_COLUMNS`: List of owner union FK columns
- `ATTRIBUTE_VALUE_COLUMNS`: List of AttributeValue union columns
- `PIVOT_TABLES`: ['attribute_owners', 'inventory_owners']
- `TABLE_TO_THRIFT_MAPPING`: Maps table names to Thrift struct names
- `ONE_TO_ONE_RELATIONSHIPS`: Defines singular relationship method names
- `VALID_OWNER_TYPES`: Per-table valid owner type constraints

## Common Operations

### CRUD Operations

```python
# Create
player = Player()
player.set_full_name('Bob')
player.save()  # INSERT (id is None)

# Read
player = Player.find(1)  # Returns Player or None

# Update
player.set_full_name('Robert')
player.save()  # UPDATE (id is set)

# Find by FK
mobiles = Mobile.find_by_owner_player_id(player.get_id())
```

### Relationships

```python
# Belongs-to (many-to-one)
mobile = Mobile.find(1)
player = mobile.get_owner_player()  # Loads parent

# Has-many (one-to-many)
player = Player.find(1)
items = Item.find_by_owner_player_id(player.get_id())  # Manual query
# OR use has-many methods if generated

# Lazy loading (for large collections)
for mobile in player.get_all_mobiles(lazy=True):  # Iterator, not list
    if mobile.get_id() == target_id:
        break  # Short-circuit
```

### Thrift Conversion

```python
# Model → Thrift (loads relationships as needed)
model = Player.find(1)
thrift_obj = model.into_thrift()

# Thrift → Model (sets fields, does NOT save)
model = Player().from_thrift(thrift_obj)
model.save()  # Must call save() to persist

# Round-trip
model1 = Player.find(1)
thrift = model1.into_thrift()
model2 = Player().from_thrift(thrift)
model2.save()
```

## Key Design Decisions

1. **Single monolithic file**: All models in one models.py (not individual files)
2. **Code generation, not ORM**: Run generator to produce models, then use them
3. **No SQL FK constraints**: Express constraints in code for flexibility
4. **Thrift types aliased**: All Thrift imports use `Thrift` prefix to avoid name collisions
5. **ID-based save logic**: `id == None` → INSERT, `id != None` → UPDATE
6. **Cascade delete on pivot remove**: `remove_attribute()` deletes both pivot and related record
7. **No caching optimization**: Removed to keep code simple (may add back if profiling shows need)

## Edge Cases

- **Missing related records**: Relationship getters return `None` or empty list
- **Unsaved models**: `get_id()` returns `None`, relationship methods return empty
- **Multiple owner FKs set**: Not validated (potential data corruption)
- **Zero owner FKs set**: Not validated (orphaned records)
- **Invalid owner types**: Not validated (e.g., item_id set on mobiles table)

## Known Issues

- **Owner union validation missing**: No code-level checks for exactly-one-owner rule
- **1-to-1 enforcement weak**: Nothing prevents multiple mobiles per player at DB level
- **Import path requires PYTHONPATH**: Must set for game.ttypes imports

## Testing

- **Framework:** Python unittest
- **Test database:** Unique per run (`gamedb_test_<8-char-hex>`)
- **Coverage:** CRUD, relationships, dirty tracking, cascade saves, pivot methods
- **Missing coverage:** Thrift conversion methods not tested

## Helper Functions (for Code Generation)

If modifying the generator:

- `TableNaming.to_pascal_case()` - snake_case → PascalCase
- `TableNaming.singularize()` - 'players' → 'player'
- `TableNaming.pluralize()` - 'player' → 'players'
- `has_thrift_mapping(table_name)` - Check if table has Thrift struct
- `is_one_to_one_relationship()` - Check if relationship is 1-to-1
- `needs_owner_conversion(columns)` - Check if table has Owner union
- `needs_attribute_value_conversion(columns)` - Check if table has AttributeValue union

## Related Documents

- **Environment:** `/vagrant/current-cycle/tasks/env.md`
- **Detailed usage:** `/vagrant/gamedb/thrift/py/db_models/README.md`
- **Thrift definitions:** `/vagrant/gamedb/thrift/game.thrift`
