"""
Configuration for model generation including table mappings and Thrift conversions.

This module defines mappings between database tables and Thrift structs,
union field configurations, validation rules for Owner unions, and 1-to-1
relationship specifications.

ATTRIBUTE RELATIONSHIP PATTERNS:
--------------------------------
Tables can relate to attributes in two ways:

1. PIVOT PATTERN (items, mobiles):
   - Uses attribute_owners pivot table
   - attribute_owners has FK to table (item_id, mobile_id)
   - attribute_owners has FK to attributes (attribute_id)
   - Generates: get_attributes(), add_attribute(), remove_attribute(), set_attributes()

2. DIRECT PATTERN (mobile_items):
   - Has dedicated table: {table_singular}_attributes
   - Direct FK from attribute table to parent (mobile_item_id)
   - Attribute data stored denormalized (not referencing attributes table)
   - Generates: get_attributes() that converts to Attribute objects for Thrift

ADDING NEW TABLE MAPPINGS:
--------------------------
When adding a new table that should have Thrift conversion support:

1. Add entry to TABLE_TO_THRIFT_MAPPING:
   TABLE_TO_THRIFT_MAPPING = {
       ...
       'your_table_name': 'YourThriftStructName',
   }

2. If the table uses Owner union (has owner_*_id columns), specify valid owner types:
   VALID_OWNER_TYPES = {
       ...
       'your_table_name': ['player', 'mobile', 'item', 'asset'],  # or subset
   }

3. If the table has a 1-to-1 relationship from another table:
   ONE_TO_ONE_RELATIONSHIPS = {
       'parent_table': {
           'your_table_name': 'foreign_key_column',
       },
   }

4. If the table needs special Thrift conversion handling:
   THRIFT_CONVERSION_CONFIG = {
       'your_table_name': {
           'has_attribute_map': True,  # if it has attributes via pivot table
           'has_embedded_relation': True,  # if it embeds related objects in Thrift
       },
   }

EXAMPLE:
--------
Adding a 'vehicles' table with Thrift struct 'Vehicle':

    TABLE_TO_THRIFT_MAPPING = {
        ...
        'vehicles': 'Vehicle',
    }

    # Vehicles can be owned by player or mobile only
    VALID_OWNER_TYPES = {
        ...
        'vehicles': ['player', 'mobile'],
    }

    # Player has one vehicle (1-to-1)
    ONE_TO_ONE_RELATIONSHIPS = {
        'players': {
            ...
            'vehicles': 'owner_player_id',
        },
    }
"""

from typing import List, Dict, Any, Optional

# Owner union columns used in various tables
# These columns represent the flattened Owner union from Thrift
OWNER_COLUMNS = [
    'owner_player_id',
    'owner_mobile_id',
    'owner_item_id',
    'owner_asset_id',
]

# AttributeValue union columns (flattened in attributes table)
# These columns represent the flattened AttributeValue union from Thrift
ATTRIBUTE_VALUE_COLUMNS = [
    'bool_value',
    'double_value',
    'vector3_x',
    'vector3_y',
    'vector3_z',
    'asset_id',
]

# Pivot table configuration
# These tables manage many-to-many relationships and do NOT have direct Thrift equivalents
# They are converted to/from Thrift maps or embedded relationships
PIVOT_TABLES = [
    'attribute_owners',
    'inventory_owners',
]

# Table-to-Thrift struct mapping
# Maps database table names to their corresponding Thrift struct names
# Pivot tables and internal-only tables are excluded as they don't have 1:1 Thrift representations
TABLE_TO_THRIFT_MAPPING = {
    'players': 'Player',
    'items': 'Item',
    'mobiles': 'Mobile',
    'inventories': 'Inventory',
    'inventory_entries': 'InventoryEntry',
    'attributes': 'Attribute',
    'item_blueprints': 'ItemBlueprint',
    'item_blueprint_components': 'ItemBlueprintComponent',
    'mobile_items': 'MobileItem',
}

# One-to-one relationships configuration
# Maps parent table -> child table -> foreign key column
# These relationships should generate singular method names (e.g., get_mobile() not get_mobiles())
ONE_TO_ONE_RELATIONSHIPS = {
    'players': {
        'mobiles': 'owner_player_id',  # Player has one Mobile (avatar)
    },
}

# Valid owner types per table
# Tables using Owner union have domain-specific constraints on which owner types are valid
# Format: table_name -> list of valid owner type strings ('player', 'mobile', 'item', 'asset')
VALID_OWNER_TYPES = {
    'mobiles': ['player', 'mobile'],  # Mobiles can only be owned by player or mobile (never item/asset)
    'items': ['player', 'mobile', 'item', 'asset'],  # Items can be owned by anything
    'inventories': ['player', 'mobile', 'item', 'asset'],  # Inventories can be owned by anything
    # attribute_owners and inventory_owners are pivot tables - they handle all owner types
}

# Thrift conversion configuration
# Defines special handling for tables that need Thrift union conversions
THRIFT_CONVERSION_CONFIG = {
    'attributes': {
        'union_fields': ATTRIBUTE_VALUE_COLUMNS,
        'union_type': 'AttributeValue',
        'has_attribute_value_union': True,
    },
    'items': {
        'has_attribute_map': True,
    },
    'mobiles': {
        'has_attribute_map': True,
    },
    'mobile_items': {
        'has_attribute_map': True,  # Via direct mobile_item_attributes table, not pivot
        'attribute_relationship': 'direct',  # Distinguishes from pivot pattern
    },
    'players': {
        'has_embedded_mobile': True,  # Player.mobile is embedded in Thrift
    },
}


def get_thrift_struct_name(table_name: str) -> Optional[str]:
    """
    Get the Thrift struct name for a database table.

    Args:
        table_name: Database table name (e.g., 'players', 'items')

    Returns:
        Thrift struct name if mapping exists, None otherwise

    Examples:
        >>> get_thrift_struct_name('players')
        'Player'
        >>> get_thrift_struct_name('items')
        'Item'
        >>> get_thrift_struct_name('unknown_table')
        None
    """
    return TABLE_TO_THRIFT_MAPPING.get(table_name)


def has_thrift_mapping(table_name: str) -> bool:
    """
    Check if a table has a corresponding Thrift struct.

    Args:
        table_name: Database table name

    Returns:
        True if table has Thrift mapping, False otherwise

    Examples:
        >>> has_thrift_mapping('players')
        True
        >>> has_thrift_mapping('unknown_table')
        False
    """
    return table_name in TABLE_TO_THRIFT_MAPPING


def needs_owner_conversion(columns: List[Dict[str, Any]]) -> bool:
    """
    Check if a table has owner union fields (owner_player_id, owner_mobile_id, etc.).

    Args:
        columns: List of column definitions

    Returns:
        True if table has owner fields, False otherwise
    """
    column_names = [col['name'] for col in columns]
    return any(oc in column_names for oc in OWNER_COLUMNS)


def needs_attribute_value_conversion(columns: List[Dict[str, Any]]) -> bool:
    """
    Check if a table stores AttributeValue union data (flattened columns).

    Args:
        columns: List of column definitions

    Returns:
        True if table has AttributeValue fields, False otherwise
    """
    column_names = [col['name'] for col in columns]
    # Check if we have attribute value columns (typically in attributes table)
    return all(
        avc in column_names
        for avc in ['bool_value', 'double_value', 'vector3_x']
    )


def needs_attribute_map_conversion(table_name: str) -> bool:
    """
    Check if a table needs attribute map conversion for Thrift.

    Args:
        table_name: Database table name

    Returns:
        True if table has attribute map relationship, False otherwise

    Examples:
        >>> needs_attribute_map_conversion('items')
        True
        >>> needs_attribute_map_conversion('players')
        False
    """
    return THRIFT_CONVERSION_CONFIG.get(
        table_name, {},
    ).get('has_attribute_map', False)


def is_pivot_table(table_name: str, columns: List[Dict[str, Any]]) -> bool:
    """
    Detect if a table is a pivot/join table.
    Uses explicit configuration list and validates multiple foreign keys.

    Args:
        table_name: Database table name
        columns: List of column definitions

    Returns:
        True if table is a pivot table, False otherwise
    """
    if table_name in PIVOT_TABLES:
        fk_count = sum(
            1
            for col in columns
            if col["name"].endswith("_id") and col["name"] != "id"
        )
        return fk_count >= 2

    return False


def is_one_to_one_relationship(parent_table: str, child_table: str, foreign_column: str) -> bool:
    """
    Check if a has-many relationship is actually a 1-to-1 relationship.

    Args:
        parent_table: The parent table name
        child_table: The child table name (foreign table)
        foreign_column: The foreign key column in the child table

    Returns:
        True if this is a 1-to-1 relationship, False otherwise

    Examples:
        >>> is_one_to_one_relationship('players', 'mobiles', 'owner_player_id')
        True
        >>> is_one_to_one_relationship('players', 'items', 'owner_player_id')
        False
    """
    if parent_table not in ONE_TO_ONE_RELATIONSHIPS:
        return False

    child_config = ONE_TO_ONE_RELATIONSHIPS[parent_table].get(child_table)
    if child_config is None:
        return False

    return child_config == foreign_column


def has_embedded_relationship(table_name: str, relationship_name: str) -> bool:
    """
    Check if a table should embed a related object in its Thrift conversion.

    Args:
        table_name: Database table name
        relationship_name: Name of the relationship (e.g., 'mobile')

    Returns:
        True if relationship should be embedded in Thrift, False otherwise
    """
    config = THRIFT_CONVERSION_CONFIG.get(table_name, {})
    return config.get(f'has_embedded_{relationship_name}', False)


def get_valid_owner_types(table_name: str) -> List[str]:
    """
    Get list of valid owner types for a table.

    Args:
        table_name: Database table name

    Returns:
        List of valid owner type strings ('player', 'mobile', 'item', 'asset')
        Defaults to all types if not specified in config

    Examples:
        >>> get_valid_owner_types('mobiles')
        ['player', 'mobile']
        >>> get_valid_owner_types('items')
        ['player', 'mobile', 'item', 'asset']
    """
    return VALID_OWNER_TYPES.get(table_name, ['player', 'mobile', 'item', 'asset'])


def validate_config(db_tables: List[str]) -> List[str]:
    """
    Validate configuration against database schema.

    Checks:
    - All table names in TABLE_TO_THRIFT_MAPPING exist in database
    - All Thrift struct names can be imported from game.ttypes
    - VALID_OWNER_TYPES only references tables in TABLE_TO_THRIFT_MAPPING
    - ONE_TO_ONE_RELATIONSHIPS references valid tables

    Args:
        db_tables: List of table names from database

    Returns:
        List of validation error messages (empty list if valid)

    Examples:
        >>> validate_config(['players', 'mobiles', 'items'])
        []  # No errors
        >>> validate_config(['players'])
        ['Table "mobiles" in TABLE_TO_THRIFT_MAPPING not found in database', ...]
    """
    errors = []

    # Check table names exist in database
    for table_name in TABLE_TO_THRIFT_MAPPING.keys():
        if table_name not in db_tables:
            errors.append(f"Table '{table_name}' in TABLE_TO_THRIFT_MAPPING not found in database")

    # Check Thrift struct names are valid
    try:
        from game import ttypes
        for table_name, struct_name in TABLE_TO_THRIFT_MAPPING.items():
            if not hasattr(ttypes, struct_name):
                errors.append(f"Thrift struct '{struct_name}' for table '{table_name}' not found in game.ttypes")
    except ImportError as e:
        errors.append(f"Cannot import game.ttypes - ensure Thrift code is generated: {e}")

    # Check VALID_OWNER_TYPES references valid tables
    for table_name in VALID_OWNER_TYPES.keys():
        if table_name not in db_tables:
            errors.append(f"Table '{table_name}' in VALID_OWNER_TYPES not found in database")

    # Check ONE_TO_ONE_RELATIONSHIPS references valid tables
    for parent_table, children in ONE_TO_ONE_RELATIONSHIPS.items():
        if parent_table not in db_tables:
            errors.append(f"Parent table '{parent_table}' in ONE_TO_ONE_RELATIONSHIPS not found in database")
        for child_table in children.keys():
            if child_table not in db_tables:
                errors.append(f"Child table '{child_table}' in ONE_TO_ONE_RELATIONSHIPS not found in database")

    return errors
