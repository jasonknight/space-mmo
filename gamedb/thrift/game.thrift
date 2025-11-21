typedef i64 AssetId
typedef i64 ItemId
typedef i64 MobileId
// The general item type is something like a parent item
// class, it gives some broad category to the item, is it 
// a consumable, virtual, weapon, These are special, globally
// interesting types for quick sorting
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
}

enum MobileType {
    PLAYER = 1,
    NPC = 2,
}

union Owner {
    1: MobileId mobile_id;
    2: ItemId item_it;
    3: AssetId asset_id;
}

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
}



struct ItemVector3 {
    1: double x;
    2: double y;
    3: double z;
}
union AttributeValue {
    1: bool bool_value;
    2: double double_value;
    3: ItemVector3 vector3;
    // when an ITEM attribute, this will be the item id
    // when a translated name, this will be the translation id
    4: AssetId asset_id; 
 }

struct Attribute {
    1: optional i64 id; // this member only matters for a materialized attribute of an owned item
    2: string internal_name;
    3: bool visible;
    4: AttributeValue value;
    5: AttributeType attribute_type;
    6: Owner owner;
}

struct Item {
    1: optional i64 id;
    2: string internal_name; // used internally to talk about the item, but
    // not shown to users, as their names/descriptions must come for i18n translations
    3: map<AttributeType, Attribute> attributes;
    4: optional i64 max_stack_size;
    5: ItemType item_type;
    // Optional because not items can be constructed by players
    6: optional ItemBlueprint blueprint;
}

struct ItemBlueprintComponent {
    // A value between 0.1 -> 1.0
    1: double ratio; // i.e. for every 1 unit of this item, how much of the target item do we get?
    2: ItemId item_id;
}
// An ItemBlueprint contains the item id and the amount of that item required
// to construct it, this is also used when recycling/breaking down an item
// into its base components
struct ItemBlueprint {
    1: optional i64 id;
    2: map<ItemId, ItemBlueprintComponent> components;
    3: i64 bake_time_ms;

}

struct ItemDb {
    1: list<Item> items;
}

struct InventoryEntry {
    1: ItemId item_id;
    2: double quantity;
    3: bool is_max_stacked = false;
}
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

struct Mobile {
    1: optional MobileId id;
    2: MobileType mobile_type;
    3: map<AttributeType, Attribute> attributes;
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

// Union of all request data types
union RequestData {
    1: LoadInventoryRequestData load_inventory;
    2: CreateInventoryRequestData create_inventory;
    3: SaveInventoryRequestData save_inventory;
    4: SplitStackRequestData split_stack;
    5: TransferItemRequestData transfer_item;
}

// Union of all response data types
union ResponseData {
    1: LoadInventoryResponseData load_inventory;
    2: CreateInventoryResponseData create_inventory;
    3: SaveInventoryResponseData save_inventory;
    4: SplitStackResponseData split_stack;
    5: TransferItemResponseData transfer_item;
}

// Generic Request structure (extensible for auth, tracing, etc.)
struct Request {
    1: RequestData data;
    // Future fields: request_id, auth_token, trace_context, etc.
}

// Generic Response structure (extensible for status, errors, etc.)
struct Response {
    1: list<GameResult> results;
    2: optional ResponseData response_data;
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
// Inventory Service Definition
// ============================================================================

service InventoryService {
    // Service discovery method
    ServiceMetadata describe(),

    // Load an inventory by ID
    Response load(1: Request request),

    // Create a new inventory
    Response create(1: Request request),

    // Save (create or update) an inventory
    Response save(1: Request request),

    // Split a stack of items within an inventory
    Response split_stack(1: Request request),

    // Transfer items between inventories
    Response transfer_item(1: Request request),
}
