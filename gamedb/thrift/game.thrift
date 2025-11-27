typedef i64 AssetId
typedef i64 ItemId
typedef i64 MobileId
typedef i64 PlayerId

//@mysql_table('players')
struct Player {
    1: optional PlayerId id;
    // Whatever the player's full legal name is
    2: string full_name;
    // The actual string we should use to refer to the player
    3: string what_we_call_you;
    // A hash of a security word
    4: string security_token;
    // Whether or not the player is over 13
    5: bool over_13;
    6: i64 year_of_birth;
    7: string email;
    8: optional Mobile mobile;
}
// The general item type is something like a parent item
// class, it gives some broad category to the item, is it 
// a consumable, virtual, weapon, These are special, globally
// interesting types for quick sorting
//@info store this as a string of the member, eg 'CONTAINER' or 'WEAPON'
enum ItemType {
    VIRTUAL = 1, // Items that never have a physical existence, like quest items.
    // To decide if someone has "done" part of a quest, we just add a Virtual item to
    // their inventory, and then we test their inventory for that item to verify
    // they've completed some stage of a quest etc... Far better than modifying the
    // player object with quest specific markers.
    CONTAINER = 2,
    WEAPON=3,
    RAWMATERIAL=4,
    REFINEDMATERIAL=5,
    BLUEPRINT=6, // only blueprint type items have an actual blueprint attached, though it
    // might seem like all of them could have them, in practice, only certain ones do. 
}

//@info store this as a string of the member, eg 'PLAYER' or 'NPC'
enum MobileType {
    PLAYER = 1,
    NPC = 2,
}

enum BackingTable {
    ATTRIBUTES = 1,
    ATTRIBUTE_OWNERS = 2,
    ITEMS = 3,
    MOBILE_ITEMS = 4,
    ITEM_BLUEPRINTS = 5,
    ITEM_BLUEPRINT_COMPONENTS = 6,
    MOBILE_ITEM_BLUEPRINTS = 7,
    MOBILE_ITEM_BLUEPRINT_COMPONENTS = 8,
    MOBILE_ITEM_ATTRIBUTES = 9,
    PLAYERS = 10,
    MOBILES = 11,
    INVENTORIES = 12,
    INVENTORY_ENTRIES = 13,
    INVENTORY_OWNERS = 14,
}

const map<BackingTable, string> TABLE2STR = {
    BackingTable.ATTRIBUTES: "attributes",
    BackingTable.ATTRIBUTE_OWNERS: "attribute_owners",
    BackingTable.ITEMS: "items",
    BackingTable.MOBILE_ITEMS: "mobile_items",
    BackingTable.ITEM_BLUEPRINTS: "item_blueprints",
    BackingTable.ITEM_BLUEPRINT_COMPONENTS: "item_blueprint_components",
    BackingTable.MOBILE_ITEM_BLUEPRINTS: "mobile_item_blueprints",
    BackingTable.MOBILE_ITEM_BLUEPRINT_COMPONENTS: "mobile_item_blueprint_components",
    BackingTable.MOBILE_ITEM_ATTRIBUTES: "mobile_item_attributes",
    BackingTable.PLAYERS: "players",
    BackingTable.MOBILES: "mobiles",
    BackingTable.INVENTORIES: "inventories",
    BackingTable.INVENTORY_ENTRIES: "inventory_entries",
    BackingTable.INVENTORY_OWNERS: "inventory_owners",
}

union Owner {
    1: MobileId mobile_id;
    2: ItemId item_id;
    3: AssetId asset_id;
    4: PlayerId player_id;
}

//@info store this as a string of the member, eg 'QUANTITY' or 'SIZE'
enum AttributeType {
    TRANSLATED_NAME = 1,
    TRANSLATED_SHORT_DESCRIPTION = 2,
    TRANSLATED_LONG_DESCRIPTION = 3,
    // Assets might have text/messages on them
    // for the player to inspect, if so, those will
    // need to be localized
    TRANSLATED_ASSET = 4,
    // Some assets can just be stored directly
    UNTRANSLATED_ASSET = 5,
    QUANTITY = 6,
    // Sometimes we have a big world to work with,
    // so that means we need to know where in our big world
    // the item is, so it can be in a Galazy, a Solar System,
    // A planet (global), or in a local space etc.
    // This allows us to aggressively cull items that cannot
    // possibly be anywhere near a play, and it also
    // allows us to report where in our big universe an item is
    GALACTIC_POSITION = 7,
    SOLAR_POSITION = 8,
    GLOBAL_POSITION = 9,
    LOCAL_POSITION = 10,
    SIZE = 11, // Vector3 where x,y,z = h,w,d
    ITEM=12, // for those items that are composed of other items
    PURITY=13,
    VOLUME=14, // how many mm3 is 1 unit
    // Character attributes for mobiles (and items that affect them)
    STRENGTH = 15, // How much a character can carry, physical power
    LUCK = 16, // Used for random chances like drop rates
    CONSTITUTION = 17, // Stamina for sprinting, carrying, physical endurance
    DEXTERITY = 18, // Weapon handling, engineering with fine equipment
    ARCANA = 19, // Discovery, item info, revealing secrets, blueprint study
    OPERATIONS = 20, // Repair, scanning, equipment use, ship weapons, mining
    BLUEPRINT_ITEM_ID = 21, // links this item to its blueprint item for manufacture.
}

//@info this is stored on the 'attributes' table as 'vector3_*', x, y, and z must be NOT NULL to be valid
struct ItemVector3 {
    1: double x;
    2: double y;
    3: double z;
}

//@info this is stored on the 'attributes' table flattened, so each member is a column, except for ItemVector3, see @info for ItemVector3
union AttributeValue {
    1: bool bool_value;
    2: double double_value;
    3: ItemVector3 vector3;
    // when an ITEM attribute, this will be the item id
    // when a translated name, this will be the translation id
    4: AssetId asset_id; 
 }

//@mysql_table('attributes')
//@info one-to-many relation through the attribute_owners table. the attribute_owners table is essential an unwrapped Owner.
struct Attribute {
    1: optional i64 id; // this member only matters for a materialized attribute of an owned item
    2: string internal_name;
    3: bool visible;
    4: AttributeValue value;
    5: AttributeType attribute_type;
    6: Owner owner;
}

//@mysql_table('items')
struct Item {
    1: optional i64 id;
    2: string internal_name; // used internally to talk about the item, but
    // not shown to users, as their names/descriptions must come for i18n translations
    3: map<AttributeType, Attribute> attributes;
    4: optional i64 max_stack_size;
    5: ItemType item_type;
    // Optional because not all items can be constructed by players
    6: optional ItemBlueprint blueprint;
    7: optional BackingTable backing_table;
}

//@mysql_table('mobile_items')
//@info this must be kept in sync with Item struct as any Item should be able to be copied into the table for MobileItem, but not the other way around.
struct MobileItem {
    // This struct is meant to mirror Item, except we have
    // some extra fields, but those need to be copied over
    // from the template
    1: optional ItemId id;
    2: ItemId item_id;
    3: MobileId mobile_id;
    4: string internal_name; // used internally to talk about the item, but
    // not shown to users, as their names/descriptions must come for i18n translations
    5: map<AttributeType, Attribute> attributes;
    6: optional i64 max_stack_size;
    7: ItemType item_type;
    // Optional because not all items can be constructed by players
    8: optional ItemBlueprint blueprint;
    9: optional BackingTable backing_table;
}

//@mysql_table('item_blueprint_components')
//@info also can be represented by 'mobile_item_blueprint_components' which is a copy.
struct ItemBlueprintComponent {
    // A value between 0.1 -> 1.0
    1: double ratio; // i.e. for every 1 unit of this item, how much of the target item do we get?
    2: ItemId item_id;
}

// An ItemBlueprint contains the item id and the amount of that item required
// to construct it, this is also used when recycling/breaking down an item
// into its base components
//@mysql_table('item_blueprints')
//@info also represented in 'mobile_item_blueprints'
struct ItemBlueprint {
    1: optional i64 id;
    2: map<ItemId, ItemBlueprintComponent> components;
    3: i64 bake_time_ms;
}

// Recursive tree structure for displaying blueprints
// Note: Thrift supports recursive structures without forward declarations
struct BlueprintTreeNode {
    1: Item item; // The item at this node
    2: optional ItemBlueprint blueprint; // Blueprint if this item has one
    3: list<BlueprintTreeNode> component_nodes; // Child nodes (recursive)
    4: list<double> component_ratios; // Ratios corresponding to component_nodes
    5: i64 total_bake_time_ms; // Sum of this blueprint's bake time + all component bake times
    6: bool max_depth_reached = false; // True if recursion stopped due to max depth
    7: bool cycle_detected = false; // True if a circular reference was detected
}

struct ItemDb {
    1: list<Item> items;
}

//@mysql_table('inventory_entries')
//@info mobile_item_id is optional becasue this may be an inventory owned by the game, in that case, we just reference the item_id, but once the item is moved into an inventory owned by a player's mobile, we need to copy over all the item data to the mobile_items and supporting tables to materialize an persistent version of the item in the game world.
struct InventoryEntry {
    1: ItemId item_id;
    2: double quantity;
    3: bool is_max_stacked = false;
    4: optional ItemId mobile_item_id;
}

//@mysql_table('inventories')
struct Inventory {
    1: optional i64 id;
    2: i64 max_entries;
    3: double max_volume;
    4: list<InventoryEntry> entries;
    5: double last_calculated_volume = 0.0;
    6: Owner owner;
}

enum StatusType {
    SUCCESS = 1,
    FAILURE = 2,
    SKIP = 3,
}

enum GameError {
    INV_MAX_ITEMS_REACHED = 1,
    INV_ALL_ENTRIES_MAX_STACKED = 2,
    INV_NEW_VOLUME_TOO_HIGH = 3,
    INV_CANNOT_ADD_ITEM = 4,
    INV_FAILED_TO_ADD = 5,
    INV_FAILED_TO_TRANSFER = 6,
    INV_COULD_NOT_FIND_ENTRY = 7,
    INV_NEW_QUANTITY_INVALID = 8,
    INV_FULL_CANNOT_SPLIT = 9,
    INV_ITEM_NOT_FOUND = 10,
    INV_INSUFFICIENT_QUANTITY = 11,
    INV_OPERATION_FAILED = 22,
    DB_CONNECTION_FAILED = 12,
    DB_TRANSACTION_FAILED = 13,
    DB_INSERT_FAILED = 14,
    DB_UPDATE_FAILED = 15,
    DB_DELETE_FAILED = 16,
    DB_QUERY_FAILED = 17,
    DB_RECORD_NOT_FOUND = 18,
    DB_INVALID_DATA = 19,
    DB_FOREIGN_KEY_VIOLATION = 20,
    DB_UNIQUE_CONSTRAINT_VIOLATION = 21,
}
struct GameResult {
    1: StatusType status;
    2: string message;
    3: optional GameError error_code;
}

const map<GameError, string> INVERR2STRING = {
    GameError.INV_MAX_ITEMS_REACHED: "item is not in inventory, and inventory has reached max items",
    GameError.INV_ALL_ENTRIES_MAX_STACKED: "item is in inventory, but all entries are max stacked",
    GameError.INV_NEW_VOLUME_TOO_HIGH: "the new_volume is too high",
    GameError.INV_CANNOT_ADD_ITEM: "cannot add this item to the inventory",
    GameError.INV_FAILED_TO_ADD: "failed to add to inventory",
    GameError.INV_FAILED_TO_TRANSFER: "failed to transfer",
    GameError.INV_COULD_NOT_FIND_ENTRY: "could not find entry",
    GameError.INV_NEW_QUANTITY_INVALID: "the new_quantity must be less than, and not equal to, the current entry.quantity",
    GameError.INV_FULL_CANNOT_SPLIT: "inventory is full, cannot split entry",
    GameError.INV_ITEM_NOT_FOUND: "item not found in inventory",
    GameError.INV_INSUFFICIENT_QUANTITY: "insufficient quantity available",
    GameError.INV_OPERATION_FAILED: "inventory operation failed",
    GameError.DB_CONNECTION_FAILED: "database connection failed",
    GameError.DB_TRANSACTION_FAILED: "database transaction failed",
    GameError.DB_INSERT_FAILED: "database insert operation failed",
    GameError.DB_UPDATE_FAILED: "database update operation failed",
    GameError.DB_DELETE_FAILED: "database delete operation failed",
    GameError.DB_QUERY_FAILED: "database query failed",
    GameError.DB_RECORD_NOT_FOUND: "database record not found",
    GameError.DB_INVALID_DATA: "invalid data provided for database operation",
    GameError.DB_FOREIGN_KEY_VIOLATION: "foreign key constraint violation",
    GameError.DB_UNIQUE_CONSTRAINT_VIOLATION: "unique constraint violation",
}

//@mysql_table('mobiles')
struct Mobile {
    1: optional MobileId id;
    2: MobileType mobile_type;
    3: map<AttributeType, Attribute> attributes;
    4: Owner owner;
    5: string what_we_call_you;
}

// ============================================================================
// Inventory Service Request/Response Structures
// ============================================================================

// Request data structures for each operation
struct LoadInventoryRequestData {
    1: i64 inventory_id;
}

struct CreateInventoryRequestData {
    1: Inventory inventory;
}

struct SaveInventoryRequestData {
    1: Inventory inventory;
}

struct SplitStackRequestData {
    1: i64 inventory_id;
    2: i64 item_id;
    3: double quantity_to_split;
}

struct TransferItemRequestData {
    1: i64 source_inventory_id;
    2: i64 destination_inventory_id;
    3: i64 item_id;
    4: double quantity;
}

struct ListInventoryRequestData {
    1: i32 page;
    2: i32 results_per_page;
    3: optional string search_string;
}

// Response data structures for each operation
struct LoadInventoryResponseData {
    1: Inventory inventory;
}

struct CreateInventoryResponseData {
    1: Inventory inventory;
}

struct SaveInventoryResponseData {
    1: Inventory inventory;
}

struct SplitStackResponseData {
    1: Inventory inventory;
}

struct TransferItemResponseData {
    1: Inventory source_inventory;
    2: Inventory destination_inventory;
}

struct ListInventoryResponseData {
    1: list<Inventory> inventories;
    2: i64 total_count;
}

// Union of all inventory request data types
union InventoryRequestData {
    1: LoadInventoryRequestData load_inventory;
    2: CreateInventoryRequestData create_inventory;
    3: SaveInventoryRequestData save_inventory;
    4: SplitStackRequestData split_stack;
    5: TransferItemRequestData transfer_item;
    6: ListInventoryRequestData list_inventory;
}

// Union of all inventory response data types
union InventoryResponseData {
    1: LoadInventoryResponseData load_inventory;
    2: CreateInventoryResponseData create_inventory;
    3: SaveInventoryResponseData save_inventory;
    4: SplitStackResponseData split_stack;
    5: TransferItemResponseData transfer_item;
    6: ListInventoryResponseData list_inventory;
}

// Inventory Request structure (extensible for auth, tracing, etc.)
struct InventoryRequest {
    1: InventoryRequestData data;
    // Future fields: request_id, auth_token, trace_context, etc.
}

// Inventory Response structure (extensible for status, errors, etc.)
struct InventoryResponse {
    1: list<GameResult> results;
    2: optional InventoryResponseData response_data;
    // Future fields: response_id, performance_metrics, etc.
}

// ============================================================================
// Item Service Request/Response Structures
// ============================================================================

// Request data structures for each operation
struct CreateItemRequestData {
    1: Item item;
}

struct LoadItemRequestData {
    1: i64 item_id;
    2: optional BackingTable backing_table;
}

struct SaveItemRequestData {
    1: Item item;
}

struct DestroyItemRequestData {
    1: i64 item_id;
}

struct ListItemRequestData {
    1: i32 page;
    2: i32 results_per_page;
    3: optional string search_string;
}

struct AutocompleteItemRequestData {
    1: string search_string;
    2: i32 max_results = 10;
}

struct LoadItemWithBlueprintTreeRequestData {
    1: i64 item_id;
    2: i32 max_depth = 10;
}

// Response data structures for each operation
struct CreateItemResponseData {
    1: Item item;
}

struct LoadItemResponseData {
    1: Item item;
}

struct SaveItemResponseData {
    1: Item item;
}

struct DestroyItemResponseData {
    1: i64 item_id;
}

struct ListItemResponseData {
    1: list<Item> items;
    2: i64 total_count;
}

struct ItemAutocompleteResult {
    1: i64 id;
    2: string internal_name;
}

struct AutocompleteItemResponseData {
    1: list<ItemAutocompleteResult> results;
}

struct LoadItemWithBlueprintTreeResponseData {
    1: BlueprintTreeNode tree;
}

// Union of all item request data types
union ItemRequestData {
    1: CreateItemRequestData create_item;
    2: LoadItemRequestData load_item;
    3: SaveItemRequestData save_item;
    4: DestroyItemRequestData destroy_item;
    5: ListItemRequestData list_item;
    6: AutocompleteItemRequestData autocomplete_item;
    7: LoadItemWithBlueprintTreeRequestData load_with_blueprint_tree;
}

// Union of all item response data types
union ItemResponseData {
    1: CreateItemResponseData create_item;
    2: LoadItemResponseData load_item;
    3: SaveItemResponseData save_item;
    4: DestroyItemResponseData destroy_item;
    5: ListItemResponseData list_item;
    6: AutocompleteItemResponseData autocomplete_item;
    7: LoadItemWithBlueprintTreeResponseData load_with_blueprint_tree;
}

// Item Request structure (extensible for auth, tracing, etc.)
struct ItemRequest {
    1: ItemRequestData data;
    // Future fields: request_id, auth_token, trace_context, etc.
}

// Item Response structure (extensible for status, errors, etc.)
struct ItemResponse {
    1: list<GameResult> results;
    2: optional ItemResponseData response_data;
    // Future fields: response_id, performance_metrics, etc.
}

// ============================================================================
// Player Service Request/Response Structures
// ============================================================================

// Request data structures for each operation
struct CreatePlayerRequestData {
    1: Player player;
}

struct LoadPlayerRequestData {
    1: i64 player_id;
}

struct SavePlayerRequestData {
    1: Player player;
}

struct DeletePlayerRequestData {
    1: i64 player_id;
}

struct ListPlayerRequestData {
    1: i32 page;
    2: i32 results_per_page;
    3: optional string search_string;
}

// Response data structures for each operation
struct CreatePlayerResponseData {
    1: Player player;
}

struct LoadPlayerResponseData {
    1: Player player;
}

struct SavePlayerResponseData {
    1: Player player;
}

struct DeletePlayerResponseData {
    1: i64 player_id;
}

struct ListPlayerResponseData {
    1: list<Player> players;
    2: i64 total_count;
}

// Union of all player request data types
union PlayerRequestData {
    1: CreatePlayerRequestData create_player;
    2: LoadPlayerRequestData load_player;
    3: SavePlayerRequestData save_player;
    4: DeletePlayerRequestData delete_player;
    5: ListPlayerRequestData list_player;
}

// Union of all player response data types
union PlayerResponseData {
    1: CreatePlayerResponseData create_player;
    2: LoadPlayerResponseData load_player;
    3: SavePlayerResponseData save_player;
    4: DeletePlayerResponseData delete_player;
    5: ListPlayerResponseData list_player;
}

// Player Request structure (extensible for auth, tracing, etc.)
struct PlayerRequest {
    1: PlayerRequestData data;
    // Future fields: request_id, auth_token, trace_context, etc.
}

// Player Response structure (extensible for status, errors, etc.)
struct PlayerResponse {
    1: list<GameResult> results;
    2: optional PlayerResponseData response_data;
    // Future fields: response_id, performance_metrics, etc.
}

// ============================================================================
// Service Discovery and Metadata (for Fiddler)
// ============================================================================

// Enum definition with string-to-int mappings
struct EnumDefinition {
    1: string enum_name;
    2: map<string, i32> values;  // e.g. {"SUCCESS": 1, "FAILURE": 2}
    3: optional string description;
}

// Field-to-enum type mapping
struct FieldEnumMapping {
    1: string field_path;  // e.g. "results[].status" or "error_code"
    2: string enum_name;   // e.g. "StatusType" or "GameError"
}

// Description of a single service method
struct MethodDescription {
    1: string method_name;
    2: string description;
    3: string example_request_json;   // Full example Request in JSON with enum strings
    4: string example_response_json;  // Example Response in JSON with enum strings
    5: list<FieldEnumMapping> request_enum_fields;   // Which request fields are enums
    6: list<FieldEnumMapping> response_enum_fields;  // Which response fields are enums
}

// Complete service metadata for discovery
struct ServiceMetadata {
    1: string service_name;
    2: string version;
    3: string description;
    4: list<MethodDescription> methods;
    5: list<EnumDefinition> enums;  // All enums used by this service
}

// ============================================================================
// Base Service Definition
// ============================================================================

service BaseService {
    // Service discovery method
    ServiceMetadata describe(),
}

// ============================================================================
// Inventory Service Definition
// ============================================================================

service InventoryService extends BaseService {
    // Load an inventory by ID
    InventoryResponse load(1: InventoryRequest request),

    // Create a new inventory
    InventoryResponse create(1: InventoryRequest request),

    // Save (create or update) an inventory
    InventoryResponse save(1: InventoryRequest request),

    // Split a stack of items within an inventory
    InventoryResponse split_stack(1: InventoryRequest request),

    // Transfer items between inventories
    InventoryResponse transfer_item(1: InventoryRequest request),

    // List inventories with pagination
    InventoryResponse list_records(1: InventoryRequest request),
}

// ============================================================================
// Item Service Definition
// ============================================================================

service ItemService extends BaseService {
    // Create a new item
    ItemResponse create(1: ItemRequest request),

    // Load an item by ID
    ItemResponse load(1: ItemRequest request),

    // Save (create or update) an item
    ItemResponse save(1: ItemRequest request),

    // Destroy (delete) an item
    ItemResponse destroy(1: ItemRequest request),

    // List items with pagination and search
    ItemResponse list_records(1: ItemRequest request),

    // Autocomplete search for items (returns lightweight results)
    ItemResponse autocomplete(1: ItemRequest request),

    // Load an item with its complete blueprint tree (recursive)
    ItemResponse load_with_blueprint_tree(1: ItemRequest request),
}

// ============================================================================
// Player Service Definition
// ============================================================================

service PlayerService extends BaseService {
    // Create a new player
    PlayerResponse create(1: PlayerRequest request),

    // Load a player by ID
    PlayerResponse load(1: PlayerRequest request),

    // Save (create or update) a player
    PlayerResponse save(1: PlayerRequest request),

    // Delete a player
    PlayerResponse delete(1: PlayerRequest request),

    // List players with pagination and search
    PlayerResponse list_records(1: PlayerRequest request),
}
