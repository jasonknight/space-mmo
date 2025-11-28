# Plan: Enhance Services Testing and Fix Critical Issues

**Plan Date:** 2025-11-28
**Target Branch:** main
**Current Commit:** c74044270c69ab07d0a703b07e172037265e4d8a
**Estimated Complexity:** Complex

**Progress Summary:**
- [ ] Step 1: Fix Critical Production Bugs (BLOCKING)
- [ ] Step 2: Add Missing Critical Test Coverage
- [ ] Step 3: Expand Error Path Testing
- [ ] Step 4: Add list_records() Test Coverage
- [ ] Step 5: Fix Encapsulation Violations
- [ ] Step 6: Fix Performance Issues
- [ ] Step 7: Add Performance Testing

## Overview

This plan addresses critical bugs and severe test coverage gaps discovered during code review of the services refactoring. The refactoring successfully migrated all three Thrift services to use db_models, but **test coverage is only 40-50%** and there are **critical production bugs** including a data corruption risk in InventoryService.transfer_item(). This plan brings the services to production-ready quality with comprehensive testing and bug fixes.

**Critical Issues:**
- InventoryService.transfer_item() lacks transaction atomicity (data corruption risk)
- Split_stack(), transfer_item(), and load_with_blueprint_tree() have 0% test coverage (362 lines untested)
- Blueprint tree has N+1 query problem causing performance degradation
- All list_records() methods bypass model encapsulation

## Context

The recent services refactoring (completed 2025-11-27 to 2025-11-28) successfully migrated PlayerService, ItemService, and InventoryService from a broken, deleted model layer to the new ActiveRecord-style db_models. All existing tests pass, but the test suite only covers happy paths for basic CRUD operations. The most complex methods - inventory operations and blueprint tree loading - are completely untested.

**Current Test Status:**
- PlayerService: ~20% coverage (80/391 lines tested)
- ItemService: ~9% coverage (60/680 lines tested)
- InventoryService: ~8% coverage (50/635 lines tested)

**Code Quality:** Generally good with proper ActiveRecord patterns, but contains critical bugs that will cause data corruption and performance issues under load.

### Environment & Constraints
> Reference `./tasks/env.md` for complete environment details

- **Language/Runtime:** Python 3.12.3
- **Key Dependencies:**
  - Apache Thrift (RPC framework)
  - mysql-connector-python (database connectivity)
  - game.ttypes (Thrift-generated types)
  - db_models.models (ActiveRecord layer)
- **Compatibility Requirements:** Maintain existing Thrift service definitions
- **Performance Constraints:** Blueprint tree must handle 50+ component trees without multi-second delays
- **Security Considerations:** Validate max_depth to prevent DoS attacks
- **Testing Framework:** Python unittest (per env.md)
- **Database:** MySQL (localhost, test databases created per test run)

### Relevant Documentation
- `./tasks/env.md` - Development environment, testing practices, coding standards
- `./tasks/plan-refactor-services-to-use-db-models.md` (Completed: 2025-11-28, Commit: 9942f61) - Recent refactoring that introduced these issues
- `./tasks/explore-services.md` (Explored: 2025-11-27, Commit: 9942f61) - Service layer architecture
- `./tasks/explore-db-models.md` (Explored: 2025-11-27, Commit: a803046) - ActiveRecord model layer
- `/vagrant/current-cycle/code-review-services-refactor.md` (Created: 2025-11-28) - Detailed analysis of current state

**Documentation Status:**
- [x] All relevant components have been explored
- [x] Exploration docs are up-to-date with current code
- [ ] Missing exploration: None

### Related Documents
- **Based on explorations:** explore-services.md, explore-db-models.md, env.md
- **Related plans:** plan-refactor-services-to-use-db-models.md (completed, introduced these issues)
- **Supersedes:** None
- **Will update explorations:** explore-services.md (should document testing patterns after implementation)

## Requirements Summary

**Critical Requirements (Blocking Production):**
- Fix InventoryService.transfer_item() to use atomic transactions
- Add comprehensive tests for split_stack(), transfer_item(), and load_with_blueprint_tree()
- Add validation to prevent DoS attacks via max_depth parameter
- Verify no data corruption scenarios exist

**High Priority Requirements:**
- Achieve 80%+ test coverage on all three services
- Test all error paths (not found, invalid data, constraint violations)
- Fix N+1 query problem in blueprint tree
- Fix encapsulation violations in list_records() methods

**Testing Requirements:**
- All tests must use existing test isolation pattern (unique database per run)
- Tests must follow naming convention: `<module_name>_test.py`
- Tests must be fast (< 10 seconds total for all services)
- Tests must be independent (no shared state)

**Constraints:**
- Cannot modify Thrift definitions (API is stable)
- Cannot modify inventory.py business logic (separate refactoring)
- Must maintain backward compatibility
- Cannot break existing passing tests

## Technical Approach

We'll fix critical bugs first (safety), then systematically add missing test coverage (confidence), then address performance issues (quality). This ordering ensures the codebase is safe before we verify it's correct, and correct before we optimize it.

**Testing Strategy:**
1. Expand existing test files rather than create new ones
2. Use class-based organization (TestInventoryServiceSplitStack, etc.)
3. Follow the existing test isolation pattern (setUpModule/tearDownModule)
4. Mock failures where needed (database errors, constraint violations)
5. Add performance assertions where relevant (query counts, execution time)

**Bug Fix Strategy:**
1. Fix bugs in isolation with tests to verify the fix
2. Add regression tests to prevent reintroduction
3. Document patterns to avoid similar bugs in future

### Key Decisions

- **Decision: Fix bugs before adding tests** - Rationale: Tests should verify correct behavior, not lock in buggy behavior
- **Decision: Class-based test organization** - Rationale: Better organization for large test suites, clearer test intent
- **Decision: Expand existing test files** - Rationale: Maintain test cohesion, avoid file proliferation
- **Decision: Add from_dict() to generator** - Rationale: Proper fix for encapsulation violations, benefits all models
- **Decision: Defer inventory.py refactoring** - Rationale: Out of scope, separate concern

### Dependencies
- **External:** None (all dependencies already present)
- **Internal:**
  - db_models.models (Item, Inventory, InventoryEntry, Player)
  - inventory.py (split_stack, transfer_item functions)
  - common.py (is_ok, is_true utilities)
  - services.base_service (BaseServiceHandler)

## Implementation Plan

---

### **STEP 1: Fix Critical Production Bugs** (BLOCKING)

---

### Step 1: Fix Critical Production Bugs

**Objective:** Eliminate data corruption risks and DoS vulnerabilities before any production deployment

**Acceptance Criteria:**
- [x] transfer_item() uses atomic transactions (commit/rollback)
- [x] Rollback test verifies atomicity (mock failure scenario)
- [x] max_depth parameter is validated and clamped
- [x] All existing tests still pass

**Testing Requirements:**
- [x] Test transfer_item() atomicity with mock failure
- [x] Test max_depth validation with extreme values
- [x] Verify no regressions in existing tests

**Tasks:**

#### Task 1.1: Fix InventoryService.transfer_item() Transaction Atomicity

**Problem:** Lines 513-514 save inventories separately without transaction. If second save fails, first is committed → items vanish from game.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/inventory_service.py:508-533` - Replace separate saves with shared connection pattern

**Implementation notes:**
```python
# Replace lines 508-514 with:
# Convert modified Thrift objects back to models
logger.debug("Saving both inventories to database with atomic transaction...")
source_model.from_thrift(thrift_source_inv)
dest_model.from_thrift(thrift_dest_inv)

# Use shared connection for atomic transaction
connection = Inventory._create_connection()
try:
    source_model.save(connection=connection)
    dest_model.save(connection=connection)
    connection.commit()
    logger.info(f"SUCCESS: Transaction committed for transfer from inventory_id={source_id} to inventory_id={dest_id}")
except Exception as e:
    connection.rollback()
    logger.error(f"Transaction rolled back due to error: {str(e)}")
    raise
finally:
    connection.close()
```

**Verification:**
- Existing transfer_item test should still pass
- Manually verify logging shows "Transaction committed" message

#### Task 1.2: Add max_depth Validation to ItemService.load_with_blueprint_tree()

**Problem:** No bounds checking on max_depth parameter. Client can send max_depth=999999 causing stack overflow or minutes-long query.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/item_service.py:523` - Add validation

**Implementation notes:**
```python
# Replace line 523 with:
max_depth_raw = tree_data.max_depth if hasattr(tree_data, 'max_depth') else 10
max_depth = min(max(1, max_depth_raw), 50)  # Clamp to 1-50 range
logger.info(f"Loading blueprint tree for item_id={item_id}, max_depth={max_depth} (requested={max_depth_raw})")
```

**Verification:**
- Manually test with max_depth=0 (should become 1)
- Manually test with max_depth=1000 (should become 50)
- Existing tests should still pass

#### Task 1.3: Add Regression Tests for Bug Fixes

Add tests to verify bugs are fixed and prevent reintroduction.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/inventory_service_test.py` - Add atomicity test
- `/vagrant/gamedb/thrift/py/services/tests/item_service_test.py` - Add validation test

**Implementation notes:**

For inventory_service_test.py, add:
```python
def test_transfer_item_atomicity():
    """
    Test that transfer_item rolls back if second save fails.
    This is a regression test for the transaction atomicity bug.
    """
    # Create two inventories and an item
    # Add item to source inventory
    # Mock dest_model.save() to raise exception
    # Attempt transfer
    # Verify source inventory unchanged (rollback worked)
    # Verify FAILURE result returned
```

For item_service_test.py, add:
```python
def test_load_blueprint_tree_max_depth_validation():
    """
    Test that max_depth is validated and clamped.
    This is a regression test for DoS vulnerability.
    """
    # Create item with blueprint
    # Request with max_depth=0 → should use 1
    # Request with max_depth=1000 → should use 50
    # Request with max_depth=25 → should use 25 (in range)
    # Verify max_depth_reached flag is set appropriately
```

**Verification:**
- Run both new tests, verify they pass
- Comment out bug fixes, verify tests fail
- Restore fixes, verify tests pass again

---

### **STEP 2: Add Missing Critical Test Coverage**

---

### Step 2: Add Missing Critical Tests for Complex Methods

**Objective:** Test the most complex, untested methods: split_stack (130 lines), transfer_item (147 lines), load_with_blueprint_tree (86 lines)

**Acceptance Criteria:**
- [x] split_stack() has 5+ test cases covering success and error paths
- [x] transfer_item() has 6+ test cases covering success, errors, and edge cases
- [x] load_with_blueprint_tree() has 4+ test cases covering recursion, cycles, depth limits
- [x] All new tests pass
- [x] No regressions in existing tests

**Testing Requirements:**
- [x] Test success scenarios (happy paths)
- [x] Test failure scenarios (not found, insufficient quantity, etc.)
- [x] Test edge cases (empty inventories, exact quantities, etc.)
- [x] Test recursive blueprint tree cases

**Tasks:**

#### Task 2.1: Add split_stack() Test Cases

Add comprehensive tests for InventoryService.split_stack() method.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/inventory_service_test.py` - Add new test class

**Implementation notes:**

Add test class after existing tests:
```python
class TestInventoryServiceSplitStack(unittest.TestCase):
    """Test split_stack() method - CRITICAL."""

    def test_split_stack_success(self):
        """Test splitting a stack successfully."""
        # Create inventory with Owner(mobile_id=100)
        # Create item with max_stack_size=100
        # Add entry: item_id=X, quantity=10
        # Split 3 items from stack
        # Verify inventory now has 2 entries: quantity=7 and quantity=3
        # Verify SUCCESS result

    def test_split_stack_insufficient_quantity(self):
        """Test splitting more items than exist."""
        # Create inventory with 10 items
        # Try to split 20 items
        # Verify FAILURE result
        # Verify inventory unchanged (still 1 entry with quantity=10)

    def test_split_stack_item_not_in_inventory(self):
        """Test splitting item that doesn't exist in inventory."""
        # Create inventory with item A
        # Try to split item B (not in inventory)
        # Verify FAILURE result with INV_ITEM_NOT_FOUND
        # Verify inventory unchanged

    def test_split_stack_exact_quantity(self):
        """Test splitting exact quantity (edge case)."""
        # Create inventory with 10 items
        # Split 10 items
        # Verify FAILURE (can't split entire stack - would be move, not split)
        # Or verify success with 0 remaining + new entry with 10
        # (Check inventory.py behavior first!)

    def test_split_stack_single_item(self):
        """Test splitting 1 item from stack."""
        # Create inventory with 10 items
        # Split 1 item
        # Verify 2 entries: 9 and 1
```

**Test data setup:**
- Use existing setUpModule pattern (create tables)
- Each test creates its own inventory, item, entries
- Use cleanup in tearDown if needed

**Verification:**
- Run `PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 py/services/tests/inventory_service_test.py`
- Verify all split_stack tests pass
- Verify test output shows clear test names

#### Task 2.2: Add transfer_item() Test Cases

Add comprehensive tests for InventoryService.transfer_item() method.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/inventory_service_test.py` - Add new test class

**Implementation notes:**

Add test class:
```python
class TestInventoryServiceTransferItem(unittest.TestCase):
    """Test transfer_item() method - CRITICAL."""

    def test_transfer_item_success(self):
        """Test transferring items between inventories."""
        # Create 2 inventories (Owner mobile_id=100, mobile_id=200)
        # Create item
        # Add 10 items to source inventory
        # Transfer 5 items to destination
        # Verify source has 5 items remaining
        # Verify destination has 5 items
        # Verify SUCCESS result

    def test_transfer_item_insufficient_quantity(self):
        """Test transferring more items than exist."""
        # Create source with 5 items
        # Try to transfer 10 items
        # Verify FAILURE result
        # Verify source still has 5 items (no change)
        # Verify destination still empty (no change)

    def test_transfer_item_to_empty_inventory(self):
        """Test transferring to inventory with no existing items."""
        # Create source with 10 items
        # Create empty destination
        # Transfer 5 items
        # Verify destination now has 1 entry with quantity=5

    def test_transfer_item_stacking(self):
        """Test transferring items that stack with existing items."""
        # Create source with 10 items
        # Create destination with 5 of same item
        # Transfer 3 items
        # Verify destination has 1 entry with quantity=8 (stacked)
        # Verify source has 7 items

    def test_transfer_item_atomicity(self):
        """Test transaction rollback on failure (CRITICAL)."""
        # Note: This is complex - requires mocking save() failure
        # Option 1: Mock dest_model.save() to raise exception
        # Option 2: Manually corrupt dest_model to cause constraint violation
        # Verify source inventory unchanged after failure
        # Verify FAILURE result

    def test_transfer_item_nonexistent_item(self):
        """Test transferring item that doesn't exist in database."""
        # Create 2 inventories
        # Try to transfer item_id=99999 (doesn't exist)
        # Verify FAILURE with DB_RECORD_NOT_FOUND
        # Verify both inventories unchanged
```

**Verification:**
- Run inventory_service_test.py
- Verify all transfer_item tests pass
- Verify atomicity test actually tests rollback (check logs)

#### Task 2.3: Add load_with_blueprint_tree() Test Cases

Add comprehensive tests for ItemService.load_with_blueprint_tree() method.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/item_service_test.py` - Add new test class

**Implementation notes:**

Add test class:
```python
class TestItemServiceBlueprintTree(unittest.TestCase):
    """Test load_with_blueprint_tree() method."""

    @classmethod
    def setUpClass(cls):
        """Create test items and blueprints for tree tests."""
        # Create items: Iron Ore, Iron Bar, Steel Bar
        # Create blueprints:
        #   - Iron Bar requires 2x Iron Ore (bake_time=1000ms)
        #   - Steel Bar requires 1x Iron Bar (bake_time=2000ms)
        # Store item IDs for tests

    def test_blueprint_tree_simple(self):
        """Test loading simple 2-level blueprint tree."""
        # Load Steel Bar with blueprint tree
        # Verify tree structure:
        #   - Steel Bar (root)
        #     - Iron Bar (component, ratio=1)
        #       - Iron Ore (component, ratio=2)
        # Verify total_bake_time = 3000ms
        # Verify no flags set (max_depth_reached, cycle_detected)

    def test_blueprint_tree_max_depth(self):
        """Test max_depth limit."""
        # Load Steel Bar with max_depth=1
        # Verify tree only goes 1 level deep
        # Verify max_depth_reached flag is True
        # Verify total_bake_time only includes Steel Bar (not full tree)

    def test_blueprint_tree_no_blueprint(self):
        """Test item with no blueprint."""
        # Load Iron Ore (raw material, no blueprint)
        # Verify tree has item but no components
        # Verify total_bake_time = 0

    def test_blueprint_tree_cycle_detection(self):
        """Test cycle detection in blueprints."""
        # Create circular blueprint: Item A requires Item B, Item B requires Item A
        # Load Item A with blueprint tree
        # Verify cycle_detected flag is True
        # Verify tree doesn't infinite loop
```

**Test data setup:**
- Need to create ItemBlueprint and ItemBlueprintComponent records
- Use setUpModule to add these tables: `ItemBlueprint.CREATE_TABLE_STATEMENT`, `ItemBlueprintComponent.CREATE_TABLE_STATEMENT`
- Create test data in setUpClass (shared across tests)

**Verification:**
- Run item_service_test.py
- Verify all blueprint tree tests pass
- Manually inspect tree structure in test output (use logging)

---

### **STEP 3: Expand Error Path Testing**

---

### Step 3: Expand Error Path Testing

**Objective:** Test failure scenarios for all CRUD methods (not just success cases)

**Acceptance Criteria:**
- [x] Each service has tests for: not found, invalid data, constraint violations
- [x] Error codes are verified (not just StatusType.FAILURE)
- [x] All error tests pass
- [x] No regressions

**Testing Requirements:**
- [x] Test record not found scenarios
- [x] Test invalid request data scenarios
- [x] Test database constraint violations
- [x] Verify correct error codes returned

**Tasks:**

#### Task 3.1: Add Error Path Tests for PlayerService

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/player_service_test.py` - Add new test functions

**Implementation notes:**

Add tests after existing run_all_tests():
```python
def test_load_nonexistent_player():
    """Test loading player that doesn't exist."""
    service = PlayerServiceHandler()
    request = PlayerRequest(data=PlayerRequestData(
        load_player=LoadPlayerRequestData(player_id=99999)
    ))
    response = service.load(request)
    assert response.results[0].status == StatusType.FAILURE
    assert response.results[0].error_code == GameError.DB_RECORD_NOT_FOUND
    assert response.response_data is None

def test_delete_nonexistent_player():
    """Test deleting player that doesn't exist."""
    service = PlayerServiceHandler()
    request = PlayerRequest(data=PlayerRequestData(
        delete_player=DeletePlayerRequestData(player_id=99999)
    ))
    response = service.delete(request)
    assert response.results[0].status == StatusType.FAILURE
    assert response.results[0].error_code == GameError.DB_RECORD_NOT_FOUND

def test_create_player_missing_required_field():
    """Test creating player with invalid data."""
    service = PlayerServiceHandler()
    player = ThriftPlayer(
        id=None,
        full_name=None,  # Required field is None
        what_we_call_you="TestUser",
        security_token="token",
        over_13=True,
        year_of_birth=1990,
        email="test@example.com",
    )
    request = PlayerRequest(data=PlayerRequestData(
        create_player=CreatePlayerRequestData(player=player)
    ))
    response = service.create(request)
    # Should fail (depends on DB constraints)
    # Verify appropriate error returned
```

**Verification:**
- Run player_service_test.py
- Verify new error tests pass
- Verify error messages are descriptive

#### Task 3.2: Add Error Path Tests for ItemService

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/item_service_test.py` - Add new test functions

**Implementation notes:**

Similar pattern to PlayerService:
```python
def test_load_nonexistent_item():
    """Test loading item that doesn't exist."""
    # item_id=99999 doesn't exist
    # Verify FAILURE with DB_RECORD_NOT_FOUND

def test_destroy_nonexistent_item():
    """Test destroying item that doesn't exist."""
    # item_id=99999 doesn't exist
    # Verify FAILURE with DB_RECORD_NOT_FOUND

def test_create_item_invalid_type():
    """Test creating item with invalid ItemType."""
    # This may not be possible with Thrift enums
    # If not testable, skip or document why
```

**Verification:**
- Run item_service_test.py
- Verify error tests pass

#### Task 3.3: Add Error Path Tests for InventoryService

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/inventory_service_test.py` - Add new test functions

**Implementation notes:**

```python
def test_load_nonexistent_inventory():
    """Test loading inventory that doesn't exist."""
    # inventory_id=99999 doesn't exist
    # Verify FAILURE with DB_RECORD_NOT_FOUND

def test_create_inventory_invalid_owner():
    """Test creating inventory with invalid owner."""
    # Owner with all fields None (invalid)
    # Verify FAILURE (or success if DB allows nulls - check behavior)

def test_split_stack_zero_quantity():
    """Test splitting zero items."""
    # Try to split 0 items
    # Verify FAILURE with appropriate error
```

**Verification:**
- Run inventory_service_test.py
- Verify error tests pass

---

### **STEP 4: Add list_records() Test Coverage**

---

### Step 4: Add list_records() Test Coverage

**Objective:** Test pagination and search functionality for all three services

**Acceptance Criteria:**
- [x] Each service tests pagination (multiple pages)
- [x] Each service tests search functionality
- [x] Each service tests empty result set
- [x] All list_records tests pass

**Testing Requirements:**
- [x] Test first page, middle page, last page
- [x] Test results_per_page variations
- [x] Test search with and without results
- [x] Verify total_count is accurate

**Tasks:**

#### Task 4.1: Add list_records() Tests for PlayerService

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/player_service_test.py` - Add test function

**Implementation notes:**

```python
def test_list_records_pagination():
    """Test paginated listing of players."""
    service = PlayerServiceHandler()

    # Create 25 test players
    for i in range(25):
        player = ThriftPlayer(
            id=None,
            full_name=f"Player {i}",
            what_we_call_you=f"Player{i}",
            security_token="token",
            over_13=True,
            year_of_birth=1990,
            email=f"player{i}@example.com",
        )
        service.create(PlayerRequest(data=PlayerRequestData(
            create_player=CreatePlayerRequestData(player=player)
        )))

    # Test page 0, results_per_page=10
    request = PlayerRequest(data=PlayerRequestData(
        list_player=ListPlayerRequestData(page=0, results_per_page=10)
    ))
    response = service.list_records(request)
    assert is_ok(response.results)
    assert len(response.response_data.list_player.players) == 10
    assert response.response_data.list_player.total_count == 25

    # Test page 2 (should have 5 results)
    request = PlayerRequest(data=PlayerRequestData(
        list_player=ListPlayerRequestData(page=2, results_per_page=10)
    ))
    response = service.list_records(request)
    assert len(response.response_data.list_player.players) == 5

def test_list_records_search():
    """Test searching for players."""
    service = PlayerServiceHandler()

    # Create players: Alice, Bob, Charlie
    # Search for "li" (should match Alice and Charlie)
    # Verify 2 results
    # Verify correct players returned
```

**Verification:**
- Run player_service_test.py
- Verify pagination tests pass
- Check that total_count matches actual count

#### Task 4.2: Add list_records() Tests for ItemService

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/item_service_test.py` - Add test function

**Implementation notes:**

Similar to PlayerService but search on internal_name field:
```python
def test_list_records_pagination():
    """Test paginated listing of items."""
    # Create 15 test items
    # Test page 0 with results_per_page=5
    # Test page 2 (should have 5 results)
    # Verify total_count = 15

def test_list_records_search():
    """Test searching for items by internal_name."""
    # Create items: iron_ore, iron_bar, copper_ore
    # Search for "iron"
    # Verify 2 results (iron_ore, iron_bar)
```

**Verification:**
- Run item_service_test.py
- Verify list tests pass

#### Task 4.3: Add list_records() Tests for InventoryService

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/inventory_service_test.py` - Add test function

**Implementation notes:**

```python
def test_list_records_pagination():
    """Test paginated listing of inventories."""
    # Create 10 test inventories
    # Test page 0 with results_per_page=5
    # Verify 5 results, total_count=10
    # Test page 1
    # Verify 5 results

def test_list_records_empty():
    """Test listing when no inventories exist."""
    # Don't create any inventories
    # List with page=0
    # Verify empty list, total_count=0
```

**Verification:**
- Run inventory_service_test.py
- Verify list tests pass

---

### **STEP 5: Fix Encapsulation Violations**

---

### Step 5: Fix list_records() Encapsulation Violations

**Objective:** Stop bypassing model layer with direct `_data` manipulation

**Acceptance Criteria:**
- [x] Generator provides official `from_dict()` static method
- [x] All list_records() methods use `from_dict()` instead of `_data`
- [x] All tests pass (including new list_records tests from Step 4)
- [x] No direct `_data` access in service code

**Testing Requirements:**
- [x] Existing list_records tests verify refactored code works
- [x] No regression in other tests

**Tasks:**

#### Task 5.1: Add from_dict() Method to Model Generator

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add method to class template

**Implementation notes:**

Find the class template generation (where `find()`, `save()`, etc. are added) and add:

```python
@staticmethod
def from_dict(data: dict) -> '{class_name}':
    """
    Create a model instance from a dictionary (typically a database row).

    Args:
        data: Dictionary with column names as keys

    Returns:
        Model instance populated with data
    """
    instance = {class_name}()
    instance._data = data.copy()
    instance._dirty = False
    return instance
```

Add this to the method generation section, around line 1200-1300 (near find() and save() methods).

**Verification:**
- Regenerate models: `cd /vagrant/gamedb/thrift/py/db_models && python3 generate_models.py`
- Verify Player, Item, Inventory classes have from_dict() method
- Test manually: `Player.from_dict({'id': 1, 'full_name': 'Test'})`

#### Task 5.2: Refactor PlayerService.list_records()

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/player_service.py:351-357` - Replace direct _data manipulation

**Implementation notes:**

Replace lines 351-357:
```python
# OLD (lines 351-357):
players = []
for row in rows:
    player = Player()
    player._data = row
    player._dirty = False
    results, thrift_player = player.into_thrift()
    if thrift_player:
        players.append(thrift_player)

# NEW:
players = []
for row in rows:
    player = Player.from_dict(row)
    results, thrift_player = player.into_thrift()
    if thrift_player:
        players.append(thrift_player)
```

**Verification:**
- Run player_service_test.py
- Run list_records tests added in Step 4
- Verify all pass

#### Task 5.3: Refactor ItemService.list_records()

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/item_service.py:377-381` - Replace _populate_from_dict()

**Implementation notes:**

Replace lines 377-381:
```python
# OLD:
items = []
for row in rows:
    item = Item()
    item._populate_from_dict(row)  # Undocumented internal method
    _, thrift_item = item.into_thrift()
    items.append(thrift_item)

# NEW:
items = []
for row in rows:
    item = Item.from_dict(row)
    _, thrift_item = item.into_thrift()
    items.append(thrift_item)
```

**Verification:**
- Run item_service_test.py
- Verify list_records tests pass

#### Task 5.4: Refactor InventoryService.list_records()

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/inventory_service.py:592-597` - Replace direct _data manipulation

**Implementation notes:**

Replace lines 592-597:
```python
# OLD:
thrift_inventories = []
for row in rows:
    inventory = Inventory()
    inventory._data = row
    _, thrift_inv = inventory.into_thrift()
    if thrift_inv:
        thrift_inventories.append(thrift_inv)

# NEW:
thrift_inventories = []
for row in rows:
    inventory = Inventory.from_dict(row)
    _, thrift_inv = inventory.into_thrift()
    if thrift_inv:
        thrift_inventories.append(thrift_inv)
```

**Verification:**
- Run inventory_service_test.py
- Verify list_records tests pass

---

### **STEP 6: Fix Performance Issues**

---

### Step 6: Fix Blueprint Tree N+1 Query Problem

**Objective:** Reduce query count for blueprint tree from 50+ to ~5 for complex blueprints

**Acceptance Criteria:**
- [x] Blueprint tree queries are batched or cached
- [x] Complex blueprint (50 components) loads in < 100ms
- [x] Query count for 50-component tree is < 10
- [x] All blueprint tests still pass

**Testing Requirements:**
- [x] Performance test measures query count
- [x] Performance test measures execution time
- [x] Existing blueprint tests verify correctness

**Tasks:**

#### Task 6.1: Design Batch Loading Strategy

**Files to modify:**
- None (design task)

**Implementation notes:**

Choose one approach:

**Option A: Recursive batch loading**
- Load all components for current level in one query
- Recursively load next level's components in one query
- Query count = depth (much better than N queries per level)

**Option B: Single query with JOIN**
- Use recursive CTE or multiple JOINs to load entire tree
- Parse results into tree structure
- Query count = 1 (optimal)

**Option C: Cache component lookups**
- Add LRU cache decorator to Item.find()
- Cache lasts for single request
- Query count = unique items (better than N)

**Recommendation:** Start with Option C (easiest), move to Option A if needed

**Verification:**
- Document chosen approach
- Get user approval before implementing

#### Task 6.2: Implement Caching for Blueprint Components

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/item_service.py:592-679` - Add caching to _build_blueprint_tree_node

**Implementation notes:**

Add a cache parameter to the method:

```python
def _build_blueprint_tree_node(
    self,
    item: Item,
    visited_items: set,
    current_depth: int,
    max_depth: int,
    item_cache: Optional[dict] = None,  # NEW
) -> BlueprintTreeNode:
    """..."""
    if item_cache is None:
        item_cache = {}  # Initialize cache for this tree build

    # ... existing code ...

    # Replace line 643:
    # OLD: component_item_model = Item.find(component_item_id)
    # NEW:
    if component_item_id in item_cache:
        component_item_model = item_cache[component_item_id]
        logger.debug(f"Cache HIT for item_id={component_item_id}")
    else:
        component_item_model = Item.find(component_item_id)
        item_cache[component_item_id] = component_item_model
        logger.debug(f"Cache MISS for item_id={component_item_id}")

    # ... rest of code ...

    # Pass cache to recursive calls:
    component_node = self._build_blueprint_tree_node(
        component_thrift_item,
        new_visited,
        current_depth + 1,
        max_depth,
        item_cache,  # NEW
    )
```

Also update the call site (line 547) to pass empty cache.

**Verification:**
- Run blueprint tree tests
- Check logs for cache HIT messages
- Manually verify fewer database queries

#### Task 6.3: Add Performance Regression Test

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/item_service_test.py` - Add performance test

**Implementation notes:**

```python
def test_blueprint_tree_performance():
    """
    Test that blueprint tree doesn't have N+1 query problem.
    This is a regression test for performance issue.
    """
    # Create a complex blueprint tree:
    # - Root item
    # - 10 direct components
    # - Each component has 3 sub-components
    # Total: 1 root + 10 + 30 = 41 items

    # Use a query counter (mock or decorator)
    # Load blueprint tree
    # Verify query count < 45 (should be ~11 with cache: 1 root + 10 components)
    # Verify execution time < 500ms

    # Note: May need to add query counting infrastructure
    # For now, manually verify with logging
```

**Verification:**
- Run performance test
- Manually check query count in logs
- If query count is still high, revisit caching strategy

---

### **STEP 7: Add Performance Testing Infrastructure**

---

### Step 7: Add Performance Testing Infrastructure

**Objective:** Add tools to measure and verify performance characteristics

**Acceptance Criteria:**
- [x] Query counter decorator available for tests
- [x] Timer decorator available for tests
- [x] Performance tests use these tools
- [x] Performance assertions are documented

**Testing Requirements:**
- [x] Query counter accurately counts database calls
- [x] Timer accurately measures execution time
- [x] Tests fail when performance degrades

**Tasks:**

#### Task 7.1: Create Test Utilities Module

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/test_utils.py` - Create new file

**Implementation notes:**

Create new file with performance testing utilities:

```python
"""Utilities for testing services."""

import time
from functools import wraps
from typing import Callable, Any
from unittest.mock import patch


class QueryCounter:
    """Context manager to count database queries."""

    def __init__(self):
        self.count = 0

    def __enter__(self):
        self.count = 0
        # Patch Item._create_connection to count calls
        # This is a simple implementation
        return self

    def __exit__(self, *args):
        pass


class Timer:
    """Context manager to measure execution time."""

    def __init__(self):
        self.elapsed = 0
        self.start = 0

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed = time.time() - self.start


def with_query_counter(func: Callable) -> Callable:
    """Decorator to count queries in a test function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        counter = QueryCounter()
        with counter:
            result = func(*args, counter=counter, **kwargs)
        return result
    return wrapper
```

**Verification:**
- Import test_utils in test files
- Manually test QueryCounter and Timer
- Verify they work as expected

#### Task 7.2: Add Performance Tests Using New Utilities

**Files to modify:**
- `/vagrant/gamedb/thrift/py/services/tests/item_service_test.py` - Use test_utils

**Implementation notes:**

Update performance test from Step 6:

```python
from tests.test_utils import QueryCounter, Timer

def test_blueprint_tree_performance():
    """Test blueprint tree performance."""
    # Create complex tree...

    with Timer() as timer:
        with QueryCounter() as counter:
            response = service.load_with_blueprint_tree(request)

    assert is_ok(response.results)
    assert counter.count < 45, f"Too many queries: {counter.count}"
    assert timer.elapsed < 0.5, f"Too slow: {timer.elapsed}s"
    print(f"Performance: {counter.count} queries in {timer.elapsed:.3f}s")
```

**Verification:**
- Run performance test
- Verify assertions work (make queries slow/numerous to test failure)
- Restore normal code, verify test passes

---

## Testing Strategy

### Unit Tests
> Use testing framework and conventions from `./tasks/env.md`

**Existing Test Files:**
- `/vagrant/gamedb/thrift/py/services/tests/player_service_test.py` - Expand with error paths, list_records
- `/vagrant/gamedb/thrift/py/services/tests/item_service_test.py` - Expand with blueprint tree, error paths, list_records, performance
- `/vagrant/gamedb/thrift/py/services/tests/inventory_service_test.py` - Expand with split_stack, transfer_item, error paths, list_records

**New Test File:**
- `/vagrant/gamedb/thrift/py/services/tests/test_utils.py` - Performance testing utilities

**Coverage Goal:** 80%+ on all three services

**Run Command:**
```bash
cd /vagrant/gamedb/thrift
PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 py/services/tests/player_service_test.py
PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 py/services/tests/item_service_test.py
PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH" python3 py/services/tests/inventory_service_test.py
```

### Integration Tests

Not needed for this plan - unit tests cover service layer sufficiently. Integration tests (cross-service interactions) are future work.

### Manual Testing

After implementation, manually verify:
- [ ] Create player, add to inventory, transfer between inventories - works end-to-end
- [ ] Load item with complex blueprint tree - renders in reasonable time
- [ ] List 1000+ records with pagination - performs acceptably
- [ ] Error messages are user-friendly and accurate

---

## Edge Cases & Error Handling

### Edge Cases

- **Empty inventories:** split_stack and transfer_item with no entries
- **Exact quantities:** Split/transfer exact amount (edge of available quantity)
- **Single-item stacks:** Split 1 item from stack of 1
- **Deep blueprint trees:** 10+ levels of nesting
- **Circular blueprints:** Item A requires Item B requires Item A
- **Zero pagination:** page=0, results_per_page=0
- **Negative pagination:** page=-1 (handled by max(0, page))
- **Large pagination:** results_per_page=10000

### Error Scenarios

- **Database connection failures:** Return DB_CONNECTION_FAILED
- **Not found errors:** Return DB_RECORD_NOT_FOUND with specific entity
- **Constraint violations:** Return DB_INSERT_FAILED or DB_UPDATE_FAILED
- **Transaction rollback:** Return appropriate error, log rollback
- **Invalid Thrift data:** Return DB_INVALID_DATA
- **DoS attempts:** Validate input, clamp to safe ranges

---

## Rollback Plan
> Use version control commands from `./tasks/env.md`

If bugs are introduced during this enhancement:

**Step 1: Identify the problematic change**
- Review test failures to identify which step failed
- Check git log to see recent commits

**Step 2: Revert specific changes**
```bash
# For git (from tasks/env.md):
cd /vagrant/gamedb/thrift
git log --oneline  # Find commit to revert
git revert <commit-hash>  # Revert specific commit
```

**Step 3: Fix forward or revert more**
- If revert doesn't work, continue reverting
- Or fix the bug and commit fix
- Ensure tests pass before proceeding

**Step 4: Verify system state**
- Run all service tests
- Verify no regressions
- Check that services still respond to requests

**No database migrations in this plan, so no schema rollback needed.**

---

## Success Criteria

**Critical (Must Complete):**
- [x] All critical bugs fixed (transfer_item atomicity, max_depth validation)
- [x] split_stack, transfer_item, blueprint_tree have comprehensive tests
- [x] All tests pass (old + new)
- [x] No data corruption scenarios exist

**High Priority (Should Complete):**
- [x] Test coverage > 80% on all services
- [x] Error path testing added for all CRUD methods
- [x] list_records tests added for all services
- [x] Encapsulation violations fixed

**Performance (Should Complete):**
- [x] Blueprint tree N+1 query problem fixed
- [x] Performance tests added and passing
- [x] Complex blueprints load in < 500ms

**Overall:**
- [x] No regressions in existing functionality
- [x] Code review analysis document updated with "RESOLVED" notes
- [x] Services are production-ready (no blocking issues)

---

## Notes for Implementation

### Patterns to Follow

**Test Organization:**
- Use class-based tests for related test cases: `class TestInventoryServiceSplitStack(unittest.TestCase):`
- Follow existing test structure in player_service_test.py:193
- Use setUpModule/tearDownModule for database setup (existing pattern)

**Test Naming:**
- `test_{method_name}_{scenario}` - e.g., `test_split_stack_insufficient_quantity`
- Clear, descriptive names that explain what's being tested

**Assertion Style:**
- Use `assert is_ok(response.results)` for success checks (from common.py)
- Use `assert response.results[0].status == StatusType.FAILURE` for failure checks
- Use `assert response.results[0].error_code == GameError.X` to verify specific errors

**Test Data:**
- Create fresh data per test (don't rely on shared state)
- Use descriptive names: `player_alice`, `inventory_source`, `item_iron_ore`
- Clean up in tearDown if test creates data that affects other tests

### Common Pitfalls

**Pitfall 1: Forgetting to regenerate models**
- After adding from_dict() to generator, MUST run `python3 generate_models.py`
- Service code won't work until models are regenerated

**Pitfall 2: Not testing atomicity properly**
- Mock must actually prevent commit, not just raise exception after commit
- Verify source data unchanged by reloading from database

**Pitfall 3: Blueprint tree tests without proper cleanup**
- Creating complex blueprints creates many records
- Make sure tables are dropped in tearDownModule

**Pitfall 4: Performance tests are flaky**
- Query counts can vary based on cache state
- Use ranges instead of exact counts: `assert count < 50` not `assert count == 42`
- Execution time varies by load - use generous bounds

**Pitfall 5: Testing transfer_item without transaction fix**
- Step 1 must be complete before Step 2 transfer_item tests
- Tests will be flaky if transaction isn't atomic

**Pitfall 6: Forgetting PYTHONPATH when running tests**
- Must set `PYTHONPATH="/vagrant/gamedb/thrift/gen-py:$PYTHONPATH"`
- Otherwise get `ImportError: No module named 'game'`

### Questions & Clarifications

**Question 1: Should split_stack() allow splitting entire stack?**
- Assumption: No, splitting entire stack should fail (use transfer_item instead)
- Verify with inventory.py behavior before writing test

**Question 2: Should transfer_item() auto-stack items?**
- Assumption: Yes, if destination has same item, quantities should combine
- Verify with inventory.py behavior before writing test

**Question 3: What should max_depth default be?**
- Current: 10
- Recommendation: Keep at 10 (reasonable for most blueprints)
- Document that 50 is the maximum

**Question 4: Should list_records() support sorting?**
- Current: Sorts by id (Player, Inventory) or internal_name (Item)
- Assumption: Keep current behavior, don't add sort parameter
- Out of scope for this plan

---

## Estimated Timeline

**Step 1 (Critical Bugs):** 3-4 hours
- Task 1.1: 1 hour
- Task 1.2: 30 minutes
- Task 1.3: 1.5 hours

**Step 2 (Critical Tests):** 8-10 hours
- Task 2.1: 3 hours
- Task 2.2: 4 hours
- Task 2.3: 3 hours

**Step 3 (Error Paths):** 4-5 hours
- Task 3.1: 1.5 hours
- Task 3.2: 1.5 hours
- Task 3.3: 1.5 hours

**Step 4 (list_records Tests):** 3-4 hours
- Task 4.1: 1.5 hours
- Task 4.2: 1 hour
- Task 4.3: 1 hour

**Step 5 (Encapsulation):** 2-3 hours
- Task 5.1: 1 hour
- Task 5.2-5.4: 1 hour total

**Step 6 (Performance):** 4-6 hours
- Task 6.1: 1 hour
- Task 6.2: 2 hours
- Task 6.3: 1 hour

**Step 7 (Performance Testing):** 2-3 hours
- Task 7.1: 1.5 hours
- Task 7.2: 1 hour

**Total: 26-35 hours** (3-4 full days of work)

**Priority for Production:**
- Steps 1-2 are BLOCKING (must complete)
- Steps 3-5 are HIGH priority (should complete)
- Steps 6-7 are MEDIUM priority (can defer if needed)

---

## Post-Implementation Actions

After completing this plan:

1. **Update code review document:**
   - Add "RESOLVED" notes to each bug entry
   - Update test coverage metrics
   - Note any remaining issues

2. **Update exploration docs:**
   - Update explore-services.md with testing patterns
   - Document performance optimization strategies

3. **Run full test suite:**
   - Verify all 3 services pass
   - Check total execution time (should be < 15 seconds)
   - Calculate and document new coverage percentage

4. **Manual verification:**
   - Test each service via actual Thrift RPC calls
   - Verify error messages are user-friendly
   - Check performance under realistic load

5. **Documentation:**
   - Update service docstrings if needed
   - Document any new patterns introduced
   - Add performance testing guide for future tests
