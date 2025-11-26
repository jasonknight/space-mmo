# PRD: Pivot Table Relationship Implementation

## Introduction/Overview

The current implementation of `attribute_owners` and `inventory_owners` tables incorrectly treats them as singular belongs-to relationships when they are actually pivot/join tables for many-to-many relationships. This causes API confusion where methods like `parent.get_attribute()` (singular) should be `parent.get_attributes()` (plural), and prevents proper management of the pivot table relationships.

**Problem:**
- AttributeOwner and InventoryOwner are pivot tables but are currently modeled as simple foreign key relationships
- No proper API for managing many-to-many relationships (add, remove, list attributes/inventories)
- Missing helper methods to determine owner types
- No cascade delete behavior for pivot records and their associated data

**Goal:**
Redesign the model generation logic to properly handle pivot tables, providing both convenience methods for common operations and explicit pivot table access when needed.

## Goals

1. Correctly model `attribute_owners` and `inventory_owners` as pivot table classes with appropriate helper methods
2. Provide intuitive plural APIs on owner models (Player, Mobile, Item) for accessing related records through pivot tables
3. Implement multiple approaches for managing relationships: convenience methods, bulk operations, and manual pivot management
4. Ensure proper cascade behavior on save (auto-save dirty records) and delete (remove both pivot and owned records)
5. Optimize database calls by detecting new/dirty records before saving
6. Maintain one-to-one Attribute-to-Owner relationship (no sharing of attributes between owners)
7. Provide comprehensive test coverage for pivot table operations

## User Stories

1. **As a developer**, I want to call `player.get_attributes()` to retrieve all attributes for a player, so that the API clearly indicates a one-to-many relationship.

2. **As a developer**, I want to call `player.add_attribute(strength_attr)` to add an attribute to a player without manually managing the pivot table, so that I can write cleaner code.

3. **As a developer**, I want to call `player.remove_attribute(strength_attr)` and have both the pivot record and the attribute itself deleted, so that orphaned records don't accumulate.

4. **As a developer**, I want to call `attribute_owner.is_player()` to determine what type of owner an attribute belongs to, so that I can write conditional logic based on owner type.

5. **As a developer**, I want to call `player.get_attribute_owners()` when I need explicit access to the pivot records (e.g., to check metadata), so that I have full control when needed.

6. **As a developer**, I want `player.save()` to automatically save all new or dirty attributes and create pivot entries, so that I don't have to manually manage transaction order.

7. **As a developer**, I want each owner to have its own Attribute records (no sharing), so that modifying one player's strength doesn't affect another player's strength.

8. **As a developer**, I want `player.set_attributes([attr1, attr2])` to replace all attributes at once, so that I can perform bulk updates efficiently.

## Functional Requirements

### Pivot Table Classes

1. `AttributeOwner` class must remain in models.py as a public class representing the pivot table
2. `InventoryOwner` class must remain in models.py as a public class representing the pivot table
3. `AttributeOwner` must provide helper methods: `is_mobile()`, `is_player()`, `is_item()`, `is_asset()`
4. `InventoryOwner` must provide helper methods: `is_mobile()`, `is_player()`, `is_item()`
5. Helper methods must return boolean values based on which foreign key is non-NULL

### Owner Model APIs (Player, Mobile, Item)

6. Each owner model must provide `get_attributes()` method returning a list of `Attribute` objects
7. Each owner model must provide `get_attribute_owners()` method returning a list of `AttributeOwner` objects
8. Each owner model must provide `add_attribute(attribute)` method that creates the pivot relationship
9. Each owner model must provide `remove_attribute(attribute)` method that deletes both pivot and Attribute records (cascade delete)
10. Each owner model must provide `set_attributes([attributes])` method that replaces all attributes (deletes old, adds new)
11. Player and Mobile models must provide `get_inventories()` method returning a list of `Inventory` objects
12. Player and Mobile models must provide `get_inventory_owners()` method returning a list of `InventoryOwner` objects
13. Player and Mobile models must provide `add_inventory(inventory)`, `remove_inventory(inventory)`, `set_inventories([inventories])` methods

### Attribute Ownership Rules

14. When creating an `AttributeOwner` record, only ONE foreign key (player_id, mobile_id, item_id, or asset_id) must be set; all others must be NULL
15. Each Attribute record must be owned by exactly ONE entity (no sharing of attributes between owners)
16. When saving an attribute through an owner, the system must ensure only the relevant owner foreign key is set

### Cascade Behavior

17. When calling `owner.save()` with cascade=True (default), all new or dirty attributes must be saved first, then pivot records created
18. The system must detect which Attribute records are new or dirty to minimize unnecessary database calls
19. When calling `owner.remove_attribute(attr)`, both the AttributeOwner pivot record AND the Attribute record must be deleted
20. The same cascade delete behavior applies to `remove_inventory()` - delete both pivot and Inventory records

### Deprecated Fields

21. The `asset_id` field in `attribute_owners` should be supported but marked as not fully implemented
22. Fields in `inventory_owners` other than `inventory_id`, `mobile_id`, and `player_id` are deprecated and should be ignored (no helper methods or API for them)

### Code Generation

23. The `generate_models.py` script must be updated to detect pivot tables automatically
24. Pivot table detection logic: table has multiple foreign keys pointing to different tables
25. For detected pivot tables, generate the appropriate helper methods and owner model APIs
26. Generated code must follow the existing ActiveRecord pattern

## Non-Goals (Out of Scope)

1. Implementing the `asset_id` relationship fully (can be added later)
2. Supporting `inventory_entries` as a pivot table (this is a different pattern - inventory items, not ownership)
3. Backward compatibility with the old singular API (`get_attribute()` - this is breaking change acceptable)
4. Supporting shared attributes between owners (each owner gets its own Attribute record)
5. Generic many-to-many relationship framework (only handling these specific pivot tables)
6. Migration scripts for existing data (this is new code being built up)

## Design Considerations

### API Design Pattern

```python
# Convenience methods (pivot hidden)
player = Player.find(1)
attributes = player.get_attributes()  # Returns list of Attribute objects
player.add_attribute(strength_attr)   # Creates pivot automatically
player.remove_attribute(speed_attr)   # Deletes both pivot and Attribute

# Explicit pivot access
attribute_owners = player.get_attribute_owners()  # Returns list of AttributeOwner objects
for ao in attribute_owners:
    if ao.is_player():
        print(f"Player owns attribute {ao.get_attribute_id()}")

# Bulk operations
player.set_attributes([attr1, attr2, attr3])  # Replace all at once
```

### Helper Method Pattern

```python
attribute_owner = AttributeOwner()
attribute_owner.set_player_id(123)
attribute_owner.set_mobile_id(None)
attribute_owner.set_item_id(None)

# Determine owner type
if attribute_owner.is_player():
    print("This is a player's attribute")
elif attribute_owner.is_mobile():
    print("This is a mobile's attribute")
```

### Cascade Save Optimization

```python
# Only save dirty/new records
player = Player()
attr1 = Attribute()  # New record (dirty by default)
attr2 = player.get_attributes()[0]  # Existing, clean

player.add_attribute(attr1)  # Will save attr1 on player.save()
player.add_attribute(attr2)  # Will only create pivot, not re-save attr2

player.save()  # Optimized: saves attr1, creates both pivots
```

## Technical Considerations

1. **generate_models.py**: Must be modified to detect pivot tables and generate different code patterns
2. **Foreign Key Detection**: Use table schema information to identify multiple FKs pointing to different tables
3. **NULL Constraint Handling**: When setting one owner FK, explicitly NULL all others to prevent ambiguity
4. **Transaction Safety**: All cascade operations should use existing connection/transaction pattern
5. **Caching Strategy**: Maintain existing cache pattern for loaded relationships
6. **Test Database**: Use existing test database setup pattern with uuid-based database names

## Success Metrics

1. All AttributeOwner and InventoryOwner tests pass with comprehensive coverage
2. API is intuitive - developers can use plural methods without confusion
3. No orphaned records in database (cascade deletes work correctly)
4. Optimized database calls - unnecessary saves are avoided through dirty detection
5. Code generation produces correct pivot table classes automatically
6. Helper methods (is_player, is_mobile, etc.) correctly identify owner types

## Open Questions

1. Should we add a `get_owner()` method on AttributeOwner that returns the actual owner object (Player/Mobile/Item) based on which FK is set?
2. Do we need validation in AttributeOwner.save() to ensure only ONE owner FK is set (raise error if multiple are non-NULL)?
3. Should `set_attributes()` be transactional - all succeed or all fail?
4. Do we need any logging/debugging output for pivot table operations during development?
