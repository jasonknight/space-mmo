#!/usr/bin/env python3
"""
Comprehensive tests for pivot table operations (AttributeOwner and InventoryOwner).
Tests AttributeOwner with Player model and InventoryOwner with Mobile model.
"""

import unittest
import mysql.connector
import os
import uuid
from dotenv import load_dotenv
from models import (
    AttributeOwner,
    Attribute,
    Player,
    Mobile,
    Inventory,
    InventoryOwner,
)

# Load environment variables
load_dotenv()

# Global test database name
TEST_DATABASE = None


def setUpModule():
    """Create a temporary test database and all tables before running any tests."""
    global TEST_DATABASE
    # Generate unique test database name
    TEST_DATABASE = f"gamedb_pivot_test_{uuid.uuid4().hex[:8]}"

    # Connect to MySQL (without database selected)
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        auth_plugin='mysql_native_password',
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()

    try:
        # Create test database
        cursor.execute(f"CREATE DATABASE `{TEST_DATABASE}`")
        connection.database = TEST_DATABASE

        # Disable foreign key checks to allow creating tables in any order
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")

        # Create tables needed for tests
        cursor.execute(Player.CREATE_TABLE_STATEMENT)
        cursor.execute(Mobile.CREATE_TABLE_STATEMENT)
        cursor.execute(Attribute.CREATE_TABLE_STATEMENT)
        cursor.execute(AttributeOwner.CREATE_TABLE_STATEMENT)
        cursor.execute(Inventory.CREATE_TABLE_STATEMENT)
        cursor.execute(InventoryOwner.CREATE_TABLE_STATEMENT)

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")

        connection.commit()
        print(f"Created test database: {TEST_DATABASE}")
    finally:
        cursor.close()
        connection.close()

    # Temporarily override the DB_DATABASE environment variable for tests
    os.environ['DB_DATABASE'] = TEST_DATABASE


def tearDownModule():
    """Drop the temporary test database after all tests complete."""
    global TEST_DATABASE
    if TEST_DATABASE:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor()
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DATABASE}`")
            connection.commit()
            print(f"Dropped test database: {TEST_DATABASE}")
        finally:
            cursor.close()
            connection.close()


class TestAttributeOwnerPivot(unittest.TestCase):
    """Comprehensive tests for AttributeOwner pivot table with Player model."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test player
        self.player = Player()
        self.player.set_full_name('Test Player')
        self.player.set_what_we_call_you('Testy')
        self.player.set_security_token('test_token_123')
        self.player.set_over_13(1)
        self.player.set_year_of_birth(2000)
        self.player.set_email('test@example.com')
        self.player.save()

    def test_attribute_owner_helper_methods(self):
        """Test is_player(), is_mobile(), is_item() helper methods on AttributeOwner."""
        # Create an attribute
        attr = Attribute()
        attr.set_internal_name('strength')
        attr.set_visible(1)
        attr.set_attribute_type('stat')
        attr.save()

        # Create pivot record with player
        pivot = AttributeOwner()
        pivot.set_player_id(self.player.get_id())
        pivot.set_attribute_id(attr.get_id())
        pivot.set_mobile_id(None)
        pivot.set_item_id(None)
        pivot.set_asset_id(None)
        pivot.save()

        # Test helper methods
        self.assertTrue(pivot.is_player())
        self.assertFalse(pivot.is_mobile())
        self.assertFalse(pivot.is_item())
        self.assertFalse(pivot.is_asset())

    def test_player_get_attributes(self):
        """Test player.get_attributes() returns list of Attribute objects."""
        # Create multiple attributes
        attr1 = Attribute()
        attr1.set_internal_name('strength')
        attr1.set_visible(1)
        attr1.set_attribute_type('stat')
        attr1.save()

        attr2 = Attribute()
        attr2.set_internal_name('dexterity')
        attr2.set_visible(1)
        attr2.set_attribute_type('stat')
        attr2.save()

        # Add attributes to player using add_attribute
        self.player.add_attribute(attr1)
        self.player.add_attribute(attr2)

        # Get attributes
        attributes = self.player.get_attributes()

        # Verify
        self.assertEqual(len(attributes), 2)
        self.assertIsInstance(attributes[0], Attribute)
        self.assertIsInstance(attributes[1], Attribute)

        # Verify they're the right attributes
        attr_names = {attr.get_internal_name() for attr in attributes}
        self.assertEqual(attr_names, {'strength', 'dexterity'})

    def test_player_get_attribute_owners(self):
        """Test player.get_attribute_owners() returns list of AttributeOwner objects."""
        # Create and add attributes
        attr1 = Attribute()
        attr1.set_internal_name('strength')
        attr1.set_visible(1)
        attr1.set_attribute_type('stat')
        self.player.add_attribute(attr1)

        attr2 = Attribute()
        attr2.set_internal_name('intelligence')
        attr2.set_visible(1)
        attr2.set_attribute_type('stat')
        self.player.add_attribute(attr2)

        # Get attribute owners
        pivot_records = self.player.get_attribute_owners()

        # Verify
        self.assertEqual(len(pivot_records), 2)
        self.assertIsInstance(pivot_records[0], AttributeOwner)
        self.assertIsInstance(pivot_records[1], AttributeOwner)

        # Verify they're linked to the player
        for pivot in pivot_records:
            self.assertEqual(pivot.get_player_id(), self.player.get_id())
            self.assertTrue(pivot.is_player())

    def test_player_add_attribute_only_sets_player_id(self):
        """Test player.add_attribute() creates pivot with only player_id set (others NULL)."""
        # Create attribute
        attr = Attribute()
        attr.set_internal_name('wisdom')
        attr.set_visible(1)
        attr.set_attribute_type('stat')

        # Add to player
        self.player.add_attribute(attr)

        # Get the pivot record
        pivots = AttributeOwner.find_by_player_id(self.player.get_id())
        self.assertEqual(len(pivots), 1)

        pivot = pivots[0]
        # Verify only player_id is set
        self.assertEqual(pivot.get_player_id(), self.player.get_id())
        self.assertEqual(pivot.get_attribute_id(), attr.get_id())
        self.assertIsNone(pivot.get_mobile_id())
        self.assertIsNone(pivot.get_item_id())
        self.assertIsNone(pivot.get_asset_id())

    def test_player_remove_attribute_cascade_delete(self):
        """Test player.remove_attribute() deletes both pivot and Attribute record."""
        # Create and add attribute
        attr = Attribute()
        attr.set_internal_name('charisma')
        attr.set_visible(1)
        attr.set_attribute_type('stat')
        self.player.add_attribute(attr)

        attr_id = attr.get_id()

        # Verify it exists
        self.assertEqual(len(self.player.get_attributes()), 1)

        # Remove attribute
        self.player.remove_attribute(attr)

        # Verify pivot record is deleted
        pivots = AttributeOwner.find_by_player_id(self.player.get_id())
        self.assertEqual(len(pivots), 0)

        # Verify attribute record is deleted
        deleted_attr = Attribute.find(attr_id)
        self.assertIsNone(deleted_attr)

        # Verify get_attributes returns empty list
        self.assertEqual(len(self.player.get_attributes(reload=True)), 0)

    def test_player_set_attributes_replaces_all(self):
        """Test player.set_attributes([attr1, attr2]) replaces all attributes."""
        # Create and add initial attributes
        attr1 = Attribute()
        attr1.set_internal_name('old_attr1')
        attr1.set_visible(1)
        attr1.set_attribute_type('stat')
        self.player.add_attribute(attr1)

        attr2 = Attribute()
        attr2.set_internal_name('old_attr2')
        attr2.set_visible(1)
        attr2.set_attribute_type('stat')
        self.player.add_attribute(attr2)

        # Verify we have 2 attributes
        self.assertEqual(len(self.player.get_attributes()), 2)

        # Create new attributes
        new_attr1 = Attribute()
        new_attr1.set_internal_name('new_attr1')
        new_attr1.set_visible(1)
        new_attr1.set_attribute_type('stat')

        new_attr2 = Attribute()
        new_attr2.set_internal_name('new_attr2')
        new_attr2.set_visible(1)
        new_attr2.set_attribute_type('stat')

        # Replace all attributes
        self.player.set_attributes([new_attr1, new_attr2])

        # Verify we now have the new attributes
        attributes = self.player.get_attributes(reload=True)
        self.assertEqual(len(attributes), 2)

        attr_names = {attr.get_internal_name() for attr in attributes}
        self.assertEqual(attr_names, {'new_attr1', 'new_attr2'})

        # Verify old attributes don't exist in database
        self.assertIsNone(Attribute.find(attr1.get_id()))
        self.assertIsNone(Attribute.find(attr2.get_id()))

    def test_optimized_save_dirty_check(self):
        """Test that only dirty attributes are saved."""
        # Create and save an attribute
        attr = Attribute()
        attr.set_internal_name('test_attr')
        attr.set_visible(1)
        attr.set_attribute_type('stat')
        attr.save()

        # Mark as not dirty
        attr._dirty = False

        # Add to player - should not re-save the attribute
        self.player.add_attribute(attr)

        # Verify the attribute was added (pivot created) but not re-saved
        attributes = self.player.get_attributes()
        self.assertEqual(len(attributes), 1)
        self.assertEqual(attributes[0].get_internal_name(), 'test_attr')

    def test_no_attribute_sharing_between_owners(self):
        """Test that each owner gets its own Attribute record (no sharing)."""
        # Create two players
        player2 = Player()
        player2.set_full_name('Player Two')
        player2.set_what_we_call_you('Two')
        player2.set_security_token('token_456')
        player2.set_over_13(1)
        player2.set_year_of_birth(1995)
        player2.set_email('two@example.com')
        player2.save()

        # Create attribute for player1
        attr1 = Attribute()
        attr1.set_internal_name('strength')
        attr1.set_visible(1)
        attr1.set_attribute_type('stat')
        self.player.add_attribute(attr1)

        # Create separate attribute for player2 (even with same name)
        attr2 = Attribute()
        attr2.set_internal_name('strength')
        attr2.set_visible(1)
        attr2.set_attribute_type('stat')
        player2.add_attribute(attr2)

        # Verify they have different attribute IDs (no sharing)
        self.assertNotEqual(attr1.get_id(), attr2.get_id())

        # Verify each player has their own attribute
        player1_attrs = self.player.get_attributes()
        player2_attrs = player2.get_attributes()

        self.assertEqual(len(player1_attrs), 1)
        self.assertEqual(len(player2_attrs), 1)
        self.assertEqual(player1_attrs[0].get_id(), attr1.get_id())
        self.assertEqual(player2_attrs[0].get_id(), attr2.get_id())


class TestInventoryOwnerPivot(unittest.TestCase):
    """Comprehensive tests for InventoryOwner pivot table with Mobile model."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test mobile
        self.mobile = Mobile()
        self.mobile.set_mobile_type('goblin')
        self.mobile.set_what_we_call_you('Gobby')
        self.mobile.save()

    def test_inventory_owner_helper_methods(self):
        """Test is_player(), is_mobile(), is_item() helper methods on InventoryOwner."""
        # Create an inventory (set owner_id to satisfy NOT NULL constraint)
        inv = Inventory()
        inv.set_owner_id(self.mobile.get_id())
        inv.set_max_entries(10)
        inv.set_max_volume(100.0)
        inv.save()

        # Create pivot record with mobile
        pivot = InventoryOwner()
        pivot.set_mobile_id(self.mobile.get_id())
        pivot.set_inventory_id(inv.get_id())
        pivot.set_player_id(None)
        pivot.set_item_id(None)
        pivot.save()

        # Test helper methods
        self.assertTrue(pivot.is_mobile())
        self.assertFalse(pivot.is_player())
        self.assertFalse(pivot.is_item())

    def test_mobile_add_inventory_cascade(self):
        """Test mobile.add_inventory() with cascade behavior."""
        # Create inventory (set owner_id to satisfy NOT NULL constraint)
        inv = Inventory()
        inv.set_owner_id(self.mobile.get_id())
        inv.set_max_entries(20)
        inv.set_max_volume(200.0)

        # Add to mobile
        self.mobile.add_inventory(inv)

        # Verify it was added
        inventories = self.mobile.get_inventories()
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].get_max_entries(), 20)

    def test_mobile_remove_inventory_cascade(self):
        """Test mobile.remove_inventory() with cascade delete."""
        # Create and add inventory (set owner_id to satisfy NOT NULL constraint)
        inv = Inventory()
        inv.set_owner_id(self.mobile.get_id())
        inv.set_max_entries(15)
        inv.set_max_volume(150.0)
        self.mobile.add_inventory(inv)

        inv_id = inv.get_id()

        # Verify it exists
        self.assertEqual(len(self.mobile.get_inventories()), 1)

        # Remove inventory
        self.mobile.remove_inventory(inv)

        # Verify pivot and inventory are deleted
        pivots = InventoryOwner.find_by_mobile_id(self.mobile.get_id())
        self.assertEqual(len(pivots), 0)

        deleted_inv = Inventory.find(inv_id)
        self.assertIsNone(deleted_inv)

    def test_mobile_set_inventories_bulk_operation(self):
        """Test mobile.set_inventories([inv1, inv2]) bulk operation."""
        # Create and add initial inventory (set owner_id to satisfy NOT NULL constraint)
        inv1 = Inventory()
        inv1.set_owner_id(self.mobile.get_id())
        inv1.set_max_entries(5)
        inv1.set_max_volume(50.0)
        self.mobile.add_inventory(inv1)

        # Create new inventories (set owner_id to satisfy NOT NULL constraint)
        inv2 = Inventory()
        inv2.set_owner_id(self.mobile.get_id())
        inv2.set_max_entries(10)
        inv2.set_max_volume(100.0)

        inv3 = Inventory()
        inv3.set_owner_id(self.mobile.get_id())
        inv3.set_max_entries(15)
        inv3.set_max_volume(150.0)

        # Replace all
        self.mobile.set_inventories([inv2, inv3])

        # Verify
        inventories = self.mobile.get_inventories(reload=True)
        self.assertEqual(len(inventories), 2)

        max_entries = {inv.get_max_entries() for inv in inventories}
        self.assertEqual(max_entries, {10, 15})

    def test_inventory_owner_only_relevant_fk_set(self):
        """Verify only relevant owner FK is set in InventoryOwner pivot records."""
        # Create and add inventory (set owner_id to satisfy NOT NULL constraint)
        inv = Inventory()
        inv.set_owner_id(self.mobile.get_id())
        inv.set_max_entries(10)
        inv.set_max_volume(100.0)
        self.mobile.add_inventory(inv)

        # Get pivot record
        pivots = InventoryOwner.find_by_mobile_id(self.mobile.get_id())
        self.assertEqual(len(pivots), 1)

        pivot = pivots[0]
        # Verify only mobile_id and inventory_id are set
        self.assertEqual(pivot.get_mobile_id(), self.mobile.get_id())
        self.assertEqual(pivot.get_inventory_id(), inv.get_id())
        self.assertIsNone(pivot.get_player_id())
        self.assertIsNone(pivot.get_item_id())


if __name__ == '__main__':
    unittest.main()
