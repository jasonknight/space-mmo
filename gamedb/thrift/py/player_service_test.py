#!/usr/bin/env python3
"""Tests for PlayerService with cache validation."""

import sys
sys.path.append('../gen-py')

from db import DB
from player_service import PlayerServiceHandler, LRUCache
from game.ttypes import (
    PlayerRequest,
    PlayerResponse,
    PlayerRequestData,
    PlayerResponseData,
    LoadPlayerRequestData,
    CreatePlayerRequestData,
    SavePlayerRequestData,
    DeletePlayerRequestData,
    Player,
    StatusType,
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

    # Create attributes table (required by mobiles)
    for stmt in db.get_attributes_table_sql(database_name):
        cursor.execute(stmt)

    # Create attribute_owners table (required by mobiles)
    for stmt in db.get_attribute_owners_table_sql(database_name):
        cursor.execute(stmt)

    # Create mobiles table (required by players)
    for stmt in db.get_mobiles_table_sql(database_name):
        cursor.execute(stmt)

    # Create players table
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


def test_create_player(service: PlayerServiceHandler, db: DB, database_name: str):
    """Test creating a new player via service."""
    print("Testing PlayerService.create()...")

    # Create player
    player = Player(
        id=None,
        full_name="John Doe",
        what_we_call_you="JohnD",
        security_token="hashed_password_123",
        over_13=True,
        year_of_birth=1990,
    )

    request = PlayerRequest(
        data=PlayerRequestData(
            create_player=CreatePlayerRequestData(
                player=player,
            ),
        ),
    )

    response = service.create(request)
    assert is_ok(response.results), f"Create failed: {response.results[0].message}"
    assert response.response_data is not None, "Response data should not be None"
    assert response.response_data.create_player is not None, "create_player data missing"

    created_player = response.response_data.create_player.player
    assert created_player.id is not None, "Created player should have an ID"
    print(f"  ✓ Created player with ID: {created_player.id}")

    # Verify it was saved to DB
    load_result, db_player = db.load_player(database_name, created_player.id)
    assert is_true(load_result), "Failed to load player from DB"
    assert db_player.full_name == "John Doe", "full_name mismatch"
    assert db_player.what_we_call_you == "JohnD", "what_we_call_you mismatch"
    assert db_player.year_of_birth == 1990, "year_of_birth mismatch"
    print("  ✓ Verified player in database")

    # Verify it's in cache
    cached_player = service.cache.get(created_player.id)
    assert cached_player is not None, "Player should be in cache"
    assert cached_player.id == created_player.id, "Cached player ID mismatch"
    print("  ✓ Verified player in cache")

    # Verify that a mobile was created for this player
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute(
        f"SELECT id, mobile_type, owner_player_id FROM {database_name}.mobiles WHERE owner_player_id = {created_player.id}",
    )
    mobile_row = cursor.fetchone()
    cursor.close()
    assert mobile_row is not None, "Mobile should have been created for player"
    mobile_id = mobile_row[0]
    mobile_type = mobile_row[1]
    owner_player_id = mobile_row[2]
    assert mobile_type == "PLAYER", f"Mobile type should be PLAYER, got {mobile_type}"
    assert owner_player_id == created_player.id, f"Mobile owner_player_id should be {created_player.id}, got {owner_player_id}"
    print(f"  ✓ Verified mobile (id={mobile_id}) created for player")

    print("  ✓ All create tests passed\n")
    return created_player


def test_load_player(service: PlayerServiceHandler, db: DB, database_name: str, player_id: int):
    """Test loading a player via service (cache miss and cache hit)."""
    print("Testing PlayerService.load()...")

    # Clear cache to test cache miss
    service.cache.clear()
    print("  Cache cleared for testing cache miss")

    # First load - cache miss
    request = PlayerRequest(
        data=PlayerRequestData(
            load_player=LoadPlayerRequestData(
                player_id=player_id,
            ),
        ),
    )

    response = service.load(request)
    assert is_ok(response.results), f"Load failed: {response.results[0].message}"
    assert response.response_data is not None, "Response data should not be None"
    assert response.response_data.load_player is not None, "load_player data missing"

    loaded_player = response.response_data.load_player.player
    assert loaded_player.id == player_id, "Loaded player ID mismatch"
    print(f"  ✓ Loaded player (cache miss): {response.results[0].message}")

    # Verify it's now in cache
    cached_player = service.cache.get(player_id)
    assert cached_player is not None, "Player should be in cache after load"
    print("  ✓ Player cached after load")

    # Second load - cache hit
    response2 = service.load(request)
    assert is_ok(response2.results), f"Second load failed: {response2.results[0].message}"
    assert "cache" in response2.results[0].message, "Second load should mention cache"
    print(f"  ✓ Loaded player (cache hit): {response2.results[0].message}")

    # Test loading non-existent player
    request_bad = PlayerRequest(
        data=PlayerRequestData(
            load_player=LoadPlayerRequestData(
                player_id=99999,
            ),
        ),
    )

    response_bad = service.load(request_bad)
    assert not is_ok(response_bad.results), "Loading non-existent player should fail"
    assert response_bad.response_data is None, "Response data should be None for failure"
    print("  ✓ Non-existent player load properly failed")

    print("  ✓ All load tests passed\n")


def test_save_player(service: PlayerServiceHandler, db: DB, database_name: str, player_id: int):
    """Test saving/updating a player via service."""
    print("Testing PlayerService.save()...")

    # Load the player
    load_result, player = db.load_player(database_name, player_id)
    assert is_true(load_result), "Failed to load player from DB"

    # Modify it
    player.full_name = "John Doe Updated"
    player.security_token = "new_hashed_password_456"

    request = PlayerRequest(
        data=PlayerRequestData(
            save_player=SavePlayerRequestData(
                player=player,
            ),
        ),
    )

    response = service.save(request)
    assert is_ok(response.results), f"Save failed: {response.results[0].message}"
    print(f"  ✓ Saved player: {response.results[0].message}")

    # Verify changes in DB
    load_result2, updated_player = db.load_player(database_name, player_id)
    assert is_true(load_result2), "Failed to load updated player from DB"
    assert updated_player.full_name == "John Doe Updated", "full_name not updated in DB"
    assert updated_player.security_token == "new_hashed_password_456", "security_token not updated in DB"
    print("  ✓ Verified updates in database")

    # Verify cache was updated
    cached_player = service.cache.get(player_id)
    assert cached_player is not None, "Player should be in cache"
    assert cached_player.full_name == "John Doe Updated", "full_name not updated in cache"
    assert cached_player.security_token == "new_hashed_password_456", "security_token not updated in cache"
    print("  ✓ Verified cache was updated")

    print("  ✓ All save tests passed\n")


def test_delete_player(service: PlayerServiceHandler, db: DB, database_name: str):
    """Test deleting a player via service."""
    print("Testing PlayerService.delete()...")

    # Create a player to delete
    player = Player(
        id=None,
        full_name="Jane Smith",
        what_we_call_you="JaneS",
        security_token="temp_token",
        over_13=True,
        year_of_birth=1995,
    )

    # Save to DB
    save_results = db.save_player(database_name, player)
    assert is_ok(save_results), "Failed to save test player"
    print(f"  ✓ Created test player with ID: {player.id}")

    # Get the mobile ID for verification later
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute(
        f"SELECT id FROM {database_name}.mobiles WHERE owner_player_id = {player.id}",
    )
    mobile_row = cursor.fetchone()
    cursor.close()
    assert mobile_row is not None, "Mobile should exist for player"
    mobile_id = mobile_row[0]
    print(f"  ✓ Found mobile (id={mobile_id}) for player")

    # Add to cache
    service.cache.put(player.id, player)
    assert service.cache.get(player.id) is not None, "Player should be in cache"

    # Delete the player
    request = PlayerRequest(
        data=PlayerRequestData(
            delete_player=DeletePlayerRequestData(
                player_id=player.id,
            ),
        ),
    )

    response = service.delete(request)
    assert is_ok(response.results), f"Delete failed: {response.results[0].message}"
    assert response.response_data is not None, "Response data should not be None"
    assert response.response_data.delete_player is not None, "delete_player data missing"
    assert response.response_data.delete_player.player_id == player.id, "Deleted player ID mismatch"
    print(f"  ✓ Deleted player: {response.results[0].message}")

    # Verify it was deleted from DB
    load_result, db_player = db.load_player(database_name, player.id)
    assert not is_true(load_result), "Player should not exist in DB"
    assert db_player is None, "Player should be None"
    print("  ✓ Verified player removed from database")

    # Verify it was removed from cache
    cached_player = service.cache.get(player.id)
    assert cached_player is None, "Player should not be in cache"
    print("  ✓ Verified player removed from cache")

    # Verify mobile was also deleted
    db.connect()
    cursor = db.connection.cursor()
    cursor.execute(
        f"SELECT id FROM {database_name}.mobiles WHERE id = {mobile_id}",
    )
    deleted_mobile_row = cursor.fetchone()
    cursor.close()
    assert deleted_mobile_row is None, "Mobile should have been deleted when player was destroyed"
    print("  ✓ Verified mobile was deleted when player was destroyed")

    # Test deleting non-existent player
    request_bad = PlayerRequest(
        data=PlayerRequestData(
            delete_player=DeletePlayerRequestData(
                player_id=99999,
            ),
        ),
    )

    response_bad = service.delete(request_bad)
    assert not is_ok(response_bad.results), "Deleting non-existent player should fail"
    assert response_bad.results[0].error_code == GameError.DB_RECORD_NOT_FOUND, "Should return DB_RECORD_NOT_FOUND"
    print("  ✓ Non-existent player delete properly failed")

    print("  ✓ All delete tests passed\n")


def test_cache_eviction(service: PlayerServiceHandler, db: DB, database_name: str):
    """Test that LRU cache eviction works properly."""
    print("Testing cache eviction...")

    # Create a service with small cache
    small_cache_service = PlayerServiceHandler(db, database_name, cache_size=3)

    # Create 4 players
    players = []
    for i in range(4):
        player = Player(
            id=None,
            full_name=f"Test Player {i}",
            what_we_call_you=f"TestP{i}",
            security_token=f"token_{i}",
            over_13=True,
            year_of_birth=2000 + i,
        )
        save_results = db.save_player(database_name, player)
        assert is_ok(save_results), f"Failed to create player {i}"
        players.append(player)
        print(f"  Created player {i} (ID: {player.id})")

    # Load first 3 into cache
    for i in range(3):
        request = PlayerRequest(
            data=PlayerRequestData(
                load_player=LoadPlayerRequestData(
                    player_id=players[i].id,
                ),
            ),
        )
        response = small_cache_service.load(request)
        assert is_ok(response.results), f"Failed to load player {i}"

    assert small_cache_service.cache.size() == 3, f"Cache should have 3 items, got {small_cache_service.cache.size()}"
    print("  ✓ Loaded 3 players into cache")

    # Access player 0 to make it recently used
    small_cache_service.cache.get(players[0].id)

    # Load player 3 - should evict player 1 (least recently used)
    request = PlayerRequest(
        data=PlayerRequestData(
            load_player=LoadPlayerRequestData(
                player_id=players[3].id,
            ),
        ),
    )
    response = small_cache_service.load(request)
    assert is_ok(response.results), "Failed to load player 3"

    assert small_cache_service.cache.size() == 3, f"Cache should still have 3 items, got {small_cache_service.cache.size()}"

    # Verify player 1 was evicted
    assert small_cache_service.cache.get(players[1].id) is None, "Player 1 should have been evicted"

    # Verify others are still in cache
    assert small_cache_service.cache.get(players[0].id) is not None, "Player 0 should still be in cache"
    assert small_cache_service.cache.get(players[2].id) is not None, "Player 2 should still be in cache"
    assert small_cache_service.cache.get(players[3].id) is not None, "Player 3 should be in cache"
    print("  ✓ LRU eviction working correctly")

    print("  ✓ All cache eviction tests passed\n")


def test_invalid_requests(service: PlayerServiceHandler):
    """Test that invalid requests are handled properly."""
    print("Testing invalid request handling...")

    # Test load without data
    request = PlayerRequest(data=PlayerRequestData())
    response = service.load(request)
    assert not is_ok(response.results), "Load without data should fail"
    assert response.results[0].error_code == GameError.DB_INVALID_DATA, "Should return DB_INVALID_DATA"
    print("  ✓ Load without data properly failed")

    # Test create without data
    response = service.create(request)
    assert not is_ok(response.results), "Create without data should fail"
    print("  ✓ Create without data properly failed")

    # Test save without data
    response = service.save(request)
    assert not is_ok(response.results), "Save without data should fail"
    print("  ✓ Save without data properly failed")

    # Test delete without data
    response = service.delete(request)
    assert not is_ok(response.results), "Delete without data should fail"
    print("  ✓ Delete without data properly failed")

    print("  ✓ All invalid request tests passed\n")


def run_all_tests():
    """Run all PlayerService tests."""
    print("=" * 60)
    print("Running PlayerService Tests")
    print("=" * 60 + "\n")

    # Setup
    db = DB(host="localhost", user="admin", password="minda")
    database_name = "test_player_service_db"

    print("Setting up test database...")
    setup_database(db, database_name)
    print("✓ Test database ready\n")

    # Create service instance
    service = PlayerServiceHandler(db, database_name, cache_size=1000)
    print("✓ PlayerService handler created\n")

    try:
        # Run tests
        created_player = test_create_player(service, db, database_name)
        test_load_player(service, db, database_name, created_player.id)
        test_save_player(service, db, database_name, created_player.id)
        test_delete_player(service, db, database_name)
        test_cache_eviction(service, db, database_name)
        test_invalid_requests(service)

        print("=" * 60)
        print("✓ All PlayerService tests passed!")
        print("=" * 60)

    finally:
        # Cleanup
        print("\nCleaning up test database...")
        teardown_database(db, database_name)
        print("✓ Test database removed")


if __name__ == "__main__":
    run_all_tests()
