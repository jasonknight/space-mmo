You are an expert python game developer.

If you find anything ambiguous, or encounter decisions of roughle equal weight, ask for clarification.

# File Locations

The definition of structs, enums, and services can be found in /vagrant/gamedb/thrift/game.thrift

To compile thrift you need to run `thrift --gen py game.thrift` the code will be output in /vagrant/gamedb/thrift/gen-py

The thrift schema is also used with the local mysql database. There is a database adapter at
/vagrant/gamedb/thrift/py/db.py which includes individual implementations of core thrift structs
located at `/vagrant/gamedb/thrift/py/dbinc/*.py` there are also `.*_test.py` files in that directory
for testing each component. 

Fiddler is a webapp in python using Bottle. It can be found at /vagrant/gamedb/thrift/fiddler. There is a README 
that decribes the service at /vagrant/gamedb/thrift/fiddler/README.md

There is a bootstrap.py script that is intended to be run once to setup the database. it is located at
`/vagrant/gamedb/thrift/py/bootstrap.py`

The thrift services are defined in `/vagrant/gamedb/thrift/py/services/.*_service.py` files, and the tests are in
`/vagrant/gamedb/thrift/py/services/.*_service_test.py`

# Database 

We currently use a MySQL database. The login credentials that you can use are user=admin, password=minda.

The db we are working with is named `gamedb`.

# Game Concepts

We split up the game into some major components. There are Items, Inventories, and Mobiles. There is also a Player concept,
however a Player is mostly intended to represent a user who can log in and possess a Mobile. This is not yet implemented.

# Items

The current implementation of Item is intended to be largely static. Items can be thought of as Platonic templates of what an
item should be before it is actually materialized in the game. 

Items also have blueprints which can define the makeup of an item for crafting. They express this in terms of a ratio. For any given
item, how much of 1 unit of that item *can* be made from any component. Some components can represent 100% of the item, some components
can only represent 50% or 25% etc. We won't be working with blueprints for the moment, they just need to save correctly for the moment.

# Mobiles

Mobiles are probably similar to the concept of a Pawn in Unreal Engine. That is, a Mobile is something that can move about in the game, and
can be possessed by a Player, or some script or even an AI that can dictate what it does, and where is is located in the universe.

# Inventories

An inventory is an abstraction of a container of InventoryEntries. Inventories can be owned by Mobiles, or by Items. Consider a Treasure Chest 
Item in the game. That Treasure Chest can contain items, and so the owner of the Inventory would be the Treasure Chest Item.

Mobiles can also own an Inventory. In this case, the Inventory is an abstract concept of what the user "possesses" in the current moment.

# Players

A player is a user, as in a human who can login into the system an possess a Mobile. We keep some information about the Player.

# What we need to do

The task at hand is to refactor this system slightly. It is mostly correct, however we need to properly represent certain relationships in the code and the database.

## Changes to Players

First, We need to add a 'email' field to the Player struct in game.thrift, and then update the db adapter for player located in py/dbinc/player.py and ensure the py/db_test.py runs. We will also need to ensure that py services/player_service.py, it's _test, and the snippets/ of json are updated properly.

Second, need to add an `optional Mobile mobile;` field to Player struct in game.thrift, and then update the db adapters to handle the case when a Mobile struct is present when updating a Player. When doing so, we should simply call into the mobile adapter to save the mobile.

Third, when creating a Player, we must also create a corresponding mobile. Only one can exist for a player at at time. 

Fourth, when we destroy a Player record, we must also delete the player's mobile. Before deleting a player, we have to check the struct to see if player.mobile is None, and if so, try to load the mobile. If the mobile can be loaded, then we will have to delete the mobile, before deleting the player. If the mobile can't be loaded because it doesn't exist, then we don't have to do anything about it.

## Changes to Mobiles

First, we need to add a `what_we_call_you` string field on the Mobile struct, as a player's account name (what we call the player) won't have to be what we call the Mobile the player controls.

Second, and this relates to Item and the items table, so let me explain the general context.

The `items` table, and all of the tables to connected to it, like `item_blueprints` and `item_blueprint_components` and `item_attributes` are just sort of Platonic Abstractions, or defaults. These tables are largely static and actually won't be updated often. Instead, when a player (and therefore his mobile) acquires an item in game, we will be copying that item from the 'item tables' into new tables that apply to the mobile.

These new tables need to be like `mobile_items`, `mobile_item_blueprints`, `mobile_item_blueprint_components`, and `mobile_item_attributes`. 

In order to make this work, we will essentially be controlling the ultimate table that the queries are run with, with a small addition of an argument that will let us generate the right SQL. This is because `mobile_items` table will need to have an extra field, mobile_id.

We will need to refactor the ItemMixin class. All of the functions that get SQL will need to take a table argument if they don't already. That table argument can default to the currently used value.

Also, in some of these methods, like get_item_sql, there are several local variables defining table names, like attributes_table=..., these will also have to become arguments, with default values as currently set. And you will have to update the callsites of these functions if necessary (with default values likely you won't need to update callsites. It's up to you.) You only need to do this with functions that don't take an instance of Item, as Item will have a new member called backing_table that we can use to derive this information from.

We will also need to add the creation of these tables to py/bootstrap.py with an explicit section creating the 'mobile' versions of the items tables.

You will also need to modify the Item struct in game.thrift, and create a new enum. That enum should be named BackingTable, and should have a member that indicates ITEMS, or MOBILE_ITEMS. You will also need to create a `map<BackingTable, string> TABLE2STR` with an entry for the ones you've created. You should also create an entry for every table we currently use, like ATTRIBUTES, ATTRIBUTE_OWNERS, PLAYERS, MOBILES, MOBILE_ITEM_BLUEPRINTS etc, and update existing constant variables in db.py, and db_test.py, and other related files in dbinc/ to use the thrift map, example in db.py there is a variable TABLE_MOBILES = "mobiles", instead, wherever you use TABLE_MOBILES you can just use TABLE2STR[BackingTable.MOBILES]. There are other constants like this you may want to update.

Then you can add an optional member to the Item struct called backing_table. This doesn't need to be saved to the database, and is really only there for admin and metadata purposes. Though you should update the load functions for items and use the table name to find out the correct BackingTable value and set it on the item.

Do not update the SQL code for Items to save the value of BackingTable, it's only metadata. Mostly this will be used when making ItemService requests to create or load an item. 

We will also need to add an optional BackingTable backing_table field to the LoadItemRequestData, and to use that value to inform how we call into the Item db adapter in ItemServiceHandler.

If you are unclear on any point hear, don't hesitate to ask. There will be a few more refactors to do after this, but we will do them in a successive session and then debug the final changes at that point.