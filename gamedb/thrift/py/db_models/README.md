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
- [AttributeOwner](#attributeowner)
  - [__init__()](#attributeowner-__init__)
  - [save()](#attributeowner-save)
  - [find()](#attributeowner-find)
  - [find_by_*()](#attributeowner-find_by)
  - [get_attribute()](#attributeowner-get_attribute)
  - [set_attribute()](#attributeowner-set_attribute)
- [Attribute](#attribute)
  - [save()](#attribute-save)
  - [find()](#attribute-find)
  - [get_attribute_owners()](#attribute-get_attribute_owners)
- [Inventory](#inventory)
  - [save()](#inventory-save)
  - [find()](#inventory-find)
  - [get_inventory_entries()](#inventory-get_inventory_entries)
  - [get_inventory_owners()](#inventory-get_inventory_owners)
- [InventoryEntry](#inventoryentry)
  - [save()](#inventoryentry-save)
  - [find()](#inventoryentry-find)
  - [get_inventory()](#inventoryentry-get_inventory)
  - [get_item()](#inventoryentry-get_item)
- [InventoryOwner](#inventoryowner)
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

## AttributeOwner

ActiveRecord-style model for the `attribute_owners` table.

**Table Schema**:
```sql
CREATE TABLE `attribute_owners` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `attribute_id` bigint NOT NULL,
  `mobile_id` bigint DEFAULT NULL,
  `item_id` bigint DEFAULT NULL,
  `asset_id` bigint DEFAULT NULL,
  `player_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `attribute_id` (`attribute_id`),
  CONSTRAINT `attribute_owners_ibfk_1` FOREIGN KEY (`attribute_id`) REFERENCES `attributes` (`id`)
)
```

### AttributeOwner.__init__

```python
def __init__(self):
    ...
```

Initializes a new model instance with empty data dictionary, no database connection, and marked as dirty (requiring save).

**Functions called:**
- None

**Examples:**

1. **Basic instantiation** (`gamedb/thrift/py/db_models/tests.py:226`)
```python
model = AttributeOwner()
```

2. **Create and save** (`gamedb/thrift/py/db_models/tests.py:238-240`)
```python
parent = AttributeOwner()
parent.set_attribute_id(related.get_id())
parent.save()
```

### AttributeOwner.save

```python
def save(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, cascade: bool = True) -> None:
    ...
```

Saves the record to the database with transaction support and optional cascading to related models.

**ASCII Execution Graph:**
```
Start
├─ Check if dirty
│  └─ [not dirty] → Return early (no save needed)
├─ Determine connection ownership
│  ├─ [owns connection] → Connect and start transaction
│  └─ [external connection] → Use provided connection
├─ Cascade save belongs-to relationships (if cascade=True)
│  ├─ Check cached attribute → Save if dirty
│  ├─ Check cached mobile → Save if dirty
│  ├─ Check cached item → Save if dirty
│  └─ Check cached player → Save if dirty
├─ Execute database operation
│  ├─ [id exists] → UPDATE existing record
│  └─ [id is None] → INSERT new record and capture lastrowid
├─ Mark model as clean (_dirty = False)
├─ Cascade save has-many relationships (if cascade=True)
├─ Commit or rollback
│  ├─ [owns connection] → Commit transaction
│  ├─ [error occurred] → Rollback if owns connection
│  └─ [external connection] → Caller handles commit
└─ End
```

**Functions called:**
- `_connect()` - [link to section](#attributeowner-_connect)
- `connection.start_transaction()` - external call
- `related.save()` - recursive save for belongs-to relationships
- `cursor.execute()` - external call
- `connection.commit()` - external call
- `connection.rollback()` - external call

**Examples:**

1. **Simple save** (`gamedb/thrift/py/db_models/tests.py:113-114`)
```python
seed['attribute1'].set_internal_name('test_internal_name_1')
seed['attribute1'].save()
```

2. **Transactional save with connection** (pattern used internally)
```python
parent.save(connection=existing_connection, cascade=True)
```

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

ActiveRecord-style model for the `inventory_owners` table.

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

**Key Methods**: Same pattern as AttributeOwner

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

ActiveRecord-style model for the `items` table.

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

**Key Methods**: Same pattern as AttributeOwner

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

ActiveRecord-style model for the `mobiles` table.

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

**Key Methods**: Same pattern as AttributeOwner

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

ActiveRecord-style model for the `players` table.

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

**Key Methods**: Same pattern as AttributeOwner

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
