# Tasks: Add Model Relationships

## Relevant Files

- `gamedb/thrift/py/db_models/generate_models.py` - The main model generator script that will be enhanced to detect relationships and generate relationship methods.
- `gamedb/thrift/py/db_models/models.py` - New single file that will contain all generated model classes (will be created by the generator).
- `gamedb/thrift/py/db_models/tests.py` - Test file for all generated models (will be updated to test relationship features).
- `gamedb/thrift/py/base_model.py` - Base model class (reference for existing patterns like connection management).
- `gamedb/thrift/py/db_models/attribute.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/inventory.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/item_blueprint.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/item_blueprint_component.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/mobile_item_blueprint_component.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/player.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/item.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/mobile.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/inventory_entry.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/attribute_owner.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/inventory_owner.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/mobile_item.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/mobile_item_attribute.py` - Individual model file (to be deleted after consolidation).
- `gamedb/thrift/py/db_models/mobile_item_blueprint.py` - Individual model file (to be deleted after consolidation).

### Notes

- Unit tests should be placed alongside the code files they are testing (e.g., `generate_models.py` and `tests.py` in the same directory).
- Use `py tests.py` to run tests for generated models.
- The generator script can be tested manually by running it and verifying the generated `models.py` output.
- After generation, imports in other files (in `dbinc/` and `services/`) may need to be updated to reference the new single-file location.

## Tasks

- [ ] 1.0 Enhance Model Generator to Detect Database Relationships
  - [ ] 1.1 Add function to query `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` for actual foreign key constraints
  - [ ] 1.2 Add function to query `INFORMATION_SCHEMA.TABLE_CONSTRAINTS` to detect UNIQUE constraints (for one-to-one relationships)
  - [ ] 1.3 Implement fallback logic to detect foreign keys by naming convention (columns ending in `_id`)
  - [ ] 1.4 Build a relationship metadata structure that stores: source table, target table, foreign key column, relationship type (one-to-one vs one-to-many)
  - [ ] 1.5 Create helper functions to convert table names to model class names and column names to relationship method names
  - [ ] 1.6 Build reverse relationship mappings (for has-many relationships on the referenced table)
- [ ] 2.0 Implement Dirty Tracking System for Models
  - [ ] 2.1 Add `_dirty: bool = False` field to the model template's `__init__` method
  - [ ] 2.2 Set `_dirty = True` for new models (models without an ID yet)
  - [ ] 2.3 Modify all generated setter methods to set `self._dirty = True` when called
  - [ ] 2.4 Update the `save()` method template to check `self._dirty` before performing INSERT/UPDATE
  - [ ] 2.5 Reset `self._dirty = False` after a successful save operation
- [ ] 3.0 Generate Belongs-To Relationship Methods (Foreign Key Side)
  - [ ] 3.1 Create a template for `get_<relation>(strict: bool = False) -> Optional[RelatedModel]` method
  - [ ] 3.2 Implement cache checking: add `_<relation>_cache` field to `__init__` and check it before querying
  - [ ] 3.3 Implement lazy loading: if not cached, call `RelatedModel.find(foreign_key_value)` and cache the result
  - [ ] 3.4 Handle NULL foreign keys by returning `None`
  - [ ] 3.5 Implement `strict` parameter: raise exception if `strict=True` and related record doesn't exist
  - [ ] 3.6 Create a template for `set_<relation>(model: Optional[RelatedModel]) -> None` method
  - [ ] 3.7 In setter: update the cache, update the foreign key field, and mark model as dirty
  - [ ] 3.8 Handle `None` input to clear the relationship (set foreign key to NULL)
- [ ] 4.0 Generate Has-Many Relationship Methods (Reverse Side)
  - [ ] 4.1 Create a template for `get_<plural_relation>(reload: bool = False, lazy: bool = False) -> Union[List[RelatedModel], Iterator[RelatedModel]]` method
  - [ ] 4.2 Implement cache checking: add `_<plural_relation>_cache` field and check it unless `reload=True`
  - [ ] 4.3 Implement `reload` parameter: clear cache and query fresh if `reload=True`
  - [ ] 4.4 Implement `lazy=False` mode: return `List[RelatedModel]` by calling `RelatedModel.find_by_<foreign_key>(self.get_id())`
  - [ ] 4.5 Implement `lazy=True` mode: return an `Iterator[RelatedModel]` that yields results on demand
  - [ ] 4.6 Cache results for non-lazy calls for subsequent access
- [ ] 5.0 Implement Cascading Saves with Transaction Support
  - [ ] 5.1 Create a transaction context manager or helper function for managing database transactions
  - [ ] 5.2 Modify the `save()` method template to support an optional `connection` parameter for sharing connections
  - [ ] 5.3 Implement cascade save logic: collect all related models from the relationship caches
  - [ ] 5.4 Save all belongs-to relationships first (recursively call `save()` with shared connection, only if dirty)
  - [ ] 5.5 Update foreign key fields with the IDs from saved belongs-to models
  - [ ] 5.6 Save the current model (INSERT or UPDATE based on whether ID exists)
  - [ ] 5.7 Save all has-many relationships (recursively call `save()` on each, only if dirty)
  - [ ] 5.8 Wrap all operations in a transaction: START TRANSACTION, perform saves, COMMIT on success, ROLLBACK on error
  - [ ] 5.9 Ensure proper error handling and cleanup for connection management
- [ ] 6.0 Refactor to Single-File Model Generation
  - [ ] 6.1 Modify `generate_models.py` to output all models to a single file `models.py` instead of individual files
  - [ ] 6.2 Add all necessary imports at the top of `models.py` (typing, Optional, List, Iterator, Union, etc.)
  - [ ] 6.3 Generate model classes in an appropriate order (or use forward references with string type hints)
  - [ ] 6.4 After successful generation, add cleanup logic to delete all old individual model files (e.g., `player.py`, `item.py`, etc.)
  - [ ] 6.5 Update or regenerate `tests.py` to import models from the new single-file location
  - [ ] 6.6 Verify that existing code in `dbinc/` and `services/` can still import models (may require import path updates)
- [ ] 7.0 Generate Comprehensive Relationship Tests
  - [ ] 7.1 Generate tests for belongs-to relationship getters (lazy loading, caching, NULL handling)
  - [ ] 7.2 Generate tests for belongs-to relationship setters (updating foreign key, marking dirty)
  - [ ] 7.3 Generate tests for the `strict` parameter in belongs-to getters (exception vs None)
  - [ ] 7.4 Generate tests for has-many relationship getters in list mode (`lazy=False`)
  - [ ] 7.5 Generate tests for has-many relationship getters in iterator mode (`lazy=True`)
  - [ ] 7.6 Generate tests for the `reload` parameter in has-many getters (cache clearing)
  - [ ] 7.7 Generate tests for dirty tracking (save only when dirty, reset after save)
  - [ ] 7.8 Generate tests for cascade saves across belongs-to relationships
  - [ ] 7.9 Generate tests for cascade saves across has-many relationships
  - [ ] 7.10 Generate tests for transaction rollback when a cascade save fails
  - [ ] 7.11 Run all generated tests to verify correctness
