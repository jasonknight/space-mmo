#!/usr/bin/env python3
"""Simplified tests for PlayerService."""

import sys

sys.path.append("../../gen-py")
sys.path.append("..")

import mysql.connector
from services.player_service import PlayerServiceHandler
from models.player_model import PlayerModel
from game.ttypes import (
    PlayerRequest,
    PlayerRequestData,
    CreatePlayerRequestData,
    LoadPlayerRequestData,
    SavePlayerRequestData,
    DeletePlayerRequestData,
    Player,
    StatusType,
    GameError,
)
from common import is_ok, is_true
from db_tables import get_table_sql


def setup_database(host, user, password, database_name):
    """Create all necessary tables for testing."""
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()

    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cursor.execute(f"CREATE DATABASE {database_name}")

    # Create players table
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {database_name}.players ("
        f"id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        f"full_name VARCHAR(255) NOT NULL, "
        f"what_we_call_you VARCHAR(255) NOT NULL, "
        f"security_token VARCHAR(255) NOT NULL, "
        f"over_13 BOOLEAN NOT NULL, "
        f"year_of_birth INT NOT NULL, "
        f"email VARCHAR(255) NOT NULL"
        f")"
    )

    # Create mobiles table
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {database_name}.mobiles ("
        f"id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        f"what_we_call_you VARCHAR(255), "
        f"mobile_type VARCHAR(50) NOT NULL, "
        f"owner_player_id BIGINT, "
        f"owner_item_id BIGINT"
        f")"
    )

    # Create attributes table
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {database_name}.attributes ("
        f"id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        f"attribute_name VARCHAR(255) NOT NULL UNIQUE, "
        f"attribute_type VARCHAR(50) NOT NULL, "
        f"description TEXT"
        f")"
    )

    # Create attribute_owners table
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {database_name}.attribute_owners ("
        f"id BIGINT AUTO_INCREMENT PRIMARY KEY, "
        f"attribute_id BIGINT NOT NULL, "
        f"owner_mobile_id BIGINT NOT NULL, "
        f"attribute_value VARCHAR(255), "
        f"FOREIGN KEY (attribute_id) REFERENCES {database_name}.attributes(id)"
        f")"
    )

    connection.commit()
    cursor.close()
    connection.close()


def teardown_database(host, user, password, database_name):
    """Delete the test database."""
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {database_name}")
    connection.commit()
    cursor.close()
    connection.close()


def run_all_tests():
    """Run all PlayerService tests."""
    print("=" * 60)
    print("Running PlayerService Tests")
    print("=" * 60 + "\n")

    host = "localhost"
    user = "admin"
    password = "minda"
    database_name = "test_player_service_db"

    print("Setting up test database...")
    setup_database(host, user, password, database_name)
    print("✓ Test database ready\n")

    service = PlayerServiceHandler(host, user, password, database_name, cache_size=1000)
    player_model = PlayerModel(host, user, password, database_name)
    print("✓ PlayerService handler created\n")

    try:
        # Test create
        print("Testing PlayerService.create()...")
        player = Player(
            id=None,
            full_name="John Doe",
            what_we_call_you="JohnD",
            security_token="hashed_password_123",
            over_13=True,
            year_of_birth=1990,
            email="john.doe@example.com",
        )

        request = PlayerRequest(
            data=PlayerRequestData(
                create_player=CreatePlayerRequestData(player=player),
            ),
        )

        response = service.create(request)
        assert is_ok(response.results), f"Create failed: {response.results[0].message}"
        assert response.response_data is not None
        created_player = response.response_data.create_player.player
        assert created_player.id is not None
        print(f"  ✓ Created player with ID: {created_player.id}\n")

        # Test load
        print("Testing PlayerService.load()...")
        service.cache.clear()

        load_request = PlayerRequest(
            data=PlayerRequestData(
                load_player=LoadPlayerRequestData(player_id=created_player.id),
            ),
        )

        response = service.load(load_request)
        assert is_ok(response.results), f"Load failed: {response.results[0].message}"
        loaded_player = response.response_data.load_player.player
        assert loaded_player.id == created_player.id
        assert loaded_player.full_name == "John Doe"
        print(f"  ✓ Loaded player (cache miss)\n")

        # Test load from cache
        response2 = service.load(load_request)
        assert is_ok(response2.results)
        assert "cache" in response2.results[0].message.lower()
        print(f"  ✓ Loaded player (cache hit)\n")

        # Test save
        print("Testing PlayerService.save()...")
        loaded_player.full_name = "John Doe Updated"
        loaded_player.security_token = "new_hashed_password_456"

        save_request = PlayerRequest(
            data=PlayerRequestData(
                save_player=SavePlayerRequestData(player=loaded_player),
            ),
        )

        response = service.save(save_request)
        assert is_ok(response.results), f"Save failed: {response.results[0].message}"
        print(f"  ✓ Saved player\n")

        # Verify save
        result, updated_player = player_model.load(created_player.id)
        assert is_true(result)
        assert updated_player.full_name == "John Doe Updated"
        assert updated_player.security_token == "new_hashed_password_456"
        print(f"  ✓ Verified updates in database\n")

        # Test delete
        print("Testing PlayerService.delete()...")
        delete_request = PlayerRequest(
            data=PlayerRequestData(
                delete_player=DeletePlayerRequestData(player_id=created_player.id),
            ),
        )

        response = service.delete(delete_request)
        assert is_ok(response.results), f"Delete failed: {response.results[0].message}"
        assert response.response_data.delete_player.player_id == created_player.id
        print(f"  ✓ Deleted player\n")

        # Verify delete
        result, deleted_player = player_model.load(created_player.id)
        assert not is_true(result)
        assert deleted_player is None
        print(f"  ✓ Verified player removed from database\n")

        print("=" * 60)
        print("✓ All PlayerService tests passed!")
        print("=" * 60)

    finally:
        print("\nCleaning up test database...")
        teardown_database(host, user, password, database_name)
        print("✓ Test database removed")


if __name__ == "__main__":
    run_all_tests()
