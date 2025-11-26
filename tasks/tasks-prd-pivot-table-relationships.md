# Task List: Pivot Table Relationship Implementation

## Relevant Files

- `gamedb/thrift/py/db_models/generate_models.py` - Main model generation script that needs pivot table detection and generation logic
- `gamedb/thrift/py/db_models/models.py` - Generated models file (will be regenerated with new pivot table logic)
- `gamedb/thrift/py/db_models/tests.py` - Existing test file that needs new pivot table tests added
- `gamedb/thrift/py/db_models/README.md` - Documentation that needs updating with pivot table pattern examples

### Notes

- Run `py gamedb/thrift/py/db_models/generate_models.py` to regenerate models.py after making changes
- Run `py gamedb/thrift/py/db_models/tests.py` to run tests
- The generate_models.py script already has an `is_pivot_table()` function that can be enhanced

## Tasks

- [ ] 1.0 Update generate_models.py to detect and handle pivot tables
  - [x] 1.1 Enhance `is_pivot_table()` function to specifically identify `attribute_owners` and `inventory_owners` as pivot tables
  - [ ] 1.2 Create a new function `get_pivot_table_info()` that returns metadata about which foreign keys point to which tables for a pivot table
  - [ ] 1.3 Modify `generate_model()` function to use different code generation logic when a table is detected as a pivot table
  - [x] 1.4 Add configuration or constants to identify which tables are pivot tables (PIVOT_TABLES list with 'attribute_owners' and 'inventory_owners')

- [ ] 2.0 Generate pivot table helper methods (is_player, is_mobile, is_item)
  - [ ] 2.1 Create a new function `generate_pivot_helper_methods()` that generates is_* methods for each foreign key in the pivot table
  - [ ] 2.2 For AttributeOwner, generate: `is_player()`, `is_mobile()`, `is_item()`, `is_asset()` methods that check if respective FK is not NULL
  - [ ] 2.3 For InventoryOwner, generate: `is_player()`, `is_mobile()`, `is_item()` methods
  - [ ] 2.4 Integrate helper method generation into the main model generation flow for pivot tables

- [ ] 3.0 Generate owner model convenience APIs for attributes (get_attributes, add_attribute, remove_attribute, set_attributes)
  - [ ] 3.1 Create function `generate_pivot_owner_methods()` that generates convenience methods on owner models
  - [ ] 3.2 Generate `get_attributes()` method that queries through AttributeOwner pivot to return list of Attribute objects
  - [ ] 3.3 Generate `get_attribute_owners()` method that returns list of AttributeOwner pivot objects
  - [ ] 3.4 Generate `add_attribute(attribute)` method that creates AttributeOwner pivot record with only the relevant owner FK set (others NULL)
  - [ ] 3.5 Generate `remove_attribute(attribute)` method that deletes both AttributeOwner pivot record and the Attribute record (cascade delete)
  - [ ] 3.6 Generate `set_attributes([attributes])` method that replaces all attributes (delete old, add new)
  - [ ] 3.7 Integrate these methods into Player, Mobile, and Item model generation

- [ ] 4.0 Generate owner model convenience APIs for inventories (get_inventories, add_inventory, remove_inventory, set_inventories)
  - [ ] 4.1 Apply same pattern as task 3.0 but for inventories through InventoryOwner pivot
  - [ ] 4.2 Generate `get_inventories()`, `get_inventory_owners()` methods
  - [ ] 4.3 Generate `add_inventory(inventory)`, `remove_inventory(inventory)`, `set_inventories([inventories])` methods
  - [ ] 4.4 Integrate these methods only into Player and Mobile models (not Item, since Item owns inventories not through pivot based on schema)

- [ ] 5.0 Implement optimized cascade save and cascade delete behavior
  - [ ] 5.1 Modify generated `save()` method for pivot tables to ensure only one owner FK is set (set others to NULL explicitly)
  - [ ] 5.2 Update `add_attribute()` implementation to check if attribute is new or dirty before saving
  - [ ] 5.3 Ensure `add_attribute()` saves the Attribute first (if dirty/new), then creates the pivot record
  - [ ] 5.4 Implement cascade delete in `remove_attribute()` - delete pivot record first, then delete the Attribute record
  - [ ] 5.5 Ensure transaction safety - all pivot operations should use existing connection pattern for rollback capability

- [ ] 6.0 Create comprehensive tests for AttributeOwner pivot operations with Player model
  - [ ] 6.1 Add test for `is_player()`, `is_mobile()`, `is_item()` helper methods on AttributeOwner
  - [ ] 6.2 Add test for `player.get_attributes()` returning list of Attribute objects
  - [ ] 6.3 Add test for `player.get_attribute_owners()` returning list of AttributeOwner objects
  - [ ] 6.4 Add test for `player.add_attribute(attr)` creating pivot with only player_id set (mobile_id, item_id, asset_id are NULL)
  - [ ] 6.5 Add test for `player.remove_attribute(attr)` deleting both pivot and Attribute record (cascade delete)
  - [ ] 6.6 Add test for `player.set_attributes([attr1, attr2])` replacing all attributes
  - [ ] 6.7 Add test for optimized save - ensure dirty attributes are saved, clean ones are not re-saved
  - [ ] 6.8 Add test verifying no attribute sharing between owners (each owner gets its own Attribute record)

- [ ] 7.0 Create comprehensive tests for InventoryOwner pivot operations with Item model
  - [ ] 7.1 Add test for `is_player()`, `is_mobile()`, `is_item()` helper methods on InventoryOwner
  - [ ] 7.2 Add test for `item.get_inventories()` (if Item can own inventories through pivot - verify schema first)
  - [ ] 7.3 Add test for `mobile.add_inventory(inv)` and `mobile.remove_inventory(inv)` with cascade behavior
  - [ ] 7.4 Add test for `mobile.set_inventories([inv1, inv2])` bulk operation
  - [ ] 7.5 Verify only relevant owner FK is set in InventoryOwner pivot records

- [ ] 8.0 Update generated models documentation
  - [ ] 8.1 Update README.md to add section explaining pivot table pattern
  - [ ] 8.2 Document AttributeOwner and InventoryOwner as pivot table classes with usage examples
  - [ ] 8.3 Update Player, Mobile, Item documentation sections to show new attribute/inventory methods
  - [ ] 8.4 Add examples showing `add_attribute()`, `get_attributes()`, `remove_attribute()` patterns
  - [ ] 8.5 Document helper methods (is_player, is_mobile, etc.) with examples
