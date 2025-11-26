# PRD: Add Model Relationships

## Introduction/Overview

The current model generator (`generate_models.py`) creates ActiveRecord-style models with basic CRUD operations (save, find, find_by_*). However, these models do not recognize or utilize foreign key relationships between tables. This feature will enhance the model generator to automatically detect database relationships and generate relationship methods (getters/setters) that support lazy loading, caching, and cascading saves. This brings the generated models closer to a full-featured ORM like Rails' ActiveRecord or SQLAlchemy.

**Problem**: Database tables have foreign key relationships (e.g., Item → Blueprint, MobileItem → Mobile), but the generated models treat these as simple integer fields, requiring manual queries to load related records.

**Goal**: Automatically generate relationship methods that make working with related models intuitive and efficient, following common ORM patterns.

## Goals

1. Detect foreign key relationships from the database schema (both actual constraints and naming conventions)
2. Generate relationship getter/setter methods for both belongs-to (foreign key) and has-many (reverse) relationships
3. Implement lazy loading with caching for related models
4. Support dirty tracking to only save models that have been modified
5. Implement cascading saves with transaction support for data consistency
6. Generate all models into a single file to avoid circular import issues
7. Generate comprehensive tests for all relationship features
8. Clean up old individually-generated model files

## User Stories

1. **As a developer**, I want to call `item.get_blueprint()` instead of manually querying the blueprints table using `item.get_blueprint_id()`, so that I can work with related objects naturally.

2. **As a developer**, I want to call `mobile.get_mobile_items()` to get all items belonging to a mobile, so that I can easily traverse one-to-many relationships.

3. **As a developer**, I want related models to be cached after first load, so that repeated access doesn't cause unnecessary database queries.

4. **As a developer**, I want to set relationships using `item.set_blueprint(blueprint_obj)` instead of manually managing foreign key IDs, so that the code is more object-oriented.

5. **As a developer**, I want `item.save()` to automatically save any modified related models in a transaction, so that data consistency is maintained without manual coordination.

6. **As a developer**, I want models to only execute database updates when they've actually been modified, so that cascading saves are efficient.

7. **As a developer**, I want all models in a single file, so that I don't have circular import issues when models reference each other.

## Functional Requirements

### 1. Relationship Detection

1.1. Query MySQL's `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` to find actual FOREIGN KEY constraints

1.2. If no foreign key constraints exist, fall back to naming convention: any column ending in `_id` is assumed to reference the table named by the prefix (e.g., `item_id` → `items` table)

1.3. Detect one-to-one relationships (foreign key with UNIQUE constraint)

1.4. Detect one-to-many relationships (reverse of foreign key relationships)

1.5. Store relationship metadata including: source table, target table, foreign key column, relationship type (one-to-one, one-to-many)

### 2. Belongs-To Relationship Methods (Foreign Key Side)

2.1. Generate `get_<relation_name>(strict: bool = False) -> Optional[RelatedModel]` method for each foreign key

2.2. The getter should:
   - Return `None` if the foreign key field is NULL
   - Check if the related model is already cached on the instance
   - If not cached, load the related model using `RelatedModel.find(foreign_key_value)`
   - Cache the loaded model for subsequent calls
   - If `strict=True` and the related record doesn't exist, raise an exception
   - If `strict=False` and the related record doesn't exist, return `None`

2.3. Generate `set_<relation_name>(model: Optional[RelatedModel]) -> None` method for each foreign key

2.4. The setter should:
   - Accept `None` to clear the relationship
   - Store the model instance in the cache
   - Update the foreign key field with the related model's ID (or `None` if model is `None`)
   - Mark the current model as dirty

2.5. Example: For `items.blueprint_id` → `blueprints.id`, generate:
   - `Item.get_blueprint(strict: bool = False) -> Optional[Blueprint]`
   - `Item.set_blueprint(blueprint: Optional[Blueprint]) -> None`

### 3. Has-Many Relationship Methods (Reverse Side)

3.1. For each foreign key relationship, generate a reverse method on the referenced table

3.2. Generate `get_<plural_relation_name>(reload: bool = False, lazy: bool = False) -> Union[List[RelatedModel], Iterator[RelatedModel]]` method

3.3. The getter should:
   - If `reload=True`, clear any cached results and query fresh from database
   - If `lazy=False` (default), return a `List[RelatedModel]` of all matching records
   - If `lazy=True`, return an `Iterator[RelatedModel]` that loads records on demand
   - Cache the results (unless lazy=True) for subsequent calls
   - Use `RelatedModel.find_by_<foreign_key>(self.get_id())` to query related records

3.4. Example: For `mobile_items.mobile_id` → `mobiles.id`, generate:
   - `Mobile.get_mobile_items(reload: bool = False, lazy: bool = False) -> Union[List[MobileItem], Iterator[MobileItem]]`

### 4. Dirty Tracking

4.1. Add a `_dirty` boolean flag to each model instance, initialized to `False`

4.2. Mark the model as dirty (`_dirty = True`) whenever any setter is called (including relationship setters)

4.3. The `save()` method should check the `_dirty` flag:
   - If `_dirty=True`, perform the database INSERT or UPDATE
   - If `_dirty=False`, skip the database operation (no-op)

4.4. After a successful save, reset `_dirty = False`

4.5. New models (no ID assigned yet) should be considered dirty by default

### 5. Cascading Saves with Transactions

5.1. When `save()` is called on a model, it should cascade to all related models that have been set or modified

5.2. The cascade should:
   - Save all belongs-to relationships first (since their IDs may be needed for foreign keys)
   - Save the current model
   - Save all has-many relationships
   - Each related model respects its own dirty flag

5.3. All operations within a cascade save should be wrapped in a single database transaction

5.4. All models in the cascade should share a single database connection

5.5. If any save operation fails, the entire transaction should be rolled back

5.6. Example: If `item.set_blueprint(new_blueprint)` is called and then `item.save()` is called:
   - Start transaction
   - Check if `new_blueprint._dirty` is True
   - If dirty, save `new_blueprint` first
   - Update `item`'s `blueprint_id` with the saved blueprint's ID
   - Save `item`
   - Commit transaction

### 6. Single File Generation

6.1. Generate all model classes into a single file named `models.py` in the `gamedb/thrift/py/db_models/` directory

6.2. Include all necessary imports at the top of the file

6.3. Order classes so that models without dependencies come first (though this isn't strictly necessary with forward references)

6.4. After successful generation, delete all old individual model files (e.g., `player.py`, `item.py`, etc.)

6.5. Keep `generate_models.py` and any template files

6.6. Update or regenerate `tests.py` to work with the new single-file structure

### 7. Code Generation Updates

7.1. Modify `generate_models.py` to query foreign key relationships from `INFORMATION_SCHEMA`

7.2. Build a relationship graph mapping tables to their foreign keys and reverse relationships

7.3. Generate relationship getter/setter methods using the template system

7.4. Add dirty tracking fields and logic to the model template

7.5. Modify the `save()` method template to implement transaction-wrapped cascade logic

7.6. Update the `__init__` method template to initialize relationship cache fields

### 8. Test Generation

8.1. Generate tests for belongs-to relationship getters and setters

8.2. Generate tests for has-many relationship getters with both list and iterator modes

8.3. Generate tests for lazy loading and caching behavior

8.4. Generate tests for cascade saves across relationships

8.5. Generate tests for dirty tracking (saving only modified models)

8.6. Generate tests for transaction rollback on cascade save failures

8.7. Generate tests for the `strict` parameter in relationship getters

8.8. Generate tests for `reload` and `lazy` parameters in has-many getters

## Non-Goals (Out of Scope)

1. **Many-to-many relationships**: This PRD only covers one-to-one and one-to-many relationships. Many-to-many (via junction tables) is not included.

2. **Query builder or advanced ORM features**: No support for complex queries, joins, or query optimization beyond basic find operations.

3. **Relationship validation**: No automatic validation of relationship integrity (e.g., checking if required relationships are set before saving).

4. **Polymorphic relationships**: No support for polymorphic associations where a foreign key can point to multiple different tables.

5. **Eager loading**: No support for eager loading multiple relationships in a single query to avoid N+1 problems.

6. **Callbacks or hooks**: No before/after save callbacks for relationship operations.

7. **Migration generation**: This does not include database migration tools or schema versioning.

8. **Refactoring existing service layer code**: The existing code in `dbinc/` and `services/` that uses the models will not be automatically updated.

## Design Considerations

### Model File Structure

- All models will be in `gamedb/thrift/py/db_models/models.py`
- Each model class will have:
  - Existing fields: `_data`, `_connection`
  - New fields: `_dirty`, `_<relation>_cache` (for each relationship)
  - Existing methods: `__init__`, `_connect`, `_disconnect`, `get_*`, `set_*`, `save`, `find`, `find_by_*`
  - New methods: `get_<relation>`, `set_<relation>`, `get_<plural_relations>`

### Relationship Naming

- Belongs-to relationships use singular names: `get_blueprint()`, `set_mobile()`
- Has-many relationships use plural names: `get_mobile_items()`, `get_inventory_entries()`
- Names are derived from the foreign key column name by removing the `_id` suffix and converting to appropriate casing

### Transaction Management

- Use the existing connection management pattern from `base_model.py` as a reference
- Implement a transaction context manager for cascade saves
- Ensure proper cleanup and rollback on errors

### Type Hints

- Use `Optional[Model]` for belongs-to relationships
- Use `Union[List[Model], Iterator[Model]]` for has-many relationships
- Use forward references (strings) where necessary to avoid issues during class definition

## Technical Considerations

### Dependencies

- `mysql.connector` - already in use
- `typing` - for type hints (List, Optional, Iterator, Union)
- No new external dependencies required

### Database Queries

- Relationship detection requires querying `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` and `INFORMATION_SCHEMA.TABLE_CONSTRAINTS`
- Lazy loading uses existing `find()` and `find_by_*()` methods
- No new SQL patterns required beyond what's already generated

### Backwards Compatibility

- Existing getter/setter methods for foreign key fields (e.g., `get_blueprint_id()`, `set_blueprint_id()`) remain unchanged
- Existing code that uses models will continue to work
- The new relationship methods are additive

### Performance

- Caching prevents redundant queries for belongs-to relationships
- Lazy iterators allow efficient handling of large has-many result sets
- Dirty tracking prevents unnecessary UPDATE statements
- Shared connections in cascade saves reduce connection overhead

### Known Constraints

- The generator assumes MySQL/MariaDB database
- The generator assumes tables follow naming conventions (snake_case, plural table names)
- All models must be in the same database (no cross-database relationships)

## Success Metrics

1. **Code reduction**: Measure reduction in manual relationship management code in services and controllers

2. **Query efficiency**: Verify that repeated access to relationships doesn't generate duplicate queries (via caching)

3. **Test coverage**: 100% test coverage of generated relationship methods

4. **Generation time**: Model generation should complete in under 10 seconds for typical database schemas

5. **Developer satisfaction**: Subjective improvement in developer experience when working with related models

## Open Questions

1. Should we support customizing relationship names via configuration/comments in the database schema?

2. Should we generate documentation/docstrings that explain the detected relationships for each model?

3. Should we add a `deep=True` parameter to `save()` to control cascade depth for nested relationships?

4. Should we log warnings when orphaned foreign keys are encountered during lazy loading?

5. Should the generator create a visual diagram or documentation of the relationship graph?

6. How should we handle self-referential relationships (e.g., a tree structure where a record references its parent in the same table)?

7. Should we generate convenience methods like `add_mobile_item(item)` or `remove_mobile_item(item)` for has-many relationships?
