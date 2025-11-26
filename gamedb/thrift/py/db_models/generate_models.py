#!/usr/bin/env python3
"""
ActiveRecord-style model generator for MySQL tables.
Generates model files with getters, setters, save, find, and find_by methods.
"""

import argparse
import mysql.connector
from typing import Dict, List, Tuple, Any
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# MySQL type to Python type mapping
MYSQL_TO_PYTHON_TYPE = {
    "int": "int",
    "tinyint": "int",
    "smallint": "int",
    "mediumint": "int",
    "bigint": "int",
    "float": "float",
    "double": "float",
    "decimal": "float",
    "char": "str",
    "varchar": "str",
    "text": "str",
    "tinytext": "str",
    "mediumtext": "str",
    "longtext": "str",
    "date": "datetime",
    "datetime": "datetime",
    "timestamp": "datetime",
    "time": "datetime",
    "year": "int",
    "binary": "bytes",
    "varbinary": "bytes",
    "blob": "bytes",
    "tinyblob": "bytes",
    "mediumblob": "bytes",
    "longblob": "bytes",
    "enum": "str",
    "set": "str",
    "bool": "bool",
    "boolean": "bool",
    "json": "Any",
}


def get_python_type(mysql_type: str) -> str:
    """Convert MySQL type to Python type annotation."""
    # Extract base type (before parentheses or spaces)
    base_type = mysql_type.split("(")[0].split(" ")[0].lower()
    return MYSQL_TO_PYTHON_TYPE.get(base_type, "Any")


def to_pascal_case(snake_str: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in snake_str.split("_"))


def singularize_table_name(table_name: str) -> str:
    """
    Convert plural table name to singular.
    Simple implementation: removes trailing 's' if present.
    Handles common cases like 'ies' -> 'y', 'sses' -> 'ss', 'ses' -> 's'.
    """
    if table_name.endswith("ies"):
        # inventories -> inventory, entries -> entry
        return table_name[:-3] + "y"
    elif table_name.endswith("sses"):
        # classes -> class, addresses -> address
        return table_name[:-2]
    elif table_name.endswith("ses"):
        # cases -> case
        return table_name[:-1]
    elif table_name.endswith("s"):
        # items -> item, players -> player
        return table_name[:-1]
    else:
        # Already singular or special case
        return table_name


def get_table_columns(cursor, database: str, table_name: str) -> List[Dict[str, Any]]:
    """Get column information for a table."""
    cursor.execute(
        f"""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """,
        (database, table_name),
    )

    columns = []
    for row in cursor.fetchall():
        # Decode bytes to strings if necessary
        def decode_if_bytes(val):
            return val.decode("utf-8") if isinstance(val, bytes) else val

        columns.append(
            {
                "name": decode_if_bytes(row[0]),
                "data_type": decode_if_bytes(row[1]),
                "is_nullable": decode_if_bytes(row[2]) == "YES",
                "is_primary_key": decode_if_bytes(row[3]) == "PRI",
                "column_type": decode_if_bytes(row[4]),
            }
        )
    return columns


def get_all_tables(cursor, database: str) -> List[str]:
    """Get all table names in the database."""
    cursor.execute(
        f"""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """,
        (database,),
    )

    def decode_if_bytes(val):
        return val.decode("utf-8") if isinstance(val, bytes) else val

    return [decode_if_bytes(row[0]) for row in cursor.fetchall()]


def get_create_table_statement(cursor, table_name: str) -> str:
    """Get the CREATE TABLE statement for a table."""
    cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
    result = cursor.fetchone()

    def decode_if_bytes(val):
        return val.decode("utf-8") if isinstance(val, bytes) else val

    # Result is (table_name, create_statement)
    create_statement = decode_if_bytes(result[1])
    return create_statement


def get_foreign_key_constraints(cursor, database: str) -> Dict[str, List[Dict[str, str]]]:
    """Get all foreign key constraints from the database."""
    cursor.execute(
        """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
        AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY TABLE_NAME, COLUMN_NAME
    """,
        (database,),
    )

    def decode_if_bytes(val):
        return val.decode("utf-8") if isinstance(val, bytes) else val

    fk_constraints = {}
    for row in cursor.fetchall():
        table_name = decode_if_bytes(row[0])
        column_name = decode_if_bytes(row[1])
        ref_table = decode_if_bytes(row[2])
        ref_column = decode_if_bytes(row[3])

        if table_name not in fk_constraints:
            fk_constraints[table_name] = []

        fk_constraints[table_name].append(
            {
                "column": column_name,
                "referenced_table": ref_table,
                "referenced_column": ref_column,
            }
        )

    return fk_constraints


def get_unique_constraints(cursor, database: str) -> Dict[str, List[str]]:
    """Get all unique constraints from the database."""
    cursor.execute(
        """
        SELECT
            TABLE_NAME,
            COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
        AND CONSTRAINT_NAME != 'PRIMARY'
        AND CONSTRAINT_NAME IN (
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_TYPE = 'UNIQUE'
            AND TABLE_SCHEMA = %s
        )
        ORDER BY TABLE_NAME, COLUMN_NAME
    """,
        (database, database),
    )

    def decode_if_bytes(val):
        return val.decode("utf-8") if isinstance(val, bytes) else val

    unique_constraints = {}
    for row in cursor.fetchall():
        table_name = decode_if_bytes(row[0])
        column_name = decode_if_bytes(row[1])

        if table_name not in unique_constraints:
            unique_constraints[table_name] = []

        unique_constraints[table_name].append(column_name)

    return unique_constraints


def detect_relationships_by_convention(
    columns: List[Dict[str, Any]],
    all_tables: List[str],
) -> List[Dict[str, Any]]:
    """
    Detect foreign key relationships by naming convention.
    Columns ending with _id are assumed to reference other tables.
    Handles prefixes like 'owner_', 'parent_', etc.
    """
    relationships = []

    # Common semantic prefixes that don't affect the referenced table
    semantic_prefixes = ['owner_', 'parent_', 'child_', 'source_', 'target_', 'primary_', 'secondary_']

    for col in columns:
        if col["name"].endswith("_id") and col["name"] != "id":
            # Remove _id suffix
            col_name = col["name"][:-3]

            # Try to find the referenced table
            # First try the full name, then try removing semantic prefixes
            candidates = [col_name]

            for prefix in semantic_prefixes:
                if col_name.startswith(prefix):
                    # Extract the base name without the prefix
                    base_name = col_name[len(prefix):]
                    candidates.append(base_name)

            found = False
            for candidate in candidates:
                # Try both singular and plural forms
                potential_tables = [
                    candidate,  # Exact match
                    candidate + "s",  # Add 's'
                    candidate + "es",  # Add 'es'
                    candidate[:-1] + "ies" if candidate.endswith("y") else None,  # y -> ies
                ]

                for potential_table in potential_tables:
                    if potential_table and potential_table in all_tables:
                        relationships.append(
                            {
                                "column": col["name"],
                                "referenced_table": potential_table,
                                "referenced_column": "id",
                                "is_nullable": col["is_nullable"],
                            }
                        )
                        found = True
                        break

                if found:
                    break

    return relationships


def build_relationship_metadata(
    all_tables: List[str],
    table_columns: Dict[str, List[Dict[str, Any]]],
    fk_constraints: Dict[str, List[Dict[str, str]]],
    unique_constraints: Dict[str, List[str]],
) -> Dict[str, Dict[str, Any]]:
    """
    Build comprehensive relationship metadata for all tables.
    Returns a dict mapping table names to their relationship info.
    """
    relationships = {}

    for table_name in all_tables:
        columns = table_columns[table_name]

        # Start with explicit foreign key constraints
        belongs_to = []
        if table_name in fk_constraints:
            for fk in fk_constraints[table_name]:
                col = next((c for c in columns if c["name"] == fk["column"]), None)
                belongs_to.append(
                    {
                        "column": fk["column"],
                        "referenced_table": fk["referenced_table"],
                        "referenced_column": fk["referenced_column"],
                        "is_nullable": col["is_nullable"] if col else True,
                        "is_unique": fk["column"] in unique_constraints.get(table_name, []),
                    }
                )

        # Add relationships detected by convention
        convention_rels = detect_relationships_by_convention(columns, all_tables)
        for rel in convention_rels:
            # Only add if not already in belongs_to
            if not any(b["column"] == rel["column"] for b in belongs_to):
                rel["is_unique"] = rel["column"] in unique_constraints.get(table_name, [])
                belongs_to.append(rel)

        # Build reverse relationships (has_many)
        has_many = []
        for other_table in all_tables:
            if other_table == table_name:
                continue

            other_belongs_to = []
            if other_table in fk_constraints:
                other_belongs_to.extend(fk_constraints[other_table])

            other_convention = detect_relationships_by_convention(
                table_columns[other_table],
                all_tables,
            )
            for rel in other_convention:
                if not any(b["column"] == rel["column"] for b in other_belongs_to):
                    other_belongs_to.append(rel)

            # Check if other_table references this table
            for rel in other_belongs_to:
                if rel["referenced_table"] == table_name:
                    other_col = next(
                        (c for c in table_columns[other_table] if c["name"] == rel["column"]),
                        None,
                    )
                    has_many.append(
                        {
                            "foreign_table": other_table,
                            "foreign_column": rel["column"],
                            "is_unique": rel.get("is_unique", False)
                            or (
                                rel["column"]
                                in unique_constraints.get(other_table, [])
                            ),
                        }
                    )

        relationships[table_name] = {
            "belongs_to": belongs_to,
            "has_many": has_many,
        }

    return relationships


def pluralize(word: str) -> str:
    """Convert singular word to plural form."""
    if word.endswith("y"):
        return word[:-1] + "ies"
    elif word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    else:
        return word + "s"


def get_relationship_name(column_name: str) -> str:
    """
    Convert foreign key column name to relationship method name.
    Example: inventory_id -> inventory, owner_player_id -> owner_player
    """
    if column_name.endswith("_id"):
        return column_name[:-3]
    return column_name


def is_pivot_table(table_name: str, columns: List[Dict[str, Any]]) -> bool:
    """
    Detect if a table is a pivot/join table.
    Pivot tables typically end with '_owners', '_members', etc. and have multiple foreign keys.
    """
    # Check for common pivot table name patterns
    pivot_suffixes = ['_owners', '_members', '_entries', '_items']
    if any(table_name.endswith(suffix) for suffix in pivot_suffixes):
        # Count foreign key columns
        fk_count = sum(1 for col in columns if col["name"].endswith("_id") and col["name"] != "id")
        # Pivot tables typically have 2+ foreign keys
        return fk_count >= 2

    return False


def generate_belongs_to_methods(
    belongs_to_rels: List[Dict[str, Any]],
    table_columns: Dict[str, List[Dict[str, Any]]],
) -> str:
    """Generate belongs-to relationship methods (getters and setters)."""
    methods = []

    for rel in belongs_to_rels:
        column_name = rel["column"]
        referenced_table = rel["referenced_table"]
        is_nullable = rel["is_nullable"]

        # Convert table name to class name
        singular_name = singularize_table_name(referenced_table)
        class_name = to_pascal_case(singular_name)

        # Relationship method name (e.g., owner_player from owner_player_id)
        rel_name = get_relationship_name(column_name)

        # Optional type annotation (use string for forward reference)
        return_type = f"Optional['{class_name}']" if is_nullable else f"'{class_name}'"

        # Getter method with lazy loading and caching
        getter = f"""    def get_{rel_name}(self, strict: bool = False) -> {return_type}:
        \"\"\"
        Get the associated {class_name} for this {rel_name} relationship.
        Uses lazy loading with caching.

        Args:
            strict: If True, raises ValueError when FK is set but record doesn't exist.
                   If False, returns None when record doesn't exist.
        \"\"\"
        # Check cache first
        cache_key = '_{rel_name}_cache'
        if hasattr(self, cache_key) and getattr(self, cache_key) is not None:
            return getattr(self, cache_key)

        # Get foreign key value
        fk_value = self.get_{column_name}()
        if fk_value is None:
            return None

        # Lazy load from database
        related = {class_name}.find(fk_value)

        if related is None and strict:
            raise ValueError(f"{{self.__class__.__name__}} has {column_name}={{fk_value}} but no {class_name} record exists")

        # Cache the result
        setattr(self, cache_key, related)
        return related"""

        methods.append(getter)

        # Setter method (also use string type hint)
        setter = f"""    def set_{rel_name}(self, model: {return_type}) -> None:
        \"\"\"
        Set the associated {class_name} for this {rel_name} relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The {class_name} instance to associate, or None to clear.
        \"\"\"
        # Update cache
        cache_key = '_{rel_name}_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_{column_name}(None)
        else:
            self.set_{column_name}(model.get_id())"""

        methods.append(setter)

    return "\n\n".join(methods) if methods else ""


def generate_has_many_methods(
    has_many_rels: List[Dict[str, Any]],
    table_columns: Dict[str, List[Dict[str, Any]]],
) -> str:
    """Generate has-many relationship methods."""
    methods = []

    for rel in has_many_rels:
        foreign_table = rel["foreign_table"]
        foreign_column = rel["foreign_column"]

        # Convert table names to class names
        foreign_singular = singularize_table_name(foreign_table)
        foreign_class = to_pascal_case(foreign_singular)

        # Relationship method name (pluralized)
        # Example: inventory_entries for has_many inventory_entries
        rel_name = foreign_table

        # Getter method with lazy loading support
        getter = f"""    def get_{rel_name}(self, reload: bool = False, lazy: bool = False):
        \"\"\"
        Get all associated {foreign_class} records.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[{foreign_class}] or Iterator[{foreign_class}]
        \"\"\"
        cache_key = '_{rel_name}_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                if lazy:
                    return iter(cached)
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return iter([]) if lazy else []

        results = {foreign_class}.find_by_{foreign_column}(my_id)

        # Cache results for non-lazy calls
        if not lazy:
            setattr(self, cache_key, results)

        return iter(results) if lazy else results"""

        methods.append(getter)

    return "\n\n".join(methods) if methods else ""


def generate_getters(columns: List[Dict[str, Any]]) -> str:
    """Generate getter methods for all columns."""
    getters = []
    for col in columns:
        python_type = get_python_type(col["data_type"])
        optional_type = (
            f"Optional[{python_type}]" if col["is_nullable"] else python_type
        )

        getter = f"""    def get_{col["name"]}(self) -> {optional_type}:
        \"\"\"Get the value of {col["name"]}.\"\"\"
        return self._data.get('{col["name"]}')"""
        getters.append(getter)

    return "\n\n".join(getters)


def generate_setters(columns: List[Dict[str, Any]]) -> str:
    """Generate setter methods for all columns."""
    setters = []
    for col in columns:
        python_type = get_python_type(col["data_type"])
        optional_type = (
            f"Optional[{python_type}]" if col["is_nullable"] else python_type
        )

        setter = f"""    def set_{col["name"]}(self, value: {optional_type}) -> None:
        \"\"\"Set the value of {col["name"]}.\"\"\"
        self._data['{col["name"]}'] = value
        self._dirty = True"""
        setters.append(setter)

    return "\n\n".join(setters)


def generate_find_by_methods(
    columns: List[Dict[str, Any]], class_name: str, table_name: str
) -> str:
    """Generate find_by methods for columns ending with _id."""
    find_by_methods = []

    for col in columns:
        if col["name"].endswith("_id"):
            python_type = get_python_type(col["data_type"])

            method = f"""    @staticmethod
    def find_by_{col["name"]}(value: {python_type}) -> List['{class_name}']:
        \"\"\"
        Find all records by {col["name"]}.
        Returns a list of instances with matching records.
        \"\"\"
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor(dictionary=True)
        results = []
        try:
            cursor.execute(f"SELECT * FROM `{table_name}` WHERE `{col["name"]}` = %s", (value,))
            rows = cursor.fetchall()
            for row in rows:
                instance = {class_name}()
                instance._data = row
                results.append(instance)
        finally:
            cursor.close()
            connection.close()
        return results"""
            find_by_methods.append(method)

    return (
        "\n\n".join(find_by_methods)
        if find_by_methods
        else "    # No find_by methods (no columns ending with _id)"
    )


def collect_required_types(columns: List[Dict[str, Any]]) -> set:
    """Collect all unique Python types needed for the model."""
    types = set()
    for col in columns:
        python_type = get_python_type(col["data_type"])
        if python_type == "datetime":
            types.add("datetime")
        elif python_type == "Any":
            types.add("Any")
    return types


def generate_imports(columns: List[Dict[str, Any]], has_relationships: bool = False) -> str:
    """Generate import statements based on column types."""
    imports = [
        "import mysql.connector",
    ]

    # Add typing imports
    typing_imports = ["Dict", "List", "Optional", "Any"]
    if has_relationships:
        typing_imports.extend(["Iterator", "Union"])

    imports.append(f"from typing import {', '.join(typing_imports)}")

    required_types = collect_required_types(columns)
    if "datetime" in required_types:
        imports.append("from datetime import datetime")

    return "\n".join(imports)


def generate_cascade_save_code(
    belongs_to_rels: List[Dict[str, Any]],
    has_many_rels: List[Dict[str, Any]],
) -> Tuple[str, str]:
    """
    Generate cascade save code for belongs-to and has-many relationships.
    Returns (belongs_to_code, has_many_code)
    """
    # Belongs-to cascade save (save parent objects first)
    belongs_to_code = []
    for rel in belongs_to_rels:
        rel_name = get_relationship_name(rel["column"])
        column_name = rel["column"]

        code = f"""# Save {rel_name} if cached and dirty
                cache_key = '_{rel_name}_cache'
                if hasattr(self, cache_key):
                    related = getattr(self, cache_key)
                    if related is not None and hasattr(related, '_dirty') and related._dirty:
                        related.save(connection=connection, cascade=cascade)
                        # Update foreign key with saved ID
                        self._data['{column_name}'] = related.get_id()"""
        belongs_to_code.append(code)

    # Has-many cascade save (save child objects after)
    has_many_code = []
    for rel in has_many_rels:
        rel_name = rel["foreign_table"]

        code = f"""# Save {rel_name} if cached
                cache_key = '_{rel_name}_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, '_dirty') and related._dirty:
                                related.save(connection=connection, cascade=cascade)"""
        has_many_code.append(code)

    belongs_to_str = "\n".join(belongs_to_code) if belongs_to_code else "pass  # No belongs-to relationships"
    has_many_str = "\n".join(has_many_code) if has_many_code else "pass  # No has-many relationships"

    return belongs_to_str, has_many_str


def generate_model(
    table_name: str,
    columns: List[Dict[str, Any]],
    create_table_stmt: str,
    template: str,
    relationships: Dict[str, Any],
    table_columns: Dict[str, List[Dict[str, Any]]],
) -> str:
    """Generate a complete model file from the template."""
    # Convert plural table name to singular class name
    singular_name = singularize_table_name(table_name)
    class_name = to_pascal_case(singular_name)

    # Get relationships for this table
    belongs_to_rels = relationships.get("belongs_to", [])
    has_many_rels = relationships.get("has_many", [])
    has_relationships = bool(belongs_to_rels or has_many_rels)

    # Generate all components
    imports = generate_imports(columns, has_relationships)
    getters = generate_getters(columns)
    setters = generate_setters(columns)
    find_by_methods = generate_find_by_methods(columns, class_name, table_name)

    # Generate relationship methods
    belongs_to_methods = generate_belongs_to_methods(belongs_to_rels, table_columns) if belongs_to_rels else ""
    has_many_methods = generate_has_many_methods(has_many_rels, table_columns) if has_many_rels else ""

    # Generate cascade save code
    cascade_save_belongs_to, cascade_save_has_many = generate_cascade_save_code(
        belongs_to_rels,
        has_many_rels,
    )

    # Escape the CREATE TABLE statement for Python heredoc string
    # Only need to escape triple quotes if they appear in the SQL
    escaped_create_table = create_table_stmt.replace('"""', r"\"\"\"")

    # Format the CREATE TABLE statement with proper indentation
    # Split into lines and indent each line with 8 spaces (class indent + 4)
    create_table_lines = escaped_create_table.split("\n")
    indented_lines = ["        " + line for line in create_table_lines]
    formatted_create_table = "\n" + "\n".join(indented_lines) + "\n    "

    # Fill in the template
    model_code = template.format(
        imports=imports,
        class_name=class_name,
        table_name=table_name,
        create_table_statement=formatted_create_table,
        getters=getters,
        setters=setters,
        belongs_to_methods=belongs_to_methods,
        has_many_methods=has_many_methods,
        cascade_save_belongs_to=cascade_save_belongs_to,
        cascade_save_has_many=cascade_save_has_many,
        find_by_methods=find_by_methods,
    )

    return model_code


def generate_seed_data_function(models: List[Dict[str, Any]]) -> str:
    """Generate comprehensive seed data creation function."""
    code = '''
def create_seed_data():
    """Create complete graph of test data covering all relationships."""
    seed = {}

    # Create base records without foreign keys first
'''

    # Group models by dependency (those without FKs first, then those with FKs)
    models_without_fks = []
    models_with_fks = []

    for model in models:
        table_name = model['table_name']
        class_name = model['class_name']
        belongs_to_rels = model.get('relationships', {}).get('belongs_to', [])

        if not belongs_to_rels:
            models_without_fks.append(model)
        else:
            models_with_fks.append(model)

    # Create base models first (no foreign keys)
    for model in models_without_fks:
        class_name = model['class_name']
        columns = model['columns']

        # Skip pivot tables and models without required fields
        if class_name in ['AttributeOwner', 'InventoryOwner', 'InventoryEntry', 'MobileItemAttribute']:
            continue

        code += f'''    # Create {class_name} records
    seed['{class_name.lower()}1'] = {class_name}()
'''

        # Set required non-nullable fields
        for col in columns:
            if col['name'] == 'id' or col['name'].endswith('_id'):
                continue
            if not col['is_nullable']:
                python_type = get_python_type(col['data_type'])
                if python_type == 'str':
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}('test_{col['name']}_1')\n"
                elif python_type == 'int':
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}(1)\n"
                elif python_type == 'bool':
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}(True)\n"
                elif python_type == 'float':
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}(1.0)\n"

        code += f"    seed['{class_name.lower()}1'].save()\n\n"

        # Create a second instance
        code += f"    seed['{class_name.lower()}2'] = {class_name}()\n"
        for col in columns:
            if col['name'] == 'id' or col['name'].endswith('_id'):
                continue
            if not col['is_nullable']:
                python_type = get_python_type(col['data_type'])
                if python_type == 'str':
                    code += f"    seed['{class_name.lower()}2'].set_{col['name']}('test_{col['name']}_2')\n"
                elif python_type == 'int':
                    code += f"    seed['{class_name.lower()}2'].set_{col['name']}(2)\n"
                elif python_type == 'bool':
                    code += f"    seed['{class_name.lower()}2'].set_{col['name']}(True)\n"
                elif python_type == 'float':
                    code += f"    seed['{class_name.lower()}2'].set_{col['name']}(2.0)\n"

        code += f"    seed['{class_name.lower()}2'].save()\n\n"

    # Create models with foreign keys
    for model in models_with_fks:
        class_name = model['class_name']
        columns = model['columns']
        belongs_to_rels = model.get('relationships', {}).get('belongs_to', [])

        # Skip pivot tables for now
        if class_name in ['AttributeOwner', 'InventoryOwner', 'InventoryEntry', 'MobileItemAttribute']:
            continue

        code += f"    # Create {class_name} records with relationships\n"
        code += f"    seed['{class_name.lower()}1'] = {class_name}()\n"

        # Set required non-nullable fields
        for col in columns:
            if col['name'] == 'id':
                continue
            if col['name'].endswith('_id'):
                # Set foreign key if it's required
                if not col['is_nullable'] and belongs_to_rels:
                    # Find the relationship for this FK
                    for rel in belongs_to_rels:
                        if rel['column'] == col['name']:
                            target_class = to_pascal_case(singularize_table_name(rel['referenced_table']))
                            # Use seed data if available
                            seed_key = f"{target_class.lower()}1"
                            code += f"    if '{seed_key}' in seed:\n"
                            code += f"        seed['{class_name.lower()}1'].set_{col['name']}(seed['{seed_key}'].get_id())\n"
                continue
            if not col['is_nullable']:
                python_type = get_python_type(col['data_type'])
                if python_type == 'str':
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}('test_{col['name']}_1')\n"
                elif python_type == 'int':
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}(1)\n"
                elif python_type == 'bool':
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}(True)\n"
                elif python_type == 'float':
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}(1.0)\n"

        code += f"    seed['{class_name.lower()}1'].save()\n\n"

    code += '''
    return seed


def cleanup_seed_data(seed):
    """Clean up seed data in reverse dependency order."""
    # Simply let the tearDownModule handle database cleanup
    pass
'''

    return code


def generate_belongs_to_tests(model: Dict[str, Any], all_models: List[Dict[str, Any]]) -> str:
    """Generate belongs-to relationship tests for a model."""
    class_name = model['class_name']
    belongs_to_rels = model.get('relationships', {}).get('belongs_to', [])

    if not belongs_to_rels:
        return ""

    tests = []

    for rel in belongs_to_rels:
        rel_name = get_relationship_name(rel['column'])
        target_class = to_pascal_case(singularize_table_name(rel['referenced_table']))
        fk_column = rel['column']

        # Basic getter test
        test_name = f"test_belongs_to_{rel_name}_basic"
        tests.append(f'''
    def {test_name}(self):
        """Test {rel_name} relationship basic getter."""
        # Create related model
        related = {target_class}()''')

        # Set required fields for target class
        target_model = next((m for m in all_models if m['class_name'] == target_class), None)
        if target_model:
            for col in target_model.get('columns', []):
                if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
                    python_type = get_python_type(col['data_type'])
                    if python_type == 'str':
                        tests.append(f"        related.set_{col['name']}('test_{col['name']}')")
                    elif python_type == 'int':
                        tests.append(f"        related.set_{col['name']}(1)")
                    elif python_type == 'bool':
                        tests.append(f"        related.set_{col['name']}(True)")

        tests.append(f'''        related.save()

        # Create parent and set FK
        parent = {class_name}()''')

        # Set required fields for parent
        for col in model['columns']:
            if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
                python_type = get_python_type(col['data_type'])
                if python_type == 'str':
                    tests.append(f"        parent.set_{col['name']}('test_{col['name']}')")
                elif python_type == 'int':
                    tests.append(f"        parent.set_{col['name']}(1)")
                elif python_type == 'bool':
                    tests.append(f"        parent.set_{col['name']}(True)")

        tests.append(f'''        parent.set_{fk_column}(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_{rel_name}()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, {target_class})
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_{rel_name}()
        self.assertIs(result, result2)
''')

        # Setter test
        test_name = f"test_belongs_to_{rel_name}_setter"
        tests.append(f'''
    def {test_name}(self):
        """Test {rel_name} relationship setter."""
        # Create related models
        related1 = {target_class}()''')

        # Re-fetch target model for setter test
        target_model_setter = next((m for m in all_models if m['class_name'] == target_class), None)
        if target_model_setter:
            for col in target_model_setter.get('columns', []):
                if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
                    python_type = get_python_type(col['data_type'])
                    if python_type == 'str':
                        tests.append(f"        related1.set_{col['name']}('test_{col['name']}_1')")
                    elif python_type == 'int':
                        tests.append(f"        related1.set_{col['name']}(1)")
                    elif python_type == 'bool':
                        tests.append(f"        related1.set_{col['name']}(True)")

        tests.append(f'''        related1.save()

        # Create parent
        parent = {class_name}()''')

        for col in model['columns']:
            if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
                python_type = get_python_type(col['data_type'])
                if python_type == 'str':
                    tests.append(f"        parent.set_{col['name']}('test_{col['name']}')")
                elif python_type == 'int':
                    tests.append(f"        parent.set_{col['name']}(1)")
                elif python_type == 'bool':
                    tests.append(f"        parent.set_{col['name']}(True)")

        tests.append(f'''
        # Use setter
        parent.set_{rel_name}(related1)

        # Verify FK updated
        self.assertEqual(parent.get_{fk_column}(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_{rel_name}(), related1)
''')

    return "\n".join(tests)


def generate_has_many_tests(model: Dict[str, Any], all_models: List[Dict[str, Any]]) -> str:
    """Generate has-many relationship tests for a model."""
    class_name = model['class_name']
    has_many_rels = model.get('relationships', {}).get('has_many', [])

    if not has_many_rels:
        return ""

    tests = []

    for rel in has_many_rels:
        rel_name = rel['foreign_table']
        foreign_class = to_pascal_case(singularize_table_name(rel['foreign_table']))
        fk_column = rel['foreign_column']

        # Find the foreign model
        foreign_model = next((m for m in all_models if m['class_name'] == foreign_class), None)
        if not foreign_model:
            continue

        # Basic getter test
        test_name = f"test_has_many_{rel_name}_basic"
        tests.append(f'''
    def {test_name}(self):
        """Test {rel_name} relationship basic getter."""
        # Create parent
        parent = {class_name}()''')

        # Set required fields for parent
        for col in model['columns']:
            if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
                python_type = get_python_type(col['data_type'])
                if python_type == 'str':
                    tests.append(f"        parent.set_{col['name']}('test_{col['name']}')")
                elif python_type == 'int':
                    tests.append(f"        parent.set_{col['name']}(1)")
                elif python_type == 'bool':
                    tests.append(f"        parent.set_{col['name']}(True)")

        tests.append("        parent.save()\n\n")

        # Find other required FK columns and create those records first
        prereq_records = {}
        for col in foreign_model['columns']:
            if col['name'] != 'id' and col['name'] != fk_column and col['name'].endswith('_id') and not col['is_nullable']:
                # Need to create a prerequisite record
                prereq_table = col['name'][:-3]  # Remove '_id' suffix
                prereq_class = to_pascal_case(singularize_table_name(prereq_table + 's'))  # Pluralize and convert

                # Find the prerequisite model
                prereq_model = next((m for m in all_models if m['table_name'] == (prereq_table + 's')), None)
                if not prereq_model:
                    # Try singular form
                    prereq_model = next((m for m in all_models if m['table_name'] == prereq_table), None)

                if prereq_model:
                    prereq_var = f"{prereq_table}_prereq"
                    prereq_records[col['name']] = prereq_var

                    tests.append(f"        # Create prerequisite {prereq_class} for {col['name']}\n")
                    tests.append(f"        {prereq_var} = {prereq_model['class_name']}()\n")

                    # Set required fields for prerequisite
                    for prereq_col in prereq_model['columns']:
                        if prereq_col['name'] != 'id' and not prereq_col['is_nullable'] and not prereq_col['name'].endswith('_id'):
                            py_type = get_python_type(prereq_col['data_type'])
                            if py_type == 'str':
                                tests.append(f"        {prereq_var}.set_{prereq_col['name']}('test_prereq')\n")
                            elif py_type == 'int':
                                tests.append(f"        {prereq_var}.set_{prereq_col['name']}(1)\n")
                            elif py_type == 'bool':
                                tests.append(f"        {prereq_var}.set_{prereq_col['name']}(True)\n")

                    tests.append(f"        {prereq_var}.save()\n\n")

        tests.append(f'''        # Create related records
        child1 = {foreign_class}()''')

        # Set required fields for child
        for col in foreign_model['columns']:
            if col['name'] != 'id' and not col['is_nullable']:
                if col['name'] == fk_column:
                    tests.append(f"        child1.set_{col['name']}(parent.get_id())")
                elif col['name'].endswith('_id'):
                    # Use prerequisite record if available
                    if col['name'] in prereq_records:
                        tests.append(f"        child1.set_{col['name']}({prereq_records[col['name']]}.get_id())")
                    else:
                        tests.append(f"        child1.set_{col['name']}(1)")
                else:
                    python_type = get_python_type(col['data_type'])
                    if python_type == 'str':
                        tests.append(f"        child1.set_{col['name']}('test_{col['name']}_1')")
                    elif python_type == 'int':
                        tests.append(f"        child1.set_{col['name']}(1)")
                    elif python_type == 'bool':
                        tests.append(f"        child1.set_{col['name']}(True)")

        tests.append(f'''        child1.save()

        child2 = {foreign_class}()''')

        for col in foreign_model['columns']:
            if col['name'] != 'id' and not col['is_nullable']:
                if col['name'] == fk_column:
                    tests.append(f"        child2.set_{col['name']}(parent.get_id())")
                elif col['name'].endswith('_id'):
                    # Use prerequisite record if available
                    if col['name'] in prereq_records:
                        tests.append(f"        child2.set_{col['name']}({prereq_records[col['name']]}.get_id())")
                    else:
                        tests.append(f"        child2.set_{col['name']}(1)")
                else:
                    python_type = get_python_type(col['data_type'])
                    if python_type == 'str':
                        tests.append(f"        child2.set_{col['name']}('test_{col['name']}_2')")
                    elif python_type == 'int':
                        tests.append(f"        child2.set_{col['name']}(2)")
                    elif python_type == 'bool':
                        tests.append(f"        child2.set_{col['name']}(True)")

        tests.append(f'''        child2.save()

        # Test getter (eager mode)
        results = parent.get_{rel_name}(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_{rel_name}(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_{rel_name}(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)
''')

        # Lazy mode test
        test_name = f"test_has_many_{rel_name}_lazy"
        tests.append(f'''
    def {test_name}(self):
        """Test {rel_name} relationship lazy loading."""
        # Create parent with children
        parent = {class_name}()''')

        for col in model['columns']:
            if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
                python_type = get_python_type(col['data_type'])
                if python_type == 'str':
                    tests.append(f"        parent.set_{col['name']}('test_{col['name']}')")
                elif python_type == 'int':
                    tests.append(f"        parent.set_{col['name']}(1)")
                elif python_type == 'bool':
                    tests.append(f"        parent.set_{col['name']}(True)")

        tests.append("        parent.save()\n\n")

        # Create prerequisite records for lazy test too
        prereq_records_lazy = {}
        for col in foreign_model['columns']:
            if col['name'] != 'id' and col['name'] != fk_column and col['name'].endswith('_id') and not col['is_nullable']:
                # Need to create a prerequisite record
                prereq_table = col['name'][:-3]
                prereq_class = to_pascal_case(singularize_table_name(prereq_table + 's'))

                # Find the prerequisite model
                prereq_model = next((m for m in all_models if m['table_name'] == (prereq_table + 's')), None)
                if not prereq_model:
                    prereq_model = next((m for m in all_models if m['table_name'] == prereq_table), None)

                if prereq_model:
                    prereq_var = f"{prereq_table}_prereq_lazy"
                    prereq_records_lazy[col['name']] = prereq_var

                    tests.append(f"        # Create prerequisite {prereq_model['class_name']} for {col['name']}\n")
                    tests.append(f"        {prereq_var} = {prereq_model['class_name']}()\n")

                    # Set required fields for prerequisite
                    for prereq_col in prereq_model['columns']:
                        if prereq_col['name'] != 'id' and not prereq_col['is_nullable'] and not prereq_col['name'].endswith('_id'):
                            py_type = get_python_type(prereq_col['data_type'])
                            if py_type == 'str':
                                tests.append(f"        {prereq_var}.set_{prereq_col['name']}('test_prereq_lazy')\n")
                            elif py_type == 'int':
                                tests.append(f"        {prereq_var}.set_{prereq_col['name']}(1)\n")
                            elif py_type == 'bool':
                                tests.append(f"        {prereq_var}.set_{prereq_col['name']}(True)\n")

                    tests.append(f"        {prereq_var}.save()\n\n")

        tests.append(f'''        # Create child
        child = {foreign_class}()''')

        for col in foreign_model['columns']:
            if col['name'] != 'id' and not col['is_nullable']:
                if col['name'] == fk_column:
                    tests.append(f"        child.set_{col['name']}(parent.get_id())")
                elif col['name'].endswith('_id'):
                    # Use prerequisite record if available
                    if col['name'] in prereq_records_lazy:
                        tests.append(f"        child.set_{col['name']}({prereq_records_lazy[col['name']]}.get_id())")
                    else:
                        tests.append(f"        child.set_{col['name']}(1)")
                else:
                    python_type = get_python_type(col['data_type'])
                    if python_type == 'str':
                        tests.append(f"        child.set_{col['name']}('test_{col['name']}')")
                    elif python_type == 'int':
                        tests.append(f"        child.set_{col['name']}(1)")
                    elif python_type == 'bool':
                        tests.append(f"        child.set_{col['name']}(True)")

        tests.append(f'''        child.save()

        # Test lazy mode
        results_iter = parent.get_{rel_name}(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], {foreign_class})
''')

    return "\n".join(tests)


def generate_dirty_tracking_tests(model: Dict[str, Any]) -> str:
    """Generate dirty tracking tests for a model."""
    class_name = model['class_name']
    columns = model['columns']

    # Find a settable column for testing
    test_col = None
    for col in columns:
        if col['name'] != 'id' and not col['name'].endswith('_id') and not col['is_nullable']:
            test_col = col
            break

    if not test_col:
        return ""

    python_type = get_python_type(test_col['data_type'])
    if python_type == 'str':
        test_value1 = "'test_value_1'"
        test_value2 = "'test_value_2'"
    elif python_type == 'int':
        test_value1 = "1"
        test_value2 = "2"
    elif python_type == 'bool':
        test_value1 = "True"
        test_value2 = "False"
    elif python_type == 'float':
        test_value1 = "1.0"
        test_value2 = "2.0"
    else:
        return ""

    tests = f'''
    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = {class_name}()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = {class_name}()'''

    # Set required fields
    for col in columns:
        if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
            py_type = get_python_type(col['data_type'])
            if py_type == 'str':
                tests += f"\n        model.set_{col['name']}('test_{col['name']}')"
            elif py_type == 'int':
                tests += f"\n        model.set_{col['name']}(1)"
            elif py_type == 'bool':
                tests += f"\n        model.set_{col['name']}(True)"
            elif py_type == 'float':
                tests += f"\n        model.set_{col['name']}(1.0)"

    tests += f'''
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = {class_name}()'''

    for col in columns:
        if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
            py_type = get_python_type(col['data_type'])
            if py_type == 'str':
                tests += f"\n        model.set_{col['name']}('test_{col['name']}')"
            elif py_type == 'int':
                tests += f"\n        model.set_{col['name']}(1)"
            elif py_type == 'bool':
                tests += f"\n        model.set_{col['name']}(True)"
            elif py_type == 'float':
                tests += f"\n        model.set_{col['name']}(1.0)"

    tests += f'''
        model.save()
        self.assertFalse(model._dirty)

        model.set_{test_col['name']}({test_value2})
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = {class_name}()'''

    for col in columns:
        if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
            py_type = get_python_type(col['data_type'])
            if py_type == 'str':
                tests += f"\n        model.set_{col['name']}('test_{col['name']}')"
            elif py_type == 'int':
                tests += f"\n        model.set_{col['name']}(1)"
            elif py_type == 'bool':
                tests += f"\n        model.set_{col['name']}(True)"
            elif py_type == 'float':
                tests += f"\n        model.set_{col['name']}(1.0)"

    tests += f'''
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)
'''

    return tests


def generate_cascade_save_tests(model: Dict[str, Any], all_models: List[Dict[str, Any]]) -> str:
    """Generate cascade save tests for a model."""
    class_name = model['class_name']
    belongs_to_rels = model.get('relationships', {}).get('belongs_to', [])

    if not belongs_to_rels:
        return ""

    # Take first belongs-to relationship for testing
    rel = belongs_to_rels[0]
    rel_name = get_relationship_name(rel['column'])
    target_class = to_pascal_case(singularize_table_name(rel['referenced_table']))

    # Find target model
    target_model = next((m for m in all_models if m['class_name'] == target_class), None)
    if not target_model:
        return ""

    tests = f'''
    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = {target_class}()'''

    # Set required fields for target
    for col in target_model.get('columns', []):
        if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
            python_type = get_python_type(col['data_type'])
            if python_type == 'str':
                tests += f"\n        related.set_{col['name']}('test_{col['name']}')"
            elif python_type == 'int':
                tests += f"\n        related.set_{col['name']}(1)"
            elif python_type == 'bool':
                tests += f"\n        related.set_{col['name']}(True)"

    tests += f'''
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = {class_name}()'''

    # Set required fields for parent
    for col in model['columns']:
        if col['name'] != 'id' and not col['is_nullable'] and not col['name'].endswith('_id'):
            python_type = get_python_type(col['data_type'])
            if python_type == 'str':
                tests += f"\n        parent.set_{col['name']}('test_{col['name']}')"
            elif python_type == 'int':
                tests += f"\n        parent.set_{col['name']}(1)"
            elif python_type == 'bool':
                tests += f"\n        parent.set_{col['name']}(True)"

    tests += f'''
        parent.set_{rel_name}(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)
'''

    return tests


def generate_tests(models: List[Dict[str, Any]]) -> str:
    """Generate comprehensive tests.py file for all models with relationship testing."""
    imports = [
        "import unittest",
        "import mysql.connector",
        "import os",
        "import uuid",
        "from dotenv import load_dotenv",
    ]

    # Import all models from the single models.py file
    class_names = [model['class_name'] for model in models]
    imports.append(f"from models import {', '.join(class_names)}")

    # Generate module-level setup/teardown
    module_setup = """
# Load environment variables
load_dotenv()

# Global test database name
TEST_DATABASE = None


def setUpModule():
    \"\"\"Create a temporary test database and all tables before running any tests.\"\"\"
    global TEST_DATABASE
    # Generate unique test database name
    TEST_DATABASE = f"gamedb_test_{uuid.uuid4().hex[:8]}"

    # Connect to MySQL (without database selected)
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        auth_plugin='mysql_native_password',
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()

    try:
        # Create test database
        cursor.execute(f"CREATE DATABASE `{TEST_DATABASE}`")
        connection.database = TEST_DATABASE

        # Disable foreign key checks to allow creating tables in any order
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")

        # Create all tables using CREATE TABLE statements from models"""

    # Add table creation for each model
    for model in models:
        module_setup += f"""
        # Create {model["table_name"]} table
        cursor.execute({model["class_name"]}.CREATE_TABLE_STATEMENT)"""

    module_setup += """

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")

        connection.commit()
        print(f"Created test database: {TEST_DATABASE}")
    finally:
        cursor.close()
        connection.close()

    # Temporarily override the DB_DATABASE environment variable for tests
    os.environ['DB_DATABASE'] = TEST_DATABASE


def tearDownModule():
    \"\"\"Drop the temporary test database after all tests complete.\"\"\"
    global TEST_DATABASE
    if TEST_DATABASE:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor()
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DATABASE}`")
            connection.commit()
            print(f"Dropped test database: {TEST_DATABASE}")
        finally:
            cursor.close()
            connection.close()
"""

    # Generate seed data function
    seed_data_code = generate_seed_data_function(models)

    test_classes = []
    for model in models:
        class_name = model["class_name"]

        # Generate comprehensive relationship tests
        test_class = f"""

class Test{class_name}Relationships(unittest.TestCase):
    \"\"\"Comprehensive relationship tests for {class_name} model.\"\"\"

    def setUp(self):
        \"\"\"Set up test fixtures.\"\"\"
        self.model = {class_name}()
"""

        # Add belongs-to tests
        belongs_to_tests = generate_belongs_to_tests(model, models)
        if belongs_to_tests:
            test_class += belongs_to_tests

        # Add has-many tests
        has_many_tests = generate_has_many_tests(model, models)
        if has_many_tests:
            test_class += has_many_tests

        # Add dirty tracking tests
        dirty_tests = generate_dirty_tracking_tests(model)
        if dirty_tests:
            test_class += dirty_tests

        # Add cascade save tests
        cascade_tests = generate_cascade_save_tests(model, models)
        if cascade_tests:
            test_class += cascade_tests

        test_classes.append(test_class)

    # Combine everything
    test_code = "\n".join(imports)
    test_code += "\nfrom datetime import datetime"
    test_code += module_setup
    test_code += seed_data_code
    test_code += "\n".join(test_classes)
    test_code += """


if __name__ == '__main__':
    unittest.main()
"""

    return test_code


def main():
    parser = argparse.ArgumentParser(
        description="Generate ActiveRecord-style models from MySQL tables"
    )
    # No arguments needed - everything comes from .env
    args = parser.parse_args()

    # Get database credentials from environment variables
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_database = os.getenv("DB_DATABASE")

    if not all([db_host, db_user, db_password, db_database]):
        print("ERROR: Missing database credentials in .env file")
        print("Please ensure DB_HOST, DB_USER, DB_PASSWORD, and DB_DATABASE are set")
        return 1

    # Connect to database
    print(f"Connecting to {db_host}/{db_database}...")
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database,
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )

    cursor = connection.cursor()

    try:
        # Load template
        template_path = os.path.join(
            os.path.dirname(__file__),
            "templates",
            "model_template.py.tmpl",
        )
        with open(template_path, "r") as f:
            template = f.read()

        # Get all tables
        tables = get_all_tables(cursor, db_database)
        print(f"Found {len(tables)} tables: {', '.join(tables)}")

        # Get foreign key constraints
        print("\nDetecting foreign key constraints...")
        fk_constraints = get_foreign_key_constraints(cursor, db_database)
        print(f"  - Found {sum(len(v) for v in fk_constraints.values())} foreign key constraints")

        # Get unique constraints
        print("Detecting unique constraints...")
        unique_constraints = get_unique_constraints(cursor, db_database)
        print(f"  - Found {sum(len(v) for v in unique_constraints.values())} unique constraints")

        # Get columns for all tables
        print("Loading column information...")
        table_columns = {}
        for table_name in tables:
            table_columns[table_name] = get_table_columns(cursor, db_database, table_name)

        # Build relationship metadata
        print("Building relationship metadata...")
        all_relationships = build_relationship_metadata(
            tables,
            table_columns,
            fk_constraints,
            unique_constraints,
        )

        # Print relationship summary
        total_belongs_to = sum(len(r["belongs_to"]) for r in all_relationships.values())
        total_has_many = sum(len(r["has_many"]) for r in all_relationships.values())
        print(f"  - Detected {total_belongs_to} belongs-to relationships")
        print(f"  - Detected {total_has_many} has-many relationships")

        # Generate all models into a single file
        print("\nGenerating single models.py file...")
        models_output = []
        generated_models = []

        # Collect all imports needed
        all_imports = set()
        all_imports.add("import mysql.connector")
        all_imports.add("import os")
        all_imports.add("from dotenv import load_dotenv")
        all_imports.add("from typing import Dict, List, Optional, Any, Iterator, Union")

        # Check if any model needs datetime
        needs_datetime = any(
            any(get_python_type(col["data_type"]) == "datetime" for col in table_columns[table])
            for table in tables
        )
        if needs_datetime:
            all_imports.add("from datetime import datetime")

        # Add header
        models_output.append("#!/usr/bin/env python3")
        models_output.append('"""')
        models_output.append("Auto-generated model classes for all database tables.")
        models_output.append("Generated from database schema - do not modify manually.")
        models_output.append('"""')
        models_output.append("")
        models_output.append("\n".join(sorted(all_imports)))
        models_output.append("")
        models_output.append("# Load environment variables")
        models_output.append("load_dotenv()")
        models_output.append("")
        models_output.append("# Database configuration from environment")
        models_output.append("DB_HOST = os.getenv('DB_HOST')")
        models_output.append("DB_USER = os.getenv('DB_USER')")
        models_output.append("DB_PASSWORD = os.getenv('DB_PASSWORD')")
        models_output.append("DB_DATABASE = os.getenv('DB_DATABASE')")
        models_output.append("")
        models_output.append("")

        # Generate each model class
        for table_name in tables:
            print(f"  - Generating class for table: {table_name}")
            columns = table_columns[table_name]
            relationships = all_relationships[table_name]

            # Extract CREATE TABLE statement
            create_table_stmt = get_create_table_statement(cursor, table_name)

            # Generate model code
            model_code = generate_model(
                table_name,
                columns,
                create_table_stmt,
                template,
                relationships,
                table_columns,
            )

            # Extract just the class definition (remove imports and env setup)
            # Split by class definition and take everything from "class" onward
            class_start = model_code.find("class ")
            if class_start > 0:
                model_class_code = model_code[class_start:]
                models_output.append(model_class_code)
                models_output.append("")
                models_output.append("")

            # Track generated model
            singular_name = singularize_table_name(table_name)
            generated_models.append(
                {
                    "table_name": table_name,
                    "class_name": to_pascal_case(singular_name),
                    "columns": columns,
                    "relationships": relationships,
                }
            )

        # Write single models.py file
        models_file = os.path.join(os.path.dirname(__file__), "models.py")
        with open(models_file, "w") as f:
            f.write("\n".join(models_output))

        print(f"✓ Written all {len(generated_models)} models to {models_file}")

        # Delete old individual model files
        print("\nCleaning up old individual model files...")
        for model_info in generated_models:
            singular_name = singularize_table_name(model_info["table_name"])
            old_file = os.path.join(os.path.dirname(__file__), f"{singular_name}.py")
            if os.path.exists(old_file):
                os.remove(old_file)
                print(f"  - Deleted {old_file}")

        print(f"\n✓ Successfully generated {len(generated_models)} models in single file!")

        # Generate tests
        print("\nGenerating tests.py...")
        test_code = generate_tests(generated_models)
        test_file = os.path.join(os.path.dirname(__file__), "tests.py")
        with open(test_file, "w") as f:
            f.write(test_code)
        print(f"  - Written to {test_file}")

        print(f"\n✓ Code generation complete!")
        print(f"  - {len(generated_models)} models generated")
        print(f"  - tests.py generated")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
