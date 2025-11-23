You are an expert python webapp developer. You also have a good understanding of apache thrift, mysql,
and the creation of CRUD web applications.

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

There is a seed_items.py script that is intended to be run once to setup the database. it is located at
`/vagrant/gamedb/thrift/py/seed_items.py`

There is a seed_players.py script that is intended to be run once to setup the database. it is located at
`/vagrant/gamedb/thrift/py/seed_items.py`

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

# Fiddler

we have a thrift exploring service called fiddler, located at `/vagrant/gamedb/thrift/fiddler` which uses JSON. This app will be good context for the one we are building, as it interfaces with the various thrift services.

# What we need to do

This may require a bit of exploration to get right, so please ask clarifying questions and display detailed information about your plan of action.

We need to create a CRUD application that will allow admins of the game create and edit the various objects of the game via well designed and aesthetically styled webforms. These webforms will need to be interactive, and be able to suggest values, and also to auto-complete.

Because this webapp will need to be worked on and iterated on, we must choose a style that is clear and easy to extend in the future. We will need to break up the "Models" of the app into separate source files, and import them as needed. 

Because this webapp will not be public facing, it does not require any security features, and it can use something simple, like Bottle as the application framework. 

The main "models" of this webapp will be the Player, the Inventory, and the Item. We will need to create CRUD actions for each of these models. The backing will not be MySQL directly, but we will interface with the PlayerService, InventoryService, and the ItemService as defined in `py/services/*`, as well as defined in game.thrift. For some features, we might have to add functions to these services, for instance for auto-complete if things like list_records is not enough, or we might have to make minor modifications to existing methods. 

Each model needs an index page that will list paginated results of the existing items fetched from the various services. There will need to be a create form for each. Each of the structs is complex, that is there are substructs, and therefore subrecords that must be created. The Create and Edit forms must allow the user to add and remove these records.

In some cases the fields of a member will be an Enum. If that is the case, those must be select inputs where the displayed value is the enum member. 

When editing items that are a foreign key into another table, these must be a hidden input, and instead we need an auto complete input that allows the user to search for an existing record, or choose to create an entirely new record, in which case we should display a subform to collect the inputs. 

Before starting, ask clarifying questions, and present options for design and layout. If you encounter situations or aspects of the task that require more thinking, think hard about the best solution considering the current goals and intent.