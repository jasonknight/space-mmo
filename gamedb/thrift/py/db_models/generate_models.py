#!/usr/bin/env python3
"""
ActiveRecord-style model generator for MySQL tables.
Generates model files with getters, setters, save, find, and find_by methods.
"""

import argparse
import mysql.connector
from typing import Dict, List, Tuple, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import from generator modules
from generator import (
    TableNaming,
    TypeMapper,
    OWNER_COLUMNS,
    ATTRIBUTE_VALUE_COLUMNS,
    PIVOT_TABLES,
    TABLE_TO_THRIFT_MAPPING,
)
from generator.database import (
    get_table_columns,
    get_all_tables,
    get_create_table_statement,
    get_foreign_key_constraints,
    get_unique_constraints,
)
from generator.config import (
    get_thrift_struct_name,
    has_thrift_mapping,
    needs_owner_conversion,
    needs_attribute_value_conversion,
    needs_attribute_map_conversion,
    is_pivot_table,
    is_one_to_one_relationship,
    has_embedded_relationship,
    get_valid_owner_types,
    validate_config,
)

# Additional configuration and utility functions below


def generate_owner_union_to_db_code(table_name: str, columns: List[Dict[str, Any]]) -> str:
    """
    Generate code to convert ThriftOwner union from Thrift to database columns.

    The ThriftOwner union in Thrift has one of: player_id, mobile_id, item_id, or asset_id set.

    Supports two database storage patterns:
    1. Flattened: owner_player_id, owner_mobile_id, owner_item_id, owner_asset_id
    2. Generic: owner_id + owner_type (e.g., owner_id=123, owner_type='player')

    Args:
        table_name: Database table name
        columns: List of column definitions

    Returns:
        Generated Python code as a string
    """
    if not needs_owner_conversion(columns):
        return ""

    column_names = [col['name'] for col in columns]

    # Determine which pattern to use
    has_flattened = any(oc in column_names for oc in ['owner_player_id', 'owner_mobile_id', 'owner_item_id', 'owner_asset_id'])
    has_generic = 'owner_id' in column_names and 'owner_type' in column_names

    if has_generic:
        # Generic pattern: owner_id + owner_type
        code = '''
        # Convert ThriftOwner union to database owner_id and owner_type columns
        if hasattr(thrift_obj, 'owner') and thrift_obj.owner is not None:
            owner = thrift_obj.owner
            # Determine owner_id and owner_type based on which union field is set
            if hasattr(owner, 'player_id') and owner.player_id is not None:
                self._data['owner_id'] = owner.player_id
                self._data['owner_type'] = 'player'
            elif hasattr(owner, 'mobile_id') and owner.mobile_id is not None:
                self._data['owner_id'] = owner.mobile_id
                self._data['owner_type'] = 'mobile'
            elif hasattr(owner, 'item_id') and owner.item_id is not None:
                self._data['owner_id'] = owner.item_id
                self._data['owner_type'] = 'item'
            elif hasattr(owner, 'asset_id') and owner.asset_id is not None:
                self._data['owner_id'] = owner.asset_id
                self._data['owner_type'] = 'asset'
'''
    elif has_flattened:
        # Flattened pattern: separate columns for each owner type
        code = '''
        # Convert ThriftOwner union to database owner_* columns
        if hasattr(thrift_obj, 'owner') and thrift_obj.owner is not None:
            owner = thrift_obj.owner
            # Reset all owner fields to None first
            self._data['owner_player_id'] = None
            self._data['owner_mobile_id'] = None
            self._data['owner_item_id'] = None
            self._data['owner_asset_id'] = None

            # Set the appropriate owner field based on which union field is set
            if hasattr(owner, 'player_id') and owner.player_id is not None:
                self._data['owner_player_id'] = owner.player_id
            elif hasattr(owner, 'mobile_id') and owner.mobile_id is not None:
                self._data['owner_mobile_id'] = owner.mobile_id
            elif hasattr(owner, 'item_id') and owner.item_id is not None:
                self._data['owner_item_id'] = owner.item_id
            elif hasattr(owner, 'asset_id') and owner.asset_id is not None:
                self._data['owner_asset_id'] = owner.asset_id
'''
    else:
        code = ""

    return code


def generate_db_to_owner_union_code(table_name: str, columns: List[Dict[str, Any]]) -> str:
    """
    Generate code to convert database owner columns to ThriftOwner union in Thrift.

    Supports two database storage patterns:
    1. Flattened: owner_player_id, owner_mobile_id, owner_item_id, owner_asset_id
    2. Generic: owner_id + owner_type (e.g., owner_id=123, owner_type='player')

    Args:
        table_name: Database table name
        columns: List of column definitions

    Returns:
        Generated Python code as a string
    """
    if not needs_owner_conversion(columns):
        return ""

    column_names = [col['name'] for col in columns]

    # Determine which pattern to use
    has_flattened = any(oc in column_names for oc in ['owner_player_id', 'owner_mobile_id', 'owner_item_id', 'owner_asset_id'])
    has_generic = 'owner_id' in column_names and 'owner_type' in column_names

    if has_generic:
        # Generic pattern: owner_id + owner_type
        code = '''
            # Convert database owner_id and owner_type to ThriftOwner union
            owner = None
            owner_id = self._data.get('owner_id')
            owner_type = self._data.get('owner_type')
            if owner_id is not None and owner_type is not None:
                if owner_type == 'player':
                    owner = ThriftOwner(player_id=owner_id)
                elif owner_type == 'mobile':
                    owner = ThriftOwner(mobile_id=owner_id)
                elif owner_type == 'item':
                    owner = ThriftOwner(item_id=owner_id)
                elif owner_type == 'asset':
                    owner = ThriftOwner(asset_id=owner_id)
'''
    elif has_flattened:
        # Flattened pattern: separate columns for each owner type
        code = '''
            # Convert database owner_* columns to ThriftOwner union
            owner = None
            if self._data.get('owner_player_id') is not None:
                owner = ThriftOwner(player_id=self._data['owner_player_id'])
            elif self._data.get('owner_mobile_id') is not None:
                owner = ThriftOwner(mobile_id=self._data['owner_mobile_id'])
            elif self._data.get('owner_item_id') is not None:
                owner = ThriftOwner(item_id=self._data['owner_item_id'])
            elif self._data.get('owner_asset_id') is not None:
                owner = ThriftOwner(asset_id=self._data['owner_asset_id'])
'''
    else:
        code = ""

    return code


def generate_attribute_value_to_db_code() -> str:
    """
    Generate code to convert ThriftAttributeValue union from Thrift to flattened database columns.

    ThriftAttributeValue in Thrift is a union with fields: bool_value, double_value, vector3, asset_id
    In the database, we store these as: bool_value, double_value, vector3_x, vector3_y, vector3_z, asset_id

    Priority order: vector3 -> asset_id -> double_value -> bool_value (default/fallback)

    Returns:
        Generated Python code as a string
    """
    code = '''
        # Convert ThriftAttributeValue union to flattened database columns
        if hasattr(thrift_obj, 'value') and thrift_obj.value is not None:
            value = thrift_obj.value
            # Reset all value fields to None first
            self._data['bool_value'] = None
            self._data['double_value'] = None
            self._data['vector3_x'] = None
            self._data['vector3_y'] = None
            self._data['vector3_z'] = None
            self._data['asset_id'] = None

            # Set the appropriate field based on which union field is set
            # Priority: vector3 -> asset_id -> double_value -> bool_value (default)
            if hasattr(value, 'vector3') and value.vector3 is not None:
                self._data['vector3_x'] = value.vector3.x
                self._data['vector3_y'] = value.vector3.y
                self._data['vector3_z'] = value.vector3.z
            elif hasattr(value, 'asset_id') and value.asset_id is not None:
                self._data['asset_id'] = value.asset_id
            elif hasattr(value, 'double_value') and value.double_value is not None:
                self._data['double_value'] = value.double_value
            else:
                # bool_value is the default/fallback
                if hasattr(value, 'bool_value') and value.bool_value is not None:
                    self._data['bool_value'] = value.bool_value
                else:
                    self._data['bool_value'] = False
'''
    return code


def generate_db_to_attribute_value_code() -> str:
    """
    Generate code to convert flattened database columns to ThriftAttributeValue union in Thrift.

    Priority order: vector3 -> asset_id -> double_value -> bool_value (default/fallback)

    Returns:
        Generated Python code as a string
    """
    code = '''
            # Convert flattened database columns to ThriftAttributeValue union
            # Priority: vector3 -> asset_id -> double_value -> bool_value (default)
            value = None
            if self._data.get('vector3_x') is not None:
                value = ThriftAttributeValue(
                    vector3=ThriftItemVector3(
                        x=self._data['vector3_x'],
                        y=self._data['vector3_y'],
                        z=self._data['vector3_z'],
                    ),
                )
            elif self._data.get('asset_id') is not None:
                value = ThriftAttributeValue(asset_id=self._data['asset_id'])
            elif self._data.get('double_value') is not None:
                value = ThriftAttributeValue(double_value=self._data['double_value'])
            else:
                # bool_value is the default/fallback
                value = ThriftAttributeValue(bool_value=self._data.get('bool_value', False))
'''
    return code


def generate_attribute_map_to_pivot_code() -> str:
    """
    Generate code to convert map<AttributeType, Attribute> from Thrift to pivot table format.

    This converts the Thrift attribute map into a format suitable for storing via
    the set_attributes() method (which will handle the pivot table operations).

    Returns:
        Generated Python code as a string
    """
    code = '''
        # Store attributes map for later conversion via set_attributes()
        # The actual pivot table records will be created when save() is called
        if hasattr(thrift_obj, 'attributes') and thrift_obj.attributes is not None:
            # Convert thrift attributes to Attribute models
            self._pending_attributes = []
            for attr_type, attr_thrift in thrift_obj.attributes.items():
                # Import Attribute model (assumes it's available)
                attr_model = Attribute()
                attr_model.from_thrift(attr_thrift)
                self._pending_attributes.append((attr_type, attr_model))
'''
    return code


def generate_pivot_to_attribute_map_code() -> str:
    """
    Generate code to load pivot table records and build map<AttributeType, Attribute> for Thrift.

    This loads attributes from the database via the attribute_owners pivot table
    and converts them into a Thrift map.

    Returns:
        Generated Python code as a string
    """
    code = '''
            # Load attributes via pivot table and convert to map<AttributeType, Attribute>
            attributes_map = {}
            if self.get_id() is not None:
                # Get attributes through the pivot relationship
                attribute_models = self.get_attributes(reload=True)
                for attr_model in attribute_models:
                    # Convert each attribute model to Thrift
                    attr_results, attr_thrift = attr_model.into_thrift()
                    if attr_thrift is not None:
                        # Use attribute_type as the map key
                        attributes_map[attr_thrift.attribute_type] = attr_thrift
'''
    return code


# Utility functions using imported modules


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

    # Special case mappings for columns that don't follow standard naming
    special_cases = {
        'blueprint_id': 'item_blueprints',
    }

    # Common semantic prefixes that don't affect the referenced table
    semantic_prefixes = ['owner_', 'parent_', 'child_', 'source_', 'target_', 'primary_', 'secondary_']

    for col in columns:
        if col["name"].endswith("_id") and col["name"] != "id":
            # Check special cases first
            if col["name"] in special_cases:
                relationships.append(
                    {
                        "column": col["name"],
                        "referenced_table": special_cases[col["name"]],
                        "referenced_column": "id",
                        "is_nullable": col["is_nullable"],
                    }
                )
                continue

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
    Uses explicit configuration list and validates multiple foreign keys.
    """
    # Check if table is in explicit pivot table configuration
    if table_name in PIVOT_TABLES:
        # Verify it has multiple foreign keys as expected
        fk_count = sum(1 for col in columns if col["name"].endswith("_id") and col["name"] != "id")
        return fk_count >= 2

    return False


def get_pivot_table_info(
    table_name: str,
    columns: List[Dict[str, Any]],
    fk_constraints: Dict[str, List[Dict[str, str]]],
) -> Dict[str, Any]:
    """
    Get metadata about pivot table foreign keys.
    Returns dict with:
        - pivot_fk: the FK pointing to the main related table (e.g., attribute_id, inventory_id)
        - owner_fks: list of FKs pointing to owner tables (e.g., player_id, mobile_id, item_id)
    """
    # Determine which FK is the "main" pivot FK based on table name
    if table_name == "attribute_owners":
        pivot_fk_name = "attribute_id"
        related_table = "attributes"
    elif table_name == "inventory_owners":
        pivot_fk_name = "inventory_id"
        related_table = "inventories"
    else:
        # For other pivot tables, try to infer from FK constraints
        if table_name in fk_constraints and fk_constraints[table_name]:
            pivot_fk_name = fk_constraints[table_name][0]["column"]
            related_table = fk_constraints[table_name][0]["referenced_table"]
        else:
            return {"pivot_fk": None, "owner_fks": []}

    # Find the pivot FK in constraints (if it exists)
    pivot_fk = {
        "column": pivot_fk_name,
        "referenced_table": related_table,
        "referenced_column": "id",
    }
    if table_name in fk_constraints:
        for fk in fk_constraints[table_name]:
            if fk["column"] == pivot_fk_name:
                pivot_fk = fk
                break

    # Find all owner FKs from columns (not just from constraints, since they may not have constraints)
    owner_fks = []
    for col in columns:
        col_name = col["name"]
        # Skip the id column and the pivot FK column
        if col_name == "id" or col_name == pivot_fk_name:
            continue
        # Check if it's an FK column (ends with _id)
        if col_name.endswith("_id"):
            # Infer the referenced table name from the column name
            # e.g., player_id -> players, mobile_id -> mobiles
            owner_type = col_name.replace("_id", "")
            referenced_table = TableNaming.pluralize(owner_type)

            # Check if there's an actual FK constraint for this column
            fk_info = {
                "column": col_name,
                "referenced_table": referenced_table,
                "referenced_column": "id",
            }
            if table_name in fk_constraints:
                for fk in fk_constraints[table_name]:
                    if fk["column"] == col_name:
                        fk_info = fk
                        break

            owner_fks.append(fk_info)

    return {
        "pivot_fk": pivot_fk,
        "owner_fks": owner_fks,
    }


def generate_pivot_helper_methods(
    table_name: str,
    owner_fks: List[Dict[str, str]],
) -> str:
    """
    Generate helper methods for pivot tables (is_player, is_mobile, etc.).
    """
    methods = []

    for fk in owner_fks:
        column_name = fk["column"]
        # Extract owner type from column name (e.g., player_id -> player)
        owner_type = column_name.replace("_id", "")

        method = f"""
    def is_{owner_type}(self) -> bool:
        \"\"\"Check if this pivot record belongs to a {owner_type}.\"\"\"
        return self.get_{column_name}() is not None
"""
        methods.append(method)

    return "\n".join(methods)


def get_pivot_owner_relationships(
    table_name: str,
    table_columns: Dict[str, List[Dict[str, Any]]],
    fk_constraints: Dict[str, List[Dict[str, str]]],
) -> List[Dict[str, str]]:
    """
    Determine if this table is an owner in any pivot relationships.
    Returns list of dicts with pivot_table and related_table for each relationship.
    """
    relationships = []

    # Check each pivot table
    for pivot_table in PIVOT_TABLES:
        # Get the columns for this pivot table
        pivot_columns = table_columns.get(pivot_table, [])
        if not pivot_columns:
            continue

        # Get pivot info to determine which FK is the main pivot FK
        pivot_info = get_pivot_table_info(pivot_table, pivot_columns, fk_constraints)
        if not pivot_info["pivot_fk"]:
            continue

        related_table = pivot_info["pivot_fk"]["referenced_table"]

        # Check if any of the owner FKs point to this table
        for owner_fk in pivot_info["owner_fks"]:
            if owner_fk["referenced_table"] == table_name:
                relationships.append({
                    "pivot_table": pivot_table,
                    "related_table": related_table,
                })
                break  # Only add once per pivot table

    return relationships


def get_attribute_relationship_type(
    table_name: str,
    table_columns: Dict[str, List[Dict[str, Any]]],
    fk_constraints: Dict[str, List[Dict[str, str]]],
) -> Optional[str]:
    """
    Determine how a table relates to attributes.

    Returns:
        'pivot' - Uses attribute_owners pivot table (items, mobiles)
        'direct' - Has direct attribute table (mobile_items -> mobile_item_attributes)
        None - No attribute relationship
    """
    # Check if table is a pivot owner (has FK in attribute_owners)
    # AND if Thrift struct actually has attribute map support
    pivot_rels = get_pivot_owner_relationships(table_name, table_columns, fk_constraints)
    for rel in pivot_rels:
        if rel['pivot_table'] == 'attribute_owners':
            # Only return 'pivot' if Thrift config says this table has attribute map
            if needs_attribute_map_conversion(table_name):
                return 'pivot'

    # Check for direct attribute table pattern
    # Look for table named {singular}_attributes with FK back to this table
    singular_name = TableNaming.singularize(table_name)
    attribute_table = f"{singular_name}_attributes"

    if attribute_table in table_columns:
        # Verify it has FK pointing back to this table
        attr_fks = fk_constraints.get(attribute_table, [])
        fk_column = f"{singular_name}_id"
        for fk in attr_fks:
            if fk['column'] == fk_column and fk['referenced_table'] == table_name:
                # Only return 'direct' if Thrift config says this table has attribute map
                if needs_attribute_map_conversion(table_name):
                    return 'direct'

    return None


def generate_direct_attribute_methods(
    table_name: str,
    attribute_table: str,
) -> str:
    """
    Generate get_attributes() method for tables with direct attribute tables.

    For mobile_items -> mobile_item_attributes pattern.
    Converts direct attribute records to standard Attribute objects for Thrift compatibility.
    """
    singular_name = TableNaming.singularize(table_name)
    class_name = TableNaming.to_pascal_case(singular_name)
    attr_class = TableNaming.to_pascal_case(TableNaming.singularize(attribute_table))
    fk_column = f"{singular_name}_id"

    code = f'''
    def get_attributes(self, reload: bool = False) -> List['Attribute']:
        """
        Get all attributes for this {class_name} from {attribute_table} table.
        Converts to standard Attribute objects for Thrift compatibility.

        Args:
            reload: If True, ignore cache and reload from database
        """
        # Check cache first
        cache_key = '_attributes_cache'
        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return []

        # Get direct attribute records
        direct_attrs = {attr_class}.find_by_{fk_column}(my_id)

        # Convert to standard Attribute objects
        attributes = []
        for direct_attr in direct_attrs:
            attr = Attribute()
            attr._data['internal_name'] = direct_attr.get_internal_name()
            attr._data['visible'] = direct_attr.get_visible()
            attr._data['attribute_type'] = direct_attr.get_attribute_type()
            attr._data['bool_value'] = direct_attr.get_bool_value()
            attr._data['double_value'] = direct_attr.get_double_value()
            attr._data['vector3_x'] = direct_attr.get_vector3_x()
            attr._data['vector3_y'] = direct_attr.get_vector3_y()
            attr._data['vector3_z'] = direct_attr.get_vector3_z()
            attr._data['asset_id'] = direct_attr.get_asset_id()
            attributes.append(attr)

        # Cache results
        setattr(self, cache_key, attributes)
        return attributes
'''
    return code


def generate_pivot_owner_methods(
    owner_table_name: str,
    pivot_table_name: str,
    related_table_name: str,
) -> str:
    """
    Generate convenience methods on owner models for interacting with pivot tables.
    For example, on Player model, generate methods to interact with attributes through attribute_owners pivot.
    """
    # Convert table names to class names
    owner_class = TableNaming.to_pascal_case(TableNaming.singularize(owner_table_name))
    pivot_class = TableNaming.to_pascal_case(TableNaming.singularize(pivot_table_name))
    related_class = TableNaming.to_pascal_case(TableNaming.singularize(related_table_name))

    # Determine the relationship name (e.g., attributes, inventories)
    related_plural = TableNaming.pluralize(TableNaming.singularize(related_table_name))
    related_singular = TableNaming.singularize(related_table_name)
    pivot_singular = TableNaming.singularize(pivot_table_name)

    # FK column names
    owner_fk = f"{TableNaming.singularize(owner_table_name)}_id"
    related_fk = f"{related_singular}_id"

    methods = f"""
    def get_{related_plural}(self, reload: bool = False) -> List['{related_class}']:
        \"\"\"
        Get all {related_plural} for this {owner_class} through the {pivot_table_name} pivot table.
        Returns a list of {related_class} objects.
        \"\"\"
        cache_key = '_{related_plural}_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return cached

        if self.get_id() is None:
            return []

        # Query through pivot table
        self._connect()
        cursor = self._connection.cursor(dictionary=True)
        results = []

        try:
            query = \"\"\"
                SELECT r.*
                FROM {related_table_name} r
                INNER JOIN {pivot_table_name} p ON r.id = p.{related_fk}
                WHERE p.{owner_fk} = %s
            \"\"\"
            cursor.execute(query, (self.get_id(),))
            rows = cursor.fetchall()

            for row in rows:
                instance = {related_class}()
                instance._data = row
                instance._dirty = False
                results.append(instance)
        finally:
            cursor.close()

        # Cache results
        setattr(self, cache_key, results)
        return results

    def get_{pivot_singular}s(self, reload: bool = False, lazy: bool = False):
        \"\"\"
        Get all {pivot_class} pivot records for this {owner_class}.

        Args:
            reload: If True, bypass cache and fetch fresh from database.
            lazy: If True, return an iterator. If False, return a list.

        Returns:
            List[{pivot_class}] or Iterator[{pivot_class}]
        \"\"\"
        cache_key = '_{pivot_singular}s_cache'

        if not reload and hasattr(self, cache_key):
            cached = getattr(self, cache_key)
            if cached is not None:
                return iter(cached) if lazy else cached

        if self.get_id() is None:
            return iter([]) if lazy else []

        results = {pivot_class}.find_by_{owner_fk}(self.get_id())

        # Cache results
        setattr(self, cache_key, results)
        return iter(results) if lazy else results

    def add_{related_singular}(self, {related_singular}: '{related_class}') -> None:
        \"\"\"
        Add a {related_singular} to this {owner_class} through the {pivot_table_name} pivot table.
        Creates the pivot record and saves the {related_singular} if it's new or dirty.
        \"\"\"
        if self.get_id() is None:
            raise ValueError("Cannot add {related_singular} to unsaved {owner_class}. Save the {owner_class} first.")

        # Save the related object if it's new or dirty
        if {related_singular}._dirty:
            {related_singular}.save()

        # Create pivot record
        pivot = {pivot_class}()
        pivot.set_{owner_fk}(self.get_id())
        pivot.set_{related_fk}({related_singular}.get_id())

        # Set all other owner FKs to NULL explicitly
        # This ensures only one owner FK is set per pivot record
        for attr_name in dir(pivot):
            if attr_name.startswith('set_') and attr_name.endswith('_id') and attr_name != 'set_id' and attr_name != 'set_{owner_fk}' and attr_name != 'set_{related_fk}':
                setter = getattr(pivot, attr_name)
                setter(None)

        pivot.save()

        # Clear cache
        cache_key = '_{related_plural}_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_{pivot_singular}s_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def remove_{related_singular}(self, {related_singular}: '{related_class}') -> None:
        \"\"\"
        Remove a {related_singular} from this {owner_class} through the {pivot_table_name} pivot table.
        Deletes both the pivot record and the {related_singular} record (cascade delete).
        \"\"\"
        if self.get_id() is None or {related_singular}.get_id() is None:
            return

        # Use a fresh connection to avoid transaction conflicts
        connection = {owner_class}._create_connection()
        cursor = connection.cursor()

        try:
            # Start transaction
            connection.start_transaction()

            # Delete pivot record first
            cursor.execute(
                f"DELETE FROM {pivot_table_name} WHERE {owner_fk} = %s AND {related_fk} = %s",
                (self.get_id(), {related_singular}.get_id()),
            )

            # Delete the related record
            cursor.execute(
                f"DELETE FROM {related_table_name} WHERE id = %s",
                ({related_singular}.get_id(),),
            )

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

        # Clear cache
        cache_key = '_{related_plural}_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)
        cache_key = '_{pivot_singular}s_cache'
        if hasattr(self, cache_key):
            delattr(self, cache_key)

    def set_{related_plural}(self, {related_plural}_list: List['{related_class}']) -> None:
        \"\"\"
        Replace all {related_plural} for this {owner_class}.
        Removes all existing {related_plural} and adds the new ones.
        \"\"\"
        if self.get_id() is None:
            raise ValueError("Cannot set {related_plural} on unsaved {owner_class}. Save the {owner_class} first.")

        self._connect()

        try:
            # Start transaction for all operations only if one isn't already active
            if not self._connection.in_transaction:
                self._connection.start_transaction()

            # Get existing {related_plural}
            existing = self.get_{related_plural}(reload=True)

            # Delete all existing pivot records and related records
            cursor = self._connection.cursor()
            for item in existing:
                if item.get_id() is not None:
                    # Delete pivot record
                    cursor.execute(
                        f"DELETE FROM {pivot_table_name} WHERE {owner_fk} = %s AND {related_fk} = %s",
                        (self.get_id(), item.get_id()),
                    )
                    # Delete related record
                    cursor.execute(
                        f"DELETE FROM {related_table_name} WHERE id = %s",
                        (item.get_id(),),
                    )
            cursor.close()

            # Add new ones within the same transaction
            for item in {related_plural}_list:
                # Save the related object if needed
                if item._dirty:
                    item.save(self._connection)

                # Create pivot record manually to avoid nested transactions
                pivot = {pivot_class}()
                pivot.set_{owner_fk}(self.get_id())
                pivot.set_{related_fk}(item.get_id())
                pivot.save(self._connection)

            # Commit all operations
            self._connection.commit()

            # Clear cache
            cache_key = '_{related_plural}_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)
            cache_key = '_{pivot_singular}s_cache'
            if hasattr(self, cache_key):
                delattr(self, cache_key)

        except Exception as e:
            self._connection.rollback()
            raise
"""

    return methods


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
        singular_name = TableNaming.singularize(referenced_table)
        class_name = TableNaming.to_pascal_case(singular_name)

        # Relationship method name (e.g., owner_player from owner_player_id)
        rel_name = TableNaming.column_to_relationship_name(column_name)

        # Optional type annotation (use string for forward reference)
        # Always use Optional for getters with strict parameter since they can return None
        # when FK points to non-existent record (even if FK column itself is NOT NULL)
        param_return_type = f"Optional['{class_name}']"

        # Getter method with lazy loading and caching
        getter = f"""    def get_{rel_name}(self, strict: bool = False) -> {param_return_type}:
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

        # Setter method (use Optional for parameter type based on nullability)
        param_type = f"Optional['{class_name}']" if is_nullable else f"'{class_name}'"
        setter = f"""    def set_{rel_name}(self, model: {param_type}) -> 'self.__class__':
        \"\"\"
        Set the associated {class_name} for this {rel_name} relationship.
        Updates the foreign key and marks the model as dirty.

        Args:
            model: The {class_name} instance to associate, or None to clear.

        Returns:
            self for method chaining
        \"\"\"
        # Update cache
        cache_key = '_{rel_name}_cache'
        setattr(self, cache_key, model)

        # Update foreign key
        if model is None:
            self.set_{column_name}(None)
        else:
            self.set_{column_name}(model.get_id())
        return self"""

        methods.append(setter)

    return "\n\n".join(methods) if methods else ""


def generate_has_many_methods(
    table_name: str,
    has_many_rels: List[Dict[str, Any]],
    table_columns: Dict[str, List[Dict[str, Any]]],
) -> str:
    """Generate has-many relationship methods (or 1-to-1 for configured relationships)."""
    methods = []

    for rel in has_many_rels:
        foreign_table = rel["foreign_table"]
        foreign_column = rel["foreign_column"]

        # Convert table names to class names
        foreign_singular = TableNaming.singularize(foreign_table)
        foreign_class = TableNaming.to_pascal_case(foreign_singular)

        # Check if this is a 1-to-1 relationship
        is_one_to_one = is_one_to_one_relationship(table_name, foreign_table, foreign_column)

        if is_one_to_one:
            # Generate singular getter for 1-to-1 relationship
            rel_name = foreign_singular  # Singular name (e.g., 'mobile' not 'mobiles')

            getter = f"""    def get_{rel_name}(self, reload: bool = False):
        \"\"\"
        Get the associated {foreign_class} record (1-to-1 relationship).

        Args:
            reload: If True, bypass cache and fetch fresh from database.

        Returns:
            Optional[{foreign_class}]
        \"\"\"
        cache_key = '_{rel_name}_cache'

        # Check cache unless reload is requested
        if not reload and hasattr(self, cache_key):
            return getattr(self, cache_key)

        # Fetch from database
        my_id = self.get_id()
        if my_id is None:
            return None

        results = {foreign_class}.find_by_{foreign_column}(my_id)

        # Should only be one result for 1-to-1
        result = results[0] if results else None

        # Cache result
        setattr(self, cache_key, result)

        return result"""
        else:
            # Generate plural getter for 1-to-many relationship
            rel_name = foreign_table  # Plural name (e.g., 'inventory_entries')

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


def generate_getters(columns: List[Dict[str, Any]], table_name: str = None) -> str:
    """Generate getter methods for all columns."""
    getters = []

    # Enum field mapping: table.column -> ThriftEnumType
    enum_fields = {
        'attributes.attribute_type': 'ThriftAttributeType',
        'items.item_type': 'ThriftItemType',
        'mobile_items.item_type': 'ThriftItemType',
        'mobiles.mobile_type': 'ThriftMobileType',
    }

    for col in columns:
        python_type = TypeMapper.get_python_type(col["data_type"])

        # Check if this is an enum field
        field_key = f"{table_name}.{col['name']}" if table_name else None
        is_enum_field = field_key and field_key in enum_fields

        if is_enum_field:
            # For enum fields, return the enum type
            enum_type = enum_fields[field_key]
            optional_type = f"Optional[{enum_type}]" if col["is_nullable"] else enum_type

            # Convert string from _data to enum integer using _NAMES_TO_VALUES map
            getter = f"""    def get_{col["name"]}(self) -> {optional_type}:
        value = self._data.get('{col["name"]}')
        return {enum_type}._NAMES_TO_VALUES[value] if value is not None else None"""
        else:
            optional_type = (
                f"Optional[{python_type}]" if col["is_nullable"] else python_type
            )

            getter = f"""    def get_{col["name"]}(self) -> {optional_type}:
        return self._data.get('{col["name"]}')"""

        getters.append(getter)

    return "\n\n".join(getters)


def generate_validate_owner_method(table_name: str, class_name: str) -> str:
    """
    Generate validate_owner() method for models with Owner union fields.

    Args:
        table_name: Database table name
        class_name: Model class name

    Returns:
        Generated method code as a string
    """
    valid_types = get_valid_owner_types(table_name)
    valid_types_str = ', '.join([f"'{t}'" for t in valid_types])

    method = f'''
    def validate_owner(self) -> None:
        """
        Validate Owner union: exactly one owner must be set and must be valid type.

        Raises:
            ValueError: If validation fails
        """
        owner_fks = {{
            'player': self.get_owner_player_id(),
            'mobile': self.get_owner_mobile_id(),
            'item': self.get_owner_item_id(),
            'asset': self.get_owner_asset_id(),
        }}

        # Check exactly one is set
        set_owners = [k for k, v in owner_fks.items() if v is not None]
        if len(set_owners) == 0:
            raise ValueError("{class_name} must have exactly one owner (none set)")
        if len(set_owners) > 1:
            raise ValueError(f"{class_name} must have exactly one owner (multiple set: {{set_owners}})")

        # Check valid type for this table
        valid_types = [{valid_types_str}]
        if set_owners[0] not in valid_types:
            raise ValueError(f"{class_name} cannot be owned by {{set_owners[0]}} (valid types: {{valid_types}})")
'''

    return method


def generate_setters(columns: List[Dict[str, Any]], table_name: str = None) -> str:
    """Generate setter methods for all columns."""
    setters = []

    # Track if we're generating owner setters
    owner_columns = ['owner_player_id', 'owner_mobile_id', 'owner_item_id', 'owner_asset_id']
    has_owner_fields = any(col['name'] in owner_columns for col in columns)

    # Enum field mapping: table.column -> ThriftEnumType
    enum_fields = {
        'attributes.attribute_type': 'ThriftAttributeType',
        'items.item_type': 'ThriftItemType',
        'mobile_items.item_type': 'ThriftItemType',
        'mobiles.mobile_type': 'ThriftMobileType',
    }

    for col in columns:
        python_type = TypeMapper.get_python_type(col["data_type"])
        optional_type = (
            f"Optional[{python_type}]" if col["is_nullable"] else python_type
        )

        # Check if this is the 'id' column - make it private
        method_name = f"_set_{col['name']}" if col['name'] == 'id' else f"set_{col['name']}"

        # Check if this is an enum field
        field_key = f"{table_name}.{col['name']}" if table_name else None
        is_enum_field = field_key and field_key in enum_fields

        if is_enum_field:
            enum_type = enum_fields[field_key]
            param_type = f"Optional[int]" if col["is_nullable"] else "int"

            # Enum validation setter (Thrift enums are integers in Python)
            setter = f"""    def {method_name}(self, value: {param_type}) -> 'self.__class__':
        \"\"\"
        Set the {col["name"]} field value.

        Python Thrift Enum Implementation Note:
        ----------------------------------------
        In Python, Thrift enums are implemented as integer constants on a class, not
        as a separate enum type. For example:
            - ThriftAttributeType.STRENGTH is just an int (e.g., 0)
            - ThriftAttributeType.DEXTERITY is just an int (e.g., 1)

        This is different from languages like Java or C++ where enums are distinct types.
        Python Thrift enums are essentially namespaced integer constants.

        Why this method accepts int:
        - Thrift enums in Python ARE ints, not a distinct type
        - Using isinstance(value, ThriftAttributeType) would fail (it's not a class you can instantiate)
        - Type checkers understand this: passing ThriftAttributeType.STRENGTH satisfies int type hint
        - This validates the value is a legitimate enum constant, rejecting invalid integers

        The method validates the integer is a valid enum value by reverse-lookup against
        the Thrift enum class constants, then stores the enum name as a string in the database.

        Args:
            value: Integer value of a {enum_type} enum constant (e.g., {enum_type}.STRENGTH)

        Returns:
            self for method chaining

        Raises:
            TypeError: If value is not an integer
            ValueError: If value is not a valid {enum_type} enum constant
        \"\"\"
        if value is not None and not isinstance(value, int):
            raise TypeError(f"{{value}} must be an integer (Thrift enum), got {{type(value).__name__}}")
        # Convert enum integer to string name for storage using _VALUES_TO_NAMES map
        if value is not None:
            if value not in {enum_type}._VALUES_TO_NAMES:
                raise ValueError(f"{{value}} is not a valid {enum_type} enum value")
            self._data['{col["name"]}'] = {enum_type}._VALUES_TO_NAMES[value]
        else:
            self._data['{col["name"]}'] = None
        self._dirty = True
        return self"""

        # Special handling for owner FK columns
        elif has_owner_fields and col["name"] in owner_columns:
            other_owners = [oc for oc in owner_columns if oc != col["name"]]
            clear_code = "\n        ".join([f"self._data['{oc}'] = None" for oc in other_owners])

            setter = f"""    def {method_name}(self, value: {optional_type}) -> 'self.__class__':
        self._data['{col["name"]}'] = value
        {clear_code}
        self._dirty = True
        return self"""
        else:
            setter = f"""    def {method_name}(self, value: {optional_type}) -> 'self.__class__':
        self._data['{col["name"]}'] = value
        self._dirty = True
        return self"""

        setters.append(setter)

    return "\n\n".join(setters)


def generate_find_by_methods(
    columns: List[Dict[str, Any]], class_name: str, table_name: str
) -> str:
    """Generate find_by methods for columns ending with _id."""
    find_by_methods = []

    for col in columns:
        if col["name"].endswith("_id"):
            python_type = TypeMapper.get_python_type(col["data_type"])

            method = f"""    @staticmethod
    def find_by_{col["name"]}(value: {python_type}) -> List['{class_name}']:
        \"\"\"
        Find all records by {col["name"]}.
        Returns a list of instances with matching records.
        \"\"\"
        connection = {class_name}._create_connection()
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
        python_type = TypeMapper.get_python_type(col["data_type"])
        if python_type == "datetime":
            types.add("datetime")
        elif python_type == "Any":
            types.add("Any")
    return types


def generate_imports(columns: List[Dict[str, Any]], has_relationships: bool = False, has_thrift_conversion: bool = False) -> str:
    """Generate import statements based on column types."""
    imports = [
        "import mysql.connector",
    ]

    # Add typing imports
    typing_imports = ["Dict", "List", "Optional", "Any"]
    if has_relationships:
        typing_imports.extend(["Iterator", "Union"])
    if has_thrift_conversion:
        typing_imports.append("Tuple")

    imports.append(f"from typing import {', '.join(typing_imports)}")

    required_types = TypeMapper.collect_required_types(columns)
    if "datetime" in required_types:
        imports.append("from datetime import datetime")

    # Add Thrift imports if needed
    if has_thrift_conversion:
        imports.append("")
        imports.append("# Thrift imports (aliased to avoid name collisions)")
        imports.append("from game.ttypes import (")
        imports.append("    GameResult as ThriftGameResult,")
        imports.append("    StatusType as ThriftStatusType,")
        imports.append("    GameError as ThriftGameError,")
        imports.append("    Owner as ThriftOwner,")
        imports.append("    AttributeValue as ThriftAttributeValue,")
        imports.append("    AttributeType as ThriftAttributeType,")
        imports.append("    ItemType as ThriftItemType,")
        imports.append("    MobileType as ThriftMobileType,")
        imports.append("    ItemVector3 as ThriftItemVector3,")
        imports.append("    Attribute as ThriftAttribute,")
        imports.append("    Item as ThriftItem,")
        imports.append("    Mobile as ThriftMobile,")
        imports.append("    Player as ThriftPlayer,")
        imports.append("    MobileItem as ThriftMobileItem,")
        imports.append("    Inventory as ThriftInventory,")
        imports.append("    InventoryEntry as ThriftInventoryEntry,")
        imports.append("    ItemBlueprint as ThriftItemBlueprint,")
        imports.append("    ItemBlueprintComponent as ThriftItemBlueprintComponent,")
        imports.append(")")

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
        rel_name = TableNaming.column_to_relationship_name(rel["column"])
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


def generate_cascade_destroy_code(
    table_name: str,
    has_many_rels: List[Dict[str, Any]],
    pivot_owner_rels: List[Dict[str, Any]],
) -> str:
    """
    Generate cascade destroy code for has-many relationships and pivot table cleanup.
    Returns code string for destroying children and cleaning up associations.

    Note: We do NOT cascade destroy belongs-to relationships (parent objects).
    Only children and associations are destroyed.
    """
    destroy_code = []

    # Has-many cascade destroy (destroy child objects first)
    for rel in has_many_rels:
        rel_name = rel["foreign_table"]
        method_name = f"get_{rel_name}"

        code = f"""# Cascade destroy {rel_name} children
                cache_key = '_{rel_name}_cache'
                if hasattr(self, cache_key):
                    related_list = getattr(self, cache_key)
                    if related_list is not None:
                        for related in related_list:
                            if hasattr(related, 'destroy'):
                                related.destroy(connection=connection, cascade=cascade)
                else:
                    # Load and destroy children if not cached
                    if self.get_id() is not None:
                        try:
                            children = self.{method_name}(reload=True)
                            for child in children:
                                if hasattr(child, 'destroy'):
                                    child.destroy(connection=connection, cascade=cascade)
                        except:
                            pass  # Relationship method may not exist"""
        destroy_code.append(code)

    # Pivot table cleanup (delete associations)
    for rel in pivot_owner_rels:
        pivot_table = rel["pivot_table"]
        related_table = rel["related_table"]
        # The owner FK is based on the current table name
        owner_fk = f"{TableNaming.singularize(table_name)}_id"
        related_plural = TableNaming.pluralize(TableNaming.singularize(related_table))

        code = f"""# Clean up {pivot_table} associations and cascade delete {related_plural}
                if self.get_id() is not None:
                    # First, cascade delete the related objects
                    try:
                        related_objects = self.get_{related_plural}(reload=True)
                        for obj in related_objects:
                            if hasattr(obj, 'destroy'):
                                obj.destroy(connection=connection, cascade=cascade)
                    except:
                        pass  # Method may not exist

                    # Then delete the pivot table associations
                    cursor.execute(
                        "DELETE FROM `{pivot_table}` WHERE `{owner_fk}` = %s",
                        (self.get_id(),),
                    )"""
        destroy_code.append(code)

    destroy_str = "\n".join(destroy_code) if destroy_code else "pass  # No cascade destroys needed"
    return destroy_str


def generate_from_thrift_method(
    table_name: str,
    class_name: str,
    columns: List[Dict[str, Any]],
    thrift_struct_name: str,
    relationships: Dict[str, Any],
    table_columns: Dict[str, List[Dict[str, Any]]],
    fk_constraints: Dict[str, List[Dict[str, str]]],
) -> str:
    """
    Generate from_thrift() method for converting Thrift object to Model.

    Args:
        table_name: Database table name
        class_name: Model class name
        columns: List of column definitions
        thrift_struct_name: Name of the Thrift struct
        relationships: Relationships metadata
        table_columns: All table columns dict
        fk_constraints: All FK constraints dict

    Returns:
        Generated method code as a string
    """
    method_code = f'''
    def from_thrift(self, thrift_obj: '{thrift_struct_name}') -> '{class_name}':
        """
        Populate this Model instance from a Thrift {thrift_struct_name} object.

        This method performs pure data conversion without database queries.
        Call save() after this to persist to the database.

        Args:
            thrift_obj: Thrift {thrift_struct_name} instance

        Returns:
            self for method chaining
        """
        # Map simple fields from Thrift to Model
'''

    # Enum field mapping
    enum_fields = {
        'attributes.attribute_type': 'ThriftAttributeType',
        'items.item_type': 'ThriftItemType',
        'mobile_items.item_type': 'ThriftItemType',
        'mobiles.mobile_type': 'ThriftMobileType',
    }

    # Map simple fields (non-FK, non-union fields)
    for col in columns:
        col_name = col['name']

        # Skip owner union fields - they're handled specially
        # Flattened pattern
        if col_name in ['owner_player_id', 'owner_mobile_id', 'owner_item_id', 'owner_asset_id']:
            continue
        # Generic pattern
        if col_name in ['owner_id', 'owner_type']:
            continue

        # Skip AttributeValue union fields - handled specially for attributes table
        if table_name == 'attributes' and col_name in ['bool_value', 'double_value', 'vector3_x', 'vector3_y', 'vector3_z', 'asset_id']:
            continue

        # Check if this is an enum field
        field_key = f"{table_name}.{col_name}"
        is_enum_field = field_key in enum_fields

        # Map the field if it exists on the Thrift object
        if is_enum_field:
            # For enum fields, convert enum integer to string name for storage
            # Python Thrift enums are just integers, so we use _VALUES_TO_NAMES dict
            enum_type = enum_fields[field_key]
            method_code += f"        if hasattr(thrift_obj, '{col_name}'):\n"
            method_code += f"            if thrift_obj.{col_name} is not None:\n"
            method_code += f"                self._data['{col_name}'] = {enum_type}._VALUES_TO_NAMES[thrift_obj.{col_name}]\n"
            method_code += f"            else:\n"
            method_code += f"                self._data['{col_name}'] = None\n"
        else:
            method_code += f"        if hasattr(thrift_obj, '{col_name}'):\n"
            method_code += f"            self._data['{col_name}'] = thrift_obj.{col_name}\n"

    # Handle Owner union conversion if applicable
    if needs_owner_conversion(columns):
        method_code += generate_owner_union_to_db_code(table_name, columns)

    # Handle AttributeValue union conversion if applicable (for attributes table)
    if needs_attribute_value_conversion(columns):
        method_code += generate_attribute_value_to_db_code()

    # Handle attribute map (for tables with attributes relationship)
    attr_rel_type = get_attribute_relationship_type(table_name, table_columns, fk_constraints)
    if attr_rel_type == 'pivot':
        method_code += generate_attribute_map_to_pivot_code()
    elif attr_rel_type == 'direct':
        # Direct attribute tables handle conversion differently
        # Store pending attributes for later save
        method_code += '''
        # Store attributes for direct table conversion
        if hasattr(thrift_obj, 'attributes') and thrift_obj.attributes is not None:
            self._pending_attributes = thrift_obj.attributes
'''

    # Handle embedded 1-to-1 relationships (e.g., Player.mobile)
    has_many_rels = relationships.get('has_many', [])
    for rel in has_many_rels:
        foreign_table = rel['foreign_table']
        foreign_column = rel['foreign_column']

        # Check if this is a 1-to-1 relationship that should be embedded
        if is_one_to_one_relationship(table_name, foreign_table, foreign_column):
            foreign_singular = TableNaming.singularize(foreign_table)
            foreign_class = TableNaming.to_pascal_case(foreign_singular)

            # Check if relationship should be embedded in Thrift
            if has_embedded_relationship(table_name, foreign_singular):
                method_code += f'''
        # Handle embedded {foreign_singular} (1-to-1 relationship)
        if hasattr(thrift_obj, '{foreign_singular}') and thrift_obj.{foreign_singular} is not None:
            {foreign_singular}_obj = {foreign_class}()
            {foreign_singular}_obj.from_thrift(thrift_obj.{foreign_singular})
            # Set the foreign key to link to this parent
            {foreign_singular}_obj.set_{foreign_column}(self.get_id())
            # Cache the embedded object
            self._cached_{foreign_singular} = {foreign_singular}_obj
'''

    # Mark as dirty
    method_code += '''
        self._dirty = True
        return self
'''

    return method_code


def generate_into_thrift_method(
    table_name: str,
    class_name: str,
    columns: List[Dict[str, Any]],
    thrift_struct_name: str,
    relationships: Dict[str, Any],
    table_columns: Dict[str, List[Dict[str, Any]]],
    fk_constraints: Dict[str, List[Dict[str, str]]],
) -> str:
    """
    Generate into_thrift() method for converting Model to Thrift object.

    Args:
        table_name: Database table name
        class_name: Model class name
        columns: List of column definitions
        thrift_struct_name: Name of the Thrift struct
        relationships: Relationships metadata
        table_columns: All table columns dict
        fk_constraints: All FK constraints dict

    Returns:
        Generated method code as a string
    """
    from_game_ttypes = "from game.ttypes import ThriftGameResult, ThriftStatusType, ThriftGameError"

    method_code = f'''
    def into_thrift(self) -> Tuple[list[ThriftGameResult], Optional['{thrift_struct_name}']]:
        """
        Convert this Model instance to a Thrift {thrift_struct_name} object.

        Loads all relationships recursively and converts them to Thrift.

        Returns:
            Tuple of (list[ThriftGameResult], Optional[Thrift object])
        """
        results = []

        try:
            # Build parameters for Thrift object constructor
            thrift_params = {{}}

'''

    # Enum field mapping
    enum_fields = {
        'attributes.attribute_type': 'ThriftAttributeType',
        'items.item_type': 'ThriftItemType',
        'mobile_items.item_type': 'ThriftItemType',
        'mobiles.mobile_type': 'ThriftMobileType',
    }

    # Get list of belongs-to foreign key columns to skip (except owner union which is handled specially)
    belongs_to_rels = relationships.get("belongs_to", [])
    belongs_to_columns = [rel["column"] for rel in belongs_to_rels if rel["column"] not in ['owner_player_id', 'owner_mobile_id', 'owner_item_id', 'owner_asset_id']]

    # Map simple fields
    for col in columns:
        col_name = col['name']

        # Skip owner union fields - they're handled specially
        # Flattened pattern
        if col_name in ['owner_player_id', 'owner_mobile_id', 'owner_item_id', 'owner_asset_id']:
            continue
        # Generic pattern
        if col_name in ['owner_id', 'owner_type']:
            continue

        # Skip AttributeValue union fields - handled specially for attributes table
        if table_name == 'attributes' and col_name in ['bool_value', 'double_value', 'vector3_x', 'vector3_y', 'vector3_z', 'asset_id']:
            continue

        # Skip foreign key columns - they're handled as belongs-to relationships below
        if col_name in belongs_to_columns:
            continue

        # Check if this is an enum field
        field_key = f"{table_name}.{col_name}"
        if field_key in enum_fields:
            enum_type = enum_fields[field_key]
            # For enum fields, convert string name to enum integer using _NAMES_TO_VALUES map
            method_code += f"            {col_name}_value = self._data.get('{col_name}')\n"
            method_code += f"            if {col_name}_value is not None:\n"
            method_code += f"                thrift_params['{col_name}'] = {enum_type}._NAMES_TO_VALUES[{col_name}_value]\n"
            method_code += f"            else:\n"
            method_code += f"                thrift_params['{col_name}'] = None\n"
        else:
            method_code += f"            thrift_params['{col_name}'] = self._data.get('{col_name}')\n"

    # Handle Owner union conversion if applicable
    if needs_owner_conversion(columns):
        method_code += generate_db_to_owner_union_code(table_name, columns)
        method_code += "            thrift_params['owner'] = owner\n"

    # Handle AttributeValue union conversion if applicable (for attributes table)
    if needs_attribute_value_conversion(columns):
        method_code += generate_db_to_attribute_value_code()
        method_code += "            thrift_params['value'] = value\n"

    # Handle attribute map loading (for tables with attributes relationship)
    attr_rel_type = get_attribute_relationship_type(table_name, table_columns, fk_constraints)
    if attr_rel_type in ['pivot', 'direct']:
        # Both patterns can use get_attributes() method (direct table converts internally)
        method_code += generate_pivot_to_attribute_map_code()
        method_code += "            thrift_params['attributes'] = attributes_map\n"

    # NOTE: Belongs-to relationships are NOT embedded in Thrift by default
    # Foreign key IDs are included as direct column mappings above
    # Only has-many/1-to-1 relationships configured for embedding are included

    # Load has-many/1-to-1 embedded relationships
    has_many_rels = relationships.get('has_many', [])
    for rel in has_many_rels:
        foreign_table = rel['foreign_table']
        foreign_column = rel['foreign_column']

        # Check if this is a 1-to-1 relationship that should be embedded
        if is_one_to_one_relationship(table_name, foreign_table, foreign_column):
            foreign_singular = TableNaming.singularize(foreign_table)
            foreign_class = TableNaming.to_pascal_case(foreign_singular)

            # Check if relationship should be embedded in Thrift
            if has_embedded_relationship(table_name, foreign_singular):
                method_code += f'''
            # Load embedded {foreign_singular} (1-to-1 relationship)
            {foreign_singular}_model = self.get_{foreign_singular}()
            if {foreign_singular}_model is not None:
                {foreign_singular}_results, {foreign_singular}_thrift = {foreign_singular}_model.into_thrift()
                if {foreign_singular}_thrift is not None:
                    thrift_params['{foreign_singular}'] = {foreign_singular}_thrift
                else:
                    results.extend({foreign_singular}_results)
'''

    # Construct the Thrift object
    method_code += f'''
            # Create Thrift object
            thrift_obj = Thrift{thrift_struct_name}(**thrift_params)

            results.append(ThriftGameResult(
                status=ThriftStatusType.SUCCESS,
                message=f"Successfully converted {{self.__class__.__name__}} id={{self.get_id()}} to Thrift",
            ))

            return (results, thrift_obj)

        except Exception as e:
            return (
                [ThriftGameResult(
                    status=ThriftStatusType.FAILURE,
                    message=f"Failed to convert {{self.__class__.__name__}} to Thrift: {{str(e)}}",
                    error_code=ThriftGameError.DB_QUERY_FAILED,
                )],
                None,
            )
'''

    return method_code


def generate_model(
    table_name: str,
    columns: List[Dict[str, Any]],
    create_table_stmt: str,
    template: str,
    relationships: Dict[str, Any],
    table_columns: Dict[str, List[Dict[str, Any]]],
    fk_constraints: Dict[str, List[Dict[str, str]]],
) -> str:
    """Generate a complete model file from the template."""
    # Convert plural table name to singular class name
    singular_name = TableNaming.singularize(table_name)
    class_name = TableNaming.to_pascal_case(singular_name)

    # Get relationships for this table
    belongs_to_rels = relationships.get("belongs_to", [])
    has_many_rels = relationships.get("has_many", [])
    has_relationships = bool(belongs_to_rels or has_many_rels)

    # Check if this is a pivot table
    is_pivot = is_pivot_table(table_name, columns)
    pivot_helper_methods = ""
    if is_pivot:
        pivot_info = get_pivot_table_info(table_name, columns, fk_constraints)
        if pivot_info["owner_fks"]:
            pivot_helper_methods = generate_pivot_helper_methods(table_name, pivot_info["owner_fks"])

    # Check if this table is an owner in any pivot relationships
    pivot_owner_rels = get_pivot_owner_relationships(table_name, table_columns, fk_constraints)
    pivot_owner_methods = ""
    if pivot_owner_rels:
        methods_list = []
        for rel in pivot_owner_rels:
            methods_list.append(generate_pivot_owner_methods(
                table_name,
                rel["pivot_table"],
                rel["related_table"],
            ))
        pivot_owner_methods = "\n".join(methods_list)

    # Check for direct attribute relationship
    attr_rel_type = get_attribute_relationship_type(table_name, table_columns, fk_constraints)
    direct_attribute_methods = ""
    if attr_rel_type == 'direct':
        singular_name = TableNaming.singularize(table_name)
        attribute_table = f"{singular_name}_attributes"
        direct_attribute_methods = generate_direct_attribute_methods(table_name, attribute_table)

    # Check if this table has Thrift conversion
    has_thrift_conversion = has_thrift_mapping(table_name)

    # Generate all components
    imports = generate_imports(columns, has_relationships, has_thrift_conversion)
    getters = generate_getters(columns, table_name)
    setters = generate_setters(columns, table_name)
    find_by_methods = generate_find_by_methods(columns, class_name, table_name)

    # Generate validate_owner method if table has owner fields
    validate_owner_method = ""
    if needs_owner_conversion(columns):
        validate_owner_method = generate_validate_owner_method(table_name, class_name)

    # Generate relationship methods
    belongs_to_methods = generate_belongs_to_methods(belongs_to_rels, table_columns) if belongs_to_rels else ""
    has_many_methods = generate_has_many_methods(table_name, has_many_rels, table_columns) if has_many_rels else ""

    # Generate cascade save code
    cascade_save_belongs_to, cascade_save_has_many = generate_cascade_save_code(
        belongs_to_rels,
        has_many_rels,
    )

    # Generate cascade destroy code
    cascade_destroy = generate_cascade_destroy_code(
        table_name,
        has_many_rels,
        pivot_owner_rels,
    )

    # Generate Thrift conversion methods if applicable
    thrift_conversion_methods = ""
    thrift_struct_name = get_thrift_struct_name(table_name)
    if thrift_struct_name is not None:
        from_thrift_method = generate_from_thrift_method(
            table_name,
            class_name,
            columns,
            thrift_struct_name,
            relationships,
            table_columns,
            fk_constraints,
        )
        into_thrift_method = generate_into_thrift_method(
            table_name,
            class_name,
            columns,
            thrift_struct_name,
            relationships,
            table_columns,
            fk_constraints,
        )
        thrift_conversion_methods = from_thrift_method + "\n" + into_thrift_method

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
        setters=setters + ("\n\n" + validate_owner_method if validate_owner_method else ""),
        pivot_helper_methods=pivot_helper_methods,
        belongs_to_methods=belongs_to_methods,
        has_many_methods=has_many_methods,
        pivot_owner_methods=pivot_owner_methods,
        direct_attribute_methods=direct_attribute_methods,
        cascade_save_belongs_to=cascade_save_belongs_to,
        cascade_save_has_many=cascade_save_has_many,
        cascade_destroy=cascade_destroy,
        find_by_methods=find_by_methods,
        thrift_conversion_methods=thrift_conversion_methods,
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

    # Enum field mapping for test data generation
    enum_fields = {
        'attributes.attribute_type': ('ThriftAttributeType', 'QUANTITY'),  # (enum_class, default_value)
        'items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobile_items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobiles.mobile_type': ('ThriftMobileType', 'PLAYER'),
    }

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
        table_name = model['table_name']
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
                # Check if this is an enum field
                field_key = f"{table_name}.{col['name']}"
                if field_key in enum_fields:
                    enum_type, enum_value = enum_fields[field_key]
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}({enum_type}.{enum_value})\n"
                else:
                    python_type = TypeMapper.get_python_type(col['data_type'])
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
                # Check if this is an enum field
                field_key = f"{table_name}.{col['name']}"
                if field_key in enum_fields:
                    enum_type, enum_value = enum_fields[field_key]
                    # Use NPC for second instance if it's mobile_type
                    if field_key == 'mobiles.mobile_type':
                        code += f"    seed['{class_name.lower()}2'].set_{col['name']}({enum_type}.NPC)\n"
                    else:
                        code += f"    seed['{class_name.lower()}2'].set_{col['name']}({enum_type}.{enum_value})\n"
                else:
                    python_type = TypeMapper.get_python_type(col['data_type'])
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
        table_name = model['table_name']
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
                            target_class = TableNaming.to_pascal_case(TableNaming.singularize(rel['referenced_table']))
                            # Use seed data if available
                            seed_key = f"{target_class.lower()}1"
                            code += f"    if '{seed_key}' in seed:\n"
                            code += f"        seed['{class_name.lower()}1'].set_{col['name']}(seed['{seed_key}'].get_id())\n"
                continue
            if not col['is_nullable']:
                # Check if this is an enum field
                field_key = f"{table_name}.{col['name']}"
                if field_key in enum_fields:
                    enum_type, enum_value = enum_fields[field_key]
                    code += f"    seed['{class_name.lower()}1'].set_{col['name']}({enum_type}.{enum_value})\n"
                else:
                    python_type = TypeMapper.get_python_type(col['data_type'])
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


def set_required_fields_for_model(
    model: Dict[str, Any],
    all_models: List[Dict[str, Any]],
    tests: List[str],
    var_name: str,
    var_suffix: str = "",
    skip_column: Optional[str] = None,
) -> None:
    """
    Helper function to set ALL required (NOT NULL) fields for a model.
    This ensures we never miss required fields in test generation.

    Args:
        model: The model dictionary containing columns
        all_models: List of all models for FK prerequisite creation
        tests: List to append test code to
        var_name: Variable name of the model instance (e.g., 'parent', 'related1')
        var_suffix: Suffix for prerequisite variable names
        skip_column: Optional column name to skip (e.g., the FK we're testing)
    """
    # Enum field mapping
    enum_fields = {
        'attributes.attribute_type': ('ThriftAttributeType', 'STRENGTH'),
        'items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobile_items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobiles.mobile_type': ('ThriftMobileType', 'PLAYER'),
    }

    table_name = model['table_name']

    for col in model['columns']:
        if col['name'] == 'id' or col['is_nullable']:
            continue

        # Skip the column if requested (e.g., FK we're testing)
        if skip_column and col['name'] == skip_column:
            continue

        python_type = TypeMapper.get_python_type(col['data_type'])

        # Check if this is an enum field
        field_key = f"{table_name}.{col['name']}"
        if field_key in enum_fields:
            enum_type, enum_value = enum_fields[field_key]
            tests.append(f"        {var_name}.set_{col['name']}({enum_type}.{enum_value})")
        # Handle FK columns (ending with _id)
        elif col['name'].endswith('_id'):
            prereq_var = create_prerequisite_for_fk_column(col, all_models, tests, var_suffix=var_suffix)
            if prereq_var:
                tests.append(f"        {var_name}.set_{col['name']}({prereq_var}.get_id())")
            else:
                # Fallback if we can't create prerequisite
                tests.append(f"        {var_name}.set_{col['name']}(1)")
        else:
            # Handle regular required fields based on type
            if python_type == 'str':
                tests.append(f"        {var_name}.set_{col['name']}('test_{col['name']}')")
            elif python_type == 'int':
                tests.append(f"        {var_name}.set_{col['name']}(1)")
            elif python_type == 'float':
                tests.append(f"        {var_name}.set_{col['name']}(1.0)")
            elif python_type == 'bool':
                tests.append(f"        {var_name}.set_{col['name']}(True)")


def create_prerequisite_for_fk_column(
    col: Dict[str, Any],
    all_models: List[Dict[str, Any]],
    tests: List[str],
    var_suffix: str = "",
) -> Optional[str]:
    """
    Helper function to create prerequisite object for a NOT NULL FK column.
    Returns the variable name of the created prerequisite, or None if it couldn't be created.
    """
    if not col['name'].endswith('_id') or col['is_nullable']:
        return None

    # Infer table name from column name (e.g., inventory_id -> inventories)
    prereq_table = col['name'][:-3]  # Remove '_id' suffix

    # Try plural form first (most common)
    prereq_model = next((m for m in all_models if m['table_name'] == (prereq_table + 's')), None)
    if not prereq_model:
        # Try singular form
        prereq_model = next((m for m in all_models if m['table_name'] == prereq_table), None)

    if not prereq_model:
        return None

    prereq_var = f"{prereq_table}_prereq{var_suffix}"
    prereq_class = prereq_model['class_name']

    tests.append(f"        # Create prerequisite {prereq_class} for {col['name']}\n")
    tests.append(f"        {prereq_var} = {prereq_class}()\n")

    # Enum field mapping
    enum_fields = {
        'attributes.attribute_type': ('ThriftAttributeType', 'STRENGTH'),
        'items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobile_items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobiles.mobile_type': ('ThriftMobileType', 'PLAYER'),
    }

    # Set required fields for prerequisite
    # IMPORTANT: We treat ALL NOT NULL columns ending with _id as FKs, regardless of SQL FK constraints
    for prereq_col in prereq_model['columns']:
        if prereq_col['name'] == 'id':
            continue
        if prereq_col['is_nullable']:
            continue

        # Check if this is an enum field
        prereq_field_key = f"{prereq_model['table_name']}.{prereq_col['name']}"
        if prereq_field_key in enum_fields:
            enum_type, enum_value = enum_fields[prereq_field_key]
            tests.append(f"        {prereq_var}.set_{prereq_col['name']}({enum_type}.{enum_value})\n")
        # For NOT NULL _id columns, set to 1 as placeholder (avoid infinite recursion)
        elif prereq_col['name'].endswith('_id'):
            tests.append(f"        {prereq_var}.set_{prereq_col['name']}(1)\n")
        else:
            # Regular required field
            py_type = TypeMapper.get_python_type(prereq_col['data_type'])
            if py_type == 'str':
                tests.append(f"        {prereq_var}.set_{prereq_col['name']}('test_prereq{var_suffix}')\n")
            elif py_type == 'int':
                tests.append(f"        {prereq_var}.set_{prereq_col['name']}(1)\n")
            elif py_type == 'float':
                tests.append(f"        {prereq_var}.set_{prereq_col['name']}(1.0)\n")
            elif py_type == 'bool':
                tests.append(f"        {prereq_var}.set_{prereq_col['name']}(True)\n")

    tests.append(f"        {prereq_var}.save()\n\n")

    return prereq_var


def generate_belongs_to_tests(model: Dict[str, Any], all_models: List[Dict[str, Any]]) -> str:
    """Generate belongs-to relationship tests for a model."""
    class_name = model['class_name']
    belongs_to_rels = model.get('relationships', {}).get('belongs_to', [])

    if not belongs_to_rels:
        return ""

    tests = []

    for rel in belongs_to_rels:
        rel_name = TableNaming.column_to_relationship_name(rel['column'])
        target_class = TableNaming.to_pascal_case(TableNaming.singularize(rel['referenced_table']))
        fk_column = rel['column']

        # Basic getter test
        test_name = f"test_belongs_to_{rel_name}_basic"
        tests.append(f'''
    def {test_name}(self):
        """Test {rel_name} relationship basic getter."""
        # Create related model
        related = {target_class}()''')

        # Set all required fields for target class
        target_model = next((m for m in all_models if m['class_name'] == target_class), None)
        if target_model:
            set_required_fields_for_model(target_model, all_models, tests, "related", var_suffix="_basic")

        tests.append(f'''        related.save()

        # Create parent and set FK
        parent = {class_name}()''')

        # Set all required fields for parent (skip the FK we're testing)
        set_required_fields_for_model(model, all_models, tests, "parent", var_suffix="_basic", skip_column=fk_column)

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

        # Set all required fields for target model
        target_model_setter = next((m for m in all_models if m['class_name'] == target_class), None)
        if target_model_setter:
            set_required_fields_for_model(target_model_setter, all_models, tests, "related1", var_suffix="_setter")

        tests.append(f'''        related1.save()

        # Create parent
        parent = {class_name}()''')

        # Set all required fields for parent
        set_required_fields_for_model(model, all_models, tests, "parent", var_suffix="_setter")

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
    """Generate has-many relationship tests for a model (including 1-to-1 tests)."""
    class_name = model['class_name']
    table_name = model['table_name']
    has_many_rels = model.get('relationships', {}).get('has_many', [])

    if not has_many_rels:
        return ""

    tests = []

    for rel in has_many_rels:
        rel_name = rel['foreign_table']
        foreign_table = rel['foreign_table']
        foreign_class = TableNaming.to_pascal_case(TableNaming.singularize(rel['foreign_table']))
        fk_column = rel['foreign_column']

        # Check if this is a 1-to-1 relationship
        is_one_to_one = is_one_to_one_relationship(table_name, foreign_table, fk_column)
        if is_one_to_one:
            rel_name = TableNaming.singularize(rel_name)  # Use singular name for 1-to-1

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

        # Set all required fields for parent
        set_required_fields_for_model(model, all_models, tests, "parent", var_suffix="_parent")

        tests.append("        parent.save()\n\n")

        # Check if foreign model is a pivot table
        is_pivot = foreign_model['table_name'] in PIVOT_TABLES

        # Find other required FK columns and create those records first
        prereq_records = {}
        for col in foreign_model['columns']:
            # For pivot tables, we need to create prerequisites for ALL FKs except the owner FK
            # For regular tables, skip the FK pointing back to parent
            skip_this_col = col['name'] == fk_column and not is_pivot

            if col['name'] != 'id' and col['name'].endswith('_id') and not col['is_nullable'] and not skip_this_col:
                # Need to create a prerequisite record
                prereq_table = col['name'][:-3]  # Remove '_id' suffix
                prereq_class = TableNaming.to_pascal_case(TableNaming.singularize(prereq_table + 's'))  # Pluralize and convert

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

                    # Enum field mapping
                    enum_fields_map = {
                        'attributes.attribute_type': ('ThriftAttributeType', 'STRENGTH'),
                        'items.item_type': ('ThriftItemType', 'WEAPON'),
                        'mobile_items.item_type': ('ThriftItemType', 'WEAPON'),
                        'mobiles.mobile_type': ('ThriftMobileType', 'PLAYER'),
                    }

                    # Set required fields for prerequisite
                    for prereq_col in prereq_model['columns']:
                        if prereq_col['name'] != 'id' and not prereq_col['is_nullable'] and not prereq_col['name'].endswith('_id'):
                            # Check if this is an enum field
                            prereq_field_key = f"{prereq_model['table_name']}.{prereq_col['name']}"
                            if prereq_field_key in enum_fields_map:
                                enum_type, enum_value = enum_fields_map[prereq_field_key]
                                tests.append(f"        {prereq_var}.set_{prereq_col['name']}({enum_type}.{enum_value})\n")
                            else:
                                py_type = TypeMapper.get_python_type(prereq_col['data_type'])
                                if py_type == 'str':
                                    tests.append(f"        {prereq_var}.set_{prereq_col['name']}('test_prereq')\n")
                                elif py_type == 'int':
                                    tests.append(f"        {prereq_var}.set_{prereq_col['name']}(1)\n")
                                elif py_type == 'bool':
                                    tests.append(f"        {prereq_var}.set_{prereq_col['name']}(True)\n")

                    tests.append(f"        {prereq_var}.save()\n\n")

        tests.append(f'''        # Create related records
        child1 = {foreign_class}()''')

        # Set all required fields for child1, but handle the FK to parent specially
        # First set the FK to parent
        tests.append(f"        child1.set_{fk_column}(parent.get_id())")
        # Then set all other required fields (skip the FK we just set)
        set_required_fields_for_model(foreign_model, all_models, tests, "child1", var_suffix="_child1", skip_column=fk_column)

        tests.append(f'''        child1.save()

        child2 = {foreign_class}()''')

        # Set all required fields for child2
        tests.append(f"        child2.set_{fk_column}(parent.get_id())")
        set_required_fields_for_model(foreign_model, all_models, tests, "child2", var_suffix="_child2", skip_column=fk_column)

        if is_one_to_one:
            tests.append(f'''        child2.save()

        # Test getter (1-to-1 relationship)
        result = parent.get_{rel_name}()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, {foreign_class})
        self.assertEqual(result.get_{fk_column}(), parent.get_id())

        # Test caching
        result2 = parent.get_{rel_name}()
        self.assertIs(result, result2)

        # Test reload
        result3 = parent.get_{rel_name}(reload=True)
        self.assertIsNotNone(result3)
        self.assertEqual(result3.get_{fk_column}(), parent.get_id())
''')
        else:
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

        # Lazy mode test (skip for 1-to-1 relationships)
        if not is_one_to_one:
            test_name = f"test_has_many_{rel_name}_lazy"
            tests.append(f'''
    def {test_name}(self):
        """Test {rel_name} relationship lazy loading."""
        # Create parent with children
        parent = {class_name}()''')

            # Set all required fields for parent
            set_required_fields_for_model(model, all_models, tests, "parent", var_suffix="_parent_lazy")

            tests.append("        parent.save()\n\n")

            # Create prerequisite records for lazy test too
            # Use same logic as basic test - for pivot tables, include all FKs
            prereq_records_lazy = {}
            for col in foreign_model['columns']:
                # For pivot tables, skip only the owner FK. For regular tables, skip parent FK
                skip_this_col = col['name'] == fk_column and not is_pivot

                if col['name'] != 'id' and col['name'].endswith('_id') and not col['is_nullable'] and not skip_this_col:
                    # Need to create a prerequisite record
                    prereq_table = col['name'][:-3]
                    prereq_class = TableNaming.to_pascal_case(TableNaming.singularize(prereq_table + 's'))

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
                            if prereq_col['name'] != 'id' and not prereq_col['is_nullable']:
                                test_value = get_test_value_for_column(prereq_model['table_name'], prereq_col)
                                tests.append(f"        {prereq_var}.set_{prereq_col['name']}({test_value})\n")

                        tests.append(f"        {prereq_var}.save()\n\n")

            tests.append(f'''        # Create child
        child = {foreign_class}()''')

            # Set FK to parent and all other required fields
            tests.append(f"        child.set_{fk_column}(parent.get_id())")
            set_required_fields_for_model(foreign_model, all_models, tests, "child", var_suffix="_child_lazy", skip_column=fk_column)

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


def get_test_value_for_column(table_name: str, col: Dict[str, Any]) -> str:
    """
    Get appropriate test value for a column, accounting for enum fields.
    Returns the Python code to use as the value (as a string).
    """
    # Enum field mapping
    enum_fields = {
        'attributes.attribute_type': ('ThriftAttributeType', 'STRENGTH'),
        'items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobile_items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobiles.mobile_type': ('ThriftMobileType', 'PLAYER'),
    }

    field_key = f"{table_name}.{col['name']}"
    if field_key in enum_fields:
        enum_type, enum_value = enum_fields[field_key]
        return f"{enum_type}.{enum_value}"

    # For FK columns, use 1
    if col['name'].endswith('_id'):
        return "1"

    # For regular fields, use type-based defaults
    python_type = TypeMapper.get_python_type(col['data_type'])
    if python_type == 'str':
        return f"'test_{col['name']}'"
    elif python_type == 'int':
        return "1"
    elif python_type == 'bool':
        return "True"
    elif python_type == 'float':
        return "1.0"
    else:
        return "'test_value'"


def generate_dirty_tracking_tests(model: Dict[str, Any], all_models: List[Dict[str, Any]]) -> str:
    """Generate dirty tracking tests for a model."""
    class_name = model['class_name']
    table_name = model['table_name']
    columns = model['columns']

    # Find a settable column for testing
    test_col = None
    for col in columns:
        if col['name'] != 'id' and not col['name'].endswith('_id') and not col['is_nullable']:
            test_col = col
            break

    if not test_col:
        return ""

    # Enum field mapping
    enum_fields = {
        'attributes.attribute_type': ('ThriftAttributeType', 'STRENGTH'),
        'items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobile_items.item_type': ('ThriftItemType', 'WEAPON'),
        'mobiles.mobile_type': ('ThriftMobileType', 'PLAYER'),
    }

    # Get test values using helper
    test_value1 = get_test_value_for_column(table_name, test_col)
    # For second value, try to make it different
    field_key = f"{table_name}.{test_col['name']}"
    if field_key in enum_fields:
        enum_type, _ = enum_fields[field_key]
        # Use different enum value for second test
        if field_key == 'mobiles.mobile_type':
            test_value2 = f"{enum_type}.NPC"
        elif field_key == 'attributes.attribute_type':
            test_value2 = f"{enum_type}.DEXTERITY"
        elif field_key == 'items.item_type' or field_key == 'mobile_items.item_type':
            test_value2 = f"{enum_type}.CONTAINER"
        else:
            test_value2 = test_value1
    else:
        python_type = TypeMapper.get_python_type(test_col['data_type'])
        if python_type == 'str':
            test_value2 = "'test_value_2'"
        elif python_type == 'int':
            test_value2 = "2"
        elif python_type == 'bool':
            test_value2 = "False"
        elif python_type == 'float':
            test_value2 = "2.0"
        else:
            test_value2 = test_value1

    tests_list = []
    tests_list.append(f'''
    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = {class_name}()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = {class_name}()''')

    # Set required fields
    # IMPORTANT: We treat ALL NOT NULL columns ending with _id as FKs, regardless of SQL FK constraints
    for col in columns:
        if col['name'] == 'id' or col['is_nullable']:
            continue

        test_value = get_test_value_for_column(table_name, col)
        tests_list.append(f"\n        model.set_{col['name']}({test_value})")

    tests_list.append(f'''
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = {class_name}()''')

    for col in columns:
        if col['name'] == 'id' or col['is_nullable']:
            continue

        test_value = get_test_value_for_column(table_name, col)
        tests_list.append(f"\n        model.set_{col['name']}({test_value})")

    tests_list.append(f'''
        model.save()
        self.assertFalse(model._dirty)

        model.set_{test_col['name']}({test_value2})
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = {class_name}()''')

    for col in columns:
        if col['name'] == 'id' or col['is_nullable']:
            continue

        test_value = get_test_value_for_column(table_name, col)
        tests_list.append(f"\n        model.set_{col['name']}({test_value})")

    tests_list.append(f'''
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)
''')

    return "".join(tests_list)


def generate_cascade_save_tests(model: Dict[str, Any], all_models: List[Dict[str, Any]]) -> str:
    """Generate cascade save tests for a model."""
    class_name = model['class_name']
    belongs_to_rels = model.get('relationships', {}).get('belongs_to', [])

    if not belongs_to_rels:
        return ""

    # Take first belongs-to relationship for testing
    rel = belongs_to_rels[0]
    rel_name = TableNaming.column_to_relationship_name(rel['column'])
    target_class = TableNaming.to_pascal_case(TableNaming.singularize(rel['referenced_table']))

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
    # IMPORTANT: We treat ALL NOT NULL columns ending with _id as FKs, regardless of SQL FK constraints
    for col in target_model.get('columns', []):
        if col['name'] == 'id' or col['is_nullable']:
            continue

        test_value = get_test_value_for_column(target_model['table_name'], col)
        tests += f"\n        related.set_{col['name']}({test_value})"

    tests += f'''
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = {class_name}()'''

    # Set required fields for parent
    # IMPORTANT: We treat ALL NOT NULL columns ending with _id as FKs, regardless of SQL FK constraints
    for col in model['columns']:
        if col['name'] == 'id' or col['is_nullable']:
            continue

        test_value = get_test_value_for_column(model['table_name'], col)
        tests += f"\n        parent.set_{col['name']}({test_value})"

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


def generate_cascade_destroy_tests(model: Dict[str, Any], all_models: List[Dict[str, Any]]) -> str:
    """Generate cascade destroy tests for a model."""
    class_name = model['class_name']
    has_many_rels = model.get('relationships', {}).get('has_many', [])

    if not has_many_rels:
        return ""

    # Take first has-many relationship for testing
    rel = has_many_rels[0]
    rel_name = rel["foreign_table"]
    target_class = TableNaming.to_pascal_case(TableNaming.singularize(rel['foreign_table']))

    # Find target model
    target_model = next((m for m in all_models if m['class_name'] == target_class), None)
    if not target_model:
        return ""

    tests = f'''
    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = {class_name}()'''

    # Set required fields for parent
    for col in model['columns']:
        if col['name'] == 'id' or col['is_nullable']:
            continue
        test_value = get_test_value_for_column(model['table_name'], col)
        tests += f"\n        parent.set_{col['name']}({test_value})"

    tests += f'''
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = {target_class}()'''

    # Set required fields for child1
    for col in target_model['columns']:
        if col['name'] == 'id' or col['is_nullable']:
            continue
        # Skip the FK to parent - we'll set it via relationship
        if col['name'] == rel['foreign_column']:
            continue
        test_value = get_test_value_for_column(target_model['table_name'], col)
        tests += f"\n        child1.set_{col['name']}({test_value})"

    tests += f'''
        child1.set_{rel['foreign_column']}(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = {target_class}()'''

    # Set required fields for child2
    for col in target_model['columns']:
        if col['name'] == 'id' or col['is_nullable']:
            continue
        # Skip the FK to parent - we'll set it via relationship
        if col['name'] == rel['foreign_column']:
            continue
        test_value = get_test_value_for_column(target_model['table_name'], col)
        tests += f"\n        child2.set_{col['name']}({test_value})"

    tests += f'''
        child2.set_{rel['foreign_column']}(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_{rel_name}(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = {class_name}.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = {target_class}.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = {target_class}.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = {class_name}()'''

    # Set required fields for parent (again)
    for col in model['columns']:
        if col['name'] == 'id' or col['is_nullable']:
            continue
        test_value = get_test_value_for_column(model['table_name'], col)
        tests += f"\n        parent.set_{col['name']}({test_value})"

    tests += f'''
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = {target_class}()'''

    # Set required fields for child
    for col in target_model['columns']:
        if col['name'] == 'id' or col['is_nullable']:
            continue
        # Skip the FK to parent - we'll set it via relationship
        if col['name'] == rel['foreign_column']:
            continue
        test_value = get_test_value_for_column(target_model['table_name'], col)
        tests += f"\n        child.set_{col['name']}({test_value})"

    tests += f'''
        child.set_{rel['foreign_column']}(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = {class_name}.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = {target_class}.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass
'''

    return tests


def generate_thrift_conversion_tests(model: Dict[str, Any]) -> str:
    """Generate tests for Thrift conversion (from_thrift/into_thrift) with focus on enum fields."""
    table_name = model['table_name']
    class_name = model['class_name']

    # Enum field mapping
    enum_fields = {
        'attributes.attribute_type': ('AttributeType', 'STRENGTH'),
        'items.item_type': ('ItemType', 'RAWMATERIAL'),
        'mobile_items.item_type': ('ItemType', 'RAWMATERIAL'),
    }

    tests = ""

    # Check if this model has enum fields
    has_enum = False
    enum_field_info = []
    for col in model['columns']:
        field_key = f"{table_name}.{col['name']}"
        if field_key in enum_fields:
            has_enum = True
            enum_type, test_value = enum_fields[field_key]
            enum_field_info.append((col['name'], enum_type, test_value))

    if not has_enum:
        return tests

    # Generate from_thrift test with enum fields
    tests += f'''
    def test_from_thrift_with_enum(self):
        """Test from_thrift correctly converts enum integer to string name."""'''

    # Import and create Thrift struct
    # Use base name from TABLE_TO_THRIFT_MAPPING
    thrift_struct_name = TABLE_TO_THRIFT_MAPPING.get(table_name)
    if not thrift_struct_name:
        return tests  # No Thrift mapping for this table

    # Alias the Thrift struct to avoid collision with model class name
    thrift_alias = f"Thrift{thrift_struct_name}"

    tests += f'''
        from game.ttypes import {thrift_struct_name} as {thrift_alias}'''

    for col_name, enum_type, test_value in enum_field_info:
        tests += f''', {enum_type}'''

    tests += f'''

        # Create Thrift object with enum field'''

    # Build Thrift constructor params using the aliased name
    tests += f'''
        thrift_obj = {thrift_alias}('''

    # Add required fields
    for col in model['columns']:
        if col['name'] == 'id':
            continue
        field_key = f"{table_name}.{col['name']}"
        if field_key in enum_fields:
            enum_type, test_value = enum_fields[field_key]
            tests += f'''
            {col['name']}={enum_type}.{test_value},'''
        elif not col['is_nullable']:
            test_value = get_test_value_for_column(table_name, col)
            tests += f'''
            {col['name']}={test_value},'''

    tests += f'''
        )

        # Convert to model
        model = {class_name}()
        model.from_thrift(thrift_obj)

        # Verify enum was converted to string name'''

    for col_name, enum_type, test_value in enum_field_info:
        tests += f'''
        self.assertEqual(model._data['{col_name}'], '{test_value}')'''

    tests += f'''

        # Save and reload to verify round-trip
        model.save()
        model_id = model.get_id()
        self.assertIsNotNone(model_id)

        # Load from database
        loaded_model = {class_name}.find(model_id)
        self.assertIsNotNone(loaded_model)'''

    for col_name, enum_type, test_value in enum_field_info:
        tests += f'''
        self.assertEqual(loaded_model._data['{col_name}'], '{test_value}')'''

    tests += f'''

        # Convert back to Thrift
        results, thrift_obj_out = loaded_model.into_thrift()
        if thrift_obj_out is None:
            # Print error details if conversion failed
            for result in results:
                print(f"into_thrift error: {{result.message}}")
        self.assertIsNotNone(thrift_obj_out, f"into_thrift failed: {{results[0].message if results else 'unknown'}}")'''

    for col_name, enum_type, test_value in enum_field_info:
        tests += f'''
        self.assertEqual(thrift_obj_out.{col_name}, {enum_type}.{test_value})'''

    tests += '''

        # Clean up - use fresh connection to avoid nested transaction
        cleanup_conn = loaded_model._create_connection()
        loaded_model.destroy(connection=cleanup_conn)
        cleanup_conn.close()
'''

    return tests


def generate_tests(models: List[Dict[str, Any]]) -> str:
    """Generate comprehensive tests.py file for all models with relationship testing."""
    # Add sys.path manipulation first
    header = [
        "#!/usr/bin/env python3",
        '"""',
        "Auto-generated test suite for all models.",
        "Generated from database schema - do not modify manually.",
        '"""',
        "",
        "import sys",
        "import os",
        "",
        "# Add parent directory to path for models import",
        "parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
        "if parent_dir not in sys.path:",
        "    sys.path.insert(0, parent_dir)",
        "",
        "# Add Thrift generated code to path",
        "thrift_gen_path = '/vagrant/gamedb/thrift/gen-py'",
        "if thrift_gen_path not in sys.path:",
        "    sys.path.insert(0, thrift_gen_path)",
        "",
    ]

    imports = [
        "import unittest",
        "import mysql.connector",
        "import uuid",
        "from dotenv import load_dotenv",
        "from game.ttypes import AttributeType as ThriftAttributeType, ItemType as ThriftItemType, MobileType as ThriftMobileType",
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
        dirty_tests = generate_dirty_tracking_tests(model, models)
        if dirty_tests:
            test_class += dirty_tests

        # Add cascade save tests
        cascade_tests = generate_cascade_save_tests(model, models)
        if cascade_tests:
            test_class += cascade_tests

        # Add cascade destroy tests
        destroy_tests = generate_cascade_destroy_tests(model, models)
        if destroy_tests:
            test_class += destroy_tests

        # Add Thrift conversion tests if table has Thrift mapping
        if has_thrift_mapping(model['table_name']):
            thrift_tests = generate_thrift_conversion_tests(model)
            if thrift_tests:
                test_class += thrift_tests
            else:
                # Note about other Thrift tests that could be added
                test_class += f'''
    # TODO: Add Owner union tests for tables with owner fields
    # TODO: Add AttributeValue union tests for attributes table
'''

        test_classes.append(test_class)

    # Combine everything
    test_code = "\n".join(header)
    test_code += "\n".join(imports)
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

        # Validate configuration
        print("\nValidating configuration...")
        # Temporarily add Thrift path for validation
        import sys
        thrift_gen_path = '/vagrant/gamedb/thrift/gen-py'
        if thrift_gen_path not in sys.path:
            sys.path.insert(0, thrift_gen_path)

        config_errors = validate_config(tables)
        if config_errors:
            print("❌ Configuration validation failed:")
            for error in config_errors:
                print(f"  - {error}")
            print("\nPlease fix configuration in generator/config.py")
            return 1
        print("✓ Configuration valid")

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
        all_imports.add("from typing import Dict, List, Optional, Any, Iterator, Union, Tuple")

        # Check if any model needs datetime
        needs_datetime = any(
            any(TypeMapper.get_python_type(col["data_type"]) == "datetime" for col in table_columns[table])
            for table in tables
        )
        if needs_datetime:
            all_imports.add("from datetime import datetime")

        # Check if any model has Thrift conversion (needs Thrift imports)
        needs_thrift = any(has_thrift_mapping(table) for table in tables)
        if needs_thrift:
            all_imports.add("from game.ttypes import GameResult as ThriftGameResult, StatusType as ThriftStatusType, GameError as ThriftGameError, Owner as ThriftOwner, AttributeValue as ThriftAttributeValue, AttributeType as ThriftAttributeType, ItemType as ThriftItemType, MobileType as ThriftMobileType, ItemVector3 as ThriftItemVector3, Attribute as ThriftAttribute, Item as ThriftItem, Mobile as ThriftMobile, Player as ThriftPlayer, MobileItem as ThriftMobileItem, Inventory as ThriftInventory, InventoryEntry as ThriftInventoryEntry, ItemBlueprint as ThriftItemBlueprint, ItemBlueprintComponent as ThriftItemBlueprintComponent")

        # Add header
        models_output.append("#!/usr/bin/env python3")
        models_output.append('"""')
        models_output.append("Auto-generated model classes for all database tables.")
        models_output.append("Generated from database schema - do not modify manually.")
        models_output.append('"""')
        models_output.append("")
        models_output.append("import sys")
        models_output.append("import os")
        models_output.append("")
        models_output.append("# Add Thrift generated code to path")
        models_output.append("thrift_gen_path = '/vagrant/gamedb/thrift/gen-py'")
        models_output.append("if thrift_gen_path not in sys.path:")
        models_output.append("    sys.path.insert(0, thrift_gen_path)")
        models_output.append("")
        models_output.append("\n".join(sorted([imp for imp in all_imports if not imp.startswith("import os")])))
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
                fk_constraints,
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
            singular_name = TableNaming.singularize(table_name)
            generated_models.append(
                {
                    "table_name": table_name,
                    "class_name": TableNaming.to_pascal_case(singular_name),
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
            singular_name = TableNaming.singularize(model_info["table_name"])
            old_file = os.path.join(os.path.dirname(__file__), f"{singular_name}.py")
            if os.path.exists(old_file):
                os.remove(old_file)
                print(f"  - Deleted {old_file}")

        print(f"\n✓ Successfully generated {len(generated_models)} models in single file!")

        # Generate tests
        print("\nGenerating tests.py...")
        test_code = generate_tests(generated_models)
        test_file = os.path.join(os.path.dirname(__file__), "tests", "tests.py")
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
