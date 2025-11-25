# MySQL Credentials
- user is 'admin'
- pass is 'minda'

# Ports and Binding

- Always bind to 0.0.0.0 and not localhost
- InventoryService is always port 9090
- ItemService is always port 9091
- PlayerService is always port 9092

# Build and Test Commands
- **Run All Tests**: `cd thrift/py && python3 db_test.py`
- **Run Single Test**: Edit `thrift/py/db_test.py` to comment out other tests in `main()`, or call specific test functions from `dbinc/`.
- **Thrift Generation**: If `game.thrift` changes, regenerate bindings (e.g. `thrift -r --gen py game.thrift`).

# Code Style & Conventions
- **Python Formatting**:
  - Indentation: 4 spaces.
  - Line Length: Keep under 80 characters.
  - **Trailing Commas**: MANDATORY for the last item in lists, dicts, function calls, and definitions.
  - Naming: `snake_case` for variables/functions. `PascalCase` for classes.
- **Imports**: `sys.path.append('../gen-py')` is common in `thrift/py` scripts to load generated code.
- **Error Handling**: Use `from common import is_ok, is_true` helpers to assert operation results (returned as objects with `message`).
- **Testing pattern**: Tests usually take `(db, database_name)` arguments. Use `setup_database` and `teardown_database` fixtures from `dbinc.item_test` (or similar).
- **Environment**: Root is `/vagrant/gamedb`. Python scripts often assume CWD is `thrift/py`.
