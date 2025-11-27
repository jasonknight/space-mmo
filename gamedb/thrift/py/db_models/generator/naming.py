"""
Table and column naming utilities for code generation.
Handles conversions between database naming conventions and Python class naming.
"""


class TableNaming:
    """Centralized table and column naming utilities."""

    @staticmethod
    def to_pascal_case(snake_str: str) -> str:
        """
        Convert snake_case to PascalCase.

        Args:
            snake_str: String in snake_case format

        Returns:
            String in PascalCase format

        Examples:
            >>> TableNaming.to_pascal_case('user_profile')
            'UserProfile'
            >>> TableNaming.to_pascal_case('item')
            'Item'
        """
        return "".join(word.capitalize() for word in snake_str.split("_"))

    @staticmethod
    def singularize(table_name: str) -> str:
        """
        Convert plural table name to singular.
        Handles common English pluralization patterns.

        Args:
            table_name: Plural table name

        Returns:
            Singular form of the table name

        Examples:
            >>> TableNaming.singularize('inventories')
            'inventory'
            >>> TableNaming.singularize('items')
            'item'
            >>> TableNaming.singularize('classes')
            'class'
        """
        if table_name.endswith("ies"):
            return table_name[:-3] + "y"
        elif table_name.endswith("sses"):
            return table_name[:-2]
        elif table_name.endswith("ses"):
            return table_name[:-1]
        elif table_name.endswith("s"):
            return table_name[:-1]
        return table_name

    @staticmethod
    def pluralize(word: str) -> str:
        """
        Convert singular word to plural form.

        Args:
            word: Singular word

        Returns:
            Plural form of the word

        Examples:
            >>> TableNaming.pluralize('inventory')
            'inventories'
            >>> TableNaming.pluralize('item')
            'items'
            >>> TableNaming.pluralize('class')
            'classes'
        """
        if word.endswith("y"):
            return word[:-1] + "ies"
        elif word.endswith(("s", "x", "z", "ch", "sh")):
            return word + "es"
        return word + "s"

    @staticmethod
    def to_class_name(table_name: str) -> str:
        """
        Convert table name to Python class name.
        Combines singularization and PascalCase conversion.

        Args:
            table_name: Database table name (usually plural, snake_case)

        Returns:
            Python class name (singular, PascalCase)

        Examples:
            >>> TableNaming.to_class_name('user_profiles')
            'UserProfile'
            >>> TableNaming.to_class_name('items')
            'Item'
        """
        return TableNaming.to_pascal_case(
            TableNaming.singularize(table_name),
        )

    @staticmethod
    def column_to_relationship_name(column_name: str) -> str:
        """
        Convert foreign key column name to relationship method name.
        Removes the _id suffix to get the relationship name.

        Args:
            column_name: Foreign key column name (e.g., 'owner_player_id')

        Returns:
            Relationship method name (e.g., 'owner_player')

        Examples:
            >>> TableNaming.column_to_relationship_name('inventory_id')
            'inventory'
            >>> TableNaming.column_to_relationship_name('owner_player_id')
            'owner_player'
        """
        if column_name.endswith("_id"):
            return column_name[:-3]
        return column_name

    @staticmethod
    def make_cache_key(name: str) -> str:
        """
        Generate a cache key from a relationship name.

        Args:
            name: Relationship name

        Returns:
            Cache key string

        Examples:
            >>> TableNaming.make_cache_key('inventory')
            '_inventory_cache'
        """
        return f"_{name}_cache"
