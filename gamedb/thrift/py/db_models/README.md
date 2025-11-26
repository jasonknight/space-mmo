# Database Models Documentation

## Dependencies
```python
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, Iterator, Union
import mysql.connector
import os
```

## Table of Contents
- [Overview](#overview)
- [Pivot Table Pattern](#pivot-table-pattern)
  - [Understanding Pivot Tables](#understanding-pivot-tables)
  - [Working with Attributes](#working-with-attributes)
  - [Working with Inventories](#working-with-inventories)
- [AttributeOwner](#attributeowner)
  - [Helper Methods](#attributeowner-helper-methods)
  - [__init__()](#attributeowner-__init__)
  - [save()](#attributeowner-save)
  - [find()](#attributeowner-find)
- [Attribute](#attribute)
- [InventoryOwner](#inventoryowner)
  - [Helper Methods](#inventoryowner-helper-methods)
- [Inventory](#inventory)
- [InventoryEntry](#inventoryentry)
- [ItemBlueprintComponent](#itemblueprintcomponent)
- [ItemBlueprint](#itemblueprint)
- [Item](#item)
- [MobileItemAttribute](#mobileitemattribute)
- [MobileItemBlueprintComponent](#mobileitemblueprintcomponent)
- [MobileItemBlueprint](#mobileitemblueprint)
- [MobileItem](#mobileitem)
- [Mobile](#mobile)
- [Player](#player)

## Overview

This module contains auto-generated ActiveRecord-style model classes for all database tables. Each model class provides:

- Property getters/setters for database columns
- Lazy-loaded relationship methods (belongs-to and has-many)
- Transaction-safe save operations with cascading support
- Static finder methods for querying records
- Connection management with MySQL

**Pattern**: All models follow the same structure. The `AttributeOwner` class below is documented in full detail as a template for understanding all other models.

---

## Pivot Table Pattern

### Understanding Pivot Tables

**Pivot tables** (`attribute_owners` and `inventory_owners`) implement many-to-many relationships between owners (Player, Mobile, Item) and their associated data (Attributes, Inventories).

**Key Characteristics:**
- Each pivot record links exactly ONE owner to ONE related record
- Only one owner foreign key is set per pivot record (others are NULL)
- Provides both convenience methods (pivot hidden) and explicit pivot access
- Cascade delete: removing a relationship deletes both the pivot and related record
- No sharing: each owner gets its own copy of related records

### Working with Attributes

#### Quick Start

```python
# Create a player
player = Player()
player.set_full_name('Alice')
player.set_what_we_call_you('Alice')
player.set_security_token('token_123')
player.set_over_13(1)
player.set_year_of_birth(2000)
player.set_email('alice@example.com')
player.save()

# Create and add an attribute
strength = Attribute()
strength.set_internal_name('strength')
strength.set_visible(1)
strength.set_attribute_type('stat')
strength.set_double_value(15.5)

player.add_attribute(strength)  # Creates pivot automatically

# Get all attributes
attributes = player.get_attributes()
for attr in attributes:
    print(f"{attr.get_internal_name()}: {attr.get_double_value()}")

# Remove an attribute (cascade delete)
player.remove_attribute(strength)  # Deletes both pivot and attribute

# Bulk replace all attributes
new_attrs = [attr1, attr2, attr3]
player.set_attributes(new_attrs)  # Removes old, adds new
```

#### Convenience Methods (Recommended)

**On Owner Models** (Player, Mobile, Item):

```python
# Get all attributes (returns List[Attribute])
attributes = player.get_attributes()
attributes = mobile.get_attributes()
attributes = item.get_attributes()

# Add an attribute
player.add_attribute(strength_attr)
# - Saves the attribute if dirty/new
# - Creates pivot with only player_id set
# - All other owner FKs set to NULL

# Remove an attribute (cascade delete)
player.remove_attribute(strength_attr)
# - Deletes the AttributeOwner pivot record
# - Deletes the Attribute record
# - Commits in single transaction

# Replace all attributes
player.set_attributes([attr1, attr2, attr3])
# - Removes all existing attributes (cascade delete)
# - Adds all new attributes
```

#### Explicit Pivot Access (Advanced)

```python
# Get pivot records directly
attribute_owners = player.get_attribute_owners()
for ao in attribute_owners:
    if ao.is_player():
        print(f"Player {ao.get_player_id()} owns attribute {ao.get_attribute_id()}")

# Manual pivot management
pivot = AttributeOwner()
pivot.set_player_id(player.get_id())
pivot.set_attribute_id(attr.get_id())
pivot.set_mobile_id(None)  # Explicitly NULL
pivot.set_item_id(None)
pivot.set_asset_id(None)
pivot.save()
```

#### Helper Methods on AttributeOwner

```python
pivot = AttributeOwner.find(pivot_id)

# Determine owner type
if pivot.is_player():
    print("Belongs to a player")
elif pivot.is_mobile():
    print("Belongs to a mobile")
elif pivot.is_item():
    print("Belongs to an item")
elif pivot.is_asset():
    print("Belongs to an asset")
```

### Working with Inventories

#### Quick Start

```python
# Create a mobile
mobile = Mobile()
mobile.set_mobile_type('goblin')
mobile.set_what_we_call_you('Gobby')
mobile.save()

# Create and add an inventory
backpack = Inventory()
backpack.set_owner_id(mobile.get_id())  # Required field
backpack.set_max_entries(20)
backpack.set_max_volume(100.0)

mobile.add_inventory(backpack)  # Creates pivot automatically

# Get all inventories
inventories = mobile.get_inventories()
for inv in inventories:
    print(f"Max entries: {inv.get_max_entries()}")

# Remove an inventory (cascade delete)
mobile.remove_inventory(backpack)

# Bulk replace
new_invs = [inv1, inv2]
mobile.set_inventories(new_invs)
```

#### Convenience Methods

**On Player and Mobile Models**:

```python
# Get all inventories (returns List[Inventory])
inventories = player.get_inventories()
inventories = mobile.get_inventories()

# Add an inventory
mobile.add_inventory(backpack_inv)
# - Saves the inventory if dirty/new
# - Creates pivot with only mobile_id set
# - All other owner FKs set to NULL

# Remove an inventory (cascade delete)
mobile.remove_inventory(backpack_inv)
# - Deletes the InventoryOwner pivot record
# - Deletes the Inventory record

# Replace all inventories
mobile.set_inventories([inv1, inv2])
```

#### Helper Methods on InventoryOwner

```python
pivot = InventoryOwner.find(pivot_id)

# Determine owner type
if pivot.is_player():
    print("Belongs to a player")
elif pivot.is_mobile():
    print("Belongs to a mobile")
elif pivot.is_item():
    print("Belongs to an item")
```

#### Important Notes

- **No Sharing**: Each owner gets its own Attribute/Inventory records - modifications don't affect other owners
- **Transaction Safety**: All operations are transaction-safe with automatic rollback on error
- **Cascade Delete**: Removing a relationship deletes both the pivot and the related record
- **Optimized Saves**: Only dirty/new records are saved to minimize database calls
- **FK Isolation**: Only one owner FK is set per pivot record to maintain data integrity

---

## AttributeOwner

**Pivot table** linking attributes to their owners (Player, Mobile, Item, Asset).

See [Pivot Table Pattern](#pivot-table-pattern) for comprehensive usage examples.

**Table Schema**:
```sql
CREATE TABLE `attribute_owners` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `attribute_id` bigint NOT NULL,
  `mobile_id` bigint DEFAULT NULL,
  `item_id` bigint DEFAULT NULL,
  `asset_id` bigint DEFAULT NULL,
  `player_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
)
```

### AttributeOwner Helper Methods

```python
def is_player(self) -> bool:
    """Check if this pivot record belongs to a player."""
    ...

def is_mobile(self) -> bool:
    """Check if this pivot record belongs to a mobile."""
    ...

def is_item(self) -> bool:
    """Check if this pivot record belongs to an item."""
    ...

def is_asset(self) -> bool:
    """Check if this pivot record belongs to an asset."""
    ...
```

**Example:**
```python
pivot = AttributeOwner.find(1)
if pivot.is_player():
    player_id = pivot.get_player_id()
    print(f"Attribute belongs to player {player_id}")
```

### Standard Methods

All standard ActiveRecord methods are available:
- `__init__()` - Initialize new instance
- `save()` - Save to database with transaction support
- `find(id)` - Find by primary key
- `find_by_attribute_id(value)` - Find all by attribute_id
- `find_by_player_id(value)` - Find all by player_id
- `find_by_mobile_id(value)` - Find all by mobile_id
- `find_by_item_id(value)` - Find all by item_id
- `find_by_asset_id(value)` - Find all by asset_id
- Getters/setters for all columns

### AttributeOwner.find

```python
@staticmethod
def find(id: int) -> Optional['AttributeOwner']:
    ...
```

Finds a single record by primary key.

**ASCII Execution Graph:**
```
Start
├─ Create new instance
├─ Connect to database
├─ Execute SELECT query with id
├─ Fetch result
│  ├─ [row found] → Load data into instance and return
│  └─ [no row] → Return None
└─ End
```

**Functions called:**
- `AttributeOwner()` - [link to section](#attributeowner-__init__)
- `_connect()` - internal call
- `cursor.execute()` - external call
- `cursor.fetchone()` - external call

**Examples:**

1. **Find by ID** (`gamedb/thrift/py/db_models/tests.py:142` pattern)
```python
related = Attribute.find(fk_value)
```

### AttributeOwner.find_by

Pattern for finding records by specific columns. Each indexed column has a dedicated finder method:

```python
@staticmethod
def find_by_attribute_id(value: int) -> List['AttributeOwner']:
    ...
```

**Available finders:**
- `find_by_attribute_id(value: int)`
- `find_by_mobile_id(value: int)`
- `find_by_item_id(value: int)`
- `find_by_asset_id(value: int)`
- `find_by_player_id(value: int)`

**ASCII Execution Graph:**
```
Start
├─ Create new connection
├─ Execute SELECT query with column filter
├─ Fetch all matching rows
├─ For each row
│  ├─ Create new instance
│  ├─ Load row data into instance
│  └─ Add to results list
├─ Close connection
└─ Return results
```

**Functions called:**
- `mysql.connector.connect()` - external call
- `cursor.execute()` - external call
- `cursor.fetchall()` - external call
- `AttributeOwner()` - [link to section](#attributeowner-__init__)

**Examples:**

No examples found in codebase

### AttributeOwner.get_attribute

```python
def get_attribute(self, strict: bool = False) -> 'Attribute':
    ...
```

Lazy-loads the associated `Attribute` record using the `attribute_id` foreign key. Results are cached after first load.

**ASCII Execution Graph:**
```
Start
├─ Check cache
│  └─ [cached] → Return cached instance
├─ Get foreign key value (attribute_id)
│  └─ [FK is None] → Return None
├─ Lazy load from database
│  └─ Call Attribute.find(fk_value)
├─ Handle strict mode
│  ├─ [result is None and strict=True] → Raise ValueError
│  └─ [result is None and strict=False] → Return None
├─ Cache the result
└─ Return result
```

**Functions called:**
- `get_attribute_id()` - internal getter
- `Attribute.find()` - [link to section](#attribute-find)

**Examples:**

1. **Basic relationship loading** (`gamedb/thrift/py/db_models/tests.py:243-246`)
```python
result = parent.get_attribute()
self.assertIsNotNone(result)
self.assertIsInstance(result, Attribute)
self.assertEqual(result.get_id(), related.get_id())
```

2. **Caching demonstration** (`gamedb/thrift/py/db_models/tests.py:248-250`)
```python
result = parent.get_attribute()
result2 = parent.get_attribute()
self.assertIs(result, result2)  # Same instance
```

### AttributeOwner.set_attribute

```python
def set_attribute(self, model: 'Attribute') -> None:
    ...
```

Sets the associated `Attribute` relationship by updating the foreign key and cache.

**ASCII Execution Graph:**
```
Start
├─ Update cache with new model
├─ Update foreign key
│  ├─ [model is None] → Set attribute_id to None
│  └─ [model provided] → Set attribute_id to model.get_id()
└─ End
```

**Functions called:**
- `set_attribute_id()` - internal setter
- `model.get_id()` - external call on related model

**Examples:**

1. **Setting a relationship** (`gamedb/thrift/py/db_models/tests.py:266-269`)
```python
parent = AttributeOwner()
parent.set_attribute(related1)
# FK automatically updated
self.assertEqual(parent.get_attribute_id(), related1.get_id())
```

---

## Attribute

ActiveRecord-style model for the `attributes` table.

**Table Schema**:
```sql
CREATE TABLE `attributes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `internal_name` varchar(256) NOT NULL,
  `visible` int NOT NULL,
  `attribute_type` varchar(256) NOT NULL,
  `bool_value` int DEFAULT NULL,
  `double_value` double DEFAULT NULL,
  `string_value` mediumtext,
  `text_value` text,
  `datetime_value` datetime DEFAULT NULL,
  `asset_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
)
```

**Key Methods** (follow same pattern as AttributeOwner):
- `__init__()`, `save()`, `find()`
- `find_by_asset_id(value: int)`
- `get_attribute_owners(reload: bool, lazy: bool)` - has-many relationship

### Attribute.save

Same pattern as [AttributeOwner.save](#attributeowner-save)

### Attribute.find

Same pattern as [AttributeOwner.find](#attributeowner-find)

### Attribute.get_attribute_owners

```python
def get_attribute_owners(self, reload: bool = False, lazy: bool = False):
    ...
```

Retrieves all `AttributeOwner` records that reference this attribute (has-many relationship).

**ASCII Execution Graph:**
```
Start
├─ Check if reload requested
│  └─ [reload=False and cached] → Return cached list
├─ [lazy=True] → Return iterator that loads on demand
├─ [lazy=False] → Load all records immediately
│  ├─ Call AttributeOwner.find_by_attribute_id(self.id)
│  ├─ Cache the results
│  └─ Return list
└─ End
```

**Functions called:**
- `get_id()` - internal getter
- `AttributeOwner.find_by_attribute_id()` - [link to section](#attributeowner-find_by)

**Examples:**

No examples found in codebase

---

## Inventory

ActiveRecord-style model for the `inventories` table.

**Table Schema**:
```sql
CREATE TABLE `inventories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `owner_id` bigint NOT NULL,
  `owner_type` varchar(256) DEFAULT NULL,
  `max_entries` int NOT NULL,
  `max_volume` float NOT NULL,
  `last_calculated_volume` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `owner_id` (`owner_id`)
)
```

**Key Methods** (follow same pattern as AttributeOwner):
- `__init__()`, `save()`, `find()`
- `find_by_owner_id(value: int)`
- `get_inventory_entries(reload: bool, lazy: bool)` - has-many relationship
- `get_inventory_owners(reload: bool, lazy: bool)` - has-many relationship

### Inventory.save

Same pattern as [AttributeOwner.save](#attributeowner-save)

### Inventory.find

Same pattern as [AttributeOwner.find](#attributeowner-find)

### Inventory.get_inventory_entries

```python
def get_inventory_entries(self, reload: bool = False, lazy: bool = False):
    ...
```

Retrieves all `InventoryEntry` records in this inventory (has-many relationship).

Same pattern as [Attribute.get_attribute_owners](#attribute-get_attribute_owners)

**Functions called:**
- `InventoryEntry.find_by_inventory_id()`

**Examples:**

1. **Create and use inventory** (`gamedb/thrift/py/db_models/tests.py:123-126`)
```python
seed['inventory1'] = Inventory()
seed['inventory1'].set_max_entries(1)
seed['inventory1'].set_max_volume(1.0)
seed['inventory1'].save()
```

### Inventory.get_inventory_owners

```python
def get_inventory_owners(self, reload: bool = False, lazy: bool = False):
    ...
```

Retrieves all `InventoryOwner` records for this inventory (has-many relationship).

Same pattern as [Attribute.get_attribute_owners](#attribute-get_attribute_owners)

**Functions called:**
- `InventoryOwner.find_by_inventory_id()`

**Examples:**

No examples found in codebase

---

## InventoryEntry

ActiveRecord-style model for the `inventory_entries` table.

**Table Schema**:
```sql
CREATE TABLE `inventory_entries` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `inventory_id` bigint NOT NULL,
  `item_id` bigint NOT NULL,
  `quantity` float NOT NULL,
  `is_max_stacked` int DEFAULT NULL,
  `mobile_item_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_id` (`inventory_id`),
  KEY `item_id` (`item_id`),
  KEY `mobile_item_id` (`mobile_item_id`),
  CONSTRAINT `inventory_entries_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventories` (`id`),
  CONSTRAINT `inventory_entries_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  CONSTRAINT `inventory_entries_ibfk_3` FOREIGN KEY (`mobile_item_id`) REFERENCES `mobile_items` (`id`)
)
```

**Key Methods** (follow same pattern as AttributeOwner):
- `__init__()`, `save()`, `find()`
- `find_by_inventory_id(value: int)`
- `find_by_item_id(value: int)`
- `find_by_mobile_item_id(value: int)`
- `get_inventory(strict: bool)` - belongs-to relationship
- `set_inventory(model: Inventory)`
- `get_item(strict: bool)` - belongs-to relationship
- `set_item(model: Item)`
- `get_mobile_item(strict: bool)` - belongs-to relationship
- `set_mobile_item(model: MobileItem)`

### InventoryEntry.save

Same pattern as [AttributeOwner.save](#attributeowner-save)

### InventoryEntry.find

Same pattern as [AttributeOwner.find](#attributeowner-find)

### InventoryEntry.get_inventory

Same pattern as [AttributeOwner.get_attribute](#attributeowner-get_attribute)

**Functions called:**
- `Inventory.find()`

**Examples:**

No examples found in codebase

### InventoryEntry.get_item

Same pattern as [AttributeOwner.get_attribute](#attributeowner-get_attribute)

**Functions called:**
- `Item.find()`

**Examples:**

No examples found in codebase

---

## InventoryOwner

**Pivot table** linking inventories to their owners (Player, Mobile, Item).

See [Pivot Table Pattern](#pivot-table-pattern) for comprehensive usage examples.

**Table Schema**:
```sql
CREATE TABLE `inventory_owners` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `inventory_id` bigint NOT NULL,
  `mobile_id` bigint DEFAULT NULL,
  `player_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_id` (`inventory_id`),
  KEY `mobile_id` (`mobile_id`),
  KEY `player_id` (`player_id`),
  CONSTRAINT `inventory_owners_ibfk_1` FOREIGN KEY (`inventory_id`) REFERENCES `inventories` (`id`),
  CONSTRAINT `inventory_owners_ibfk_2` FOREIGN KEY (`mobile_id`) REFERENCES `mobiles` (`id`),
  CONSTRAINT `inventory_owners_ibfk_3` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`)
)
```

### InventoryOwner Helper Methods

```python
def is_player(self) -> bool:
    """Check if this pivot record belongs to a player."""
    ...

def is_mobile(self) -> bool:
    """Check if this pivot record belongs to a mobile."""
    ...

def is_item(self) -> bool:
    """Check if this pivot record belongs to an item."""
    ...
```

**Example:**
```python
pivot = InventoryOwner.find(1)
if pivot.is_mobile():
    mobile_id = pivot.get_mobile_id()
    print(f"Inventory belongs to mobile {mobile_id}")
```

### Standard Methods

All standard ActiveRecord methods are available:
- `__init__()` - Initialize new instance
- `save()` - Save to database with transaction support
- `find(id)` - Find by primary key
- `find_by_inventory_id(value)` - Find all by inventory_id
- `find_by_player_id(value)` - Find all by player_id
- `find_by_mobile_id(value)` - Find all by mobile_id
- Getters/setters for all columns

---

## ItemBlueprintComponent

ActiveRecord-style model for the `item_blueprint_components` table.

**Table Schema**:
```sql
CREATE TABLE `item_blueprint_components` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `item_blueprint_id` bigint NOT NULL,
  `item_id` bigint DEFAULT NULL,
  `mobile_item_id` bigint DEFAULT NULL,
  `ratio` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `item_blueprint_id` (`item_blueprint_id`),
  CONSTRAINT `item_blueprint_components_ibfk_1` FOREIGN KEY (`item_blueprint_id`) REFERENCES `item_blueprints` (`id`)
)
```

**Key Methods**: Same pattern as AttributeOwner

**Examples:**

1. **Create blueprint component** (`gamedb/thrift/py/db_models/tests.py:182-186`)
```python
seed['itemblueprintcomponent1'] = ItemBlueprintComponent()
if 'itemblueprint1' in seed:
    seed['itemblueprintcomponent1'].set_item_blueprint_id(seed['itemblueprint1'].get_id())
seed['itemblueprintcomponent1'].set_ratio(1.0)
seed['itemblueprintcomponent1'].save()
```

---

## ItemBlueprint

ActiveRecord-style model for the `item_blueprints` table.

**Table Schema**:
```sql
CREATE TABLE `item_blueprints` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bake_time_ms` int NOT NULL,
  PRIMARY KEY (`id`)
)
```

**Key Methods**: Same pattern as AttributeOwner

**Examples:**

1. **Create blueprint** (`gamedb/thrift/py/db_models/tests.py:134-136`)
```python
seed['itemblueprint1'] = ItemBlueprint()
seed['itemblueprint1'].set_bake_time_ms(1)
seed['itemblueprint1'].save()
```

---

## Item

ActiveRecord-style model for the `items` table. Items can have attributes through the AttributeOwner pivot table.

**Table Schema**:
```sql
CREATE TABLE `items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `internal_name` varchar(256) NOT NULL,
  `item_type` varchar(256) NOT NULL,
  `max_stack_size` int DEFAULT NULL,
  `volume` float DEFAULT NULL,
  `visible` int DEFAULT NULL,
  `asset_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
)
```

### Attribute Convenience Methods

See [Pivot Table Pattern](#pivot-table-pattern) for comprehensive usage guide.

```python
# Get all attributes
attributes = item.get_attributes()

# Get attribute pivot records
attribute_owners = item.get_attribute_owners()

# Add an attribute (creates AttributeOwner pivot)
item.add_attribute(strength_attr)

# Remove an attribute (cascade delete pivot and attribute)
item.remove_attribute(strength_attr)

# Replace all attributes
item.set_attributes([attr1, attr2])
```

### Standard Methods

All standard ActiveRecord methods are available:
- `__init__()`, `save()`, `find()`
- `find_by_asset_id(value: int)`
- Standard getters/setters for all columns

**Examples:**

1. **Create item** (`gamedb/thrift/py/db_models/tests.py:143-146`)
```python
seed['item1'] = Item()
seed['item1'].set_internal_name('test_internal_name_1')
seed['item1'].set_item_type('test_item_type_1')
seed['item1'].save()
```

2. **Use in relationship** (`gamedb/thrift/py/db_models/tests.py:329-332`)
```python
related = Item()
related.set_internal_name('test_internal_name')
related.set_item_type('test_item_type')
related.save()
```

---

## MobileItemAttribute

ActiveRecord-style model for the `mobile_item_attributes` table.

**Table Schema**:
```sql
CREATE TABLE `mobile_item_attributes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `attribute_id` bigint NOT NULL,
  `mobile_item_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `attribute_id` (`attribute_id`),
  KEY `mobile_item_id` (`mobile_item_id`),
  CONSTRAINT `mobile_item_attributes_ibfk_1` FOREIGN KEY (`attribute_id`) REFERENCES `attributes` (`id`),
  CONSTRAINT `mobile_item_attributes_ibfk_2` FOREIGN KEY (`mobile_item_id`) REFERENCES `mobile_items` (`id`)
)
```

**Key Methods**: Same pattern as AttributeOwner

---

## MobileItemBlueprintComponent

ActiveRecord-style model for the `mobile_item_blueprint_components` table.

**Table Schema**:
```sql
CREATE TABLE `mobile_item_blueprint_components` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `item_blueprint_id` bigint NOT NULL,
  `item_id` bigint DEFAULT NULL,
  `mobile_item_id` bigint DEFAULT NULL,
  `ratio` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `item_blueprint_id` (`item_blueprint_id`),
  CONSTRAINT `mobile_item_blueprint_components_ibfk_1` FOREIGN KEY (`item_blueprint_id`) REFERENCES `mobile_item_blueprints` (`id`)
)
```

**Key Methods**: Same pattern as AttributeOwner

**Examples:**

1. **Create mobile blueprint component** (`gamedb/thrift/py/db_models/tests.py:189-193`)
```python
seed['mobileitemblueprintcomponent1'] = MobileItemBlueprintComponent()
if 'mobileitemblueprint1' in seed:
    seed['mobileitemblueprintcomponent1'].set_item_blueprint_id(seed['mobileitemblueprint1'].get_id())
seed['mobileitemblueprintcomponent1'].set_ratio(1.0)
seed['mobileitemblueprintcomponent1'].save()
```

---

## MobileItemBlueprint

ActiveRecord-style model for the `mobile_item_blueprints` table.

**Table Schema**:
```sql
CREATE TABLE `mobile_item_blueprints` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bake_time_ms` int NOT NULL,
  PRIMARY KEY (`id`)
)
```

**Key Methods**: Same pattern as AttributeOwner

**Examples:**

1. **Create mobile blueprint** (`gamedb/thrift/py/db_models/tests.py:154-156`)
```python
seed['mobileitemblueprint1'] = MobileItemBlueprint()
seed['mobileitemblueprint1'].set_bake_time_ms(1)
seed['mobileitemblueprint1'].save()
```

---

## MobileItem

ActiveRecord-style model for the `mobile_items` table.

**Table Schema**:
```sql
CREATE TABLE `mobile_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `mobile_id` bigint NOT NULL,
  `internal_name` varchar(256) NOT NULL,
  `item_type` varchar(256) NOT NULL,
  `slot` varchar(256) DEFAULT NULL,
  `max_stack_size` int DEFAULT NULL,
  `volume` float DEFAULT NULL,
  `visible` int DEFAULT NULL,
  `asset_id` bigint DEFAULT NULL,
  `item_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mobile_id` (`mobile_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `mobile_items_ibfk_1` FOREIGN KEY (`mobile_id`) REFERENCES `mobiles` (`id`),
  CONSTRAINT `mobile_items_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
)
```

**Key Methods**: Same pattern as AttributeOwner

**Examples:**

1. **Create mobile item** (`gamedb/thrift/py/db_models/tests.py:196-203`)
```python
seed['mobileitem1'] = MobileItem()
if 'mobile1' in seed:
    seed['mobileitem1'].set_mobile_id(seed['mobile1'].get_id())
seed['mobileitem1'].set_internal_name('test_internal_name_1')
seed['mobileitem1'].set_item_type('test_item_type_1')
if 'item1' in seed:
    seed['mobileitem1'].set_item_id(seed['item1'].get_id())
seed['mobileitem1'].save()
```

---

## Mobile

ActiveRecord-style model for the `mobiles` table. Mobiles can have both attributes and inventories through pivot tables.

**Table Schema**:
```sql
CREATE TABLE `mobiles` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `mobile_type` varchar(256) NOT NULL,
  `what_we_call_you` varchar(256) NOT NULL,
  `asset_id` bigint DEFAULT NULL,
  `spawn_probability` float DEFAULT NULL,
  `spawn_zone` varchar(256) DEFAULT NULL,
  `behavior_id` bigint DEFAULT NULL,
  `security_token` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
)
```

### Attribute Convenience Methods

See [Pivot Table Pattern](#pivot-table-pattern) for comprehensive usage guide.

```python
# Get all attributes
attributes = mobile.get_attributes()

# Get attribute pivot records
attribute_owners = mobile.get_attribute_owners()

# Add an attribute (creates AttributeOwner pivot)
mobile.add_attribute(strength_attr)

# Remove an attribute (cascade delete pivot and attribute)
mobile.remove_attribute(strength_attr)

# Replace all attributes
mobile.set_attributes([attr1, attr2])
```

### Inventory Convenience Methods

See [Pivot Table Pattern](#pivot-table-pattern) for comprehensive usage guide.

```python
# Get all inventories
inventories = mobile.get_inventories()

# Get inventory pivot records
inventory_owners = mobile.get_inventory_owners()

# Add an inventory (creates InventoryOwner pivot)
mobile.add_inventory(backpack_inv)

# Remove an inventory (cascade delete pivot and inventory)
mobile.remove_inventory(backpack_inv)

# Replace all inventories
mobile.set_inventories([inv1, inv2])
```

### Standard Methods

All standard ActiveRecord methods are available:
- `__init__()`, `save()`, `find()`
- `find_by_asset_id(value: int)`
- `find_by_behavior_id(value: int)`
- Standard getters/setters for all columns

**Examples:**

1. **Create mobile** (`gamedb/thrift/py/db_models/tests.py:206-209`)
```python
seed['mobile1'] = Mobile()
seed['mobile1'].set_mobile_type('test_mobile_type_1')
seed['mobile1'].set_what_we_call_you('test_what_we_call_you_1')
seed['mobile1'].save()
```

2. **Use in relationship** (`gamedb/thrift/py/db_models/tests.py:281-284`)
```python
related = Mobile()
related.set_mobile_type('test_mobile_type')
related.set_what_we_call_you('test_what_we_call_you')
related.save()
```

---

## Player

ActiveRecord-style model for the `players` table. Players can have both attributes and inventories through pivot tables.

**Table Schema**:
```sql
CREATE TABLE `players` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `full_name` varchar(256) NOT NULL,
  `what_we_call_you` varchar(256) NOT NULL,
  `security_token` varchar(256) NOT NULL,
  `over_13` int NOT NULL,
  `year_of_birth` int NOT NULL,
  `email` varchar(256) NOT NULL,
  `asset_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
)
```

### Attribute Convenience Methods

See [Pivot Table Pattern](#pivot-table-pattern) for comprehensive usage guide.

```python
# Get all attributes
attributes = player.get_attributes()

# Get attribute pivot records
attribute_owners = player.get_attribute_owners()

# Add an attribute (creates AttributeOwner pivot)
player.add_attribute(strength_attr)

# Remove an attribute (cascade delete pivot and attribute)
player.remove_attribute(strength_attr)

# Replace all attributes
player.set_attributes([attr1, attr2])
```

### Inventory Convenience Methods

See [Pivot Table Pattern](#pivot-table-pattern) for comprehensive usage guide.

```python
# Get all inventories
inventories = player.get_inventories()

# Get inventory pivot records
inventory_owners = player.get_inventory_owners()

# Add an inventory (creates InventoryOwner pivot)
player.add_inventory(backpack_inv)

# Remove an inventory (cascade delete pivot and inventory)
player.remove_inventory(backpack_inv)

# Replace all inventories
player.set_inventories([inv1, inv2])
```

### Standard Methods

All standard ActiveRecord methods are available:
- `__init__()`, `save()`, `find()`
- `find_by_asset_id(value: int)`
- Standard getters/setters for all columns

**Examples:**

1. **Create player** (`gamedb/thrift/py/db_models/tests.py:163-170`)
```python
seed['player1'] = Player()
seed['player1'].set_full_name('test_full_name_1')
seed['player1'].set_what_we_call_you('test_what_we_call_you_1')
seed['player1'].set_security_token('test_security_token_1')
seed['player1'].set_over_13(1)
seed['player1'].set_year_of_birth(1)
seed['player1'].set_email('test_email_1')
seed['player1'].save()
```

2. **Create multiple players** (`gamedb/thrift/py/db_models/tests.py:172-179`)
```python
seed['player2'] = Player()
seed['player2'].set_full_name('test_full_name_2')
seed['player2'].set_what_we_call_you('test_what_we_call_you_2')
seed['player2'].set_security_token('test_security_token_2')
seed['player2'].set_over_13(2)
seed['player2'].set_year_of_birth(2)
seed['player2'].set_email('test_email_2')
seed['player2'].save()
```
