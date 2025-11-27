"""
Centralized table creation SQL statements for the game database.

All table schemas are based on the authoritative MySQL database.
Each table creation statement uses {database} as a format placeholder
to allow dynamic database naming.
"""

# Dictionary mapping table names to their CREATE TABLE SQL statements
TABLE_SCHEMAS = {
    "players": (
        "CREATE TABLE IF NOT EXISTS {database}.players ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "full_name VARCHAR(255) NOT NULL, "
        "what_we_call_you VARCHAR(255) NOT NULL, "
        "security_token VARCHAR(255) NOT NULL, "
        "over_13 BOOLEAN NOT NULL, "
        "year_of_birth BIGINT NOT NULL, "
        "email VARCHAR(255) NOT NULL"
        ");"
    ),
    "mobiles": (
        "CREATE TABLE IF NOT EXISTS {database}.mobiles ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "mobile_type VARCHAR(50) NOT NULL, "
        "owner_mobile_id BIGINT, "
        "owner_item_id BIGINT, "
        "owner_asset_id BIGINT, "
        "owner_player_id BIGINT, "
        "what_we_call_you VARCHAR(255) NOT NULL"
        ");"
    ),
    "attributes": (
        "CREATE TABLE IF NOT EXISTS {database}.attributes ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "internal_name VARCHAR(255) NOT NULL, "
        "visible BOOLEAN NOT NULL, "
        "attribute_type VARCHAR(50) NOT NULL, "
        "bool_value BOOLEAN, "
        "double_value DOUBLE, "
        "vector3_x DOUBLE, "
        "vector3_y DOUBLE, "
        "vector3_z DOUBLE, "
        "asset_id BIGINT"
        ");"
    ),
    "attribute_owners": (
        "CREATE TABLE IF NOT EXISTS {database}.attribute_owners ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "attribute_id BIGINT NOT NULL, "
        "mobile_id BIGINT, "
        "item_id BIGINT, "
        "asset_id BIGINT, "
        "player_id BIGINT, "
        "FOREIGN KEY (attribute_id) REFERENCES {database}.attributes(id)"
        ");"
    ),
    "items": (
        "CREATE TABLE IF NOT EXISTS {database}.items ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "internal_name VARCHAR(255) NOT NULL, "
        "max_stack_size BIGINT, "
        "item_type VARCHAR(50) NOT NULL, "
        "blueprint_id BIGINT"
        ");"
    ),
    "item_blueprints": (
        "CREATE TABLE IF NOT EXISTS {database}.item_blueprints ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "bake_time_ms BIGINT NOT NULL"
        ");"
    ),
    "item_blueprint_components": (
        "CREATE TABLE IF NOT EXISTS {database}.item_blueprint_components ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "item_blueprint_id BIGINT NOT NULL, "
        "component_item_id BIGINT NOT NULL, "
        "ratio DOUBLE NOT NULL, "
        "FOREIGN KEY (item_blueprint_id) REFERENCES {database}.item_blueprints(id)"
        ");"
    ),
    "inventories": (
        "CREATE TABLE IF NOT EXISTS {database}.inventories ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "owner_id BIGINT NOT NULL, "
        "owner_type VARCHAR(50), "
        "max_entries BIGINT NOT NULL, "
        "max_volume DOUBLE NOT NULL, "
        "last_calculated_volume DOUBLE DEFAULT 0"
        ");"
    ),
    "inventory_entries": (
        "CREATE TABLE IF NOT EXISTS {database}.inventory_entries ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "inventory_id BIGINT NOT NULL, "
        "item_id BIGINT NOT NULL, "
        "quantity DOUBLE NOT NULL, "
        "is_max_stacked BOOLEAN DEFAULT FALSE, "
        "mobile_item_id BIGINT, "
        "FOREIGN KEY (inventory_id) REFERENCES {database}.inventories(id)"
        ");"
    ),
    "inventory_owners": (
        "CREATE TABLE IF NOT EXISTS {database}.inventory_owners ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "inventory_id BIGINT NOT NULL, "
        "mobile_id BIGINT, "
        "item_id BIGINT, "
        "asset_id BIGINT, "
        "player_id BIGINT, "
        "FOREIGN KEY (inventory_id) REFERENCES {database}.inventories(id)"
        ");"
    ),
    "mobile_items": (
        "CREATE TABLE IF NOT EXISTS {database}.mobile_items ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "mobile_id BIGINT NOT NULL, "
        "internal_name VARCHAR(255) NOT NULL, "
        "max_stack_size BIGINT, "
        "item_type VARCHAR(50) NOT NULL, "
        "blueprint_id BIGINT, "
        "item_id BIGINT NOT NULL"
        ");"
    ),
    "mobile_item_blueprints": (
        "CREATE TABLE IF NOT EXISTS {database}.mobile_item_blueprints ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "bake_time_ms BIGINT NOT NULL"
        ");"
    ),
    "mobile_item_blueprint_components": (
        "CREATE TABLE IF NOT EXISTS {database}.mobile_item_blueprint_components ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "item_blueprint_id BIGINT NOT NULL, "
        "component_item_id BIGINT NOT NULL, "
        "ratio DOUBLE NOT NULL, "
        "FOREIGN KEY (item_blueprint_id) REFERENCES {database}.mobile_item_blueprints(id)"
        ");"
    ),
    "mobile_item_attributes": (
        "CREATE TABLE IF NOT EXISTS {database}.mobile_item_attributes ("
        "id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        "mobile_item_id BIGINT NOT NULL, "
        "internal_name VARCHAR(255) NOT NULL, "
        "visible BOOLEAN NOT NULL, "
        "attribute_type VARCHAR(50) NOT NULL, "
        "bool_value BOOLEAN, "
        "double_value DOUBLE, "
        "vector3_x DOUBLE, "
        "vector3_y DOUBLE, "
        "vector3_z DOUBLE, "
        "asset_id BIGINT, "
        "FOREIGN KEY (mobile_item_id) REFERENCES {database}.mobile_items(id)"
        ");"
    ),
}


def get_table_sql(table_name: str, database: str) -> str:
    """
    Get the CREATE TABLE SQL for a specific table.

    Args:
        table_name: Name of the table
        database: Database name to use in the SQL

    Returns:
        SQL statement with database name formatted in

    Raises:
        KeyError: If table_name is not found in TABLE_SCHEMAS
    """
    if table_name not in TABLE_SCHEMAS:
        raise KeyError(
            f"Table '{table_name}' not found. "
            f"Available tables: {', '.join(TABLE_SCHEMAS.keys())}"
        )
    return TABLE_SCHEMAS[table_name].format(database=database)
