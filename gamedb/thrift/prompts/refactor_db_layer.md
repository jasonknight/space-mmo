You are an expert python programmer with experience refactoring application.

We are in the middle of a refactor, so the code is not currently in a working state. In the middle of the refactor, it was discovered that our underlying implementation is inadequate, and needs to be changed. There are uncommitted changes in the codebase, and that is fine.

Currently, the DB class in py/db.py uses Mixins sourced from py/dbinc/ however this pattern is not flexible enough. We want to shift to using providers that satisfy an interface. 

The interface we want is:

interface Model:
  create()
  load() -> ThriftObject
  update() -> bool
  destroy() -> bool
  search() list[ThriftObject]

We then want ItemMixin, MobileItemMixin, PlayerMixin, InventoryMixin, MobileMixin to implement this model. This interface is just an example, the actual return types will be similar to the existing classes, i.e. like `Tuple[GameResult, Optional[ThriftObject]]`

In ItemMixin and MobileItemMixin we refer to the same blueprint structs. Only the backing table of the blueprint structs is different, also there is no BlueprintMixin, but we need to create a Blueprint and BlueprintComponent implementation of the Model interface so that it can handle create, load, update, destroy, and find.

Backing tables are defined with a hashman called TABLE2STR and the BackingTable enum. The enum fields are named very close to the existing table names.

In db.py we have things like: `dispatch_map =` which are a dispatch map to various functions provided by the Mixins. There are also missing implementations of the mixins, for instance there is also no current implementation for Attribute etc, the Attribute handling code is actually implements on db.py's DB class. We need to implement an Attribute instance of the Model interface as well.

In each Mixin there are references to tables throughout, these need to become easily editatble class constants on the Model implementation so that there is a single source of truth.

We will need to refactor the existing classes, create the missing classes, and update the testing files that refer to them. Also, throughout the code there are many imports. All imports should be lifted to the top of the file for clarity.

Some arguments, like table and database will no longer be needed, as these should be class constants on the Model implementation as well. 

Our key goal is to eliminate the db.py entirely, and instead of trying to go through db.py, we need to update the code using db.py to use the actual model instance directly. So instead of choosing `DB.save_item(...)` we would want something like `model = ItemModel(database, item_table, item_attributes_table); model.save(obj=item)`, In the case of `load()` method, this should be an instance method, so that we can call it like `ItemModel(database, ...).load(id=123)` the main state that we are maintaining are just the db connection and db info.

To accomplish the refactor from DB class, which also manages the connection, and transactions, you will need to create a BaseModel class in `base_model.py` and inherit from that to manage the shared code.

Most of the code implemented in these classes will remain the same, we only want to transform the outer shell and representation of each class, and then update the tests and callsites across the codebase. This will include updating the usage in the py/services/*_service.py files as well. 

Ask questions to clarify the tasks. Come up with a comprehensive plan for the refactor, let's start with just Item, and Blueprint classes for the moment, and get the py/dbinc/item_test.py to function. Then we can continue with the other classes.

# Summary of Progress so far.

Key Changes Made:
1. Replaced DB(host, user, password) with specific model instances like PlayerModel(host, user, password, database_name)
2. Changed method calls from db.save_player(database_name, player) to player_model.save(player)
3. Updated setup_database() and teardown_database() functions to:
   - Take (host, user, password, database_name) parameters instead of (db, database_name)
   - Create database connections directly using mysql.connector
   - Create only the necessary tables for each test
4. Fixed missing owner_item_id column in mobiles table definitions
📋 Remaining Tasks (Lower Priority):
- inventory_test.py - Still uses old DB pattern (marked as medium priority)
- mobile_item_test.py - Still uses old DB pattern (marked as low priority)
- blueprint_test.py - need to create this for completeness and to ensure the central logic works, regardless of item and mobile item changes. 