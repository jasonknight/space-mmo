"""
Database introspection utilities for reading schema information.
"""

from typing import Dict, List, Any


def decode_if_bytes(val: Any) -> Any:
    """
    Decode bytes to string if necessary.

    Args:
        val: Value that might be bytes or string

    Returns:
        String value, decoded if it was bytes

    Examples:
        >>> decode_if_bytes(b'hello')
        'hello'
        >>> decode_if_bytes('hello')
        'hello'
    """
    return val.decode("utf-8") if isinstance(val, bytes) else val


def get_table_columns(cursor, database: str, table_name: str) -> List[Dict[str, Any]]:
    """
    Get column information for a table.

    Args:
        cursor: Database cursor
        database: Database name
        table_name: Table name

    Returns:
        List of column definitions with keys: name, data_type, is_nullable,
        is_primary_key, column_type
    """
    cursor.execute(
        """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """,
        (database, table_name),
    )

    columns = []
    for row in cursor.fetchall():
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
    """
    Get all table names in the database.

    Args:
        cursor: Database cursor
        database: Database name

    Returns:
        List of table names
    """
    cursor.execute(
        """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """,
        (database,),
    )

    return [decode_if_bytes(row[0]) for row in cursor.fetchall()]


def get_create_table_statement(cursor, table_name: str) -> str:
    """
    Get the CREATE TABLE statement for a table.

    Args:
        cursor: Database cursor
        table_name: Table name

    Returns:
        CREATE TABLE statement as string
    """
    cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
    result = cursor.fetchone()

    # Result is (table_name, create_statement)
    create_statement = decode_if_bytes(result[1])
    return create_statement


def get_foreign_key_constraints(cursor, database: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Get all foreign key constraints from the database.

    Args:
        cursor: Database cursor
        database: Database name

    Returns:
        Dict mapping table names to lists of FK constraint definitions.
        Each constraint has keys: column, referenced_table, referenced_column
    """
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
    """
    Get all unique constraints from the database.

    Args:
        cursor: Database cursor
        database: Database name

    Returns:
        Dict mapping table names to lists of unique column names
    """
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

    unique_constraints = {}
    for row in cursor.fetchall():
        table_name = decode_if_bytes(row[0])
        column_name = decode_if_bytes(row[1])

        if table_name not in unique_constraints:
            unique_constraints[table_name] = []

        unique_constraints[table_name].append(column_name)

    return unique_constraints
