You are a python engineer and tooling and automation expert.

You need to create a data seeding script for an MMO game written in Python. This seeding script will allow us
to test variations in the database schema, as well as seed testing environments for integration tests.

If at any point you find anything ambiguous, or a decision with two or more options of equal weight or usefulness,
ask for clarification. 

In db.py there are methods on the db class with the name prefix 'save_', the text after the 'save_' is a snake-cased
name of a thrift object (a struct or union) that can be found in game.thrift. The goal of these methods is to take 
a `table_name: str`, and an instance of some object from game.thrift that the user has created, for example an Inventory, and to save it to the database.

The schema of the struct, and the schema of the database are similar, but not identical, so you will have to figure out how to use the schema
of the database to properly store the thrift instance.

When the value of a member on a thrift struct is a complex container, such as a list, or map, this usually indicates that the data should be stored on
another table in a one-to-many relationship. For instance, if the value of a member is list<InventoryEntry>, the the table to store the entries on will
be `inventory_entries`. The final word is pluralized, so that inventory_entry becomes inventory_entries. All table names are pluralized, for instance
an Attribute thrift struct becomes `attributes` for the table that stores them.

When the value of a member is an enum, we normally store that value as a string of the enum member's name, instead of the Enum's value. 

When the value of a member is a union, we have two ways of representing it. First, in the case of AttributeValue, we simply flatten the AttributeValue and store all possible valueson the `attributes` table, each one is nullable. When the member of a union is itself a struct, as in the case of ItemVector3, we also flatten that and store it directly on the
`attributes` table. The second way we store a member that is a union is as a one-to-one relationship with another table. For example Owner is a union of multiple id types, and that is stored on attribute_owners table.

You must fill in each `save_` method with the necessary code to generate, and then execute the necessary SQL statements to store that entire structure in the database.
To do this we want to execute these steps.

1. Create a complementary `get_` method to get the list[str] of SQL statements to store the item. When we have a complex type with a one-to-many relationship we need to put a {last_insert_id} place holder in the next statement, that we will later fill out by making a database request for the last_insert_id. If the relationship is one-to-one, the process is inverted. We have to create the foreign record first, get the last_insert_id and then add that to the next statement (for the main record). We'll also need to add two arguments, drop and truncate, both boolean. both should default to False. If both are true, then set truncate to false, because there is no need to truncate a table and drop it at the same time. If drop is true, then we should add a drop table statement as the first statement to execute. If truncate is true, we should add a truncate SQL statement.
2. In the `save_` method, iterate over the list[str] of SQL statements, executing each one, and ensuring that they were successful.
2a. If the thing being saved is complex and has a one-to-many relationship with another table, we should get the last inserted id, and
    fill out the foreign key to ensure that the data can be found later. The best strategy will be that, for any INSERT statement we make, we always get the last insert id and store it. 
3. Each `save_` method should use transactions to ensure that all the data is saved, or none of it. Because we are expecting all data to be saved,
   any failure should immediately raise an Exception with a helpful message which tells the user the database, the table, and key information about the thing being saved. The best information are things like `internal_name`, or item_id, or mobile_id

In db.py, for each `save_` method, we must create a `load_` method that will be used to load the information back from the database, and return the thrift instance with the data filled in that was loaded from the database. This method should return a Tuple[GameResult, ...], where ... is the kind of struct we are loading. The reason to return the Tuple is so that the user can test to see if the GameResult part of the Tuple `is_ok`.

Once we've created the seeding script, we now need to create a db_test.py that can perform a test of each operation. For each `save_` method in db.py, we will
create a test that will:

1. Create a stub of the struct to be saved
1a. For member variables that are lists and maps, we must create at least 2-3 stub entries with quasi-random values. We do not need to create every possible combination.
2. We should execute the save method.
3. If the save function succeeded, we should call the `load_` method, which will return a Tuple[GameResult, ...] where ... is the type we are trying to load. We should test that the GameResult part of the Tuple `is_ok`, and then we should compare all parts of the thrift struct to the stub struct we created earlier to ensure that all data is loaded back correctly.

When running these tests, we should fill out the database name value as "test_run_db". At the end of the test we should delete the test database, it does not need to persist.


