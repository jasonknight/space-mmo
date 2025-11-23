import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../gen-py"))

from db import DB
from game.ttypes import (
    Mobile,
    MobileType,
    Attribute,
    AttributeType,
    ItemVector3,
    Owner,
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


def test_mobile(db: DB, database_name: str):
    """Test Mobile save and load."""
    print("Testing Mobile...")

    # Create mobile with attributes and owner
    attributes = {
        AttributeType.TRANSLATED_NAME: Attribute(
            id=None,
            internal_name="player_name",
            visible=True,
            value=12345,
            attribute_type=AttributeType.TRANSLATED_NAME,
            owner=7000,
        ),
        AttributeType.LOCAL_POSITION: Attribute(
            id=None,
            internal_name="player_position",
            visible=False,
            value=ItemVector3(x=100.0, y=50.0, z=200.0),
            attribute_type=AttributeType.LOCAL_POSITION,
            owner=7000,
        ),
        # Add character attributes
        AttributeType.STRENGTH: Attribute(
            id=None,
            internal_name="strength",
            visible=True,
            value=0.025,
            attribute_type=AttributeType.STRENGTH,
            owner=7000,
        ),
        AttributeType.LUCK: Attribute(
            id=None,
            internal_name="luck",
            visible=True,
            value=0.018,
            attribute_type=AttributeType.LUCK,
            owner=7000,
        ),
        AttributeType.CONSTITUTION: Attribute(
            id=None,
            internal_name="constitution",
            visible=True,
            value=0.032,
            attribute_type=AttributeType.CONSTITUTION,
            owner=7000,
        ),
        AttributeType.DEXTERITY: Attribute(
            id=None,
            internal_name="dexterity",
            visible=True,
            value=0.041,
            attribute_type=AttributeType.DEXTERITY,
            owner=7000,
        ),
        AttributeType.ARCANA: Attribute(
            id=None,
            internal_name="arcana",
            visible=True,
            value=0.015,
            attribute_type=AttributeType.ARCANA,
            owner=7000,
        ),
        AttributeType.OPERATIONS: Attribute(
            id=None,
            internal_name="operations",
            visible=True,
            value=0.037,
            attribute_type=AttributeType.OPERATIONS,
            owner=7000,
        ),
    }

    # Create owner for mobile
    owner = Owner()
    owner.mobile_id = 999

    mobile = Mobile(
        id=None,
        mobile_type=MobileType.PLAYER,
        attributes=attributes,
        owner=owner,
    )

    # Save mobile
    save_results = db.save_mobile(database_name, mobile)
    assert is_ok(save_results), f"Failed to save Mobile: {save_results[0].message}"
    print(f"  ✓ Saved: {save_results[0].message}")

    # Load mobile
    load_result, loaded_mobile = db.load_mobile(database_name, mobile.id)
    assert is_true(load_result), f"Failed to load Mobile: {load_result.message}"
    print(f"  ✓ Loaded: {load_result.message}")

    # Compare
    assert loaded_mobile.id == mobile.id, "ID mismatch"
    assert loaded_mobile.mobile_type == mobile.mobile_type, "mobile_type mismatch"
    assert len(loaded_mobile.attributes) == len(mobile.attributes), (
        "Attributes count mismatch"
    )

    # Verify owner was saved and loaded correctly
    assert loaded_mobile.owner is not None, "Owner is None"
    assert hasattr(loaded_mobile.owner, "mobile_id"), "Owner should have mobile_id"
    assert loaded_mobile.owner.mobile_id == 999, (
        f"Owner mobile_id mismatch: {loaded_mobile.owner.mobile_id}"
    )

    # Verify character attributes were saved and loaded correctly
    char_attrs = [
        AttributeType.STRENGTH,
        AttributeType.LUCK,
        AttributeType.CONSTITUTION,
        AttributeType.DEXTERITY,
        AttributeType.ARCANA,
        AttributeType.OPERATIONS,
    ]
    for attr_type in char_attrs:
        assert attr_type in loaded_mobile.attributes, (
            f"Missing character attribute: {attr_type}"
        )
        assert (
            loaded_mobile.attributes[attr_type].value
            == mobile.attributes[attr_type].value
        ), f"Character attribute value mismatch for {attr_type}"
    print("  ✓ All character attributes verified")

    # Test update
    print("  Testing update...")
    loaded_mobile.mobile_type = MobileType.NPC
    loaded_mobile.attributes[AttributeType.LOCAL_POSITION].value = ItemVector3(
        x=500.0, y=600.0, z=700.0
    )

    update_results = db.save_mobile(database_name, loaded_mobile)
    assert is_ok(update_results), (
        f"Failed to update Mobile: {update_results[0].message}"
    )
    print(f"  ✓ Updated: {update_results[0].message}")

    # Load again and verify updates
    load_result2, updated_mobile = db.load_mobile(database_name, loaded_mobile.id)
    assert is_true(load_result2), (
        f"Failed to load updated Mobile: {load_result2.message}"
    )
    assert updated_mobile.mobile_type == MobileType.NPC, "Updated mobile_type mismatch"
    print("  ✓ Update verified")

    # Test destroy
    print("  Testing destroy...")
    destroy_results = db.destroy_mobile(database_name, loaded_mobile.id)
    assert is_ok(destroy_results), (
        f"Failed to destroy Mobile: {destroy_results[0].message}"
    )
    print(f"  ✓ Destroyed: {destroy_results[0].message}")

    # Verify load fails after destroy
    load_result3, destroyed_mobile = db.load_mobile(database_name, loaded_mobile.id)
    assert not is_true(load_result3), "Load should fail after destroy"
    assert destroyed_mobile is None, "Destroyed mobile should be None"
    assert load_result3.error_code == GameError.DB_RECORD_NOT_FOUND, (
        f"Expected DB_RECORD_NOT_FOUND, got {load_result3.error_code}"
    )
    print("  ✓ Destroy verified: load failed with DB_RECORD_NOT_FOUND")

    print("  ✓ All assertions passed for Mobile\n")


def main():
    """Run all tests."""
    # Database configuration
    host = "localhost"
    user = "admin"
    password = "minda"
    database_name = "test_mobile_db"

    print("=" * 60)
    print("Mobile Test Suite")
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
        test_mobile(db, database_name)

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
