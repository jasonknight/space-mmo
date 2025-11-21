You are an expert python developer with knowledge of apache thrift and mysql.

If at any point you find something ambiguous, or have a decision with equally weighted solutions, ask for clarification.

In db.py we have several methods prefixed with `save_` that save thrift structs that are defined in game.thrift

If you think abou the problem in terms of CRUD (Create, Read, Update, Delete), these functions should really be named 'create_' because they would only work with new structs. Let's rename these functions, changing the prefix to 'create_' instead of 'save_'.

You also need to implement update functions, but the problem is not that simple. Currently, every thrift struct has a 'id' field, that is meant to store the id for a record in the database, and this helps us call the functions prefixed with 'load_'. However, once we have used a 'create_' function, we wouldn't really be able to update existing records. 

What we need to do is change all of the 'id' fields to be optional. Then in db.py, we need to update the new 'create_' functions to take into account that the id field is now optional, and to set that 'id' based on the insert id from the database when we create new records.

We then need to create 'update_' functions, similar to the 'create_' functions, but these expect that the struct's 'id' field is not None. We need to fully update the record, and all subrecords along similar lines as the established code, making necessary changes to ensure it all works correctly.

Then we will need to recreate the 'save_' functions, but these will now check the struct passed to them to see if the 'id' field is None, if it is None, then they need to pass the arguments along to the 'create_' functions. If the 'id' is not None, then we need to pass the arguments along to the 'update_' functions.

Then we will need to update db_test.py and ensure that the code there reflects our changes (such as setting the id=None for new records), and then we will need to add a second case in each test function. Currently we create a record, then load it back and compare. Not we will need to add updating. So after we have loaded the record, we need to modify all of the values, and then call the 'save_' function again, and now we expect it to have edited the item in the database, so we have to call 'load_' again and compare the loaded record to the modified record.

Please use the code in these files, and surrounding files, to inform your coding style and standards.
