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

The thrift services are defined in `/vagrant/gamedb/thrift/py/.*_service.py` files, and the tests are in
`/vagrant/gamedb/thrift/py/.*_service_test.py`

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

The task at hand is to refactor this system slightly. It is mostly correct, however we need to properly represent certain relationships
in the code and the database.

Let's update the locations of some files. Let's move all `*_service.*` files, like `player_service.py` etc, into a new directory. 
Create a directory `/vagrant/gamedb/thrift/py/services/` and move the service definitions into this folder.

Then back out to `/vagrant/gamedb` and grep for all instances of importing those files, with the list of callsites, update each
callsite to correctly import the right files. Be sure to test that fiddler/app.py and py/run_servers.py work still.

In each service file, like inventory_service.py etc, there is an LRUCache implementation. Let's refactor these service implementations by
moving the LRUCache class implementation to its own file, call it lru_cache.py, it can be in the py/services directory as it's only used
by the services. Then update all of the service impls to import the LRUCache code.

Each one of these service files also follows the same pattern, specifically having a describe method.

In game.thrift create a new service called BaseService, and move the describe method to that service. 

Then make the other services, like InventoryService, and PlayerService etc, to inherit from BaseService. 

run `thrift --gen py game.thrift` to update the generate thrift, and then create a BaseService implementation in `py/services/base_service.py` that implements the describe method. 
To make this easier, add an argument to the constructor of BaseService that takes the 'klass:Any' (use this spelling) and stores it. 

Then in the describe method, you can test 'self.klass' to see which implementation it is, and generate the result of a call to 'describe' accordingly.

Try to minimize code duplication if you can. But write the code for clarity and being explicit.

When you are done, check to see that `run_servers.py` and `fiddler/app.py` run. Also run the `_service_test.py` tests for each service and debug as needed.

Ask any questions, also, when you encounter an error, you can ask me if I have any suggestions to debug if you aren't sure how to proceed.
