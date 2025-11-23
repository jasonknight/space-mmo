import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../gen-py"))

from db import DB
from game.ttypes import (
    Player,
    Mobile,
    MobileType,
    Owner,
    Attribute,
    AttributeType,
    GameError,
)
from common import is_ok, is_true


def setup_database(db: DB, database_name: str):
    """Create all necessary tables for testing."""
    db.connect()
    cursor = db.connection.cursor()

    # Create database
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
    cursor.execute(f"CREATE DATABASE {database_name};")

    # Create all tables
    for stmt in db.get_item_blueprints_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_item_blueprint_components_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_items_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_attributes_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_attribute_owners_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_inventories_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_inventory_entries_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_inventory_owners_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_mobiles_table_sql(database_name):
        cursor.execute(stmt)

    for stmt in db.get_players_table_sql(database_name):
        cursor.execute(stmt)

    db.connection.commit()
    cursor.close()


def teardown_database(db: DB, database_name: str):
    """Delete the test database."""
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
    db.connection.commit()
    cursor.close()
    db.disconnect()


def test_player(db: DB, database_name: str):
    """Test Player save and load."""
    print("Testing Player...")

    # Create player
    player = Player(
        id=None,
        full_name="John Doe",
        what_we_call_you="Johnny",
        security_token="abc123def456",
        over_13=True,
        year_of_birth=1990,
        email="john.doe@example.com",
    )

    # Save player
    save_results = db.save_player(database_name, player)
    assert is_ok(save_results), f"Failed to save Player: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Verify that a mobile was created for this player
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute(
        f"SELECT id, mobile_type, owner_player_id FROM {database_name}.mobiles WHERE owner_player_id = {player.id}",
    )
    mobile_row = cursor.fetchone()
    cursor.close()
    assert mobile_row is not None, "Mobile should have been created for player"
    mobile_id = mobile_row[0]
    mobile_type = mobile_row[1]
    owner_player_id = mobile_row[2]
    assert mobile_type == "PLAYER", f"Mobile type should be PLAYER, got {mobile_type}"
    assert owner_player_id == player.id, (
        f"Mobile owner_player_id should be {player.id}, got {owner_player_id}"
    )
    print(
        f"  ✓ Verified mobile (id={mobile_id}) created for player with correct type and owner"
    )

    # Load player
    load_result, loaded_player = db.load_player(database_name, player.id)
    assert is_true(load_result), f"Failed to load Player: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_player.id == player.id, "ID mismatch"
    assert loaded_player.full_name == player.full_name, "full_name mismatch"
    assert loaded_player.what_we_call_you == player.what_we_call_you, (
        "what_we_call_you mismatch"
    )
    assert loaded_player.security_token == player.security_token, (
        "security_token mismatch"
    )
    assert loaded_player.over_13 == player.over_13, "over_13 mismatch"
    assert loaded_player.year_of_birth == player.year_of_birth, "year_of_birth mismatch"

    # Verify mobile was loaded
    assert hasattr(loaded_player, "mobile") and loaded_player.mobile is not None, (
        "Player should have a mobile loaded"
    )
    assert loaded_player.mobile.what_we_call_you == player.what_we_call_you, (
        f"Mobile what_we_call_you should match player: expected '{player.what_we_call_you}', "
        f"got '{loaded_player.mobile.what_we_call_you}'"
    )
    print(
        f"  ✓ Verified mobile loaded with what_we_call_you='{loaded_player.mobile.what_we_call_you}'"
    )

    # Test update
    print("  Testing update...")
    loaded_player.full_name = "Jane Smith"
    loaded_player.what_we_call_you = "Janie"
    loaded_player.year_of_birth = 1995

    update_results = db.save_player(database_name, loaded_player)
    assert is_ok(update_results), (
        f"Failed to update Player: {update_results[0].message}"
    )
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_player = db.load_player(database_name, loaded_player.id)
    assert is_true(load_result2), (
        f"Failed to load updated Player: {load_result2.message}"
    )
    assert updated_player.full_name == "Jane Smith", "Updated full_name mismatch"
    assert updated_player.what_we_call_you == "Janie", (
        "Updated what_we_call_you mismatch"
    )
    assert updated_player.year_of_birth == 1995, "Updated year_of_birth mismatch"
    print("  ✓ Update verified")

    # Verify mobile still exists after update
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute(
        f"SELECT id FROM {database_name}.mobiles WHERE owner_player_id = {loaded_player.id}",
    )
    mobile_row_after_update = cursor.fetchone()
    cursor.close()
    assert mobile_row_after_update is not None, (
        "Mobile should still exist after player update"
    )
    print("  ✓ Verified mobile still exists after player update")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = db.destroy_player(database_name, loaded_player.id)
    assert is_ok(destroy_results), (
        f"Failed to destroy Player: {destroy_results[0].message}"
    )
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_player = db.load_player(database_name, loaded_player.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_player is None, "Destroyed player should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, (
        f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    )
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    # Verify mobile was also deleted
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute(
        f"SELECT id FROM {database_name}.mobiles WHERE id = {mobile_id}",
    )
    deleted_mobile_row = cursor.fetchone()
    cursor.close()
    assert deleted_mobile_row is None, (
        "Mobile should have been deleted when player was destroyed"
    )
    print("  ✓ Verified mobile was deleted when player was destroyed")

    print("  ✓ All assertions passed for Player\n")


def test_list_player(db: DB, database_name: str):
    """Test Player list functionality with pagination and search."""
    print("Testing Player list functionality...")

    import random
    import string

    # Generate random string helper
    def random_string(length=10):
        return "".join(random.choices(string.ascii_letters, k=length))

    # Create 100 players with random data
    print("  Creating 100 players...")
    created_players = []
    search_test_names = []

    for i in range(100):
        full_name = f"Player_{random_string(8)}"
        nickname = f"Nick_{random_string(6)}"

        # Save some names for search testing
        if i < 5:
            search_test_names.append((full_name, nickname))

        player = Player(
            id=None,
            full_name=full_name,
            what_we_call_you=nickname,
            security_token=random_string(20),
            over_13=random.choice([True, False]),
            year_of_birth=random.randint(1950, 2010),
            email=f"{nickname.lower()}@test.com",
        )

        save_results = db.save_player(database_name, player)
        assert is_ok(save_results), (
            f"Failed to save player {i}: {save_results[0].message}"
        )
        created_players.append(player)

    print(f"  ✓ Created {len(created_players)} players")

    # Test pagination - iterate through all pages with 10 results per page
    print("  Testing pagination (10 results per page)...")
    all_paginated_players = []
    page = 0
    results_per_page = 10

    while True:
        result, players, total_count = db.list_player(
            database_name,
            page,
            results_per_page,
        )
        assert is_true(result), f"Failed to list players page {page}: {result.message}"

        if not players:
            break

        all_paginated_players.extend(players)
        print(
            f"    Page {page}: retrieved {len(players)} players (total: {total_count})"
        )

        # Check if this is the last page
        if len(all_paginated_players) >= total_count:
            break

        page += 1

    assert len(all_paginated_players) == 100, (
        f"Expected 100 players, got {len(all_paginated_players)}"
    )
    print(
        f"  ✓ Pagination test passed: retrieved all {len(all_paginated_players)} players across {page + 1} pages"
    )

    # Test search on full_name
    print("  Testing search on full_name...")
    search_full_name = search_test_names[0][0]
    result, players, total_count = db.list_player(
        database_name,
        0,
        100,
        search_string=search_full_name,
    )
    assert is_true(result), f"Failed to search players: {result.message}"
    assert len(players) >= 1, (
        f"Expected at least 1 player matching '{search_full_name}', got {len(players)}"
    )
    assert any(p.full_name == search_full_name for p in players), (
        f"Expected to find player with full_name '{search_full_name}'"
    )
    print(
        f"  ✓ Search on full_name '{search_full_name}' found {len(players)} player(s)"
    )

    # Test search on what_we_call_you
    print("  Testing search on what_we_call_you...")
    search_nickname = search_test_names[1][1]
    result, players, total_count = db.list_player(
        database_name,
        0,
        100,
        search_string=search_nickname,
    )
    assert is_true(result), f"Failed to search players: {result.message}"
    assert len(players) >= 1, (
        f"Expected at least 1 player matching '{search_nickname}', got {len(players)}"
    )
    assert any(p.what_we_call_you == search_nickname for p in players), (
        f"Expected to find player with what_we_call_you '{search_nickname}'"
    )
    print(
        f"  ✓ Search on what_we_call_you '{search_nickname}' found {len(players)} player(s)"
    )

    # Test partial search
    print("  Testing partial search...")
    partial_search = "Player_"
    result, players, total_count = db.list_player(
        database_name,
        0,
        100,
        search_string=partial_search,
    )
    assert is_true(result), f"Failed to search players: {result.message}"
    assert len(players) == 100, (
        f"Expected 100 players matching '{partial_search}', got {len(players)}"
    )
    print(f"  ✓ Partial search '{partial_search}' found {len(players)} player(s)")

    print("  ✓ All list tests passed for Player\n")


def test_player_with_character_attributes(db: DB, database_name: str):
    """Test Player with mobile character attributes."""
    print("Testing Player with character attributes...")

    import random

    # Create mobile with character attributes
    mobile_owner = Owner()
    mobile_owner.player_id = None  # Will be set after player creation

    # Generate character attributes with random values in range 0.001 to 0.05
    mobile_attributes = {}
    char_attrs = [
        (AttributeType.STRENGTH, "strength"),
        (AttributeType.LUCK, "luck"),
        (AttributeType.CONSTITUTION, "constitution"),
        (AttributeType.DEXTERITY, "dexterity"),
        (AttributeType.ARCANA, "arcana"),
        (AttributeType.OPERATIONS, "operations"),
    ]

    for attr_type, internal_name in char_attrs:
        value = random.uniform(0.001, 0.05)
        mobile_attributes[attr_type] = Attribute(
            id=None,
            internal_name=internal_name,
            visible=True,
            value=value,
            attribute_type=attr_type,
            owner=0,
        )

    mobile = Mobile(
        id=None,
        mobile_type=MobileType.PLAYER,
        attributes=mobile_attributes,
        owner=mobile_owner,
        what_we_call_you="TestChar",
    )

    # Create player
    player = Player(
        id=None,
        full_name="Test Character",
        what_we_call_you="TestChar",
        security_token="test_token_123",
        over_13=True,
        year_of_birth=1995,
        email="test@example.com",
        mobile=mobile,
    )

    # Save player
    save_results = db.save_player(database_name, player)
    assert is_ok(save_results), f"Failed to save Player: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load player
    load_result, loaded_player = db.load_player(database_name, player.id)
    assert is_true(load_result), f"Failed to load Player: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Verify mobile exists and has character attributes
    assert hasattr(loaded_player, "mobile") and loaded_player.mobile is not None, (
        "Mobile should exist"
    )

    # Verify all character attributes exist and have correct values
    for attr_type, internal_name in char_attrs:
        assert attr_type in loaded_player.mobile.attributes, (
            f"Missing character attribute: {internal_name}"
        )
        original_value = mobile_attributes[attr_type].value
        loaded_value = loaded_player.mobile.attributes[attr_type].value
        assert abs(loaded_value - original_value) < 0.00001, (
            f"Attribute {internal_name} value mismatch: expected {original_value}, got {loaded_value}"
        )

    print(f"  ✓ Verified {len(char_attrs)} character attributes")

    # Verify mobile name matches player name
    assert loaded_player.mobile.what_we_call_you == player.what_we_call_you, (
        f"Mobile name should match player name: expected '{player.what_we_call_you}', "
        f"got '{loaded_player.mobile.what_we_call_you}'"
    )
    print(
        f"  ✓ Mobile name matches player name: '{loaded_player.mobile.what_we_call_you}'"
    )

    print("  ✓ All assertions passed for Player with character attributes\n")


def main():
    """Run all tests."""
    # Database configuration
    host = "localhost"
    user = "admin"
    password = "minda"
    database_name = "test_player_db"

    print("=" * 60)
    print("Player Test Suite")
    print("=" * 60)
    print()

    # Initialize database connection
    db = DB(host, user, password)

    try:
        # Setup database and tables
        print("Setting up test database...")
        setup_database(db, database_name)
        print("✓ Database setup complete\n")

        # Run tests
        test_player(db, database_name)
        test_list_player(db, database_name)
        test_player_with_character_attributes(db, database_name)

        print("=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
    finally:
        # Teardown database
        print("\nCleaning up test database...")
        teardown_database(db, database_name)
        print("✓ Cleanup complete")


if __name__ == "__main__":
    main()
