# PRD: Comprehensive Model Relationship Testing

## Overview

This PRD outlines the requirements for enhancing the model generator (`gamedb/thrift/py/db_models/generate_models.py`) to produce comprehensive relationship tests. The current test generation creates basic CRUD tests but does not validate the relationship features implemented in the previous PRD (dirty tracking, caching, cascade saves, lazy loading, etc.).

## Goals

1. Generate comprehensive tests that validate all relationship features using seed data
2. Test internal mechanisms: dirty tracking, caching, cascade saves, lazy/eager loading, strict mode
3. Test both belongs-to and has-many relationships across all models
4. Ensure tests are maintainable and run efficiently using seed data and transactions
5. Validate error handling and edge cases (NULL foreign keys, missing records, transaction rollbacks)

## Current State

### What We Have
- **Basic CRUD tests**: `test_create_and_find` for each model
- **Module-level setup/teardown**: Creates temporary test database and tables
- **Simple test values**: Hardcoded values for first 3 columns only
- **No relationship testing**: No tests for belongs-to, has-many, or cascade behavior

### Test Generation Location
- File: `/vagrant/gamedb/thrift/py/db_models/generate_models.py`
- Function: `generate_tests()` (starts at line 762)
- Output: `/vagrant/gamedb/thrift/py/db_models/tests.py`

### Current Generated Models
14 models with relationships:
- AttributeOwner, Attribute, Inventory, InventoryEntry, InventoryOwner
- ItemBlueprintComponent, ItemBlueprint, Item
- MobileItemAttribute, MobileItemBlueprintComponent, MobileItemBlueprint, MobileItem
- Mobile, Player

### Relationship Features to Test
1. **Dirty tracking**: Models only save when modified
2. **Caching**: Relationship getters cache results
3. **Lazy loading**: Belongs-to getters load on access
4. **Eager vs lazy loading**: Has-many getters support both list and iterator modes
5. **Cascade saves**: Saving parent saves related models in transaction
6. **Reload parameter**: Bypasses cache when `reload=True`
7. **Strict mode**: Raises exception when related record missing if `strict=True`
8. **Transaction rollback**: Failed cascade saves rollback all changes

## Requirements

### 1. Seed Data Generation

**1.1 Create Seed Data Helper in Test Module**
- Add `create_seed_data()` function to test module setup
- Function should create a complete graph of related records
- Use realistic test data that covers all relationship types
- Return dictionary of created records keyed by model and identifier
- Examples:
  - Create players with inventories, items, attributes
  - Create mobiles with items, attributes, owners
  - Create item blueprints with components
  - Create mobile blueprints with components

**1.2 Seed Data Requirements**
- Must cover all relationship types (belongs-to, has-many)
- Must include NULL foreign keys where allowed
- Must include records with no relationships
- Must be created in correct order (respecting FK constraints)
- Must be reusable across multiple test classes

**1.3 Seed Data Cleanup**
- Add `cleanup_seed_data()` function to teardown
- Should delete all seed data in reverse dependency order
- Should be called after each test class or at module teardown

### 2. Belongs-To Relationship Tests

For each belongs-to relationship in each model, generate tests for:

**2.1 Basic Getter Test** (`test_belongs_to_<relation>_basic`)
- Set foreign key value
- Call getter method
- Assert returned model is correct type
- Assert returned model has correct ID
- Verify no database query on second call (caching)

**2.2 Lazy Loading Test** (`test_belongs_to_<relation>_lazy_load`)
- Create parent and related model in database
- Create new instance and load parent
- Verify related model is None initially
- Access via getter
- Assert related model is loaded correctly

**2.3 Caching Test** (`test_belongs_to_<relation>_caching`)
- Load parent with foreign key
- Call getter once
- Mock or count database queries
- Call getter again
- Assert no additional database queries (cached result used)

**2.4 NULL Foreign Key Test** (`test_belongs_to_<relation>_null`)
- Create model with NULL foreign key
- Call getter
- Assert returns None
- Assert no exception raised

**2.5 Strict Mode Test** (`test_belongs_to_<relation>_strict_mode`)
- Create model with foreign key pointing to non-existent record
- Call getter with `strict=False`
- Assert returns None
- Call getter with `strict=True`
- Assert raises ValueError with appropriate message

**2.6 Setter Test** (`test_belongs_to_<relation>_setter`)
- Create parent and related models
- Call setter with related model
- Assert foreign key field updated
- Assert model marked dirty
- Assert getter returns same instance (cache updated)
- Call setter with None
- Assert foreign key set to NULL

**2.7 Setter Marks Dirty Test** (`test_belongs_to_<relation>_setter_marks_dirty`)
- Create and save parent model
- Assert model is not dirty
- Call setter with new related model
- Assert model is dirty

### 3. Has-Many Relationship Tests

For each has-many relationship in each model, generate tests for:

**3.1 Basic Getter Test** (`test_has_many_<relation>_basic`)
- Create parent with several related records in database
- Call getter (eager mode)
- Assert returns list
- Assert correct number of records
- Assert all records are correct type
- Assert records have correct foreign key values

**3.2 Empty Relationship Test** (`test_has_many_<relation>_empty`)
- Create parent with no related records
- Call getter
- Assert returns empty list (not None)

**3.3 Lazy Mode Test** (`test_has_many_<relation>_lazy`)
- Create parent with related records
- Call getter with `lazy=True`
- Assert returns iterator
- Consume iterator
- Assert correct number of items
- Verify items are correct

**3.4 Eager Mode Test** (`test_has_many_<relation>_eager`)
- Create parent with related records
- Call getter with `lazy=False` (default)
- Assert returns list
- Verify list contains all related records

**3.5 Caching Test** (`test_has_many_<relation>_caching`)
- Create parent with related records
- Call getter (eager mode)
- Mock or count database queries
- Call getter again
- Assert no additional queries (cached)

**3.6 Reload Test** (`test_has_many_<relation>_reload`)
- Create parent with related records
- Call getter (cached)
- Add more related records directly to database
- Call getter with `reload=False`
- Assert returns cached results (old count)
- Call getter with `reload=True`
- Assert returns fresh results (new count)

**3.7 Unsaved Parent Test** (`test_has_many_<relation>_unsaved_parent`)
- Create parent without saving (no ID)
- Call getter
- Assert returns empty list or iterator

### 4. Dirty Tracking Tests

**4.1 New Model Dirty Test** (`test_dirty_tracking_new_model`)
- Create new model instance
- Assert model is dirty

**4.2 Saved Model Clean Test** (`test_dirty_tracking_saved_model`)
- Create and save model
- Assert model is not dirty

**4.3 Setter Marks Dirty Test** (`test_dirty_tracking_setter`)
- Create and save model
- Assert not dirty
- Call any setter
- Assert model is dirty

**4.4 Save Clears Dirty Test** (`test_dirty_tracking_save_clears`)
- Create model
- Assert dirty
- Save model
- Assert not dirty
- Modify model
- Assert dirty
- Save again
- Assert not dirty

**4.5 No-Op Save Test** (`test_dirty_tracking_skip_save`)
- Create and save model
- Assert not dirty
- Mock database operations
- Call save again
- Assert no database operations performed

### 5. Cascade Save Tests

**5.1 Belongs-To Cascade Test** (`test_cascade_save_belongs_to`)
- Create parent and related model (both unsaved)
- Set relationship using setter
- Assert both models dirty
- Save parent with cascade
- Assert both models saved to database
- Assert both have IDs
- Assert both marked clean

**5.2 Has-Many Cascade Test** (`test_cascade_save_has_many`)
- Create parent and multiple related models (all unsaved)
- Add related models to parent's collection
- Save parent with cascade
- Assert all models saved
- Assert all have IDs
- Assert foreign keys set correctly

**5.3 Deep Cascade Test** (`test_cascade_save_deep`)
- Create hierarchy: A belongs-to B, B belongs-to C
- All unsaved
- Save A with cascade
- Assert all three saved in correct order
- Assert foreign keys set correctly

**5.4 Transaction Rollback Test** (`test_cascade_save_rollback`)
- Create parent and related models
- Mock one of the related models to raise exception on save
- Call save with cascade
- Assert exception propagated
- Assert transaction rolled back
- Assert no records in database

**5.5 Cascade Disabled Test** (`test_cascade_save_disabled`)
- Create parent and related model
- Set relationship
- Save parent with `cascade=False`
- Assert parent saved
- Assert related model not saved (no ID)

**5.6 Skip Clean Models Test** (`test_cascade_save_skip_clean`)
- Create and save related model
- Create parent and set relationship
- Assert related model not dirty
- Mock related model's save
- Save parent with cascade
- Assert related model's save not called (already clean)

### 6. Transaction Tests

**6.1 Transaction Sharing Test** (`test_transaction_sharing`)
- Create connection and start transaction
- Create model
- Save model with connection parameter
- Assert no commit called (transaction still open)
- Manually commit
- Verify record in database

**6.2 Transaction Rollback Test** (`test_transaction_rollback`)
- Create connection and start transaction
- Create and save model with connection
- Rollback transaction
- Assert record not in database

**6.3 Nested Save Test** (`test_nested_transaction_save`)
- Create parent and related models
- Start transaction
- Save parent (which cascades to related)
- Assert all saves use same transaction
- Commit
- Verify all records saved

### 7. Edge Case Tests

**7.1 Circular Reference Test** (`test_circular_reference`)
- Create two models that reference each other (if such relationships exist)
- Set relationships
- Save with cascade
- Assert both saved without infinite loop

**7.2 Self-Referential Test** (`test_self_referential`)
- If any model has self-referential FK (e.g., mobile owned by mobile)
- Create parent and child of same type
- Set relationship
- Save with cascade
- Assert both saved correctly

**7.3 Multiple Parents Test** (`test_multiple_parents`)
- Create one child record
- Create two different parents
- Set same child in both parents' relationships
- Save both parents
- Assert child only saved once

**7.4 Pivot Table Test** (`test_pivot_table_relationships`)
- For pivot tables (attribute_owners, inventory_owners)
- Create owner and owned records
- Create pivot record linking them
- Test that queries through pivot work correctly

## Implementation Strategy

### Test Generation Architecture

**Modify `generate_tests()` function to:**
1. Detect all relationships for each model (belongs-to and has-many)
2. Generate test methods for each relationship type
3. Add seed data generation and cleanup functions
4. Organize tests into logical test classes
5. Use parameterized tests where possible to reduce duplication

**New Functions to Add:**
- `generate_seed_data_function()`: Creates seed data setup
- `generate_belongs_to_tests()`: Generates all belongs-to tests for a model
- `generate_has_many_tests()`: Generates all has-many tests for a model
- `generate_dirty_tracking_tests()`: Generates dirty tracking tests
- `generate_cascade_save_tests()`: Generates cascade save tests
- `generate_transaction_tests()`: Generates transaction tests
- `generate_edge_case_tests()`: Generates edge case tests

### Seed Data Structure

```python
def create_seed_data():
    """Create complete graph of test data."""
    seed = {}

    # Create players
    seed['player1'] = Player()
    seed['player1'].set_name('Test Player 1')
    seed['player1'].set_over_13(True)
    seed['player1'].save()

    seed['player2'] = Player()
    seed['player2'].set_name('Test Player 2')
    seed['player2'].set_over_13(True)
    seed['player2'].save()

    # Create mobiles owned by player1
    seed['mobile1'] = Mobile()
    seed['mobile1'].set_name('Test Mobile 1')
    seed['mobile1'].set_owner_player_id(seed['player1'].get_id())
    seed['mobile1'].save()

    # ... create more seed data covering all relationships

    return seed
```

### Test Organization

```python
class TestPlayerRelationships(unittest.TestCase):
    """Test Player model relationships."""

    @classmethod
    def setUpClass(cls):
        """Create seed data once for all tests in this class."""
        cls.seed = create_seed_data()

    @classmethod
    def tearDownClass(cls):
        """Clean up seed data."""
        cleanup_seed_data(cls.seed)

    def test_belongs_to_owner_player_basic(self):
        # Test implementation
        pass

    # ... more tests
```

## Test Output Requirements

### Test Naming Convention
- Use descriptive names: `test_<relationship_type>_<relation_name>_<aspect>`
- Examples:
  - `test_belongs_to_owner_player_basic`
  - `test_has_many_mobile_items_lazy`
  - `test_cascade_save_belongs_to`

### Test Documentation
- Each test should have docstring explaining what it validates
- Include example usage if complex
- Document expected behavior clearly

### Test Performance
- Use seed data to avoid repeated setup
- Run tests in parallel where possible (thread-safe)
- Use transactions for isolation
- Keep tests fast (< 100ms each)

### Test Coverage
- Aim for 100% coverage of relationship code
- Test all generated methods
- Test all parameters and modes
- Test error conditions

## Acceptance Criteria

### Functionality
- [ ] All belongs-to relationships tested with 7 test cases each
- [ ] All has-many relationships tested with 7 test cases each
- [ ] Dirty tracking fully tested (5 test cases)
- [ ] Cascade saves fully tested (6 test cases)
- [ ] Transaction support tested (3 test cases)
- [ ] Edge cases covered (4+ test cases)

### Code Quality
- [ ] Tests are generated programmatically by `generate_models.py`
- [ ] Test code follows project conventions (snake_case, type hints, etc.)
- [ ] Seed data is comprehensive and reusable
- [ ] Tests are isolated and can run in any order
- [ ] Tests clean up after themselves

### Performance
- [ ] Full test suite completes in < 30 seconds
- [ ] Individual tests complete in < 100ms average
- [ ] No test flakiness (100% pass rate when code is correct)

### Documentation
- [ ] Each test has clear docstring
- [ ] Seed data structure is documented
- [ ] Test organization is logical and clear
- [ ] PRD is updated with actual implementation details

### Validation
- [ ] Run `py tests.py` successfully with 100% pass rate
- [ ] All relationship features validated
- [ ] No regressions in existing functionality
- [ ] Tests catch intentional bugs (verify by breaking code)

## Non-Goals

- Testing business logic (that belongs in service layer tests)
- Testing database constraints (tested by MySQL itself)
- Testing performance under load (separate performance test suite)
- Testing the model generator itself (separate meta-tests)
- Manual test creation (all tests should be auto-generated)

## Risks and Mitigations

### Risk: Seed Data Becomes Too Large
- **Mitigation**: Create minimal seed data covering each relationship type once
- **Mitigation**: Use class-level setup to share seed data across tests
- **Mitigation**: Only create data needed for specific test class

### Risk: Tests Become Slow
- **Mitigation**: Use transactions for isolation instead of deleting/recreating
- **Mitigation**: Run tests in parallel using unittest's test runner
- **Mitigation**: Use in-memory database for tests (if supported)

### Risk: Tests Become Brittle
- **Mitigation**: Use seed data helper functions for consistent setup
- **Mitigation**: Don't hardcode IDs, use relationships
- **Mitigation**: Test behavior, not implementation details

### Risk: Generated Tests Are Hard to Debug
- **Mitigation**: Use descriptive test names and clear docstrings
- **Mitigation**: Add comments in generated test code
- **Mitigation**: Keep tests simple and focused on one aspect

## Future Enhancements

- Performance benchmarking tests for relationship loading
- Concurrency tests (multiple threads accessing same relationships)
- Memory usage tests (lazy loading vs eager loading)
- Integration tests with service layer
- Property-based tests (hypothesis library)
- Mutation testing to verify test effectiveness

## References

- Original PRD: `/vagrant/tasks/tasks-prd-add-model-relationships.md`
- Model Generator: `/vagrant/gamedb/thrift/py/db_models/generate_models.py`
- Generated Models: `/vagrant/gamedb/thrift/py/db_models/models.py`
- Current Tests: `/vagrant/gamedb/thrift/py/db_models/tests.py`
- Template: `/vagrant/gamedb/thrift/py/db_models/templates/model_template.py.tmpl`
