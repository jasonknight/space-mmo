"""
Type mapping utilities for converting MySQL types to Python types.
"""

from typing import Optional, Set, List, Dict, Any


class TypeMapper:
    """Maps database types to Python types."""

    MAPPINGS = {
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

    @classmethod
    def get_python_type(cls, mysql_type: str) -> str:
        """
        Convert MySQL type to Python type annotation.

        Args:
            mysql_type: MySQL column type (e.g., 'varchar(255)', 'int(11)')

        Returns:
            Python type annotation string (e.g., 'str', 'int')

        Examples:
            >>> TypeMapper.get_python_type('varchar(255)')
            'str'
            >>> TypeMapper.get_python_type('int(11)')
            'int'
            >>> TypeMapper.get_python_type('datetime')
            'datetime'
        """
        base_type = mysql_type.split("(")[0].split(" ")[0].lower()
        return cls.MAPPINGS.get(base_type, "Any")

    @classmethod
    def get_import_for_type(cls, python_type: str) -> Optional[str]:
        """
        Get required import statement for a Python type.

        Args:
            python_type: Python type name (e.g., 'datetime', 'int')

        Returns:
            Import statement string if needed, None otherwise

        Examples:
            >>> TypeMapper.get_import_for_type('datetime')
            'from datetime import datetime'
            >>> TypeMapper.get_import_for_type('int')
            None
        """
        if python_type == "datetime":
            return "from datetime import datetime"
        return None

    @classmethod
    def collect_required_types(cls, columns: List[Dict[str, Any]]) -> Set[str]:
        """
        Collect all unique Python types needed for a set of columns.

        Args:
            columns: List of column definitions with 'data_type' keys

        Returns:
            Set of Python type strings

        Examples:
            >>> columns = [
            ...     {'data_type': 'varchar(255)'},
            ...     {'data_type': 'int(11)'},
            ...     {'data_type': 'datetime'},
            ... ]
            >>> TypeMapper.collect_required_types(columns)
            {'str', 'int', 'datetime'}
        """
        return {cls.get_python_type(col["data_type"]) for col in columns}

    @classmethod
    def needs_datetime_import(cls, columns: List[Dict[str, Any]]) -> bool:
        """
        Check if any column requires datetime import.

        Args:
            columns: List of column definitions

        Returns:
            True if datetime import is needed, False otherwise
        """
        return "datetime" in cls.collect_required_types(columns)
