# Tasks: Thrift-Model Bidirectional Conversion

Based on PRD: `prd-thrift-model-conversion.md`

## Relevant Files

- `gamedb/thrift/py/db_models/generate_models.py` - Modified model generator that emits Thrift conversion methods ✓
- `gamedb/thrift/py/db_models/templates/model_template.py.tmpl` - Modified template to include thrift_conversion_methods placeholder ✓
- `gamedb/thrift/py/db_models/models.py` - Auto-generated file containing all Model classes with from_thrift() and into_thrift() methods ✓
- `gamedb/thrift/py/db_models/THRIFT_CONVERSION.md` - Documentation for using Thrift conversion methods ✓
- `gamedb/thrift/py/db_models/tests.py` - Auto-generated test file (not yet updated with Thrift conversion tests)
- `gamedb/thrift/game.thrift` - Thrift schema definition (reference only, not modified)
- `gamedb/thrift/gen-py/game/ttypes.py` - Generated Thrift types (reference only, not modified)

### Notes

- The main work is in modifying `generate_models.py` to emit the new conversion methods
- After modifying the generator, run it to regenerate `models.py` and `tests.py`
- Tests are auto-generated alongside the models
- Use `py gamedb/thrift/py/db_models/tests.py` to run tests

## Tasks

- [x] 1.0 Analyze and Map Thrift Structs to Database Models
  - [x] 1.1 Create a `TABLE_TO_THRIFT_MAPPING` dictionary in `generate_models.py` that maps table names to Thrift struct names (e.g., `"items": "Item"`, `"players": "Player"`)
  - [x] 1.2 Add a helper function `get_thrift_struct_name(table_name: str) -> Optional[str]` that returns the Thrift struct name if one exists for the table
  - [x] 1.3 Identify and document pivot tables that do NOT have Thrift equivalents (e.g., `attribute_owners`, `inventory_owners`)
  - [x] 1.4 For each mapped table, document field differences in comments (e.g., Owner union fields, AttributeValue flattened fields, BackingTable enum)
  - [x] 1.5 Create a function `has_thrift_mapping(table_name: str) -> bool` to check if a table should have Thrift conversion methods

- [x] 2.0 Implement Field Mapping Utilities for Complex Types
  - [x] 2.1 Create `generate_owner_union_to_db_code(table_name: str, columns: List[Dict]) -> str` function that generates code to convert Owner union → database columns (checks which union field is set, sets corresponding `owner_*_id` column)
  - [x] 2.2 Create `generate_db_to_owner_union_code(table_name: str, columns: List[Dict]) -> str` function that generates code to convert database columns → Owner union (checks which `owner_*_id` is non-NULL, creates Owner with that field)
  - [x] 2.3 Create `generate_attribute_value_to_db_code() -> str` function that generates code to convert AttributeValue union → flattened columns (`vector3.x` → `vector3_x`, etc.)
  - [x] 2.4 Create `generate_db_to_attribute_value_code() -> str` function that generates code to convert flattened columns → AttributeValue union
  - [x] 2.5 Create `generate_attribute_map_to_pivot_code() -> str` function for converting `map<AttributeType, Attribute>` to pivot table records
  - [x] 2.6 Create `generate_pivot_to_attribute_map_code() -> str` function for loading pivot records and building the attribute map
  - [x] 2.7 Add helper function `needs_owner_conversion(columns: List[Dict]) -> bool` to detect if a table has owner union fields
  - [x] 2.8 Add helper function `needs_attribute_value_conversion(columns: List[Dict]) -> bool` to detect if a table stores AttributeValue data

- [x] 3.0 Generate from_thrift() Methods in Model Classes
  - [x] 3.1 Create `generate_from_thrift_method(table_name: str, class_name: str, columns: List[Dict], thrift_struct_name: str) -> str` function in `generate_models.py`
  - [x] 3.2 Generate method signature: `def from_thrift(self, thrift_obj: {ThriftStructName}) -> Self:`
  - [x] 3.3 Generate code to map simple fields (direct 1:1 mappings like `internal_name`, `email`, `max_stack_size`)
  - [x] 3.4 For tables with Owner fields, insert the Owner union → database conversion code using helper from 2.1
  - [x] 3.5 For Attribute table, insert AttributeValue union → flattened columns conversion code using helper from 2.3
  - [x] 3.6 Generate code to handle nested Thrift objects by recursively calling `from_thrift()` on related Models (e.g., `Player.mobile` → `MobileModel().from_thrift(thrift_obj.mobile)`)
  - [x] 3.7 Generate code to store the nested Model ID in the parent's foreign key field
  - [x] 3.8 Handle `map<AttributeType, Attribute>` by calling helper method to convert to pivot format (defer actual save to when user calls `.save()`)
  - [x] 3.9 Generate code to handle optional fields (check `if thrift_obj.field is not None` before setting)
  - [x] 3.10 Add `return self` at the end for fluent interface
  - [x] 3.11 Add necessary Thrift imports at the top of the generated models.py file (e.g., `from game.ttypes import Player, Item, Owner, AttributeValue, ...`)
  - [x] 3.12 Integrate `generate_from_thrift_method()` into the main model generation loop, only for tables with Thrift mappings

- [x] 4.0 Generate into_thrift() Methods in Model Classes
  - [x] 4.1 Create `generate_into_thrift_method(table_name: str, class_name: str, columns: List[Dict], relationships: Dict, thrift_struct_name: str) -> str` function
  - [x] 4.2 Generate method signature: `def into_thrift(self) -> Tuple[list[GameResult], Optional[{ThriftStructName}]]:`
  - [x] 4.3 Generate code to initialize empty `results: list[GameResult] = []` list
  - [x] 4.4 Generate code to map simple fields from `self._data` to Thrift object constructor parameters
  - [x] 4.5 For belongs-to relationships, generate code to load the related Model (using existing `get_*()` methods) and call its `into_thrift()` method recursively
  - [x] 4.6 Add error handling for relationship loading failures (append FAILURE GameResult and return early)
  - [x] 4.7 For has-many relationships, generate code to load the collection and convert each item by calling its `into_thrift()` method
  - [x] 4.8 For tables with `owner_*_id` columns, generate code using helper from 2.2 to build the Owner union
  - [x] 4.9 For Attribute table, generate code using helper from 2.4 to build AttributeValue union from flattened columns
  - [x] 4.10 For tables with attribute relationships via pivot, generate code using helper from 2.6 to build `map<AttributeType, Attribute>`
  - [x] 4.11 Generate code to construct the Thrift object with all converted fields
  - [x] 4.12 Generate code to return `(results + [GameResult(status=SUCCESS, message=...)], thrift_obj)` on success
  - [x] 4.13 Add try-except block to catch conversion errors and return `([GameResult(status=FAILURE, error_code=DB_QUERY_FAILED, message=...)], None)`
  - [x] 4.14 Integrate `generate_into_thrift_method()` into the main model generation loop

- [ ] 5.0 Add Thrift Conversion Tests to Test Generator
  - [ ] 5.1 Create `generate_from_thrift_new_record_test(model: Dict) -> str` function that generates a test for creating a new record (id=None) from Thrift
  - [ ] 5.2 Create `generate_from_thrift_existing_record_test(model: Dict) -> str` function that generates a test for updating an existing record (id set) from Thrift
  - [ ] 5.3 Create `generate_into_thrift_test(model: Dict) -> str` function that generates a test loading a Model and converting to Thrift with all relationships
  - [ ] 5.4 Create `generate_round_trip_test(model: Dict) -> str` function that tests: Thrift → from_thrift() → save() → load() → into_thrift() → compare
  - [ ] 5.5 Create `generate_owner_union_conversion_test(model: Dict) -> str` for models with Owner fields (test that Owner(player_id=X) correctly sets owner_player_id=X)
  - [ ] 5.6 Create `generate_attribute_value_conversion_test() -> str` for Attribute model (test that vector3, double, bool, asset conversions work)
  - [ ] 5.7 Create `generate_attribute_map_conversion_test() -> str` for models with attribute relationships (test that map<AttributeType, Attribute> loads correctly)
  - [ ] 5.8 Add a test class `TestThriftConversion` to the generated tests.py file
  - [ ] 5.9 Integrate all Thrift conversion test generation functions into `generate_tests()` function, only for models with Thrift mappings
  - [ ] 5.10 Ensure test data factories create valid Thrift objects for testing

- [ ] 6.0 Integration Testing and Documentation
  - [x] 6.1 Run `python3 gamedb/thrift/py/db_models/generate_models.py` to regenerate models.py with new conversion methods
  - [x] 6.2 Verify that models.py contains `from_thrift()` and `into_thrift()` methods for appropriate models
  - [ ] 6.3 Run `py gamedb/thrift/py/db_models/tests.py` to execute all auto-generated tests
  - [ ] 6.4 Fix any test failures by adjusting the generator code (iterate on tasks 2-5 as needed)
  - [ ] 6.5 Manually test round-trip conversion with a real Player object: create Thrift Player → from_thrift() → save() → load() → into_thrift() → verify fields match
  - [ ] 6.6 Manually test with an Item that has Attributes to verify pivot table conversion works
  - [ ] 6.7 Manually test with a Mobile that has an Owner union to verify Owner conversion works
  - [x] 6.8 Add inline code comments in generated methods explaining complex conversions (especially Owner and AttributeValue)
  - [ ] 6.9 Delete the old `gamedb/thrift/py/dbinc/` directory as it's now obsolete
  - [ ] 6.10 Update any service layer code that was using the old dbinc/ classes to use the new Model conversion methods
  - [ ] 6.11 Run full test suite (including service tests) to ensure nothing broke
  - [x] 6.12 Document the usage pattern in a README or inline docstrings (e.g., "To save a Thrift object: `Model().from_thrift(thrift_obj).save()`")
