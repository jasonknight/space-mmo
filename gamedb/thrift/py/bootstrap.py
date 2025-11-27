#!/usr/bin/env python3
"""
Bootstrap script to create the gamedb database and all necessary tables.
"""

import sys

sys.path.append("../gen-py")

from db import DB


def check_column_exists(cursor, database, table, column):
    """Check if a column exists in a table."""
    cursor.execute(
        """
        SELECT COUNT(*) as col_exists
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = %s
        AND COLUMN_NAME = %s;
        """,
        (
            database,
            table,
            column,
        ),
    )
    result = cursor.fetchone()
    return result[0] > 0


def add_column_if_not_exists(
    cursor,
    database,
    table,
    column,
    column_def,
):
    """Add a column to a table if it doesn't already exist."""
    if check_column_exists(cursor, database, table, column):
        print(f"   - Column {column} already exists in {table}")
        return False
    else:
        alter_sql = f"ALTER TABLE {database}.{table} ADD COLUMN {column} {column_def};"
        cursor.execute(alter_sql)
        print(f"   ✓ Added column {column} to {table}")
        return True


def apply_migrations(db, database_name):
    """Apply schema migrations to existing tables."""
    print(f"\n4. Applying schema migrations to '{database_name}'...")

    try:
        cursor = db.connection.cursor()

        # Migration: Add mobile_item_id to inventory_entries
        add_column_if_not_exists(
            cursor,
            database_name,
            "inventory_entries",
            "mobile_item_id",
            "BIGINT NULL",
        )

        db.connection.commit()
        cursor.close()
        print("   ✓ All migrations applied successfully")
        return True
    except Exception as e:
        print(f"   ✗ Error applying migrations: {e}")
        db.connection.rollback()
        return False


def main():
    """Create the gamedb database and all tables."""
    print("=" * 60)
    print("Database Bootstrap Script")
    print("=" * 60)

    # Initialize database connection
    db = DB(
        host="localhost",
        user="admin",
        password="minda",
    )

    database_name = "gamedb"

    try:
        print(f"\n1. Connecting to MySQL server...")
        db.connect()
        cursor = db.connection.cursor()

        print(f"2. Creating database '{database_name}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name};")
        db.connection.commit()
        print(f"   ✓ Database '{database_name}' created (or already exists)")

        print(f"\n3. Creating tables in '{database_name}'...")

        # Create players table
        print("   - Creating players table...")
        for stmt in db.get_players_table_sql(database_name):
            cursor.execute(stmt)

        # Create mobiles table
        print("   - Creating mobiles table...")
        for stmt in db.get_mobiles_table_sql(database_name):
            cursor.execute(stmt)

        # Create items table
        print("   - Creating items table...")
        for stmt in db.get_items_table_sql(database_name):
            cursor.execute(stmt)

        # Create item_blueprints table
        print("   - Creating item_blueprints table...")
        for stmt in db.get_item_blueprints_table_sql(database_name):
            cursor.execute(stmt)

        # Create item_blueprint_components table
        print("   - Creating item_blueprint_components table...")
        for stmt in db.get_item_blueprint_components_table_sql(database_name):
            cursor.execute(stmt)

        # Create attributes table
        print("   - Creating attributes table...")
        for stmt in db.get_attributes_table_sql(database_name):
            cursor.execute(stmt)

        # Create attribute_owners table
        print("   - Creating attribute_owners table...")
        for stmt in db.get_attribute_owners_table_sql(database_name):
            cursor.execute(stmt)

        # Create inventories table
        print("   - Creating inventories table...")
        for stmt in db.get_inventories_table_sql(database_name):
            cursor.execute(stmt)

        # Create inventory_entries table
        print("   - Creating inventory_entries table...")
        for stmt in db.get_inventory_entries_table_sql(database_name):
            cursor.execute(stmt)

        # Create inventory_owners table
        print("   - Creating inventory_owners table...")
        for stmt in db.get_inventory_owners_table_sql(database_name):
            cursor.execute(stmt)

        # Create mobile_items table
        print("   - Creating mobile_items table...")
        for stmt in db.get_mobile_items_table_sql(database_name):
            cursor.execute(stmt)

        # Create mobile_item_blueprints table
        print("   - Creating mobile_item_blueprints table...")
        for stmt in db.get_mobile_item_blueprints_table_sql(database_name):
            cursor.execute(stmt)

        # Create mobile_item_blueprint_components table
        print("   - Creating mobile_item_blueprint_components table...")
        for stmt in db.get_mobile_item_blueprint_components_table_sql(database_name):
            cursor.execute(stmt)

        # Create mobile_item_attributes table
        print("   - Creating mobile_item_attributes table...")
        for stmt in db.get_mobile_item_attributes_table_sql(database_name):
            cursor.execute(stmt)

        db.connection.commit()
        print("\n   ✓ All tables created successfully")

        # Apply schema migrations
        apply_migrations(db, database_name)

        cursor.close()
        db.disconnect()

        print("\n" + "=" * 60)
        print("Bootstrap completed successfully!")
        print(f"Database: {database_name}")
        print(f"Host: localhost")
        print(f"User: admin")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during bootstrap: {e}")
        db.disconnect()
        sys.exit(1)


if __name__ == "__main__":
    main()
