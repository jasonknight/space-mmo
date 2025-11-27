# PRD: Thrift-Model Bidirectional Conversion

## 1. Introduction/Overview

This feature adds bidirectional conversion methods (`into_thrift()` and `from_thrift()`) to auto-generated database Model classes. These methods enable seamless conversion between database Models and Thrift objects, separating the storage layer (optimized for persistence) from the transport layer (optimized for network communication).

**Problem Statement**: The game system uses Thrift as the source of truth for domain objects. Communication between client↔server and server↔server uses Thrift for serialization. However, the database schema is shaped to efficiently store these Thrift objects with normalized relationships. Currently, there's no clean way to convert between the database representation (Models) and the network representation (Thrift objects), forcing developers to manually handle conversions and relationship loading.

**Goal**: Provide automatic, type-safe conversion methods that handle:
- Converting Thrift objects to Model instances for database persistence
- Converting Model instances (with all relationships loaded) to Thrift objects for network transmission
- Complex field mappings (unions, flattened structures, pivot tables)
- Recursive relationship loading to ensure complete object graphs

## 2. Goals

1. **Automatic Code Generation**: Modify `generate_models.py` to emit `into_thrift()` and `from_thrift()` methods for all Models that have corresponding Thrift structs
2. **Zero Database Queries in `from_thrift()`**: Pure data conversion from Thrift → Model attributes with no side effects
3. **Complete Relationship Loading in `into_thrift()`**: Recursively load and convert all relationships when preparing objects for network transmission
4. **Fluent Interface for `from_thrift()`**: Return `self` to enable method chaining (e.g., `Model().from_thrift(obj).save()`)
5. **Consistent Error Handling**: Use existing `GameResult` pattern for reporting conversion errors
6. **Handle Complex Mappings**: Correctly convert Owner unions, AttributeValue unions, flattened structures, and pivot table relationships

## 3. User Stories

### US1: Create New Record from Thrift
**As a** service developer
**I want to** receive a Thrift object from the network and save it to the database
**So that** I can persist client requests without manual field mapping

**Example**:
```python
# Receive Thrift object from network
thrift_player = Player(
    id=None,  # None means new record
    full_name="Jane Doe",
    what_we_call_you="Jane",
    security_token="hashed_token",
    over_13=True,
    year_of_birth=1990,
    email="jane@example.com",
)

# Convert and save in one fluent chain
results = PlayerModel().from_thrift(thrift_player).save()
```

### US2: Update Existing Record from Thrift
**As a** service developer
**I want to** receive a Thrift object with an ID and update the corresponding database record
**So that** I can persist client updates without checking if the record exists

**Example**:
```python
# Receive Thrift object with existing ID
thrift_item = Item(
    id=42,  # Existing record
    internal_name="iron_ore",
    attributes={...},
    max_stack_size=1000,
    item_type=ItemType.RAWMATERIAL,
)

# Convert and save (will UPDATE because id is not None)
results = ItemModel().from_thrift(thrift_item).save()
```

### US3: Send Complete Object to Client
**As a** service developer
**I want to** load a Model from the database and convert it to a complete Thrift object
**So that** I can send the full object graph (with all relationships) to the client

**Example**:
```python
# Load from database
player_model = PlayerModel.find(player_id)

# Convert to Thrift with all relationships loaded
game_results, thrift_player = player_model.into_thrift()

if is_ok(game_results):
    # thrift_player includes the player's mobile, inventory, etc.
    send_to_client(thrift_player)
```

### US4: Handle Complex Attribute Conversions
**As a** service developer
**I want to** convert between flattened database columns and Thrift union types
**So that** I don't have to manually pack/unpack AttributeValue unions and Owner unions

**Example**:
```python
# Database has: vector3_x=1.0, vector3_y=2.0, vector3_z=3.0
# Model.into_thrift() produces:
# Attribute(value=AttributeValue(vector3=ItemVector3(x=1.0, y=2.0, z=3.0)))

# Database has: owner_player_id=123, owner_mobile_id=NULL, ...
# Model.into_thrift() produces:
# Mobile(owner=Owner(player_id=123))
```

## 4. Functional Requirements

### FR1: Code Generation in `generate_models.py`
**Requirement**: Modify the model generator to emit `into_thrift()` and `from_thrift()` methods for all Model classes that have corresponding Thrift struct definitions.

**Details**:
- Detect which database tables align with Thrift structs by naming convention (e.g., `items` table → `Item` Thrift struct)
- Generate methods only for Models with Thrift counterparts
- Add necessary imports for Thrift types (`from game.ttypes import ...`)

### FR2: `from_thrift()` Method - Thrift to Model Conversion
**Requirement**: Generate a `from_thrift(self, thrift_obj: ThriftType) -> Self` method that populates the Model's internal attributes from a Thrift object.

**Details**:
- Takes a single Thrift object as input
- Maps Thrift fields to Model attributes (handles naming differences, structural differences)
- Sets `self._data` dictionary with converted values
- Handles `None` values for optional fields
- Does **NOT** execute any database queries
- Returns `self` to enable method chaining
- Marks the model as dirty if new data is set

**Special Conversions**:
- **Owner unions**: Convert `Owner(player_id=X)` → set `owner_player_id=X`, other owner fields to `None`
- **AttributeValue unions**: Convert `AttributeValue(vector3=ItemVector3(x=1, y=2, z=3))` → set `vector3_x=1, vector3_y=2, vector3_z=3`
- **Nested Thrift objects**: Convert nested objects recursively (e.g., `Player.mobile` → call `MobileModel().from_thrift(thrift_player.mobile)`)
- **Attribute maps**: Convert `map<AttributeType, Attribute>` to normalized pivot table records (handle via `set_attributes()` method)

**ID Field Handling**:
- If `thrift_obj.id` is `None`: Model will be marked for creation (INSERT)
- If `thrift_obj.id` is set: Model will be marked for update (UPDATE)

### FR3: `into_thrift()` Method - Model to Thrift Conversion
**Requirement**: Generate an `into_thrift(self) -> Tuple[list[GameResult], Optional[ThriftType]]` method that converts the Model to a complete Thrift object with all relationships loaded.

**Details**:
- Reads current Model state from `self._data`
- Loads all related Models from database recursively
- Converts each related Model by calling its `into_thrift()` method
- Returns tuple of `(GameResults, Thrift object or None)`
- Returns `(FAILURE GameResult, None)` if conversion fails

**Recursive Loading**:
- **Belongs-to relationships**: Load foreign key references (e.g., `ItemModel` loads its `ItemBlueprintModel`)
- **Has-many relationships**: Load collections (e.g., `PlayerModel` loads all its `AttributeOwner` records and the associated `Attribute` records)
- **Pivot table relationships**: Load through join tables (e.g., load `Mobile.attributes` via `attribute_owners` pivot)

**Special Conversions**:
- **Owner fields to Owner union**: If `owner_player_id=X`, create `Owner(player_id=X)`
- **Flattened columns to AttributeValue union**: If `vector3_x=1, vector3_y=2, vector3_z=3`, create `AttributeValue(vector3=ItemVector3(x=1, y=2, z=3))`
- **Attribute pivot to map**: Convert pivot table records to `map<AttributeType, Attribute>`

### FR4: Model-Thrift Alignment Detection
**Requirement**: Automatically detect which Models have corresponding Thrift types based on naming conventions.

**Mapping Rules**:
- `items` table → `Item` Thrift struct
- `players` table → `Player` Thrift struct
- `mobiles` table → `Mobile` Thrift struct
- `inventories` table → `Inventory` Thrift struct
- `attributes` table → `Attribute` Thrift struct
- `item_blueprints` table → `ItemBlueprint` Thrift struct
- Pivot tables (`attribute_owners`, `inventory_owners`) do NOT have direct Thrift equivalents

### FR5: Field Mapping Configuration
**Requirement**: Handle differences between database schema and Thrift definitions.

**Known Mappings**:
1. **Owner Union Pattern**:
   - DB: `owner_player_id`, `owner_mobile_id`, `owner_item_id`, `owner_asset_id` (exactly one is set, others NULL)
   - Thrift: `Owner` union with one field set

2. **AttributeValue Union Pattern**:
   - DB: `bool_value`, `double_value`, `vector3_x`, `vector3_y`, `vector3_z`, `asset_id` (exactly one group is set)
   - Thrift: `AttributeValue` union with one field set

3. **Attribute Map Pattern**:
   - DB: Normalized tables (`attributes`, `attribute_owners` pivot)
   - Thrift: `map<AttributeType, Attribute>`

4. **Computed Fields**:
   - `over_13` is computed from `year_of_birth` (already handled by existing code)

5. **BackingTable Field**:
   - Thrift has `backing_table` field; might be removed in future (include for now)

### FR6: Error Handling
**Requirement**: Use consistent error handling patterns with `GameResult`.

**Return Values**:
- `into_thrift()`: Returns `(list[GameResult], Optional[ThriftType])`
  - On success: `([GameResult(status=SUCCESS, message="...")], thrift_obj)`
  - On failure: `([GameResult(status=FAILURE, error_code=..., message="...")], None)`

**Failure Scenarios**:
- Database query fails when loading relationships
- Required relationship is missing
- Data type conversion fails
- Invalid data in database (should be rare due to constraints)

### FR7: Integration with Existing Save/Load Methods
**Requirement**: Ensure `from_thrift()` and `into_thrift()` work seamlessly with existing Model methods.

**Integration Points**:
- `from_thrift()` populates `self._data`, then user calls `.save()` which uses existing `create()`/`update()` logic
- `into_thrift()` uses existing relationship loading methods (`get_*()`, `find()`)
- Existing transaction management in `save()` handles all database writes
- No changes needed to `BaseModel` class

## 5. Non-Goals (Out of Scope)

1. **Modify BaseModel**: Keep `BaseModel` generic; do not add abstract methods for Thrift conversion
2. **Bidirectional sync**: Not building real-time sync; conversion is explicit and one-way at a time
3. **Partial object loading**: `into_thrift()` always loads all relationships (no lazy/selective loading)
4. **Validation beyond Thrift**: Thrift enforces structural validation; no additional business logic validation in conversion methods
5. **Backward compatibility**: The old `dbinc/` directory will be deleted; no migration path needed
6. **Optimistic concurrency**: Not handling version conflicts or ETags
7. **Batch conversion utilities**: Only single-object conversion; batch operations are out of scope

## 6. Design Considerations

### Thrift Import Location
The generator will need to import from `game.ttypes`:
```python
from game.ttypes import (
    Player,
    Item,
    Mobile,
    Attribute,
    AttributeValue,
    AttributeType,
    ItemVector3,
    Owner,
    # ... other types as needed
)
```

### Owner Union Handling Strategy
Given the complexity mentioned by the user, the implementation should:
1. **In `from_thrift()`**: Check which field is set in the `Owner` union, set only that `owner_*_id` field in the database
2. **In `into_thrift()`**: Check which `owner_*_id` field is non-NULL, create `Owner` union with that field set
3. Include clear inline comments and examples in generated code
4. Present Owner union conversion code to user for review before finalizing

### Recursive Loading Safety
To prevent infinite loops in circular relationships:
- Track visited model IDs during recursion
- Stop at a reasonable depth (e.g., 10 levels)
- Log warning if maximum depth reached

### Performance Considerations
- `into_thrift()` may trigger many queries for deep object graphs
- Use existing caching mechanisms in Model classes (`_*_cache` attributes)
- Consider adding query counting in test mode to detect N+1 problems

## 7. Technical Considerations

### Dependencies
- `game.ttypes` from the generated Thrift code (`gamedb/thrift/gen-py/`)
- Existing `mysql.connector` for database queries
- Existing `GameResult`, `StatusType`, `GameError` enums from Thrift

### Code Generation Strategy
1. Detect Models with Thrift counterparts (table name → Thrift struct name mapping)
2. For each Model, generate:
   - `from_thrift()` method with field mappings
   - `into_thrift()` method with relationship loading
   - Helper methods for complex conversions (Owner, AttributeValue)
3. Generate type hints for better IDE support
4. Include docstrings explaining the conversion process

### Testing Strategy
- Modify existing test generator to create tests for Thrift conversion
- Test cases should cover:
  - Create flow: `from_thrift()` → `save()` → `load()` → `into_thrift()`
  - Update flow: `from_thrift()` (with id) → `save()` → verify update
  - Relationship loading: Verify all nested objects are loaded
  - Owner union conversions
  - AttributeValue union conversions
  - Error cases (missing relationships, invalid data)

## 8. Success Metrics

1. **Code Coverage**: 100% of Models with Thrift counterparts have conversion methods generated
2. **Round-trip Accuracy**: `thrift_obj → from_thrift() → save() → load() → into_thrift()` produces equivalent object (within database precision limits)
3. **Test Pass Rate**: All generated tests for Thrift conversion pass
4. **Developer Efficiency**: Reduce Thrift↔Model conversion code from ~100 lines to 1-2 lines per operation
5. **Zero Manual Conversions**: Eliminate all manual field mapping in service layer code

## 9. Open Questions

1. **Owner Union Edge Cases**: What happens if multiple `owner_*_id` fields are non-NULL in the database (constraint violation)? Should we raise an error or pick the first non-NULL?

2. **AttributeValue Union Edge Cases**: Similar question for AttributeValue - what if both `double_value` and `vector3_x` are set? Should this be prevented at database level?

3. **Missing Relationships**: If `into_thrift()` tries to load a foreign key that points to a deleted record, should it:
   - Return FAILURE GameResult?
   - Continue with NULL for that field?
   - Raise an exception?

4. **Thrift Struct Discovery**: Should we parse `game.thrift` to automatically detect which structs exist, or hardcode the table→struct mapping in the generator?

5. **Pivot Table Conversion**: For `attribute_owners`, should `from_thrift()` create the pivot records immediately, or should the user call `save()` first, then add attributes separately?

6. **Partial Updates**: If a Thrift object has an ID but some fields are None/default, should we treat them as "unset" (don't update) or "set to NULL" (clear the field)?

7. **BackingTable Field**: Should we automatically set `backing_table` when calling `from_thrift()` based on which table the Model represents, or expect the Thrift object to have it set?

---

## Next Steps

After PRD approval:
1. Review and approve this PRD
2. Load `/vagrant/tasks.md` for task generation context
3. Generate detailed implementation tasks from this PRD
