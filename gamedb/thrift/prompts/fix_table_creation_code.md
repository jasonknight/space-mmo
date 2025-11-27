Throughout the codebase we have various instances of table creation logic for mysql.
There is a lot of duplication, we want to centralize all table creation to a single file,
and import from there. 

The current correct table schemas can be found on the mysql database called 'gamedb', the user=admin and password='minda'. You can connect to mysql, get it to describe a table, and use that as an authoritative schema.

You can put all of these schemas into a python file in py/db_tables.py. Put them into a hashtable where the table name is the key. All of these table creation snippets of code usually have a format item, like '{database}' and this needs to be preserved.

Once you've created the central file with all table creation logic, update all other sites in the code by removing the table creation logic, importing the db_tables and looking up the table in the hash.