# Plan: Refactor DB Models Generator - Fix Critical Issues

**Plan Date:** 2025-11-27
**Target Branch:** main
**Current Commit:** a803046747bf543d1649097e62aa2f9d038936ba
**Estimated Complexity:** Complex

## Overview

This plan addresses critical and high-priority technical debt in the db_models code generator to achieve a working state. The generator currently cannot run tests due to import path issues, generates incorrect API for 1-to-1 relationships, lacks validation for union types, and has maintainability issues. This refactor focuses on fixing these core issues while adding comprehensive test coverage. Future refactors will address remaining technical debt (caching removal, annotation-based config, attribute map improvements).

## Context

The db_models component is a code generator that introspects MySQL schemas and generates ActiveRecord-style Python models with Thrift integration. It's the new approach replacing legacy hand-written models in `/vagrant/gamedb/thrift/py/dbinc/`. The generator creates a single monolithic `models.py` file with all model classes plus a corresponding `tests.py` file.

Currently, the generated code is broken and cannot be tested. This blocks all development and prevents validation of the generator's output. This refactor will establish a working baseline with proper test coverage.

### Environment & Constraints
> Reference `./tasks/env.md` for complete environment details

- **Language/Runtime:** Python 3.12.3
- **Key Dependencies:**
  - mysql-connector-python (database connectivity)
  - python-dotenv (environment configuration)
  - jinja2 (template engine)
  - Apache Thrift (code generation and RPC)
- **Compatibility Requirements:** Must work with existing game.thrift definitions and MySQL schema
- **Performance Constraints:** Generator runs during development only, performance not critical
- **Security Considerations:** Owner union validation prevents data corruption; sanitization deferred to future work
- **Testing Framework:** Python unittest (mix of library and adhoc approaches)
- **Database:** MySQL (localhost, credentials: admin/minda)

### Relevant Documentation
- `./tasks/explore-db-models.md` (Explored: 2025-11-27, Commit: a803046) - Comprehensive exploration of generator architecture, domain model, and all known issues

**Documentation Status:**
- [x] All relevant components have been explored
- [x] Exploration docs are up-to-date with current code
- [ ] Missing exploration: None

### Related Documents
- **Based on explorations:** explore-db-models.md
- **Related plans:** None (first refactor of this component)
- **Supersedes:** None
- **Will update explorations:** explore-db-models.md (after implementation, update "Known Issues" section to reflect fixes)

## Requirements Summary

**Goals:**
1. Get the generator to a working state (tests can run and pass)
2. Eliminate critical and high-priority technical debt

**Core Requirements:**
- Fix import path so tests run without PYTHONPATH workaround
- Generate correct singular methods for 1-to-1 relationships (Player.get_mobile())
- Add Owner union validation to prevent data corruption
- Improve config.py maintainability and add validation
- Generate comprehensive tests for Thrift conversion and union handling

**Constraints:**
- Never directly edit generated files (models.py, tests.py) - always fix the generator
- Each step must update generator and regenerate code
- Tests must run after each step to provide continuous feedback
- Keep focused on critical/high issues - defer other tech debt to future refactors

**Out of Scope (Future Refactors):**
- Removing relationship caching
- Implementing Thrift annotation parsing
- Attribute map delete-then-recreate logic
- Pass-through relationships
- Cascade delete behavior refinement

## Technical Approach

The refactor will modify the generator scripts in `/vagrant/gamedb/thrift/py/db_models/` to fix critical issues and improve code quality. Each step will:

1. Modify generator scripts (generate_models.py, generator/*.py, templates/*.tmpl)
2. Regenerate models.py and tests.py completely
3. Run tests to verify changes
4. Ensure all tests pass before moving to next step

The order is critical: fix imports first so subsequent steps can run tests immediately.

### Key Decisions

- **Import Path Fix:** Modify generated code header to add gen-py to sys.path, avoiding need for PYTHONPATH environment variable
- **1-to-1 Detection:** Analyze Thrift struct field types during generation - if FK references table with singular field name in Thrift, generate singular getter
- **Owner Union Validation:** Add validation methods to base model generation that check exactly one owner FK is set and validate per-table rules
- **Config Validation:** Add startup validation in generate_models.py that verifies all tables in config exist and all Thrift structs are valid
- **Test Generation:** Extend test generation to cover Thrift conversion round-trips and union variant handling

### Dependencies

- **External:** None (all dependencies already installed)
- **Internal:**
  - game.thrift Thrift definitions
  - MySQL gamedb database schema
  - generator/*.py utility modules
  - templates/model_template.py.tmpl Jinja2 template

## Implementation Plan

### Step 1: Fix Import Path Issues

**Objective:** Make tests runnable to provide continuous feedback throughout refactor

**Acceptance Criteria:**
- [ ] Generated models.py imports from game.ttypes without PYTHONPATH workaround
- [ ] Tests can be executed with simple `python3 tests.py` command
- [ ] Tests run and report results (may fail initially, but must execute without import errors)
- [ ] Generator adds path manipulation code to generated file header

**Testing Requirements:**
- [ ] Run `cd /vagrant/gamedb/thrift/py/db_models && python3 tests.py` without setting PYTHONPATH
- [ ] Verify import errors are resolved
- [ ] Confirm tests execute (even if some fail)

**Tasks:**

#### Task 1.1: Add sys.path manipulation to generated code header

Modify `generate_models.py` to inject path setup code at the top of generated models.py file.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add path setup to generated file header

**Implementation notes:**
- Add import sys and sys.path manipulation in the generated code template
- Path to add: `/vagrant/gamedb/thrift/gen-py`
- Insert this code before any game.ttypes imports
- Use absolute path to avoid issues with current working directory

**Example code to generate:**
```python
import sys
import os
# Add Thrift generated code to path
thrift_gen_path = '/vagrant/gamedb/thrift/gen-py'
if thrift_gen_path not in sys.path:
    sys.path.insert(0, thrift_gen_path)
```

#### Task 1.2: Apply same fix to generated tests.py

Modify test generation to include same path setup code.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add path setup to generated tests.py header

**Implementation notes:**
- Use identical path manipulation code as Task 1.1
- Place before any imports from models or game.ttypes
- Ensure tests can import both models.py and game.ttypes

#### Task 1.3: Regenerate and verify tests run

Regenerate all code and verify tests execute.

**Files to modify:**
- N/A (regeneration only)

**Implementation notes:**
- Run: `cd /vagrant/gamedb/thrift/py/db_models && python3 generate_models.py`
- Backup old models.py and tests.py if desired
- Run: `python3 tests.py`
- Verify tests execute without import errors (failures are OK at this stage)

**Verification:**
- Navigate to `/vagrant/gamedb/thrift/py/db_models`
- Run `python3 tests.py` without any PYTHONPATH setup
- Confirm no ImportError for game.ttypes
- Tests should run and report results (some may fail, that's expected)

---

### Step 2: Fix Player-Mobile 1-to-1 Relationship

**Objective:** Generate correct singular method name and enforce 1-to-1 constraint according to design intent

**Acceptance Criteria:**
- [ ] Generator detects 1-to-1 relationships automatically from Thrift struct field names
- [ ] Generated code has `player.get_mobile()` (singular) not `get_mobiles()` (plural)
- [ ] `Player.from_thrift()` updates existing mobile or creates new (no duplicates)
- [ ] `Player.into_thrift()` loads and embeds mobile inline in Player Thrift object
- [ ] Generated has_many method name uses singular form for 1-to-1 relationships

**Testing Requirements:**
- [ ] Test 1-to-1 relationship detection logic in generator
- [ ] Test Player.get_mobile() returns single Mobile object (not list)
- [ ] Test Player.set_mobile() updates FK correctly
- [ ] Test from_thrift/into_thrift with embedded mobile round-trips correctly
- [ ] Verify no duplicate mobiles created when calling from_thrift multiple times
- [ ] All tests pass

**Tasks:**

#### Task 2.1: Add 1-to-1 relationship detection logic

Modify generator to detect 1-to-1 relationships by analyzing Thrift struct fields.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add function to detect 1-to-1 relationships
- `/vagrant/gamedb/thrift/py/db_models/generator/database.py` - Add helper to check if Thrift field is singular

**Implementation notes:**
- Parse game.thrift to read struct field definitions
- For each FK relationship, check if corresponding Thrift field is singular (not list/set)
- Example: Player struct has `optional Mobile mobile` (singular) → 1-to-1
- Store this metadata with relationship information
- Consider field name patterns: singular nouns indicate 1-to-1, plural indicate 1-to-many

**Detection logic:**
```python
def is_one_to_one_relationship(table_name, fk_column, thrift_struct):
    """
    Check if FK represents 1-to-1 relationship by examining Thrift struct.
    Returns True if Thrift field is singular (not list/set).
    """
    # Get field name from FK column (e.g., "owner_mobile_id" → "mobile")
    field_name = fk_column.replace('_id', '').replace('owner_', '')

    # Check if Thrift struct has singular field with this name
    # Parse game.thrift or use thrift generated metadata
    thrift_field = find_thrift_field(thrift_struct, field_name)

    if thrift_field and not is_collection_type(thrift_field):
        return True
    return False
```

#### Task 2.2: Generate singular method names for 1-to-1 relationships

Modify relationship method generation to use singular names for 1-to-1.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Update `generate_has_many_methods()` to check 1-to-1 flag
- `/vagrant/gamedb/thrift/py/db_models/generator/naming.py` - Add function to get singular/plural based on relationship type

**Implementation notes:**
- For 1-to-1 relationships detected in Task 2.1, generate singular method name
- Example: `get_mobile()` instead of `get_mobiles()`
- Return single object instead of list
- Update method signature: `def get_mobile(self, reload=False)` not `def get_mobiles(self, lazy=False, reload=False)`
- Remove lazy parameter for 1-to-1 (not applicable)

**Example generated code:**
```python
def get_mobile(self, reload=False):
    """Get the mobile owned by this player (1-to-1 relationship)"""
    if not reload and hasattr(self, '_mobile_cache'):
        return self._mobile_cache

    if self.get_id() is None:
        return None

    conn = self._create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM mobiles WHERE owner_player_id = %s LIMIT 1",
        (self.get_id(),),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        mobile = Mobile()
        mobile._data = row
        self._mobile_cache = mobile
        return mobile
    return None
```

#### Task 2.3: Update from_thrift to handle 1-to-1 embedded objects

Modify from_thrift generation to update existing related objects for 1-to-1.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Update `generate_from_thrift_method()` to handle embedded 1-to-1

**Implementation notes:**
- For 1-to-1 relationships, check if embedded object exists in Thrift object
- If embedded object has ID, update existing record
- If no ID, create new record
- Set FK to link parent to child
- Example: `Player.from_thrift()` with embedded mobile should update that mobile's data

**Example logic:**
```python
@staticmethod
def from_thrift(thrift_obj, connection=None):
    player = Player()
    player.set_id(thrift_obj.id)
    player.set_name(thrift_obj.name)
    # ... other fields ...

    # Handle embedded mobile (1-to-1)
    if thrift_obj.mobile:
        mobile = Mobile.from_thrift(thrift_obj.mobile, connection)
        # Set owner FK
        mobile.set_owner_player_id(player.get_id())
        player._mobile_cache = mobile

    return player
```

#### Task 2.4: Update into_thrift to embed 1-to-1 objects

Modify into_thrift generation to load and embed 1-to-1 related objects.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Update `generate_into_thrift_method()` to embed 1-to-1

**Implementation notes:**
- For 1-to-1 relationships, load related object
- Convert to Thrift and embed in parent Thrift object
- Example: `Player.into_thrift()` should load mobile and set `player_thrift.mobile = mobile.into_thrift()`

**Example logic:**
```python
def into_thrift(self):
    from game.ttypes import Player as ThriftPlayer
    thrift_obj = ThriftPlayer()
    thrift_obj.id = self.get_id()
    thrift_obj.name = self.get_name()
    # ... other fields ...

    # Embed mobile (1-to-1)
    mobile = self.get_mobile()
    if mobile:
        thrift_obj.mobile = mobile.into_thrift()

    return thrift_obj
```

#### Task 2.5: Add tests for 1-to-1 relationships

Generate tests that verify 1-to-1 constraint and methods.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Update `generate_tests()` to add 1-to-1 test cases

**Implementation notes:**
- Test singular method name exists and works
- Test method returns single object, not list
- Test from_thrift/into_thrift round-trip with embedded object
- Test that updating existing mobile via from_thrift doesn't create duplicates
- Add test case: create player, create mobile, link them, verify get_mobile() returns correct object

**Example test:**
```python
def test_player_mobile_one_to_one(self):
    """Test Player-Mobile 1-to-1 relationship"""
    # Create player
    player = Player()
    player.set_name("TestPlayer")
    player.save(conn)

    # Create mobile
    mobile = Mobile()
    mobile.set_name("PlayerAvatar")
    mobile.set_owner_player_id(player.get_id())
    mobile.save(conn)

    # Test get_mobile returns single object
    loaded_mobile = player.get_mobile()
    self.assertIsNotNone(loaded_mobile)
    self.assertEqual(loaded_mobile.get_name(), "PlayerAvatar")
    self.assertIsInstance(loaded_mobile, Mobile)

    # Verify it's not a list
    self.assertFalse(isinstance(loaded_mobile, list))
```

#### Task 2.6: Regenerate and verify Player-Mobile relationship

Regenerate code and run tests to verify fix.

**Files to modify:**
- N/A (regeneration only)

**Implementation notes:**
- Run: `cd /vagrant/gamedb/thrift/py/db_models && python3 generate_models.py`
- Verify models.py has `get_mobile()` not `get_mobiles()`
- Run: `python3 tests.py`
- Verify 1-to-1 tests pass

**Verification:**
- Check generated models.py contains `def get_mobile(self, reload=False):` for Player class
- Confirm method returns single Mobile object
- Run tests: all Player-Mobile relationship tests pass
- Verify no duplicate mobile creation when calling from_thrift multiple times

---

### Step 3: Add Owner Union Validation

**Objective:** Prevent data corruption from invalid owner configurations (multiple owners, invalid owner types)

**Acceptance Criteria:**
- [ ] Validation ensures exactly one owner FK is set (never zero, never multiple)
- [ ] Per-table validation enforces valid owner types (e.g., mobiles: only player/mobile, never item/asset)
- [ ] Validation in `set_owner_*()` methods automatically clears other owner FKs
- [ ] Validation in `from_thrift()` enforces constraints and raises clear errors
- [ ] Generated models include `validate_owner()` method
- [ ] Config.py documents valid owner types per table

**Testing Requirements:**
- [ ] Test setting multiple owner FKs is rejected with clear error
- [ ] Test setting invalid owner type for each table is rejected
- [ ] Test valid owner types work correctly for each table
- [ ] Test from_thrift with Owner union creates correct FK
- [ ] Test set_owner_* methods clear other owner FKs
- [ ] All validation tests pass

**Tasks:**

#### Task 3.1: Define valid owner types per table in config

Add configuration mapping of valid owner types for each table.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generator/config.py` - Add `VALID_OWNER_TYPES` dict

**Implementation notes:**
- Create dict mapping table names to list of valid owner types
- Based on domain rules from exploration doc
- Example: `'mobiles': ['player', 'mobile']` (never item/asset)
- Example: `'items': ['player', 'mobile', 'item', 'asset']` (all valid)

**Configuration to add:**
```python
# Valid owner types per table
# Tables using Owner union but with domain-specific constraints
VALID_OWNER_TYPES = {
    'mobiles': ['player', 'mobile'],  # Mobiles can only be owned by player or mobile
    'items': ['player', 'mobile', 'item', 'asset'],  # Items can be owned by anything
    'inventories': ['player', 'mobile', 'item', 'asset'],  # Inventories can be owned by anything
    # Add other tables as needed
}

def get_valid_owner_types(table_name: str) -> List[str]:
    """Get list of valid owner types for a table"""
    return VALID_OWNER_TYPES.get(table_name, ['player', 'mobile', 'item', 'asset'])
```

#### Task 3.2: Generate validate_owner method for models with Owner union

Add validation method generation for models with owner columns.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add `generate_owner_validation_method()`
- `/vagrant/gamedb/thrift/py/db_models/templates/model_template.py.tmpl` - Add validation method template

**Implementation notes:**
- Generate `validate_owner()` method for models with owner_*_id columns
- Method checks exactly one owner FK is non-None
- Method checks owner type is valid for this table (from config)
- Raises ValueError with clear message if validation fails

**Example generated method:**
```python
def validate_owner(self):
    """Validate Owner union: exactly one owner must be set and must be valid type"""
    owner_fks = {
        'player': self.get_owner_player_id(),
        'mobile': self.get_owner_mobile_id(),
        'item': self.get_owner_item_id(),
        'asset': self.get_owner_asset_id(),
    }

    # Check exactly one is set
    set_owners = [k for k, v in owner_fks.items() if v is not None]
    if len(set_owners) == 0:
        raise ValueError("Mobile must have exactly one owner (none set)")
    if len(set_owners) > 1:
        raise ValueError(f"Mobile must have exactly one owner (multiple set: {set_owners})")

    # Check valid type for this table
    valid_types = ['player', 'mobile']  # From config for mobiles table
    if set_owners[0] not in valid_types:
        raise ValueError(f"Mobile cannot be owned by {set_owners[0]} (valid types: {valid_types})")
```

#### Task 3.3: Update set_owner_* methods to clear other owners

Modify setter generation to automatically clear other owner FKs.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Update `generate_setters()` for owner columns

**Implementation notes:**
- When setting owner_player_id, automatically set owner_mobile_id/item_id/asset_id to None
- This enforces "exactly one owner" constraint at setter level
- Add validation call after setting
- Prevents accidentally creating invalid state

**Example generated setter:**
```python
def set_owner_player_id(self, value):
    """Set owner_player_id and clear other owner FKs"""
    self._data['owner_player_id'] = value
    # Clear other owner FKs to enforce exactly-one constraint
    self._data['owner_mobile_id'] = None
    self._data['owner_item_id'] = None
    self._data['owner_asset_id'] = None
    self._dirty = True
    # Validate after setting
    if value is not None:
        self.validate_owner()
```

#### Task 3.4: Add validation calls in from_thrift and save methods

Insert validation calls at key points to catch invalid states.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Update `generate_from_thrift_method()` and save method generation

**Implementation notes:**
- Call `validate_owner()` at end of from_thrift() for models with owner union
- Call `validate_owner()` in save() before executing INSERT/UPDATE
- This ensures invalid owner configurations never reach database

**Example in from_thrift:**
```python
@staticmethod
def from_thrift(thrift_obj, connection=None):
    mobile = Mobile()
    # ... set all fields ...

    # Handle Owner union
    if thrift_obj.owner.player_id:
        mobile.set_owner_player_id(thrift_obj.owner.player_id)
    elif thrift_obj.owner.mobile_id:
        mobile.set_owner_mobile_id(thrift_obj.owner.mobile_id)
    # ... other variants ...

    # Validate owner constraint
    mobile.validate_owner()

    return mobile
```

#### Task 3.5: Generate validation tests for Owner union

Add comprehensive test cases for owner validation.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Update `generate_tests()` to add owner validation tests

**Implementation notes:**
- Test setting multiple owners raises ValueError
- Test setting zero owners raises ValueError on save
- Test setting invalid owner type for table raises ValueError
- Test valid owner types work correctly
- Test from_thrift with Owner union
- Generate tests for each table that uses Owner union

**Example test:**
```python
def test_mobile_owner_validation_multiple_owners(self):
    """Test that setting multiple owners is rejected"""
    mobile = Mobile()
    mobile.set_name("TestMobile")
    mobile.set_owner_player_id(1)

    # Try to set second owner - should raise
    with self.assertRaises(ValueError) as ctx:
        mobile.set_owner_mobile_id(2)
    self.assertIn("exactly one owner", str(ctx.exception))

def test_mobile_owner_validation_invalid_type(self):
    """Test that invalid owner type is rejected"""
    mobile = Mobile()
    mobile.set_name("TestMobile")

    # Try to set invalid owner type for mobiles
    with self.assertRaises(ValueError) as ctx:
        mobile.set_owner_item_id(1)
    self.assertIn("cannot be owned by item", str(ctx.exception))

def test_mobile_owner_validation_valid_types(self):
    """Test that valid owner types work"""
    mobile = Mobile()
    mobile.set_name("TestMobile")

    # Valid: player owner
    mobile.set_owner_player_id(1)
    mobile.validate_owner()  # Should not raise

    # Valid: mobile owner (clears player)
    mobile.set_owner_mobile_id(2)
    mobile.validate_owner()  # Should not raise
    self.assertIsNone(mobile.get_owner_player_id())
```

#### Task 3.6: Regenerate and verify owner validation

Regenerate code and run validation tests.

**Files to modify:**
- N/A (regeneration only)

**Implementation notes:**
- Run: `cd /vagrant/gamedb/thrift/py/db_models && python3 generate_models.py`
- Verify models.py has `validate_owner()` methods
- Verify setters clear other owner FKs
- Run: `python3 tests.py`
- Verify all owner validation tests pass

**Verification:**
- Check generated models.py contains validate_owner() method for tables with owner union
- Confirm set_owner_* methods clear other owner FKs
- Run tests: all owner validation tests pass
- Manually test: creating object with multiple owners fails with clear error

---

### Step 4: Improve Config.py Maintainability

**Objective:** Make Thrift struct mappings easier to maintain, validate, and document

**Acceptance Criteria:**
- [ ] Config.py has clear documentation for each configuration section
- [ ] Config includes validation function to catch missing/incorrect mappings
- [ ] Clear instructions added for adding new table mappings
- [ ] Generator validates config at startup and reports specific errors
- [ ] Validation checks table names exist in database
- [ ] Validation checks Thrift struct names are valid

**Testing Requirements:**
- [ ] Test config validation catches missing table in TABLE_TO_THRIFT_MAPPING
- [ ] Test config validation catches invalid table name (not in database)
- [ ] Test config validation catches invalid Thrift struct name
- [ ] Verify all current mappings pass validation
- [ ] Generator fails fast with clear error if config is invalid

**Tasks:**

#### Task 4.1: Add comprehensive documentation to config.py

Improve documentation with examples and instructions.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generator/config.py` - Add detailed docstrings and comments

**Implementation notes:**
- Add module-level docstring explaining purpose
- Document each configuration dict with examples
- Add "Adding New Mappings" section with step-by-step instructions
- Document VALID_OWNER_TYPES with domain rules
- Add examples of valid vs invalid configurations

**Documentation to add:**
```python
"""
Configuration for db_models code generator.

This module defines mappings between database tables and Thrift structs,
union field configurations, and validation rules for Owner unions.

ADDING NEW TABLE MAPPINGS:
1. Add entry to TABLE_TO_THRIFT_MAPPING: {'table_name': 'ThriftStructName'}
2. If table uses Owner union, add valid owner types to VALID_OWNER_TYPES
3. If table has attribute map, add to THRIFT_CONVERSION_CONFIG
4. Run generator and verify no validation errors

EXAMPLE:
    # Database table: 'vehicles' with Thrift struct 'Vehicle'
    TABLE_TO_THRIFT_MAPPING = {
        ...
        'vehicles': 'Vehicle',
    }

    # Vehicles can be owned by player or mobile only
    VALID_OWNER_TYPES = {
        ...
        'vehicles': ['player', 'mobile'],
    }
"""
```

#### Task 4.2: Create config validation function

Add function to validate config correctness.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generator/config.py` - Add `validate_config()` function

**Implementation notes:**
- Check all table names in TABLE_TO_THRIFT_MAPPING exist in database
- Check all Thrift struct names are valid (can be imported from game.ttypes)
- Check VALID_OWNER_TYPES only references tables in TABLE_TO_THRIFT_MAPPING
- Return list of validation errors with specific messages

**Validation function:**
```python
def validate_config(db_tables: List[str]) -> List[str]:
    """
    Validate configuration against database schema.

    Args:
        db_tables: List of table names from database

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check table names exist
    for table_name in TABLE_TO_THRIFT_MAPPING.keys():
        if table_name not in db_tables:
            errors.append(f"Table '{table_name}' in TABLE_TO_THRIFT_MAPPING not found in database")

    # Check Thrift struct names are valid
    try:
        from game import ttypes
        for table_name, struct_name in TABLE_TO_THRIFT_MAPPING.items():
            if not hasattr(ttypes, struct_name):
                errors.append(f"Thrift struct '{struct_name}' for table '{table_name}' not found in game.ttypes")
    except ImportError:
        errors.append("Cannot import game.ttypes - ensure Thrift code is generated")

    # Check VALID_OWNER_TYPES references valid tables
    for table_name in VALID_OWNER_TYPES.keys():
        if table_name not in TABLE_TO_THRIFT_MAPPING:
            errors.append(f"Table '{table_name}' in VALID_OWNER_TYPES not in TABLE_TO_THRIFT_MAPPING")

    return errors
```

#### Task 4.3: Add config validation to generator startup

Call validation at generator startup and fail fast if invalid.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add validation call in `main()`

**Implementation notes:**
- After connecting to database and getting table list, validate config
- If validation errors found, print them and exit with error code
- This prevents generating broken code from misconfigured mappings

**Validation call in main():**
```python
def main():
    # ... database connection ...

    # Get all tables from database
    tables = get_all_tables(connection)
    table_names = [t['name'] for t in tables]

    # Validate configuration
    print("Validating configuration...")
    errors = validate_config(table_names)
    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("Configuration valid")

    # ... continue with generation ...
```

#### Task 4.4: Add validation tests

Create tests for config validation logic.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generator/config.py` - Add test functions at bottom (or separate test file)

**Implementation notes:**
- Test validate_config catches missing tables
- Test validate_config catches invalid Thrift structs
- Test validate_config accepts valid configuration
- Can use doctest or simple assert statements

**Example tests:**
```python
def test_validate_config():
    """Test config validation catches errors"""
    # Valid config
    errors = validate_config(['players', 'mobiles', 'items', 'inventories'])
    assert len(errors) == 0, f"Valid config should have no errors: {errors}"

    # Missing table
    errors = validate_config(['players'])  # Missing mobiles, items, etc
    assert len(errors) > 0, "Should catch missing tables"
    assert any('not found in database' in e for e in errors)

    print("Config validation tests passed")

if __name__ == '__main__':
    test_validate_config()
```

#### Task 4.5: Regenerate and verify config validation

Regenerate and test config validation works.

**Files to modify:**
- N/A (regeneration only)

**Implementation notes:**
- Run: `cd /vagrant/gamedb/thrift/py/db_models && python3 generate_models.py`
- Should see "Validating configuration..." and "Configuration valid" messages
- Temporarily break config (add invalid table name) and verify generator catches it
- Restore valid config

**Verification:**
- Generator validates config at startup
- Invalid config causes generator to exit with clear error message
- Valid config allows generation to proceed
- All existing table mappings are validated successfully

---

### Step 5: Add Missing Test Coverage

**Objective:** Generate comprehensive tests for Thrift conversion, union handling, and relationship constraints

**Acceptance Criteria:**
- [ ] Tests generated for from_thrift() methods (all models)
- [ ] Tests generated for into_thrift() methods (all models)
- [ ] Tests generated for Owner union conversion (all variants: player, mobile, item, asset)
- [ ] Tests generated for AttributeValue union conversion (all variants: bool, double, vector3, asset)
- [ ] Tests generated for 1-to-1 constraint enforcement
- [ ] Tests verify round-trip conversion (object → Thrift → object)
- [ ] All generated tests pass

**Testing Requirements:**
- [ ] Run full test suite: `python3 tests.py`
- [ ] Verify all new test scenarios execute
- [ ] All tests pass (no failures)
- [ ] Test output shows coverage of new scenarios

**Tasks:**

#### Task 5.1: Generate from_thrift/into_thrift round-trip tests

Add test generation for Thrift conversion methods.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Update `generate_tests()` to add conversion tests

**Implementation notes:**
- For each model with Thrift mapping, generate round-trip test
- Test creates object, populates fields, converts to Thrift, converts back, verifies equality
- Test all field types (string, int, bool, datetime, etc.)
- Test null/optional fields

**Example generated test:**
```python
def test_player_thrift_conversion_round_trip(self):
    """Test Player from_thrift/into_thrift round-trip"""
    # Create Thrift object
    from game.ttypes import Player as ThriftPlayer
    thrift_player = ThriftPlayer()
    thrift_player.id = 123
    thrift_player.name = "TestPlayer"
    thrift_player.email = "test@example.com"

    # Convert to model
    player = Player.from_thrift(thrift_player)
    self.assertEqual(player.get_id(), 123)
    self.assertEqual(player.get_name(), "TestPlayer")
    self.assertEqual(player.get_email(), "test@example.com")

    # Convert back to Thrift
    thrift_player_2 = player.into_thrift()
    self.assertEqual(thrift_player_2.id, 123)
    self.assertEqual(thrift_player_2.name, "TestPlayer")
    self.assertEqual(thrift_player_2.email, "test@example.com")
```

#### Task 5.2: Generate Owner union conversion tests

Add test generation for Owner union variants.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add Owner union test generation

**Implementation notes:**
- For models with owner union (mobiles, items, inventories), test each variant
- Test player owner: creates Owner union with player_id set
- Test mobile owner: creates Owner union with mobile_id set
- Test item/asset owners where valid
- Verify from_thrift sets correct FK column
- Verify into_thrift creates correct Owner union variant

**Example generated test:**
```python
def test_mobile_owner_union_player(self):
    """Test Mobile Owner union with player_id"""
    from game.ttypes import Mobile as ThriftMobile, Owner

    # Create Thrift Mobile with player owner
    thrift_mobile = ThriftMobile()
    thrift_mobile.id = 456
    thrift_mobile.name = "PlayerAvatar"
    thrift_mobile.owner = Owner(player_id=123)

    # Convert to model
    mobile = Mobile.from_thrift(thrift_mobile)
    self.assertEqual(mobile.get_owner_player_id(), 123)
    self.assertIsNone(mobile.get_owner_mobile_id())
    self.assertIsNone(mobile.get_owner_item_id())
    self.assertIsNone(mobile.get_owner_asset_id())

    # Convert back to Thrift
    thrift_mobile_2 = mobile.into_thrift()
    self.assertEqual(thrift_mobile_2.owner.player_id, 123)
    self.assertIsNone(thrift_mobile_2.owner.mobile_id)

def test_mobile_owner_union_mobile(self):
    """Test Mobile Owner union with mobile_id (minion)"""
    from game.ttypes import Mobile as ThriftMobile, Owner

    # Create Thrift Mobile with mobile owner
    thrift_mobile = ThriftMobile()
    thrift_mobile.id = 789
    thrift_mobile.name = "Minion"
    thrift_mobile.owner = Owner(mobile_id=456)

    # Convert to model
    mobile = Mobile.from_thrift(thrift_mobile)
    self.assertIsNone(mobile.get_owner_player_id())
    self.assertEqual(mobile.get_owner_mobile_id(), 456)

    # Convert back to Thrift
    thrift_mobile_2 = mobile.into_thrift()
    self.assertEqual(thrift_mobile_2.owner.mobile_id, 456)
```

#### Task 5.3: Generate AttributeValue union conversion tests

Add test generation for AttributeValue union variants.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add AttributeValue union test generation

**Implementation notes:**
- For Attribute model, test each AttributeValue variant
- Test bool value: creates AttributeValue with bool set
- Test double value: creates AttributeValue with double set (including 0.0, negative)
- Test vector3 value: creates AttributeValue with x/y/z set
- Test asset value: creates AttributeValue with asset_id set
- Verify priority-based detection works correctly

**Example generated test:**
```python
def test_attribute_value_union_bool(self):
    """Test Attribute AttributeValue union with bool"""
    from game.ttypes import Attribute as ThriftAttribute, AttributeValue

    # Create Thrift Attribute with bool value
    thrift_attr = ThriftAttribute()
    thrift_attr.id = 1
    thrift_attr.attribute_type = 1  # Some type enum
    thrift_attr.value = AttributeValue(bool_value=True)

    # Convert to model
    attr = Attribute.from_thrift(thrift_attr)
    self.assertEqual(attr.get_bool_value(), True)
    self.assertIsNone(attr.get_double_value())

    # Convert back to Thrift
    thrift_attr_2 = attr.into_thrift()
    self.assertTrue(thrift_attr_2.value.bool_value)

def test_attribute_value_union_vector3(self):
    """Test Attribute AttributeValue union with Vector3"""
    from game.ttypes import Attribute as ThriftAttribute, AttributeValue, Vector3

    # Create Thrift Attribute with Vector3 value
    thrift_attr = ThriftAttribute()
    thrift_attr.id = 2
    thrift_attr.attribute_type = 2
    thrift_attr.value = AttributeValue(vector3_value=Vector3(x=1.0, y=2.0, z=3.0))

    # Convert to model
    attr = Attribute.from_thrift(thrift_attr)
    self.assertEqual(attr.get_vector3_x(), 1.0)
    self.assertEqual(attr.get_vector3_y(), 2.0)
    self.assertEqual(attr.get_vector3_z(), 3.0)

    # Convert back to Thrift
    thrift_attr_2 = attr.into_thrift()
    self.assertEqual(thrift_attr_2.value.vector3_value.x, 1.0)
    self.assertEqual(thrift_attr_2.value.vector3_value.y, 2.0)
    self.assertEqual(thrift_attr_2.value.vector3_value.z, 3.0)
```

#### Task 5.4: Generate 1-to-1 constraint enforcement tests

Add tests that verify 1-to-1 relationships are enforced.

**Files to modify:**
- `/vagrant/gamedb/thrift/py/db_models/generate_models.py` - Add 1-to-1 constraint tests

**Implementation notes:**
- Test Player can only have one Mobile (from Step 2)
- Test calling from_thrift multiple times updates existing mobile, doesn't create duplicates
- Test set_mobile replaces existing mobile reference
- Could extend to test database constraint if added later

**Example generated test:**
```python
def test_player_mobile_no_duplicates_from_thrift(self):
    """Test that calling from_thrift multiple times doesn't create duplicate mobiles"""
    from game.ttypes import Player as ThriftPlayer, Mobile as ThriftMobile

    conn = self._create_connection()

    # Create player
    player = Player()
    player.set_name("TestPlayer")
    player.save(conn)
    player_id = player.get_id()

    # Create initial mobile via from_thrift
    thrift_player = ThriftPlayer()
    thrift_player.id = player_id
    thrift_player.name = "TestPlayer"
    thrift_player.mobile = ThriftMobile(id=None, name="Mobile1")

    player_1 = Player.from_thrift(thrift_player)
    player_1.save(conn, cascade=True)

    # Get mobile count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mobiles WHERE owner_player_id = %s", (player_id,))
    count_1 = cursor.fetchone()[0]
    self.assertEqual(count_1, 1, "Should have exactly 1 mobile")

    # Update via from_thrift again
    thrift_player.mobile = ThriftMobile(id=player_1.get_mobile().get_id(), name="Mobile1Updated")
    player_2 = Player.from_thrift(thrift_player)
    player_2.save(conn, cascade=True)

    # Verify still only 1 mobile
    cursor.execute("SELECT COUNT(*) FROM mobiles WHERE owner_player_id = %s", (player_id,))
    count_2 = cursor.fetchone()[0]
    self.assertEqual(count_2, 1, "Should still have exactly 1 mobile (updated, not duplicated)")

    cursor.close()
    conn.close()
```

#### Task 5.5: Regenerate with comprehensive test coverage

Regenerate code with all new tests.

**Files to modify:**
- N/A (regeneration only)

**Implementation notes:**
- Run: `cd /vagrant/gamedb/thrift/py/db_models && python3 generate_models.py`
- Verify tests.py has new test methods
- Should see tests for: from_thrift, into_thrift, Owner union variants, AttributeValue variants, 1-to-1 constraints

**Verification:**
- Check generated tests.py contains new test methods
- Estimated test count increase: 20-30 new tests added
- Verify test names clearly describe what they test

#### Task 5.6: Run full test suite and verify all pass

Run complete test suite and fix any failures.

**Files to modify:**
- May need to fix generator if tests reveal issues

**Implementation notes:**
- Run: `cd /vagrant/gamedb/thrift/py/db_models && python3 tests.py`
- All tests should pass
- If any failures, investigate and fix generator
- May need to iterate: fix generator → regenerate → retest

**Verification:**
- Run full test suite: `python3 tests.py`
- All tests pass (100% success rate)
- No import errors, no assertion failures
- Test output shows execution of all new test scenarios
- Verify specific scenarios: Owner union variants, AttributeValue variants, 1-to-1 relationships, round-trip conversions

---

## Testing Strategy

### Unit Tests
> Use testing framework and conventions from `./tasks/env.md`

All tests are automatically generated in `tests.py` by the generator. Each step adds new test scenarios.

**Test execution:**
```bash
cd /vagrant/gamedb/thrift/py/db_models
python3 tests.py
```

**Coverage:**
- Step 1: Import path fixes (tests can run)
- Step 2: 1-to-1 relationship methods and constraints
- Step 3: Owner union validation (all rules)
- Step 4: Config validation
- Step 5: Thrift conversion round-trips, union variants

**Test naming convention:** `test_<model>_<scenario>` (e.g., `test_player_mobile_one_to_one`)

### Integration Tests

No separate integration tests needed for this refactor. The generated tests cover integration between:
- Models and database (CRUD operations)
- Models and Thrift (conversion methods)
- Validation and setters (Owner union)

### Manual Testing

After all steps complete, manually verify:
- [ ] Run generator: `python3 generate_models.py` completes without errors
- [ ] Run tests: `python3 tests.py` shows all tests passing
- [ ] Check generated code quality: review models.py for proper formatting
- [ ] Verify no PYTHONPATH workaround needed

## Edge Cases & Error Handling

### Edge Cases

- **Case 1: Player with no mobile** - `player.get_mobile()` returns None (not error)
- **Case 2: Mobile with mobile owner (minion)** - Owner union validation allows mobile_id for mobiles table
- **Case 3: Attribute with 0.0 double value** - Should be detected as double type, not bool (priority order)
- **Case 4: Thrift object with missing optional field** - from_thrift() handles None gracefully
- **Case 5: Round-trip with embedded null mobile** - into_thrift() handles None mobile, from_thrift() doesn't create mobile

### Error Scenarios

- **Error 1: Multiple owner FKs set** - Owner validation raises ValueError with clear message listing which owners are set
- **Error 2: Invalid owner type for table** - Validation raises ValueError explaining which types are valid for this table
- **Error 3: Config has invalid table name** - Generator exits at startup with specific error message
- **Error 4: Config has invalid Thrift struct** - Generator exits at startup with import error message
- **Error 5: from_thrift with malformed Owner union** - Validation catches and raises clear error

## Rollback Plan
> Use version control commands from `./tasks/env.md`

If issues arise during or after implementation:

**Step 1: Identify which step introduced the issue**
- Check git log to see recent commits
- Test each step's changes independently if needed

**Step 2: Revert generator changes**
```bash
cd /vagrant/gamedb/thrift/py/db_models
# Revert specific file(s) that were modified
git checkout HEAD~1 generate_models.py
# Or revert entire directory
git checkout HEAD~1 .
```

**Step 3: Regenerate with reverted generator**
```bash
python3 generate_models.py
```

**Step 4: Verify tests pass with reverted code**
```bash
python3 tests.py
```

**Alternative: Revert to commit before refactor**
```bash
cd /vagrant
git log --oneline  # Find commit hash before refactor started
git checkout <commit-hash>
```

**Note:** Since generated files (models.py, tests.py) should not be committed separately from generator changes, reverting generator commits should be sufficient. If generated files were committed separately, revert both generator and generated files together.

## Success Criteria

This refactor is complete and successful when:

- [ ] Tests run without PYTHONPATH workaround (`python3 tests.py` works)
- [ ] All generated tests pass (100% success rate)
- [ ] Player has `get_mobile()` method (singular, not plural)
- [ ] Player-Mobile 1-to-1 relationship enforced (no duplicates)
- [ ] Owner union validation prevents invalid configurations
- [ ] Config.py has comprehensive documentation
- [ ] Generator validates config at startup
- [ ] Tests cover Thrift conversion round-trips
- [ ] Tests cover all Owner union variants
- [ ] Tests cover all AttributeValue union variants
- [ ] Tests verify 1-to-1 constraints
- [ ] No regressions in existing functionality (all old tests still pass)
- [ ] Generated code is clean and well-formatted
- [ ] Generator runs without errors or warnings

## Notes for Implementation

### Patterns to Follow

**Generator structure:**
- Main orchestration: `generate_models.py:main()`
- Utility functions: `generator/*.py` modules
- Templates: `templates/*.tmpl` Jinja2 templates
- Follow existing pattern: modify generator → regenerate → test

**Code generation patterns:**
- See how `generate_from_thrift_method()` builds method code
- See how `generate_tests()` creates test cases
- Use string building or Jinja2 templates consistently
- Follow Python code style from `/vagrant/CLAUDE.md`

**Test generation patterns:**
- See existing relationship tests in generated `tests.py`
- Follow unittest TestCase structure
- Use descriptive test method names
- Include docstrings explaining what is tested

### Common Pitfalls

**Pitfall 1: Editing generated files directly**
- **Problem:** Changes will be lost on next generation
- **Solution:** Always modify the generator, never edit models.py or tests.py directly
- **How to avoid:** Add reminder comments in generated file headers

**Pitfall 2: Forgetting to regenerate after generator changes**
- **Problem:** Testing old generated code, changes not reflected
- **Solution:** Always run `python3 generate_models.py` after modifying generator
- **How to avoid:** Include regeneration step in each task

**Pitfall 3: Breaking existing tests while adding new ones**
- **Problem:** New generator logic breaks old functionality
- **Solution:** Run tests after each task, fix failures immediately
- **How to avoid:** Run `python3 tests.py` frequently during development

**Pitfall 4: Validation logic too strict or too permissive**
- **Problem:** False positives (rejects valid data) or false negatives (allows invalid data)
- **Solution:** Test both valid and invalid cases thoroughly
- **How to avoid:** Generate comprehensive validation tests in Step 3

**Pitfall 5: Import path fix breaks when run from different directory**
- **Problem:** Using relative paths that only work from specific directory
- **Solution:** Use absolute path for sys.path manipulation
- **How to avoid:** Test running tests from different working directories

**Pitfall 6: Not handling None/null values in Thrift conversion**
- **Problem:** from_thrift crashes on None fields
- **Solution:** Always check if Thrift field is set before accessing
- **How to avoid:** Test round-trips with optional fields unset

### Questions & Clarifications

**Assumption 1:** Thrift code is already generated (game.thrift → gen-py/)
- If not, run: `cd /vagrant/gamedb/thrift && thrift --gen py game.thrift`

**Assumption 2:** MySQL database 'gamedb' exists and has current schema
- Tests create their own test databases, but generator needs to introspect production schema

**Assumption 3:** No concurrent modification of generated files
- Generator overwrites models.py and tests.py completely
- Don't edit these files while generator is running

**Assumption 4:** 1-to-1 relationship detection based on Thrift field name singularity
- May need to parse game.thrift or use naming heuristics
- If unclear, ask user for clarification on detection strategy

**Assumption 5:** Owner union validation errors should be raised immediately
- Alternative would be to collect errors and report all at once
- Current approach: fail fast on first validation error
