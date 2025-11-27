#!/usr/bin/env python3
"""
Seed script to import items from item_db.py into the gamedb database.
Items are imported in dependency order (raw materials before refined materials).
"""

import sys
import random
sys.path.append('../gen-py')

from db import DB
from item_db import CONFIG
from common import is_ok, is_true
from game.ttypes import (
    Item,
    ItemType,
    AttributeType,
    ItemVector3,
)


def drop_and_recreate_item_tables(db: DB, database_name: str):
    """Drop and recreate all item-related tables."""
    print(f"\nDropping and recreating item tables in '{database_name}'...")
    db.connect()
    cursor = db.connection.cursor()

    # Drop tables in reverse order of dependencies
    print("  - Dropping attribute_owners table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.attribute_owners;")

    print("  - Dropping attributes table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.attributes;")

    print("  - Dropping item_blueprint_components table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.item_blueprint_components;")

    print("  - Dropping items table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.items;")

    print("  - Dropping item_blueprints table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.item_blueprints;")

    db.connection.commit()

    # Recreate tables
    print("\n  - Creating item_blueprints table...")
    for stmt in db.get_item_blueprints_table_sql(database_name):
        cursor.execute(stmt)

    print("  - Creating item_blueprint_components table...")
    for stmt in db.get_item_blueprint_components_table_sql(database_name):
        cursor.execute(stmt)

    print("  - Creating items table...")
    for stmt in db.get_items_table_sql(database_name):
        cursor.execute(stmt)

    print("  - Creating attributes table...")
    for stmt in db.get_attributes_table_sql(database_name):
        cursor.execute(stmt)

    print("  - Creating attribute_owners table...")
    for stmt in db.get_attribute_owners_table_sql(database_name):
        cursor.execute(stmt)

    db.connection.commit()
    cursor.close()
    print("  ✓ Tables recreated successfully\n")


def sort_items_by_dependency(items: list[Item]) -> list[Item]:
    """
    Sort items in dependency order: items without blueprints first,
    then items whose dependencies have all been saved.
    """
    # Separate items into those without and with blueprints
    items_without_blueprints = []
    items_with_blueprints = []

    for item in items:
        if item.blueprint is None:
            items_without_blueprints.append(item)
        else:
            items_with_blueprints.append(item)

    # Start with items that have no dependencies
    sorted_items = items_without_blueprints[:]
    saved_item_ids = {item.id for item in items_without_blueprints}

    # Iteratively add items whose dependencies are all saved
    remaining = items_with_blueprints[:]
    max_iterations = len(items_with_blueprints) + 1
    iterations = 0

    while remaining and iterations < max_iterations:
        iterations += 1
        newly_ready = []

        for item in remaining:
            # Check if all component item_ids are in saved_item_ids
            all_deps_satisfied = True
            if item.blueprint and item.blueprint.components:
                for component_item_id in item.blueprint.components.keys():
                    if component_item_id not in saved_item_ids:
                        all_deps_satisfied = False
                        break

            if all_deps_satisfied:
                newly_ready.append(item)
                saved_item_ids.add(item.id)

        if not newly_ready:
            # No progress made, we have circular dependencies or missing items
            if remaining:
                print(f"\n⚠ Warning: Could not resolve dependencies for {len(remaining)} items:")
                for item in remaining:
                    print(f"    - {item.internal_name} (id={item.id})")
                    if item.blueprint and item.blueprint.components:
                        missing = [cid for cid in item.blueprint.components.keys() if cid not in saved_item_ids]
                        print(f"      Missing dependencies: {missing}")
            break

        sorted_items.extend(newly_ready)
        remaining = [item for item in remaining if item not in newly_ready]

    # Add any remaining items at the end (circular dependencies)
    sorted_items.extend(remaining)

    return sorted_items


def deep_compare_item(original: Item, loaded: Item) -> tuple[bool, str]:
    """
    Deep comparison of two items. Returns (success, error_message).
    """
    # Compare basic fields
    if original.id != loaded.id:
        return False, f"ID mismatch: {original.id} != {loaded.id}"

    if original.internal_name != loaded.internal_name:
        return False, f"internal_name mismatch: {original.internal_name} != {loaded.internal_name}"

    if original.max_stack_size != loaded.max_stack_size:
        return False, f"max_stack_size mismatch: {original.max_stack_size} != {loaded.max_stack_size}"

    if original.item_type != loaded.item_type:
        return False, f"item_type mismatch: {original.item_type} != {loaded.item_type}"

    # Compare attributes
    if len(original.attributes) != len(loaded.attributes):
        return False, f"attributes count mismatch: {len(original.attributes)} != {len(loaded.attributes)}"

    for attr_type, orig_attr in original.attributes.items():
        if attr_type not in loaded.attributes:
            return False, f"attribute {attr_type} missing in loaded item"

        loaded_attr = loaded.attributes[attr_type]

        if orig_attr.internal_name != loaded_attr.internal_name:
            return False, f"attribute {attr_type} internal_name mismatch: {orig_attr.internal_name} != {loaded_attr.internal_name}"

        if orig_attr.visible != loaded_attr.visible:
            return False, f"attribute {attr_type} visible mismatch: {orig_attr.visible} != {loaded_attr.visible}"

        if orig_attr.attribute_type != loaded_attr.attribute_type:
            return False, f"attribute {attr_type} type mismatch: {orig_attr.attribute_type} != {loaded_attr.attribute_type}"

        # Compare values - extract primitive from AttributeValue union if needed
        from game.ttypes import AttributeValue

        orig_value = orig_attr.value
        if isinstance(orig_value, AttributeValue):
            # Extract primitive value from union
            if orig_value.bool_value is not None:
                orig_value = orig_value.bool_value
            elif orig_value.double_value is not None:
                orig_value = orig_value.double_value
            elif orig_value.vector3 is not None:
                orig_value = orig_value.vector3
            elif orig_value.asset_id is not None:
                orig_value = orig_value.asset_id

        loaded_value = loaded_attr.value

        if isinstance(orig_value, ItemVector3):
            if not isinstance(loaded_value, ItemVector3):
                return False, f"attribute {attr_type} value type mismatch: expected ItemVector3"
            if (orig_value.x != loaded_value.x or
                orig_value.y != loaded_value.y or
                orig_value.z != loaded_value.z):
                return False, f"attribute {attr_type} vector3 value mismatch"
        else:
            if orig_value != loaded_value:
                return False, f"attribute {attr_type} value mismatch: {orig_value} != {loaded_value}"

    # Compare blueprint
    if (original.blueprint is None) != (loaded.blueprint is None):
        return False, f"blueprint existence mismatch: original={original.blueprint is not None}, loaded={loaded.blueprint is not None}"

    if original.blueprint is not None:
        if original.blueprint.bake_time_ms != loaded.blueprint.bake_time_ms:
            return False, f"blueprint bake_time_ms mismatch: {original.blueprint.bake_time_ms} != {loaded.blueprint.bake_time_ms}"

        if len(original.blueprint.components) != len(loaded.blueprint.components):
            return False, f"blueprint components count mismatch: {len(original.blueprint.components)} != {len(loaded.blueprint.components)}"

        for component_id, orig_component in original.blueprint.components.items():
            if component_id not in loaded.blueprint.components:
                return False, f"blueprint component {component_id} missing in loaded item"

            loaded_component = loaded.blueprint.components[component_id]

            if orig_component.item_id != loaded_component.item_id:
                return False, f"blueprint component {component_id} item_id mismatch: {orig_component.item_id} != {loaded_component.item_id}"

            if orig_component.ratio != loaded_component.ratio:
                return False, f"blueprint component {component_id} ratio mismatch: {orig_component.ratio} != {loaded_component.ratio}"

    return True, ""


def seed_items(db: DB, database_name: str, items: list[Item], validation_rate: float = 0.2):
    """
    Seed items into the database in dependency order.
    Validates random sample based on validation_rate.
    """
    print(f"\nSeeding {len(items)} items into '{database_name}'...")

    # Sort items by dependency
    sorted_items = sort_items_by_dependency(items)

    print(f"\n  Items sorted by dependency:")
    print(f"    - Items without blueprints: {sum(1 for item in sorted_items if item.blueprint is None)}")
    print(f"    - Items with blueprints: {sum(1 for item in sorted_items if item.blueprint is not None)}")

    # Save each item
    saved_count = 0
    validated_count = 0

    print(f"\n  Saving items...")
    for i, item in enumerate(sorted_items, 1):
        # Create the item (use create_item instead of save_item since these have IDs but don't exist yet)
        save_results = db.create_item(database_name, item)

        if not is_ok(save_results):
            error_msg = save_results[0].message
            print(f"\n✗ Failed to save item '{item.internal_name}' (id={item.id})")
            print(f"  Error: {error_msg}")
            raise Exception(f"Failed to save item '{item.internal_name}': {error_msg}")

        saved_count += 1

        # Determine if we should validate this item
        should_validate = random.random() < validation_rate

        if should_validate:
            # Load the item back
            load_result, loaded_item = db.load_item(database_name, item.id)

            if not is_true(load_result):
                error_msg = load_result.message
                print(f"\n✗ Failed to load item '{item.internal_name}' (id={item.id}) for validation")
                print(f"  Error: {error_msg}")
                raise Exception(f"Failed to load item '{item.internal_name}' for validation: {error_msg}")

            # Deep compare
            success, error_msg = deep_compare_item(item, loaded_item)

            if not success:
                print(f"\n✗ Validation failed for item '{item.internal_name}' (id={item.id})")
                print(f"  Error: {error_msg}")
                raise Exception(f"Validation failed for item '{item.internal_name}': {error_msg}")

            validated_count += 1
            print(f"    [{i}/{len(sorted_items)}] ✓ Saved and validated: {item.internal_name} (id={item.id})")
        else:
            print(f"    [{i}/{len(sorted_items)}] ✓ Saved: {item.internal_name} (id={item.id})")

    print(f"\n  ✓ Successfully saved {saved_count} items")
    print(f"  ✓ Validated {validated_count} items ({validation_rate*100:.0f}% sample rate)")


def main():
    """Import items from item_db into the gamedb database."""
    print("=" * 60)
    print("Item Seeding Script")
    print("=" * 60)

    # Database configuration
    database_name = "gamedb"

    # Initialize database connection
    db = DB(
        host="localhost",
        user="admin",
        password="minda",
    )

    try:
        print(f"\n1. Connecting to MySQL server...")
        db.connect()
        print(f"   ✓ Connected")

        # Drop and recreate item tables
        drop_and_recreate_item_tables(db, database_name)

        # Get items from item_db
        items = CONFIG.items
        print(f"Loaded {len(items)} items from item_db.py")

        # Seed items with 20% validation rate
        seed_items(db, database_name, items, validation_rate=0.2)

        print("\n" + "=" * 60)
        print("Seeding completed successfully!")
        print(f"Database: {database_name}")
        print(f"Total items: {len(items)}")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        sys.exit(1)
    finally:
        db.disconnect()


if __name__ == '__main__':
    main()
