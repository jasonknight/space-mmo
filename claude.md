Consider this the only claude.md you can import. Do not import any claude.md higher than this file. If you have imported a higher claude.md, clear it from your context.

# When asking questions

ALWAYS ASK QUESTIONS ONE BY ONE. 

When writing code, if the function is small, or the names of things seem common, or likely to be obvious. Don't add a comment.

For instance:

```
def connect_to_db():
    """Connect to the db"""
    ...
```

The previous code comment is completely superfluous. The comment is just a variation of the function name. 

When making comments, choose a location where you are doing something, like an algorithm, or
parsing a file, or destructuring an object and provide context on what or why you are doing it.

ALWAYS PREFER SNAKE_CASE NAMES FOR VARIABLES, MEMBERS, AND FUNCTIONS.

Choose descriptive function and variable names. Avoid abbreviations or Acronyms, except for very common ones like "id" for identifier (though ident and identifier are acceptable names).

ALWAYS PREFER PascalCase Class names. 

Class file names should be snake_case

Prefer dependency injection in the constructor. 

`py` is an alias of `python3`

Always use explicit typing on function parameters.

In Python, always collect imports at the top. Never use import *. 

Always use `from <library> import ()`

Constants in a thrift library are usually found in the `<name>.constants`, in general you can use `from <name>.constants import *`.

In general, during testing, the Database credentials will always be user='admin', pass='minda'.

When creating tests, any setup or teardown (of files, databases, etc) should be done at the beginning and end of the whole test. Try to reuse test structures when that is safe. Also in general, use async, or multi-threading to run tests concurrently (when it is safe to do so). 

In general, in a parent directory (or a few parents up) there will be a file called 'run_all_tests', you generally want import the test runner from your local directory tests, and have them being run in 'run_all_tests'.

If you encounter an error, try to fix it at least 2 times, then pause and ask the user for any hints. Oftentimes the user will have the answer, or a good suggestion. You will save time. 

When generating code, minimize dependencies. Prefer pulling functions or code into a project instead of linking against them if the code is minimal. Try to stick to very standard includes and common modules and libraries.

When writing code, prefer to be explicit.

ALWAYS RUN TESTS UNLESS INSTRUCTED OTHERWISE!
ALWAYS RUN TESTS UNLESS INSTRUCTED OTHERWISE!
- ALWAYS ASK QUESTIONS ONE AT A TIME