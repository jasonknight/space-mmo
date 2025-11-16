typedef i64 AssetId
typedef i64 ItemId
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

enum ItemAttributeType {
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

// Sometimes items can be present in stacks, this
// decides whether or not we can stack the item.
// non-stacking items enforce a limit on players, how
// many they can hold becomes a function of how big their
// inventory is, and also how many of this item a container
// can hold.
struct NotApplicable {}
struct StackabilityInfo {
    1: i64 max_stack_size;
}

union Stackability {
    1: NotApplicable not_applicable;
    2: StackabilityInfo stackable;
}

struct ItemVector3 {
    1: double x;
    2: double y;
    3: double z;
}
union ItemAttributeValue {
    1: bool bool_value;
    2: double double_value;
    3: ItemVector3 vector3;
    // when an ITEM attribute, this will be the item id
    // when a translated name, this will be the translation id
    4: AssetId asset_id; 
 }

struct ItemAttribute {
    1: i64 id; // this member only matters for a materialized attribute of an owned item
    2: string internal_name;
    3: bool visible;
    4: ItemAttributeValue value;
    5: ItemAttributeType attribute_type;
}

struct Item {
    1: i64 id;
    2: string internal_name; // used internally to talk about the item, but
    // not shown to users, as their names/descriptions must come for i18n translations
    3: map<ItemAttributeType, ItemAttribute> attributes;
    4: Stackability stackable;
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
    1: map<ItemId, ItemBlueprintComponent> components;
    2: i64 bake_time_ms;

}

struct ItemDb {
    1: list<Item> items;
}

struct InventoryEntry {
    1: ItemId item_id;
    2: double quantity;
}
struct Inventory {
    1: i64 id;
    2: i64 max_items;
    3: double max_volume;
    4: list<InventoryEntry> entries;
    5: double last_calculated_volume = 0.0;
}