#!/usr/bin/env python3
"""
Seed script to create test players with varying ages in the gamedb database.
Creates 5 test players: under 13, under 18, under 30, under 75, and adult.
"""

import sys
import hashlib
from datetime import datetime

sys.path.append('../gen-py')

from db import DB
from common import is_ok, is_true
from game.ttypes import Player


def generate_security_token(password: str) -> str:
    """Generate a security token hash from a password."""
    return hashlib.sha256(password.encode()).hexdigest()


def drop_and_recreate_player_tables(db: DB, database_name: str):
    """Drop and recreate all player-related tables."""
    print(f"\nDropping and recreating player tables in '{database_name}'...")
    db.connect()
    cursor = db.connection.cursor()

    # Drop tables in reverse order of dependencies
    print("  - Dropping attribute_owners table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.attribute_owners;")

    print("  - Dropping attributes table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.attributes;")

    print("  - Dropping mobiles table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.mobiles;")

    print("  - Dropping players table...")
    cursor.execute(f"DROP TABLE IF EXISTS {database_name}.players;")

    db.connection.commit()

    # Recreate tables
    print("\n  - Creating players table...")
    for stmt in db.get_players_table_sql(database_name):
        cursor.execute(stmt)

    print("  - Creating mobiles table...")
    for stmt in db.get_mobiles_table_sql(database_name):
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


def create_test_players(db: DB, database_name: str) -> list[Player]:
    """
    Create 5 test players with varying ages.
    Returns list of created players.
    """
    current_year = datetime.now().year

    # Define test players with different age ranges
    test_players_data = [
        {
            'full_name': 'Emma Young',
            'what_we_call_you': 'Emma',
            'email': 'emma.young@test.com',
            'year_of_birth': current_year - 10,  # Under 13 (10 years old)
            'password': 'password123',
        },
        {
            'full_name': 'Oliver Teen',
            'what_we_call_you': 'Ollie',
            'email': 'oliver.teen@test.com',
            'year_of_birth': current_year - 15,  # Under 18 (15 years old)
            'password': 'password123',
        },
        {
            'full_name': 'Sophia Miller',
            'what_we_call_you': 'Sophie',
            'email': 'sophia.miller@test.com',
            'year_of_birth': current_year - 25,  # Under 30 (25 years old)
            'password': 'password123',
        },
        {
            'full_name': 'James Anderson',
            'what_we_call_you': 'Jim',
            'email': 'james.anderson@test.com',
            'year_of_birth': current_year - 45,  # Under 75 (45 years old)
            'password': 'password123',
        },
        {
            'full_name': 'Margaret Wilson',
            'what_we_call_you': 'Maggie',
            'email': 'margaret.wilson@test.com',
            'year_of_birth': current_year - 68,  # Under 75 (68 years old)
            'password': 'password123',
        },
    ]

    print(f"\nCreating {len(test_players_data)} test players...")
    created_players = []

    for i, player_data in enumerate(test_players_data, 1):
        # Create Player object (over_13 will be set automatically in create_player)
        player = Player(
            id=None,
            full_name=player_data['full_name'],
            what_we_call_you=player_data['what_we_call_you'],
            security_token=generate_security_token(player_data['password']),
            over_13=False,  # Will be automatically set based on year_of_birth
            year_of_birth=player_data['year_of_birth'],
            email=player_data['email'],
        )

        # Create the player
        results = db.create_player(database_name, player)

        if not is_ok(results):
            error_msg = results[0].message
            print(f"\n✗ Failed to create player '{player.full_name}'")
            print(f"  Error: {error_msg}")
            raise Exception(f"Failed to create player '{player.full_name}': {error_msg}")

        print(f"  [{i}/{len(test_players_data)}] ✓ Created: {player.full_name} (age={current_year - player.year_of_birth}, id={player.id})")
        created_players.append(player)

    print(f"\n  ✓ Successfully created {len(created_players)} players")
    return created_players


def validate_players(db: DB, database_name: str, players: list[Player]):
    """
    Validate that all players were created correctly and have associated mobiles.
    """
    print(f"\nValidating {len(players)} players...")
    current_year = datetime.now().year

    for i, original_player in enumerate(players, 1):
        # Load the player back
        load_result, loaded_player = db.load_player(database_name, original_player.id)

        if not is_true(load_result):
            error_msg = load_result.message
            print(f"\n✗ Failed to load player '{original_player.full_name}' (id={original_player.id})")
            print(f"  Error: {error_msg}")
            raise Exception(f"Failed to load player for validation: {error_msg}")

        # Validate basic fields
        if loaded_player.full_name != original_player.full_name:
            raise Exception(f"Player validation failed: full_name mismatch")

        if loaded_player.email != original_player.email:
            raise Exception(f"Player validation failed: email mismatch")

        # Validate over_13 was set correctly
        expected_over_13 = (current_year - loaded_player.year_of_birth) >= 13
        if loaded_player.over_13 != expected_over_13:
            raise Exception(
                f"Player validation failed: over_13 mismatch for {loaded_player.full_name}. "
                f"Expected {expected_over_13}, got {loaded_player.over_13}"
            )

        # Validate mobile was created
        if not hasattr(loaded_player, 'mobile') or loaded_player.mobile is None:
            raise Exception(
                f"Player validation failed: mobile not created for {loaded_player.full_name} (id={loaded_player.id})"
            )

        # Validate mobile has correct owner
        if not hasattr(loaded_player.mobile, 'owner') or loaded_player.mobile.owner is None:
            raise Exception(
                f"Player validation failed: mobile owner not set for {loaded_player.full_name}"
            )

        if not hasattr(loaded_player.mobile.owner, 'player_id') or loaded_player.mobile.owner.player_id != loaded_player.id:
            raise Exception(
                f"Player validation failed: mobile owner player_id mismatch for {loaded_player.full_name}"
            )

        age = current_year - loaded_player.year_of_birth
        print(
            f"  [{i}/{len(players)}] ✓ Validated: {loaded_player.full_name} "
            f"(age={age}, over_13={loaded_player.over_13}, mobile_id={loaded_player.mobile.id})"
        )

    print(f"\n  ✓ All {len(players)} players validated successfully")


def main():
    """Create test players in the gamedb database."""
    print("=" * 60)
    print("Player Seeding Script")
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

        # Drop and recreate player tables
        drop_and_recreate_player_tables(db, database_name)

        # Create test players
        players = create_test_players(db, database_name)

        # Validate players and their mobiles
        validate_players(db, database_name, players)

        print("\n" + "=" * 60)
        print("Seeding completed successfully!")
        print(f"Database: {database_name}")
        print(f"Total players: {len(players)}")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        sys.exit(1)
    finally:
        db.disconnect()


if __name__ == '__main__':
    main()
