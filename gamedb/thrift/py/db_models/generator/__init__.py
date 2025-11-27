"""
Generator module for ActiveRecord-style models.
Contains utilities and code generators for creating database models.
"""

from .naming import TableNaming
from .type_mapping import TypeMapper
from .database import (
    decode_if_bytes,
    get_table_columns,
    get_all_tables,
    get_create_table_statement,
    get_foreign_key_constraints,
    get_unique_constraints,
)
from .config import (
    OWNER_COLUMNS,
    ATTRIBUTE_VALUE_COLUMNS,
    PIVOT_TABLES,
    TABLE_TO_THRIFT_MAPPING,
    THRIFT_CONVERSION_CONFIG,
)

__all__ = [
    'TableNaming',
    'TypeMapper',
    'decode_if_bytes',
    'get_table_columns',
    'get_all_tables',
    'get_create_table_statement',
    'get_foreign_key_constraints',
    'get_unique_constraints',
    'OWNER_COLUMNS',
    'ATTRIBUTE_VALUE_COLUMNS',
    'PIVOT_TABLES',
    'TABLE_TO_THRIFT_MAPPING',
    'THRIFT_CONVERSION_CONFIG',
]
