#!/usr/bin/env python3
"""Tests for PlayerService using db_models."""

import sys
import os
import uuid

thrift_gen_path = '/vagrant/gamedb/thrift/gen-py'
if thrift_gen_path not in sys.path:
    sys.path.insert(0, thrift_gen_path)

py_path = '/vagrant/gamedb/thrift/py'
if py_path not in sys.path:
    sys.path.insert(0, py_path)

from dotenv import load_dotenv
load_dotenv()

import mysql.connector
from services.player_service import PlayerServiceHandler
from db_models.models import Player
from game.ttypes import (
    PlayerRequest,
    PlayerRequestData,
    CreatePlayerRequestData,
    LoadPlayerRequestData,
    SavePlayerRequestData,
    DeletePlayerRequestData,
    Player as ThriftPlayer,
    StatusType,
    GameError,
)
from common import is_ok

TEST_DATABASE = None


def setUpModule():
    """Create unique test database and tables."""
    global TEST_DATABASE
    TEST_DATABASE = f"gamedb_test_{uuid.uuid4().hex[:8]}"

    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD', 'minda'),
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()

    cursor.execute(f"CREATE DATABASE `{TEST_DATABASE}`")
    connection.database = TEST_DATABASE

    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.execute(Player.CREATE_TABLE_STATEMENT)
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")

    connection.commit()
    cursor.close()
    connection.close()

    os.environ['DB_DATABASE'] = TEST_DATABASE
    print(f"✓ Test database created: {TEST_DATABASE}")


def tearDownModule():
    """Drop test database."""
    global TEST_DATABASE
    if TEST_DATABASE:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'admin'),
            password=os.environ.get('DB_PASSWORD', 'minda'),
            auth_plugin="mysql_native_password",
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DATABASE}`")
        connection.commit()
        cursor.close()
        connection.close()
        print(f"✓ Test database dropped: {TEST_DATABASE}")


def run_all_tests():
    """Run all PlayerService tests."""
    print("=" * 60)
    print("Running PlayerService Tests")
    print("=" * 60 + "\n")

    service = PlayerServiceHandler()
    print("✓ PlayerService handler created\n")

    try:
        # Test create
        print("Testing PlayerService.create()...")
        player = ThriftPlayer(
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
        print(f"  ✓ Loaded player\n")

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
        updated_player = Player.find(created_player.id)
        assert updated_player is not None
        assert updated_player.get_full_name() == "John Doe Updated"
        assert updated_player.get_security_token() == "new_hashed_password_456"
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
        deleted_player = Player.find(created_player.id)
        assert deleted_player is None
        print(f"  ✓ Verified player removed from database\n")

        print("=" * 60)
        print("✓ All PlayerService tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with exception: {type(e).__name__}: {str(e)}")
        raise


if __name__ == "__main__":
    setUpModule()
    try:
        run_all_tests()
    finally:
        tearDownModule()
