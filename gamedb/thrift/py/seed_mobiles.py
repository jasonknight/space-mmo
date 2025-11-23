#!/usr/bin/env python3
"""
Seed script to create test NPC mobiles with Fantasy/Sci-fi names.
Creates 20 NPC mobiles with randomized names and character attributes.
"""

import sys
import random

sys.path.append("../gen-py")

from db import DB
from common import is_ok, is_true
from game.ttypes import (
    Mobile,
    MobileType,
    Owner,
    Attribute,
    AttributeType,
    AttributeValue,
)


def generate_character_attributes(mobile_id: int) -> dict:
    """
    Generate random character attributes for a mobile.
    Values are in range 0.001 to 0.05 for starting characters.

    Args:
        mobile_id: The mobile ID for the attribute owner

    Returns:
        Dictionary mapping AttributeType to Attribute
    """
    attributes = {}

    # Define the character attribute types
    character_attr_types = [
        (AttributeType.STRENGTH, "strength"),
        (AttributeType.LUCK, "luck"),
        (AttributeType.CONSTITUTION, "constitution"),
        (AttributeType.DEXTERITY, "dexterity"),
        (AttributeType.ARCANA, "arcana"),
        (AttributeType.OPERATIONS, "operations"),
    ]

    for attr_type, internal_name in character_attr_types:
        # Generate random value between 0.001 and 0.05
        value = random.uniform(0.001, 0.05)

        # Create owner pointing to mobile
        owner = Owner()
        owner.mobile_id = mobile_id

        attributes[attr_type] = Attribute(
            id=None,
            internal_name=internal_name,
            visible=True,
            value=AttributeValue(double_value=value),
            attribute_type=attr_type,
            owner=owner,
        )

    return attributes


def get_fantasy_names():
    """Return a list of Fantasy-style NPC names."""
    return [
        "Thorin Ironforge",
        "Elara Moonwhisper",
        "Garrick Stormhammer",
        "Lyanna Nightshade",
        "Zephyr Windrunner",
        "Morgana Shadowbane",
        "Aldric Dragonheart",
        "Seraphina Starfire",
        "Brynn Oakenshield",
        "Thalia Frostblade",
        "Kellan Brightsword",
        "Aria Silvermoon",
        "Ragnar Bloodaxe",
        "Celeste Dawnbringer",
        "Dorian Nightfall",
    ]


def get_scifi_names():
    """Return a list of Sci-fi-style NPC names."""
    return [
        "Xander-7",
        "Nova Starlight",
        "Kael-9",
        "Zenith Prime",
        "Orion Vex",
        "Cipher-12",
        "Astra Volt",
        "Nexus-5",
        "Quantum Reyes",
        "Echo-88",
        "Vega Storm",
        "Helix-3",
        "Photon Cross",
        "Zeta Kane",
        "Matrix-17",
    ]


def create_test_mobiles(db: DB, database_name: str) -> list[Mobile]:
    """
    Create 20 test NPC mobiles with Fantasy and Sci-fi names.
    Returns list of created mobiles.
    """
    # Mix fantasy and sci-fi names
    all_names = get_fantasy_names() + get_scifi_names()
    random.shuffle(all_names)

    # Take first 20 (or all if less than 20)
    test_names = all_names[:20]

    print(f"\nCreating {len(test_names)} test NPC mobiles...")
    created_mobiles = []

    for i, name in enumerate(test_names, 1):
        # Create mobile with NPC type
        mobile = Mobile(
            id=None,
            mobile_type=MobileType.NPC,
            attributes={},
            owner=None,
            what_we_call_you=name,
        )

        # Create the mobile first to get its ID
        results = db.create_mobile(database_name, mobile)

        if not is_ok(results):
            error_msg = results[0].message
            print(f"\n✗ Failed to create NPC mobile '{name}'")
            print(f"  Error: {error_msg}")
            raise Exception(f"Failed to create mobile '{name}': {error_msg}")

        # Now generate attributes with the mobile ID
        mobile.attributes = generate_character_attributes(mobile.id)

        # Update the mobile with attributes
        update_results = db.update_mobile(database_name, mobile)

        if not is_ok(update_results):
            error_msg = update_results[0].message
            print(f"\n✗ Failed to update NPC mobile '{name}' with attributes")
            print(f"  Error: {error_msg}")
            raise Exception(
                f"Failed to update mobile '{name}' with attributes: {error_msg}"
            )

        print(
            f"  [{i}/{len(test_names)}] ✓ Created: {name} (id={mobile.id}, attrs={len(mobile.attributes)})"
        )
        created_mobiles.append(mobile)

    print(f"\n  ✓ Successfully created {len(created_mobiles)} NPC mobiles")
    return created_mobiles


def validate_mobiles(db: DB, database_name: str, mobiles: list[Mobile]):
    """
    Validate that all mobiles were created correctly.
    """
    print(f"\nValidating {len(mobiles)} NPC mobiles...")

    for i, original_mobile in enumerate(mobiles, 1):
        # Load the mobile back
        load_result, loaded_mobile = db.load_mobile(
            database_name,
            original_mobile.id,
        )

        if not is_true(load_result):
            error_msg = load_result.message
            print(
                f"\n✗ Failed to load mobile '{original_mobile.what_we_call_you}' (id={original_mobile.id})"
            )
            print(f"  Error: {error_msg}")
            raise Exception(f"Failed to load mobile for validation: {error_msg}")

        # Validate basic fields
        if loaded_mobile.what_we_call_you != original_mobile.what_we_call_you:
            raise Exception(f"Mobile validation failed: name mismatch")

        # Validate mobile_type is NPC
        if loaded_mobile.mobile_type != MobileType.NPC:
            raise Exception(
                f"Mobile validation failed: mobile_type should be NPC, got {loaded_mobile.mobile_type}"
            )

        # Validate mobile has character attributes
        required_attrs = [
            AttributeType.STRENGTH,
            AttributeType.LUCK,
            AttributeType.CONSTITUTION,
            AttributeType.DEXTERITY,
            AttributeType.ARCANA,
            AttributeType.OPERATIONS,
        ]

        for attr_type in required_attrs:
            if attr_type not in loaded_mobile.attributes:
                raise Exception(
                    f"Mobile validation failed: missing {attr_type} attribute for {loaded_mobile.what_we_call_you}"
                )

            # Verify attribute value is in expected range (0.001 to 0.05)
            attr = loaded_mobile.attributes[attr_type]
            if attr.value is None:
                raise Exception(
                    f"Mobile validation failed: {attr_type} has no value for {loaded_mobile.what_we_call_you}"
                )

            # Get the value - it might be stored as double_value field or direct value
            if (
                hasattr(attr.value, "double_value")
                and attr.value.double_value is not None
            ):
                attr_value = attr.value.double_value
            elif isinstance(attr.value, (int, float)):
                attr_value = float(attr.value)
            else:
                raise Exception(
                    f"Mobile validation failed: {attr_type} has unexpected value type for {loaded_mobile.what_we_call_you}"
                )
            if attr_value < 0.001 or attr_value > 0.05:
                raise Exception(
                    f"Mobile validation failed: {attr_type} value {attr_value} out of range for {loaded_mobile.what_we_call_you}"
                )

        print(
            f"  [{i}/{len(mobiles)}] ✓ Validated: {loaded_mobile.what_we_call_you} "
            f"(id={loaded_mobile.id}, type=NPC, attrs={len(loaded_mobile.attributes)})"
        )

    print(f"\n  ✓ All {len(mobiles)} NPC mobiles validated successfully")


def main():
    """Create test NPC mobiles in the gamedb database."""
    print("=" * 60)
    print("NPC Mobile Seeding Script")
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

        # Note: We don't drop/recreate tables here since mobiles share
        # tables with players. The tables should already exist.

        # Create test mobiles
        mobiles = create_test_mobiles(db, database_name)

        # Validate mobiles
        validate_mobiles(db, database_name, mobiles)

        print("\n" + "=" * 60)
        print("Seeding completed successfully!")
        print(f"Database: {database_name}")
        print(f"Total NPC mobiles: {len(mobiles)}")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        sys.exit(1)
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
