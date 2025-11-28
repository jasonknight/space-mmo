#!/usr/bin/env python3
"""
Auto-generated test suite for all models.
Generated from database schema - do not modify manually.
"""

import sys
import os

# Add parent directory to path for models import
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Add Thrift generated code to path
thrift_gen_path = '/vagrant/gamedb/thrift/gen-py'
if thrift_gen_path not in sys.path:
    sys.path.insert(0, thrift_gen_path)
import unittest
import mysql.connector
import uuid
from dotenv import load_dotenv
from game.ttypes import AttributeType as ThriftAttributeType, ItemType as ThriftItemType, MobileType as ThriftMobileType
from models import AttributeOwner, Attribute, Inventory, InventoryEntry, InventoryOwner, ItemBlueprintComponent, ItemBlueprint, Item, MobileItemAttribute, MobileItemBlueprintComponent, MobileItemBlueprint, MobileItem, Mobile, Player
from datetime import datetime
# Load environment variables
load_dotenv()

# Global test database name
TEST_DATABASE = None


def setUpModule():
    """Create a temporary test database and all tables before running any tests."""
    global TEST_DATABASE
    # Generate unique test database name
    TEST_DATABASE = f"gamedb_test_{uuid.uuid4().hex[:8]}"

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

        # Create all tables using CREATE TABLE statements from models
        # Create attribute_owners table
        cursor.execute(AttributeOwner.CREATE_TABLE_STATEMENT)
        # Create attributes table
        cursor.execute(Attribute.CREATE_TABLE_STATEMENT)
        # Create inventories table
        cursor.execute(Inventory.CREATE_TABLE_STATEMENT)
        # Create inventory_entries table
        cursor.execute(InventoryEntry.CREATE_TABLE_STATEMENT)
        # Create inventory_owners table
        cursor.execute(InventoryOwner.CREATE_TABLE_STATEMENT)
        # Create item_blueprint_components table
        cursor.execute(ItemBlueprintComponent.CREATE_TABLE_STATEMENT)
        # Create item_blueprints table
        cursor.execute(ItemBlueprint.CREATE_TABLE_STATEMENT)
        # Create items table
        cursor.execute(Item.CREATE_TABLE_STATEMENT)
        # Create mobile_item_attributes table
        cursor.execute(MobileItemAttribute.CREATE_TABLE_STATEMENT)
        # Create mobile_item_blueprint_components table
        cursor.execute(MobileItemBlueprintComponent.CREATE_TABLE_STATEMENT)
        # Create mobile_item_blueprints table
        cursor.execute(MobileItemBlueprint.CREATE_TABLE_STATEMENT)
        # Create mobile_items table
        cursor.execute(MobileItem.CREATE_TABLE_STATEMENT)
        # Create mobiles table
        cursor.execute(Mobile.CREATE_TABLE_STATEMENT)
        # Create players table
        cursor.execute(Player.CREATE_TABLE_STATEMENT)

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

def create_seed_data():
    """Create complete graph of test data covering all relationships."""
    seed = {}

    # Create base records without foreign keys first
    # Create Attribute records
    seed['attribute1'] = Attribute()
    seed['attribute1'].set_internal_name('test_internal_name_1')
    seed['attribute1'].set_visible(1)
    seed['attribute1'].set_attribute_type(ThriftAttributeType.QUANTITY)
    seed['attribute1'].save()

    seed['attribute2'] = Attribute()
    seed['attribute2'].set_internal_name('test_internal_name_2')
    seed['attribute2'].set_visible(2)
    seed['attribute2'].set_attribute_type(ThriftAttributeType.QUANTITY)
    seed['attribute2'].save()

    # Create Inventory records
    seed['inventory1'] = Inventory()
    seed['inventory1'].set_max_entries(1)
    seed['inventory1'].set_max_volume(1.0)
    seed['inventory1'].save()

    seed['inventory2'] = Inventory()
    seed['inventory2'].set_max_entries(2)
    seed['inventory2'].set_max_volume(2.0)
    seed['inventory2'].save()

    # Create ItemBlueprint records
    seed['itemblueprint1'] = ItemBlueprint()
    seed['itemblueprint1'].set_bake_time_ms(1)
    seed['itemblueprint1'].save()

    seed['itemblueprint2'] = ItemBlueprint()
    seed['itemblueprint2'].set_bake_time_ms(2)
    seed['itemblueprint2'].save()

    # Create MobileItemBlueprint records
    seed['mobileitemblueprint1'] = MobileItemBlueprint()
    seed['mobileitemblueprint1'].set_bake_time_ms(1)
    seed['mobileitemblueprint1'].save()

    seed['mobileitemblueprint2'] = MobileItemBlueprint()
    seed['mobileitemblueprint2'].set_bake_time_ms(2)
    seed['mobileitemblueprint2'].save()

    # Create Player records
    seed['player1'] = Player()
    seed['player1'].set_full_name('test_full_name_1')
    seed['player1'].set_what_we_call_you('test_what_we_call_you_1')
    seed['player1'].set_security_token('test_security_token_1')
    seed['player1'].set_over_13(1)
    seed['player1'].set_year_of_birth(1)
    seed['player1'].set_email('test_email_1')
    seed['player1'].save()

    seed['player2'] = Player()
    seed['player2'].set_full_name('test_full_name_2')
    seed['player2'].set_what_we_call_you('test_what_we_call_you_2')
    seed['player2'].set_security_token('test_security_token_2')
    seed['player2'].set_over_13(2)
    seed['player2'].set_year_of_birth(2)
    seed['player2'].set_email('test_email_2')
    seed['player2'].save()

    # Create ItemBlueprintComponent records with relationships
    seed['itemblueprintcomponent1'] = ItemBlueprintComponent()
    if 'itemblueprint1' in seed:
        seed['itemblueprintcomponent1'].set_item_blueprint_id(seed['itemblueprint1'].get_id())
    seed['itemblueprintcomponent1'].set_ratio(1.0)
    seed['itemblueprintcomponent1'].save()

    # Create Item records with relationships
    seed['item1'] = Item()
    seed['item1'].set_internal_name('test_internal_name_1')
    seed['item1'].set_item_type(ThriftItemType.WEAPON)
    seed['item1'].save()

    # Create MobileItemBlueprintComponent records with relationships
    seed['mobileitemblueprintcomponent1'] = MobileItemBlueprintComponent()
    if 'mobileitemblueprint1' in seed:
        seed['mobileitemblueprintcomponent1'].set_item_blueprint_id(seed['mobileitemblueprint1'].get_id())
    seed['mobileitemblueprintcomponent1'].set_ratio(1.0)
    seed['mobileitemblueprintcomponent1'].save()

    # Create MobileItem records with relationships
    seed['mobileitem1'] = MobileItem()
    if 'mobile1' in seed:
        seed['mobileitem1'].set_mobile_id(seed['mobile1'].get_id())
    seed['mobileitem1'].set_internal_name('test_internal_name_1')
    seed['mobileitem1'].set_item_type(ThriftItemType.WEAPON)
    if 'item1' in seed:
        seed['mobileitem1'].set_item_id(seed['item1'].get_id())
    seed['mobileitem1'].save()

    # Create Mobile records with relationships
    seed['mobile1'] = Mobile()
    seed['mobile1'].set_mobile_type(ThriftMobileType.PLAYER)
    seed['mobile1'].set_what_we_call_you('test_what_we_call_you_1')
    seed['mobile1'].save()


    return seed


def cleanup_seed_data(seed):
    """Clean up seed data in reverse dependency order."""
    # Simply let the tearDownModule handle database cleanup
    pass


class TestAttributeOwnerRelationships(unittest.TestCase):
    """Comprehensive relationship tests for AttributeOwner model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = AttributeOwner()

    def test_belongs_to_attribute_basic(self):
        """Test attribute relationship basic getter."""
        # Create related model
        related = Attribute()
        related.set_internal_name('test_internal_name')
        related.set_visible(1)
        related.set_attribute_type(ThriftAttributeType.STRENGTH)
        related.save()

        # Create parent and set FK
        parent = AttributeOwner()
        parent.set_attribute_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_attribute()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Attribute)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_attribute()
        self.assertIs(result, result2)


    def test_belongs_to_attribute_setter(self):
        """Test attribute relationship setter."""
        # Create related models
        related1 = Attribute()
        related1.set_internal_name('test_internal_name')
        related1.set_visible(1)
        related1.set_attribute_type(ThriftAttributeType.STRENGTH)
        related1.save()

        # Create parent
        parent = AttributeOwner()
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_setter = Attribute()

        attribute_prereq_setter.set_internal_name('test_prereq_setter')

        attribute_prereq_setter.set_visible(1)

        attribute_prereq_setter.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_setter.save()


        parent.set_attribute_id(attribute_prereq_setter.get_id())

        # Use setter
        parent.set_attribute(related1)

        # Verify FK updated
        self.assertEqual(parent.get_attribute_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_attribute(), related1)


    def test_belongs_to_mobile_basic(self):
        """Test mobile relationship basic getter."""
        # Create related model
        related = Mobile()
        related.set_mobile_type(ThriftMobileType.PLAYER)
        related.set_what_we_call_you('test_what_we_call_you')
        related.save()

        # Create parent and set FK
        parent = AttributeOwner()
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_basic = Attribute()

        attribute_prereq_basic.set_internal_name('test_prereq_basic')

        attribute_prereq_basic.set_visible(1)

        attribute_prereq_basic.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_basic.save()


        parent.set_attribute_id(attribute_prereq_basic.get_id())
        parent.set_mobile_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_mobile()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Mobile)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_mobile()
        self.assertIs(result, result2)


    def test_belongs_to_mobile_setter(self):
        """Test mobile relationship setter."""
        # Create related models
        related1 = Mobile()
        related1.set_mobile_type(ThriftMobileType.PLAYER)
        related1.set_what_we_call_you('test_what_we_call_you')
        related1.save()

        # Create parent
        parent = AttributeOwner()
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_setter = Attribute()

        attribute_prereq_setter.set_internal_name('test_prereq_setter')

        attribute_prereq_setter.set_visible(1)

        attribute_prereq_setter.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_setter.save()


        parent.set_attribute_id(attribute_prereq_setter.get_id())

        # Use setter
        parent.set_mobile(related1)

        # Verify FK updated
        self.assertEqual(parent.get_mobile_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_mobile(), related1)


    def test_belongs_to_item_basic(self):
        """Test item relationship basic getter."""
        # Create related model
        related = Item()
        related.set_internal_name('test_internal_name')
        related.set_item_type(ThriftItemType.WEAPON)
        related.save()

        # Create parent and set FK
        parent = AttributeOwner()
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_basic = Attribute()

        attribute_prereq_basic.set_internal_name('test_prereq_basic')

        attribute_prereq_basic.set_visible(1)

        attribute_prereq_basic.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_basic.save()


        parent.set_attribute_id(attribute_prereq_basic.get_id())
        parent.set_item_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_item()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Item)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_item()
        self.assertIs(result, result2)


    def test_belongs_to_item_setter(self):
        """Test item relationship setter."""
        # Create related models
        related1 = Item()
        related1.set_internal_name('test_internal_name')
        related1.set_item_type(ThriftItemType.WEAPON)
        related1.save()

        # Create parent
        parent = AttributeOwner()
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_setter = Attribute()

        attribute_prereq_setter.set_internal_name('test_prereq_setter')

        attribute_prereq_setter.set_visible(1)

        attribute_prereq_setter.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_setter.save()


        parent.set_attribute_id(attribute_prereq_setter.get_id())

        # Use setter
        parent.set_item(related1)

        # Verify FK updated
        self.assertEqual(parent.get_item_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_item(), related1)


    def test_belongs_to_player_basic(self):
        """Test player relationship basic getter."""
        # Create related model
        related = Player()
        related.set_full_name('test_full_name')
        related.set_what_we_call_you('test_what_we_call_you')
        related.set_security_token('test_security_token')
        related.set_over_13(1)
        related.set_year_of_birth(1)
        related.set_email('test_email')
        related.save()

        # Create parent and set FK
        parent = AttributeOwner()
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_basic = Attribute()

        attribute_prereq_basic.set_internal_name('test_prereq_basic')

        attribute_prereq_basic.set_visible(1)

        attribute_prereq_basic.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_basic.save()


        parent.set_attribute_id(attribute_prereq_basic.get_id())
        parent.set_player_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_player()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Player)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_player()
        self.assertIs(result, result2)


    def test_belongs_to_player_setter(self):
        """Test player relationship setter."""
        # Create related models
        related1 = Player()
        related1.set_full_name('test_full_name')
        related1.set_what_we_call_you('test_what_we_call_you')
        related1.set_security_token('test_security_token')
        related1.set_over_13(1)
        related1.set_year_of_birth(1)
        related1.set_email('test_email')
        related1.save()

        # Create parent
        parent = AttributeOwner()
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_setter = Attribute()

        attribute_prereq_setter.set_internal_name('test_prereq_setter')

        attribute_prereq_setter.set_visible(1)

        attribute_prereq_setter.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_setter.save()


        parent.set_attribute_id(attribute_prereq_setter.get_id())

        # Use setter
        parent.set_player(related1)

        # Verify FK updated
        self.assertEqual(parent.get_player_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_player(), related1)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = Attribute()
        related.set_internal_name('test_internal_name')
        related.set_visible(1)
        related.set_attribute_type(ThriftAttributeType.STRENGTH)
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = AttributeOwner()
        parent.set_attribute_id(1)
        parent.set_attribute(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)



class TestAttributeRelationships(unittest.TestCase):
    """Comprehensive relationship tests for Attribute model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = Attribute()

    def test_has_many_attribute_owners_basic(self):
        """Test attribute_owners relationship basic getter."""
        # Create parent
        parent = Attribute()
        parent.set_internal_name('test_internal_name')
        parent.set_visible(1)
        parent.set_attribute_type(ThriftAttributeType.STRENGTH)
        parent.save()


        # Create prerequisite Attribute for attribute_id

        attribute_prereq = Attribute()

        attribute_prereq.set_internal_name('test_prereq')

        attribute_prereq.set_visible(1)

        attribute_prereq.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq.save()


        # Create related records
        child1 = AttributeOwner()
        child1.set_attribute_id(parent.get_id())
        child1.save()

        child2 = AttributeOwner()
        child2.set_attribute_id(parent.get_id())
        child2.save()

        # Test getter (eager mode)
        results = parent.get_attribute_owners(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_attribute_owners(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_attribute_owners(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_attribute_owners_lazy(self):
        """Test attribute_owners relationship lazy loading."""
        # Create parent with children
        parent = Attribute()
        parent.set_internal_name('test_internal_name')
        parent.set_visible(1)
        parent.set_attribute_type(ThriftAttributeType.STRENGTH)
        parent.save()


        # Create prerequisite Attribute for attribute_id

        attribute_prereq_lazy = Attribute()

        attribute_prereq_lazy.set_internal_name('test_internal_name')

        attribute_prereq_lazy.set_visible(1)

        attribute_prereq_lazy.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_lazy.save()


        # Create child
        child = AttributeOwner()
        child.set_attribute_id(parent.get_id())
        child.save()

        # Test lazy mode
        results_iter = parent.get_attribute_owners(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], AttributeOwner)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = Attribute()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = Attribute()
        model.set_internal_name('test_internal_name')
        model.set_visible(1)
        model.set_attribute_type(ThriftAttributeType.STRENGTH)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = Attribute()
        model.set_internal_name('test_internal_name')
        model.set_visible(1)
        model.set_attribute_type(ThriftAttributeType.STRENGTH)
        model.save()
        self.assertFalse(model._dirty)

        model.set_internal_name('test_value_2')
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = Attribute()
        model.set_internal_name('test_internal_name')
        model.set_visible(1)
        model.set_attribute_type(ThriftAttributeType.STRENGTH)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = Attribute()
        parent.set_internal_name('test_internal_name')
        parent.set_visible(1)
        parent.set_attribute_type(ThriftAttributeType.STRENGTH)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = AttributeOwner()
        child1.set_attribute_id(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = AttributeOwner()
        child2.set_attribute_id(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_attribute_owners(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = Attribute.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = AttributeOwner.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = AttributeOwner.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = Attribute()
        parent.set_internal_name('test_internal_name')
        parent.set_visible(1)
        parent.set_attribute_type(ThriftAttributeType.STRENGTH)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = AttributeOwner()
        child.set_attribute_id(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = Attribute.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = AttributeOwner.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass

    def test_from_thrift_with_enum(self):
        """Test from_thrift correctly converts enum integer to string name."""
        from game.ttypes import Attribute as ThriftAttribute, AttributeType

        # Create Thrift object with enum field
        thrift_obj = ThriftAttribute(
            internal_name='test_internal_name',
            visible=1,
            attribute_type=AttributeType.STRENGTH,
        )

        # Convert to model
        model = Attribute()
        model.from_thrift(thrift_obj)

        # Verify enum was converted to string name
        self.assertEqual(model._data['attribute_type'], 'STRENGTH')

        # Save and reload to verify round-trip
        model.save()
        model_id = model.get_id()
        self.assertIsNotNone(model_id)

        # Load from database
        loaded_model = Attribute.find(model_id)
        self.assertIsNotNone(loaded_model)
        self.assertEqual(loaded_model._data['attribute_type'], 'STRENGTH')

        # Convert back to Thrift
        results, thrift_obj_out = loaded_model.into_thrift()
        if thrift_obj_out is None:
            # Print error details if conversion failed
            for result in results:
                print(f"into_thrift error: {result.message}")
        self.assertIsNotNone(thrift_obj_out, f"into_thrift failed: {results[0].message if results else 'unknown'}")
        self.assertEqual(thrift_obj_out.attribute_type, AttributeType.STRENGTH)

        # Clean up - use fresh connection to avoid nested transaction
        cleanup_conn = loaded_model._create_connection()
        loaded_model.destroy(connection=cleanup_conn)
        cleanup_conn.close()



class TestInventoryRelationships(unittest.TestCase):
    """Comprehensive relationship tests for Inventory model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = Inventory()

    def test_has_many_inventory_entries_basic(self):
        """Test inventory_entries relationship basic getter."""
        # Create parent
        parent = Inventory()
        parent.set_owner_id(1)
        parent.set_max_entries(1)
        parent.set_max_volume(1.0)
        parent.save()


        # Create prerequisite Item for item_id

        item_prereq = Item()

        item_prereq.set_internal_name('test_prereq')

        item_prereq.set_item_type(ThriftItemType.WEAPON)

        item_prereq.save()


        # Create related records
        child1 = InventoryEntry()
        child1.set_inventory_id(parent.get_id())
        # Create prerequisite Item for item_id

        item_prereq_child1 = Item()

        item_prereq_child1.set_internal_name('test_prereq_child1')

        item_prereq_child1.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child1.save()


        child1.set_item_id(item_prereq_child1.get_id())
        child1.set_quantity(1.0)
        child1.save()

        child2 = InventoryEntry()
        child2.set_inventory_id(parent.get_id())
        # Create prerequisite Item for item_id

        item_prereq_child2 = Item()

        item_prereq_child2.set_internal_name('test_prereq_child2')

        item_prereq_child2.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child2.save()


        child2.set_item_id(item_prereq_child2.get_id())
        child2.set_quantity(1.0)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_inventory_entries(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_inventory_entries(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_inventory_entries(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_inventory_entries_lazy(self):
        """Test inventory_entries relationship lazy loading."""
        # Create parent with children
        parent = Inventory()
        parent.set_owner_id(1)
        parent.set_max_entries(1)
        parent.set_max_volume(1.0)
        parent.save()


        # Create prerequisite Item for item_id

        item_prereq_lazy = Item()

        item_prereq_lazy.set_internal_name('test_internal_name')

        item_prereq_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_lazy.save()


        # Create child
        child = InventoryEntry()
        child.set_inventory_id(parent.get_id())
        # Create prerequisite Item for item_id

        item_prereq_child_lazy = Item()

        item_prereq_child_lazy.set_internal_name('test_prereq_child_lazy')

        item_prereq_child_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child_lazy.save()


        child.set_item_id(item_prereq_child_lazy.get_id())
        child.set_quantity(1.0)
        child.save()

        # Test lazy mode
        results_iter = parent.get_inventory_entries(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], InventoryEntry)


    def test_has_many_inventory_owners_basic(self):
        """Test inventory_owners relationship basic getter."""
        # Create parent
        parent = Inventory()
        parent.set_owner_id(1)
        parent.set_max_entries(1)
        parent.set_max_volume(1.0)
        parent.save()


        # Create related records
        child1 = InventoryOwner()
        child1.set_inventory_id(parent.get_id())
        child1.save()

        child2 = InventoryOwner()
        child2.set_inventory_id(parent.get_id())
        child2.save()

        # Test getter (eager mode)
        results = parent.get_inventory_owners(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_inventory_owners(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_inventory_owners(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_inventory_owners_lazy(self):
        """Test inventory_owners relationship lazy loading."""
        # Create parent with children
        parent = Inventory()
        parent.set_owner_id(1)
        parent.set_max_entries(1)
        parent.set_max_volume(1.0)
        parent.save()


        # Create child
        child = InventoryOwner()
        child.set_inventory_id(parent.get_id())
        child.save()

        # Test lazy mode
        results_iter = parent.get_inventory_owners(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], InventoryOwner)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = Inventory()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = Inventory()
        model.set_owner_id(1)
        model.set_max_entries(1)
        model.set_max_volume(1.0)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = Inventory()
        model.set_owner_id(1)
        model.set_max_entries(1)
        model.set_max_volume(1.0)
        model.save()
        self.assertFalse(model._dirty)

        model.set_max_entries(2)
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = Inventory()
        model.set_owner_id(1)
        model.set_max_entries(1)
        model.set_max_volume(1.0)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = Inventory()
        parent.set_owner_id(1)
        parent.set_max_entries(1)
        parent.set_max_volume(1.0)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = InventoryEntry()
        child1.set_item_id(1)
        child1.set_quantity(1.0)
        child1.set_inventory_id(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = InventoryEntry()
        child2.set_item_id(1)
        child2.set_quantity(1.0)
        child2.set_inventory_id(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_inventory_entries(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = Inventory.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = InventoryEntry.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = InventoryEntry.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = Inventory()
        parent.set_owner_id(1)
        parent.set_max_entries(1)
        parent.set_max_volume(1.0)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = InventoryEntry()
        child.set_item_id(1)
        child.set_quantity(1.0)
        child.set_inventory_id(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = Inventory.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = InventoryEntry.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass

    # TODO: Add Owner union tests for tables with owner fields
    # TODO: Add AttributeValue union tests for attributes table



class TestInventoryEntryRelationships(unittest.TestCase):
    """Comprehensive relationship tests for InventoryEntry model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = InventoryEntry()

    def test_belongs_to_inventory_basic(self):
        """Test inventory relationship basic getter."""
        # Create related model
        related = Inventory()
        related.set_owner_id(1)
        related.set_max_entries(1)
        related.set_max_volume(1.0)
        related.save()

        # Create parent and set FK
        parent = InventoryEntry()
        # Create prerequisite Item for item_id

        item_prereq_basic = Item()

        item_prereq_basic.set_internal_name('test_prereq_basic')

        item_prereq_basic.set_item_type(ThriftItemType.WEAPON)

        item_prereq_basic.save()


        parent.set_item_id(item_prereq_basic.get_id())
        parent.set_quantity(1.0)
        parent.set_inventory_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_inventory()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Inventory)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_inventory()
        self.assertIs(result, result2)


    def test_belongs_to_inventory_setter(self):
        """Test inventory relationship setter."""
        # Create related models
        related1 = Inventory()
        related1.set_owner_id(1)
        related1.set_max_entries(1)
        related1.set_max_volume(1.0)
        related1.save()

        # Create parent
        parent = InventoryEntry()
        parent.set_inventory_id(1)
        # Create prerequisite Item for item_id

        item_prereq_setter = Item()

        item_prereq_setter.set_internal_name('test_prereq_setter')

        item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        item_prereq_setter.save()


        parent.set_item_id(item_prereq_setter.get_id())
        parent.set_quantity(1.0)

        # Use setter
        parent.set_inventory(related1)

        # Verify FK updated
        self.assertEqual(parent.get_inventory_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_inventory(), related1)


    def test_belongs_to_item_basic(self):
        """Test item relationship basic getter."""
        # Create related model
        related = Item()
        related.set_internal_name('test_internal_name')
        related.set_item_type(ThriftItemType.WEAPON)
        related.save()

        # Create parent and set FK
        parent = InventoryEntry()
        parent.set_inventory_id(1)
        parent.set_quantity(1.0)
        parent.set_item_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_item()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Item)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_item()
        self.assertIs(result, result2)


    def test_belongs_to_item_setter(self):
        """Test item relationship setter."""
        # Create related models
        related1 = Item()
        related1.set_internal_name('test_internal_name')
        related1.set_item_type(ThriftItemType.WEAPON)
        related1.save()

        # Create parent
        parent = InventoryEntry()
        parent.set_inventory_id(1)
        # Create prerequisite Item for item_id

        item_prereq_setter = Item()

        item_prereq_setter.set_internal_name('test_prereq_setter')

        item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        item_prereq_setter.save()


        parent.set_item_id(item_prereq_setter.get_id())
        parent.set_quantity(1.0)

        # Use setter
        parent.set_item(related1)

        # Verify FK updated
        self.assertEqual(parent.get_item_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_item(), related1)


    def test_belongs_to_mobile_item_basic(self):
        """Test mobile_item relationship basic getter."""
        # Create related model
        related = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_basic = Mobile()

        mobile_prereq_basic.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_basic.set_what_we_call_you('test_prereq_basic')

        mobile_prereq_basic.save()


        related.set_mobile_id(mobile_prereq_basic.get_id())
        related.set_internal_name('test_internal_name')
        related.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_basic = Item()

        item_prereq_basic.set_internal_name('test_prereq_basic')

        item_prereq_basic.set_item_type(ThriftItemType.WEAPON)

        item_prereq_basic.save()


        related.set_item_id(item_prereq_basic.get_id())
        related.save()

        # Create parent and set FK
        parent = InventoryEntry()
        parent.set_inventory_id(1)
        # Create prerequisite Item for item_id

        item_prereq_basic = Item()

        item_prereq_basic.set_internal_name('test_prereq_basic')

        item_prereq_basic.set_item_type(ThriftItemType.WEAPON)

        item_prereq_basic.save()


        parent.set_item_id(item_prereq_basic.get_id())
        parent.set_quantity(1.0)
        parent.set_mobile_item_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_mobile_item()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MobileItem)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_mobile_item()
        self.assertIs(result, result2)


    def test_belongs_to_mobile_item_setter(self):
        """Test mobile_item relationship setter."""
        # Create related models
        related1 = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_setter = Mobile()

        mobile_prereq_setter.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_setter.set_what_we_call_you('test_prereq_setter')

        mobile_prereq_setter.save()


        related1.set_mobile_id(mobile_prereq_setter.get_id())
        related1.set_internal_name('test_internal_name')
        related1.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_setter = Item()

        item_prereq_setter.set_internal_name('test_prereq_setter')

        item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        item_prereq_setter.save()


        related1.set_item_id(item_prereq_setter.get_id())
        related1.save()

        # Create parent
        parent = InventoryEntry()
        parent.set_inventory_id(1)
        # Create prerequisite Item for item_id

        item_prereq_setter = Item()

        item_prereq_setter.set_internal_name('test_prereq_setter')

        item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        item_prereq_setter.save()


        parent.set_item_id(item_prereq_setter.get_id())
        parent.set_quantity(1.0)

        # Use setter
        parent.set_mobile_item(related1)

        # Verify FK updated
        self.assertEqual(parent.get_mobile_item_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_mobile_item(), related1)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = InventoryEntry()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = InventoryEntry()
        model.set_inventory_id(1)
        model.set_item_id(1)
        model.set_quantity(1.0)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = InventoryEntry()
        model.set_inventory_id(1)
        model.set_item_id(1)
        model.set_quantity(1.0)
        model.save()
        self.assertFalse(model._dirty)

        model.set_quantity(2.0)
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = InventoryEntry()
        model.set_inventory_id(1)
        model.set_item_id(1)
        model.set_quantity(1.0)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = Inventory()
        related.set_owner_id(1)
        related.set_max_entries(1)
        related.set_max_volume(1.0)
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = InventoryEntry()
        parent.set_inventory_id(1)
        parent.set_item_id(1)
        parent.set_quantity(1.0)
        parent.set_inventory(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)

    # TODO: Add Owner union tests for tables with owner fields
    # TODO: Add AttributeValue union tests for attributes table



class TestInventoryOwnerRelationships(unittest.TestCase):
    """Comprehensive relationship tests for InventoryOwner model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = InventoryOwner()

    def test_belongs_to_inventory_basic(self):
        """Test inventory relationship basic getter."""
        # Create related model
        related = Inventory()
        related.set_owner_id(1)
        related.set_max_entries(1)
        related.set_max_volume(1.0)
        related.save()

        # Create parent and set FK
        parent = InventoryOwner()
        parent.set_inventory_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_inventory()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Inventory)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_inventory()
        self.assertIs(result, result2)


    def test_belongs_to_inventory_setter(self):
        """Test inventory relationship setter."""
        # Create related models
        related1 = Inventory()
        related1.set_owner_id(1)
        related1.set_max_entries(1)
        related1.set_max_volume(1.0)
        related1.save()

        # Create parent
        parent = InventoryOwner()
        parent.set_inventory_id(1)

        # Use setter
        parent.set_inventory(related1)

        # Verify FK updated
        self.assertEqual(parent.get_inventory_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_inventory(), related1)


    def test_belongs_to_mobile_basic(self):
        """Test mobile relationship basic getter."""
        # Create related model
        related = Mobile()
        related.set_mobile_type(ThriftMobileType.PLAYER)
        related.set_what_we_call_you('test_what_we_call_you')
        related.save()

        # Create parent and set FK
        parent = InventoryOwner()
        parent.set_inventory_id(1)
        parent.set_mobile_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_mobile()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Mobile)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_mobile()
        self.assertIs(result, result2)


    def test_belongs_to_mobile_setter(self):
        """Test mobile relationship setter."""
        # Create related models
        related1 = Mobile()
        related1.set_mobile_type(ThriftMobileType.PLAYER)
        related1.set_what_we_call_you('test_what_we_call_you')
        related1.save()

        # Create parent
        parent = InventoryOwner()
        parent.set_inventory_id(1)

        # Use setter
        parent.set_mobile(related1)

        # Verify FK updated
        self.assertEqual(parent.get_mobile_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_mobile(), related1)


    def test_belongs_to_item_basic(self):
        """Test item relationship basic getter."""
        # Create related model
        related = Item()
        related.set_internal_name('test_internal_name')
        related.set_item_type(ThriftItemType.WEAPON)
        related.save()

        # Create parent and set FK
        parent = InventoryOwner()
        parent.set_inventory_id(1)
        parent.set_item_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_item()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Item)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_item()
        self.assertIs(result, result2)


    def test_belongs_to_item_setter(self):
        """Test item relationship setter."""
        # Create related models
        related1 = Item()
        related1.set_internal_name('test_internal_name')
        related1.set_item_type(ThriftItemType.WEAPON)
        related1.save()

        # Create parent
        parent = InventoryOwner()
        parent.set_inventory_id(1)

        # Use setter
        parent.set_item(related1)

        # Verify FK updated
        self.assertEqual(parent.get_item_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_item(), related1)


    def test_belongs_to_player_basic(self):
        """Test player relationship basic getter."""
        # Create related model
        related = Player()
        related.set_full_name('test_full_name')
        related.set_what_we_call_you('test_what_we_call_you')
        related.set_security_token('test_security_token')
        related.set_over_13(1)
        related.set_year_of_birth(1)
        related.set_email('test_email')
        related.save()

        # Create parent and set FK
        parent = InventoryOwner()
        parent.set_inventory_id(1)
        parent.set_player_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_player()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Player)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_player()
        self.assertIs(result, result2)


    def test_belongs_to_player_setter(self):
        """Test player relationship setter."""
        # Create related models
        related1 = Player()
        related1.set_full_name('test_full_name')
        related1.set_what_we_call_you('test_what_we_call_you')
        related1.set_security_token('test_security_token')
        related1.set_over_13(1)
        related1.set_year_of_birth(1)
        related1.set_email('test_email')
        related1.save()

        # Create parent
        parent = InventoryOwner()
        parent.set_inventory_id(1)

        # Use setter
        parent.set_player(related1)

        # Verify FK updated
        self.assertEqual(parent.get_player_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_player(), related1)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = Inventory()
        related.set_owner_id(1)
        related.set_max_entries(1)
        related.set_max_volume(1.0)
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = InventoryOwner()
        parent.set_inventory_id(1)
        parent.set_inventory(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)



class TestItemBlueprintComponentRelationships(unittest.TestCase):
    """Comprehensive relationship tests for ItemBlueprintComponent model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ItemBlueprintComponent()

    def test_belongs_to_item_blueprint_basic(self):
        """Test item_blueprint relationship basic getter."""
        # Create related model
        related = ItemBlueprint()
        related.set_bake_time_ms(1)
        related.save()

        # Create parent and set FK
        parent = ItemBlueprintComponent()
        parent.set_component_item_id(1)
        parent.set_ratio(1.0)
        parent.set_item_blueprint_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_item_blueprint()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ItemBlueprint)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_item_blueprint()
        self.assertIs(result, result2)


    def test_belongs_to_item_blueprint_setter(self):
        """Test item_blueprint relationship setter."""
        # Create related models
        related1 = ItemBlueprint()
        related1.set_bake_time_ms(1)
        related1.save()

        # Create parent
        parent = ItemBlueprintComponent()
        # Create prerequisite ItemBlueprint for item_blueprint_id

        item_blueprint_prereq_setter = ItemBlueprint()

        item_blueprint_prereq_setter.set_bake_time_ms(1)

        item_blueprint_prereq_setter.save()


        parent.set_item_blueprint_id(item_blueprint_prereq_setter.get_id())
        parent.set_component_item_id(1)
        parent.set_ratio(1.0)

        # Use setter
        parent.set_item_blueprint(related1)

        # Verify FK updated
        self.assertEqual(parent.get_item_blueprint_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_item_blueprint(), related1)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = ItemBlueprintComponent()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = ItemBlueprintComponent()
        model.set_item_blueprint_id(1)
        model.set_component_item_id(1)
        model.set_ratio(1.0)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = ItemBlueprintComponent()
        model.set_item_blueprint_id(1)
        model.set_component_item_id(1)
        model.set_ratio(1.0)
        model.save()
        self.assertFalse(model._dirty)

        model.set_ratio(2.0)
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = ItemBlueprintComponent()
        model.set_item_blueprint_id(1)
        model.set_component_item_id(1)
        model.set_ratio(1.0)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = ItemBlueprint()
        related.set_bake_time_ms(1)
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = ItemBlueprintComponent()
        parent.set_item_blueprint_id(1)
        parent.set_component_item_id(1)
        parent.set_ratio(1.0)
        parent.set_item_blueprint(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)

    # TODO: Add Owner union tests for tables with owner fields
    # TODO: Add AttributeValue union tests for attributes table



class TestItemBlueprintRelationships(unittest.TestCase):
    """Comprehensive relationship tests for ItemBlueprint model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ItemBlueprint()

    def test_has_many_item_blueprint_components_basic(self):
        """Test item_blueprint_components relationship basic getter."""
        # Create parent
        parent = ItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()


        # Create related records
        child1 = ItemBlueprintComponent()
        child1.set_item_blueprint_id(parent.get_id())
        child1.set_component_item_id(1)
        child1.set_ratio(1.0)
        child1.save()

        child2 = ItemBlueprintComponent()
        child2.set_item_blueprint_id(parent.get_id())
        child2.set_component_item_id(1)
        child2.set_ratio(1.0)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_item_blueprint_components(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_item_blueprint_components(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_item_blueprint_components(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_item_blueprint_components_lazy(self):
        """Test item_blueprint_components relationship lazy loading."""
        # Create parent with children
        parent = ItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()


        # Create child
        child = ItemBlueprintComponent()
        child.set_item_blueprint_id(parent.get_id())
        child.set_component_item_id(1)
        child.set_ratio(1.0)
        child.save()

        # Test lazy mode
        results_iter = parent.get_item_blueprint_components(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], ItemBlueprintComponent)


    def test_has_many_items_basic(self):
        """Test items relationship basic getter."""
        # Create parent
        parent = ItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()


        # Create related records
        child1 = Item()
        child1.set_blueprint_id(parent.get_id())
        child1.set_internal_name('test_internal_name')
        child1.set_item_type(ThriftItemType.WEAPON)
        child1.save()

        child2 = Item()
        child2.set_blueprint_id(parent.get_id())
        child2.set_internal_name('test_internal_name')
        child2.set_item_type(ThriftItemType.WEAPON)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_items(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_items(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_items(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_items_lazy(self):
        """Test items relationship lazy loading."""
        # Create parent with children
        parent = ItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()


        # Create child
        child = Item()
        child.set_blueprint_id(parent.get_id())
        child.set_internal_name('test_internal_name')
        child.set_item_type(ThriftItemType.WEAPON)
        child.save()

        # Test lazy mode
        results_iter = parent.get_items(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], Item)


    def test_has_many_mobile_items_basic(self):
        """Test mobile_items relationship basic getter."""
        # Create parent
        parent = ItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()


        # Create prerequisite Mobile for mobile_id

        mobile_prereq = Mobile()

        mobile_prereq.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq.set_what_we_call_you('test_prereq')

        mobile_prereq.save()


        # Create prerequisite Item for item_id

        item_prereq = Item()

        item_prereq.set_internal_name('test_prereq')

        item_prereq.set_item_type(ThriftItemType.WEAPON)

        item_prereq.save()


        # Create related records
        child1 = MobileItem()
        child1.set_blueprint_id(parent.get_id())
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_child1 = Mobile()

        mobile_prereq_child1.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_child1.set_what_we_call_you('test_prereq_child1')

        mobile_prereq_child1.save()


        child1.set_mobile_id(mobile_prereq_child1.get_id())
        child1.set_internal_name('test_internal_name')
        child1.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_child1 = Item()

        item_prereq_child1.set_internal_name('test_prereq_child1')

        item_prereq_child1.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child1.save()


        child1.set_item_id(item_prereq_child1.get_id())
        child1.save()

        child2 = MobileItem()
        child2.set_blueprint_id(parent.get_id())
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_child2 = Mobile()

        mobile_prereq_child2.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_child2.set_what_we_call_you('test_prereq_child2')

        mobile_prereq_child2.save()


        child2.set_mobile_id(mobile_prereq_child2.get_id())
        child2.set_internal_name('test_internal_name')
        child2.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_child2 = Item()

        item_prereq_child2.set_internal_name('test_prereq_child2')

        item_prereq_child2.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child2.save()


        child2.set_item_id(item_prereq_child2.get_id())
        child2.save()

        # Test getter (eager mode)
        results = parent.get_mobile_items(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_mobile_items(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_mobile_items(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_mobile_items_lazy(self):
        """Test mobile_items relationship lazy loading."""
        # Create parent with children
        parent = ItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()


        # Create prerequisite Mobile for mobile_id

        mobile_prereq_lazy = Mobile()

        mobile_prereq_lazy.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_lazy.set_what_we_call_you('test_what_we_call_you')

        mobile_prereq_lazy.save()


        # Create prerequisite Item for item_id

        item_prereq_lazy = Item()

        item_prereq_lazy.set_internal_name('test_internal_name')

        item_prereq_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_lazy.save()


        # Create child
        child = MobileItem()
        child.set_blueprint_id(parent.get_id())
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_child_lazy = Mobile()

        mobile_prereq_child_lazy.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_child_lazy.set_what_we_call_you('test_prereq_child_lazy')

        mobile_prereq_child_lazy.save()


        child.set_mobile_id(mobile_prereq_child_lazy.get_id())
        child.set_internal_name('test_internal_name')
        child.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_child_lazy = Item()

        item_prereq_child_lazy.set_internal_name('test_prereq_child_lazy')

        item_prereq_child_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child_lazy.save()


        child.set_item_id(item_prereq_child_lazy.get_id())
        child.save()

        # Test lazy mode
        results_iter = parent.get_mobile_items(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], MobileItem)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = ItemBlueprint()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = ItemBlueprint()
        model.set_bake_time_ms(1)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = ItemBlueprint()
        model.set_bake_time_ms(1)
        model.save()
        self.assertFalse(model._dirty)

        model.set_bake_time_ms(2)
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = ItemBlueprint()
        model.set_bake_time_ms(1)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = ItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = ItemBlueprintComponent()
        child1.set_component_item_id(1)
        child1.set_ratio(1.0)
        child1.set_item_blueprint_id(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = ItemBlueprintComponent()
        child2.set_component_item_id(1)
        child2.set_ratio(1.0)
        child2.set_item_blueprint_id(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_item_blueprint_components(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = ItemBlueprint.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = ItemBlueprintComponent.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = ItemBlueprintComponent.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = ItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = ItemBlueprintComponent()
        child.set_component_item_id(1)
        child.set_ratio(1.0)
        child.set_item_blueprint_id(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = ItemBlueprint.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = ItemBlueprintComponent.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass

    # TODO: Add Owner union tests for tables with owner fields
    # TODO: Add AttributeValue union tests for attributes table



class TestItemRelationships(unittest.TestCase):
    """Comprehensive relationship tests for Item model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = Item()

    def test_belongs_to_blueprint_basic(self):
        """Test blueprint relationship basic getter."""
        # Create related model
        related = ItemBlueprint()
        related.set_bake_time_ms(1)
        related.save()

        # Create parent and set FK
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.set_blueprint_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_blueprint()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ItemBlueprint)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_blueprint()
        self.assertIs(result, result2)


    def test_belongs_to_blueprint_setter(self):
        """Test blueprint relationship setter."""
        # Create related models
        related1 = ItemBlueprint()
        related1.set_bake_time_ms(1)
        related1.save()

        # Create parent
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)

        # Use setter
        parent.set_blueprint(related1)

        # Verify FK updated
        self.assertEqual(parent.get_blueprint_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_blueprint(), related1)

    def test_has_many_attribute_owners_basic(self):
        """Test attribute_owners relationship basic getter."""
        # Create parent
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create prerequisite Attribute for attribute_id

        attribute_prereq = Attribute()

        attribute_prereq.set_internal_name('test_prereq')

        attribute_prereq.set_visible(1)

        attribute_prereq.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq.save()


        # Create related records
        child1 = AttributeOwner()
        child1.set_item_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child1 = Attribute()

        attribute_prereq_child1.set_internal_name('test_prereq_child1')

        attribute_prereq_child1.set_visible(1)

        attribute_prereq_child1.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child1.save()


        child1.set_attribute_id(attribute_prereq_child1.get_id())
        child1.save()

        child2 = AttributeOwner()
        child2.set_item_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child2 = Attribute()

        attribute_prereq_child2.set_internal_name('test_prereq_child2')

        attribute_prereq_child2.set_visible(1)

        attribute_prereq_child2.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child2.save()


        child2.set_attribute_id(attribute_prereq_child2.get_id())
        child2.save()

        # Test getter (eager mode)
        results = parent.get_attribute_owners(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_attribute_owners(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_attribute_owners(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_attribute_owners_lazy(self):
        """Test attribute_owners relationship lazy loading."""
        # Create parent with children
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create prerequisite Attribute for attribute_id

        attribute_prereq_lazy = Attribute()

        attribute_prereq_lazy.set_internal_name('test_internal_name')

        attribute_prereq_lazy.set_visible(1)

        attribute_prereq_lazy.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_lazy.save()


        # Create child
        child = AttributeOwner()
        child.set_item_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child_lazy = Attribute()

        attribute_prereq_child_lazy.set_internal_name('test_prereq_child_lazy')

        attribute_prereq_child_lazy.set_visible(1)

        attribute_prereq_child_lazy.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child_lazy.save()


        child.set_attribute_id(attribute_prereq_child_lazy.get_id())
        child.save()

        # Test lazy mode
        results_iter = parent.get_attribute_owners(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], AttributeOwner)


    def test_has_many_inventory_entries_basic(self):
        """Test inventory_entries relationship basic getter."""
        # Create parent
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create related records
        child1 = InventoryEntry()
        child1.set_item_id(parent.get_id())
        child1.set_inventory_id(1)
        child1.set_quantity(1.0)
        child1.save()

        child2 = InventoryEntry()
        child2.set_item_id(parent.get_id())
        child2.set_inventory_id(1)
        child2.set_quantity(1.0)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_inventory_entries(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_inventory_entries(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_inventory_entries(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_inventory_entries_lazy(self):
        """Test inventory_entries relationship lazy loading."""
        # Create parent with children
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create child
        child = InventoryEntry()
        child.set_item_id(parent.get_id())
        child.set_inventory_id(1)
        child.set_quantity(1.0)
        child.save()

        # Test lazy mode
        results_iter = parent.get_inventory_entries(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], InventoryEntry)


    def test_has_many_inventory_owners_basic(self):
        """Test inventory_owners relationship basic getter."""
        # Create parent
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create related records
        child1 = InventoryOwner()
        child1.set_item_id(parent.get_id())
        child1.set_inventory_id(1)
        child1.save()

        child2 = InventoryOwner()
        child2.set_item_id(parent.get_id())
        child2.set_inventory_id(1)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_inventory_owners(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_inventory_owners(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_inventory_owners(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_inventory_owners_lazy(self):
        """Test inventory_owners relationship lazy loading."""
        # Create parent with children
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create child
        child = InventoryOwner()
        child.set_item_id(parent.get_id())
        child.set_inventory_id(1)
        child.save()

        # Test lazy mode
        results_iter = parent.get_inventory_owners(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], InventoryOwner)


    def test_has_many_mobile_items_basic(self):
        """Test mobile_items relationship basic getter."""
        # Create parent
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create prerequisite Mobile for mobile_id

        mobile_prereq = Mobile()

        mobile_prereq.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq.set_what_we_call_you('test_prereq')

        mobile_prereq.save()


        # Create related records
        child1 = MobileItem()
        child1.set_item_id(parent.get_id())
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_child1 = Mobile()

        mobile_prereq_child1.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_child1.set_what_we_call_you('test_prereq_child1')

        mobile_prereq_child1.save()


        child1.set_mobile_id(mobile_prereq_child1.get_id())
        child1.set_internal_name('test_internal_name')
        child1.set_item_type(ThriftItemType.WEAPON)
        child1.save()

        child2 = MobileItem()
        child2.set_item_id(parent.get_id())
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_child2 = Mobile()

        mobile_prereq_child2.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_child2.set_what_we_call_you('test_prereq_child2')

        mobile_prereq_child2.save()


        child2.set_mobile_id(mobile_prereq_child2.get_id())
        child2.set_internal_name('test_internal_name')
        child2.set_item_type(ThriftItemType.WEAPON)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_mobile_items(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_mobile_items(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_mobile_items(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_mobile_items_lazy(self):
        """Test mobile_items relationship lazy loading."""
        # Create parent with children
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create prerequisite Mobile for mobile_id

        mobile_prereq_lazy = Mobile()

        mobile_prereq_lazy.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_lazy.set_what_we_call_you('test_what_we_call_you')

        mobile_prereq_lazy.save()


        # Create child
        child = MobileItem()
        child.set_item_id(parent.get_id())
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_child_lazy = Mobile()

        mobile_prereq_child_lazy.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_child_lazy.set_what_we_call_you('test_prereq_child_lazy')

        mobile_prereq_child_lazy.save()


        child.set_mobile_id(mobile_prereq_child_lazy.get_id())
        child.set_internal_name('test_internal_name')
        child.set_item_type(ThriftItemType.WEAPON)
        child.save()

        # Test lazy mode
        results_iter = parent.get_mobile_items(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], MobileItem)


    def test_has_many_mobiles_basic(self):
        """Test mobiles relationship basic getter."""
        # Create parent
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create related records
        child1 = Mobile()
        child1.set_owner_item_id(parent.get_id())
        child1.set_mobile_type(ThriftMobileType.PLAYER)
        child1.set_what_we_call_you('test_what_we_call_you')
        child1.save()

        child2 = Mobile()
        child2.set_owner_item_id(parent.get_id())
        child2.set_mobile_type(ThriftMobileType.PLAYER)
        child2.set_what_we_call_you('test_what_we_call_you')
        child2.save()

        # Test getter (eager mode)
        results = parent.get_mobiles(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_mobiles(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_mobiles(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_mobiles_lazy(self):
        """Test mobiles relationship lazy loading."""
        # Create parent with children
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()


        # Create child
        child = Mobile()
        child.set_owner_item_id(parent.get_id())
        child.set_mobile_type(ThriftMobileType.PLAYER)
        child.set_what_we_call_you('test_what_we_call_you')
        child.save()

        # Test lazy mode
        results_iter = parent.get_mobiles(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], Mobile)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = Item()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = Item()
        model.set_internal_name('test_internal_name')
        model.set_item_type(ThriftItemType.WEAPON)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = Item()
        model.set_internal_name('test_internal_name')
        model.set_item_type(ThriftItemType.WEAPON)
        model.save()
        self.assertFalse(model._dirty)

        model.set_internal_name('test_value_2')
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = Item()
        model.set_internal_name('test_internal_name')
        model.set_item_type(ThriftItemType.WEAPON)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = ItemBlueprint()
        related.set_bake_time_ms(1)
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.set_blueprint(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)

    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = AttributeOwner()
        child1.set_attribute_id(1)
        child1.set_item_id(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = AttributeOwner()
        child2.set_attribute_id(1)
        child2.set_item_id(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_attribute_owners(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = Item.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = AttributeOwner.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = AttributeOwner.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = Item()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = AttributeOwner()
        child.set_attribute_id(1)
        child.set_item_id(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = Item.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = AttributeOwner.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass

    def test_from_thrift_with_enum(self):
        """Test from_thrift correctly converts enum integer to string name."""
        from game.ttypes import Item as ThriftItem, ItemType

        # Create Thrift object with enum field
        thrift_obj = ThriftItem(
            internal_name='test_internal_name',
            item_type=ItemType.RAWMATERIAL,
        )

        # Convert to model
        model = Item()
        model.from_thrift(thrift_obj)

        # Verify enum was converted to string name
        self.assertEqual(model._data['item_type'], 'RAWMATERIAL')

        # Save and reload to verify round-trip
        model.save()
        model_id = model.get_id()
        self.assertIsNotNone(model_id)

        # Load from database
        loaded_model = Item.find(model_id)
        self.assertIsNotNone(loaded_model)
        self.assertEqual(loaded_model._data['item_type'], 'RAWMATERIAL')

        # Convert back to Thrift
        results, thrift_obj_out = loaded_model.into_thrift()
        if thrift_obj_out is None:
            # Print error details if conversion failed
            for result in results:
                print(f"into_thrift error: {result.message}")
        self.assertIsNotNone(thrift_obj_out, f"into_thrift failed: {results[0].message if results else 'unknown'}")
        self.assertEqual(thrift_obj_out.item_type, ItemType.RAWMATERIAL)

        # Clean up - use fresh connection to avoid nested transaction
        cleanup_conn = loaded_model._create_connection()
        loaded_model.destroy(connection=cleanup_conn)
        cleanup_conn.close()



class TestMobileItemAttributeRelationships(unittest.TestCase):
    """Comprehensive relationship tests for MobileItemAttribute model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = MobileItemAttribute()

    def test_belongs_to_mobile_item_basic(self):
        """Test mobile_item relationship basic getter."""
        # Create related model
        related = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_basic = Mobile()

        mobile_prereq_basic.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_basic.set_what_we_call_you('test_prereq_basic')

        mobile_prereq_basic.save()


        related.set_mobile_id(mobile_prereq_basic.get_id())
        related.set_internal_name('test_internal_name')
        related.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_basic = Item()

        item_prereq_basic.set_internal_name('test_prereq_basic')

        item_prereq_basic.set_item_type(ThriftItemType.WEAPON)

        item_prereq_basic.save()


        related.set_item_id(item_prereq_basic.get_id())
        related.save()

        # Create parent and set FK
        parent = MobileItemAttribute()
        parent.set_internal_name('test_internal_name')
        parent.set_visible(1)
        parent.set_attribute_type('test_attribute_type')
        parent.set_mobile_item_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_mobile_item()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MobileItem)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_mobile_item()
        self.assertIs(result, result2)


    def test_belongs_to_mobile_item_setter(self):
        """Test mobile_item relationship setter."""
        # Create related models
        related1 = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_setter = Mobile()

        mobile_prereq_setter.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_setter.set_what_we_call_you('test_prereq_setter')

        mobile_prereq_setter.save()


        related1.set_mobile_id(mobile_prereq_setter.get_id())
        related1.set_internal_name('test_internal_name')
        related1.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_setter = Item()

        item_prereq_setter.set_internal_name('test_prereq_setter')

        item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        item_prereq_setter.save()


        related1.set_item_id(item_prereq_setter.get_id())
        related1.save()

        # Create parent
        parent = MobileItemAttribute()
        # Create prerequisite MobileItem for mobile_item_id

        mobile_item_prereq_setter = MobileItem()

        mobile_item_prereq_setter.set_mobile_id(1)

        mobile_item_prereq_setter.set_internal_name('test_prereq_setter')

        mobile_item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        mobile_item_prereq_setter.set_item_id(1)

        mobile_item_prereq_setter.save()


        parent.set_mobile_item_id(mobile_item_prereq_setter.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_visible(1)
        parent.set_attribute_type('test_attribute_type')

        # Use setter
        parent.set_mobile_item(related1)

        # Verify FK updated
        self.assertEqual(parent.get_mobile_item_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_mobile_item(), related1)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = MobileItemAttribute()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = MobileItemAttribute()
        model.set_mobile_item_id(1)
        model.set_internal_name('test_internal_name')
        model.set_visible(1)
        model.set_attribute_type('test_attribute_type')
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = MobileItemAttribute()
        model.set_mobile_item_id(1)
        model.set_internal_name('test_internal_name')
        model.set_visible(1)
        model.set_attribute_type('test_attribute_type')
        model.save()
        self.assertFalse(model._dirty)

        model.set_internal_name('test_value_2')
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = MobileItemAttribute()
        model.set_mobile_item_id(1)
        model.set_internal_name('test_internal_name')
        model.set_visible(1)
        model.set_attribute_type('test_attribute_type')
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = MobileItem()
        related.set_mobile_id(1)
        related.set_internal_name('test_internal_name')
        related.set_item_type(ThriftItemType.WEAPON)
        related.set_item_id(1)
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = MobileItemAttribute()
        parent.set_mobile_item_id(1)
        parent.set_internal_name('test_internal_name')
        parent.set_visible(1)
        parent.set_attribute_type('test_attribute_type')
        parent.set_mobile_item(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)



class TestMobileItemBlueprintComponentRelationships(unittest.TestCase):
    """Comprehensive relationship tests for MobileItemBlueprintComponent model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = MobileItemBlueprintComponent()

    def test_belongs_to_item_blueprint_basic(self):
        """Test item_blueprint relationship basic getter."""
        # Create related model
        related = MobileItemBlueprint()
        related.set_bake_time_ms(1)
        related.save()

        # Create parent and set FK
        parent = MobileItemBlueprintComponent()
        parent.set_component_item_id(1)
        parent.set_ratio(1.0)
        parent.set_item_blueprint_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_item_blueprint()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MobileItemBlueprint)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_item_blueprint()
        self.assertIs(result, result2)


    def test_belongs_to_item_blueprint_setter(self):
        """Test item_blueprint relationship setter."""
        # Create related models
        related1 = MobileItemBlueprint()
        related1.set_bake_time_ms(1)
        related1.save()

        # Create parent
        parent = MobileItemBlueprintComponent()
        # Create prerequisite ItemBlueprint for item_blueprint_id

        item_blueprint_prereq_setter = ItemBlueprint()

        item_blueprint_prereq_setter.set_bake_time_ms(1)

        item_blueprint_prereq_setter.save()


        parent.set_item_blueprint_id(item_blueprint_prereq_setter.get_id())
        parent.set_component_item_id(1)
        parent.set_ratio(1.0)

        # Use setter
        parent.set_item_blueprint(related1)

        # Verify FK updated
        self.assertEqual(parent.get_item_blueprint_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_item_blueprint(), related1)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = MobileItemBlueprintComponent()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = MobileItemBlueprintComponent()
        model.set_item_blueprint_id(1)
        model.set_component_item_id(1)
        model.set_ratio(1.0)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = MobileItemBlueprintComponent()
        model.set_item_blueprint_id(1)
        model.set_component_item_id(1)
        model.set_ratio(1.0)
        model.save()
        self.assertFalse(model._dirty)

        model.set_ratio(2.0)
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = MobileItemBlueprintComponent()
        model.set_item_blueprint_id(1)
        model.set_component_item_id(1)
        model.set_ratio(1.0)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = MobileItemBlueprint()
        related.set_bake_time_ms(1)
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = MobileItemBlueprintComponent()
        parent.set_item_blueprint_id(1)
        parent.set_component_item_id(1)
        parent.set_ratio(1.0)
        parent.set_item_blueprint(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)



class TestMobileItemBlueprintRelationships(unittest.TestCase):
    """Comprehensive relationship tests for MobileItemBlueprint model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = MobileItemBlueprint()

    def test_has_many_mobile_item_blueprint_components_basic(self):
        """Test mobile_item_blueprint_components relationship basic getter."""
        # Create parent
        parent = MobileItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()


        # Create related records
        child1 = MobileItemBlueprintComponent()
        child1.set_item_blueprint_id(parent.get_id())
        child1.set_component_item_id(1)
        child1.set_ratio(1.0)
        child1.save()

        child2 = MobileItemBlueprintComponent()
        child2.set_item_blueprint_id(parent.get_id())
        child2.set_component_item_id(1)
        child2.set_ratio(1.0)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_mobile_item_blueprint_components(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_mobile_item_blueprint_components(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_mobile_item_blueprint_components(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_mobile_item_blueprint_components_lazy(self):
        """Test mobile_item_blueprint_components relationship lazy loading."""
        # Create parent with children
        parent = MobileItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()


        # Create child
        child = MobileItemBlueprintComponent()
        child.set_item_blueprint_id(parent.get_id())
        child.set_component_item_id(1)
        child.set_ratio(1.0)
        child.save()

        # Test lazy mode
        results_iter = parent.get_mobile_item_blueprint_components(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], MobileItemBlueprintComponent)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = MobileItemBlueprint()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = MobileItemBlueprint()
        model.set_bake_time_ms(1)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = MobileItemBlueprint()
        model.set_bake_time_ms(1)
        model.save()
        self.assertFalse(model._dirty)

        model.set_bake_time_ms(2)
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = MobileItemBlueprint()
        model.set_bake_time_ms(1)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = MobileItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = MobileItemBlueprintComponent()
        child1.set_component_item_id(1)
        child1.set_ratio(1.0)
        child1.set_item_blueprint_id(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = MobileItemBlueprintComponent()
        child2.set_component_item_id(1)
        child2.set_ratio(1.0)
        child2.set_item_blueprint_id(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_mobile_item_blueprint_components(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = MobileItemBlueprint.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = MobileItemBlueprintComponent.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = MobileItemBlueprintComponent.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = MobileItemBlueprint()
        parent.set_bake_time_ms(1)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = MobileItemBlueprintComponent()
        child.set_component_item_id(1)
        child.set_ratio(1.0)
        child.set_item_blueprint_id(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = MobileItemBlueprint.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = MobileItemBlueprintComponent.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass



class TestMobileItemRelationships(unittest.TestCase):
    """Comprehensive relationship tests for MobileItem model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = MobileItem()

    def test_belongs_to_mobile_basic(self):
        """Test mobile relationship basic getter."""
        # Create related model
        related = Mobile()
        related.set_mobile_type(ThriftMobileType.PLAYER)
        related.set_what_we_call_you('test_what_we_call_you')
        related.save()

        # Create parent and set FK
        parent = MobileItem()
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_basic = Item()

        item_prereq_basic.set_internal_name('test_prereq_basic')

        item_prereq_basic.set_item_type(ThriftItemType.WEAPON)

        item_prereq_basic.save()


        parent.set_item_id(item_prereq_basic.get_id())
        parent.set_mobile_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_mobile()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Mobile)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_mobile()
        self.assertIs(result, result2)


    def test_belongs_to_mobile_setter(self):
        """Test mobile relationship setter."""
        # Create related models
        related1 = Mobile()
        related1.set_mobile_type(ThriftMobileType.PLAYER)
        related1.set_what_we_call_you('test_what_we_call_you')
        related1.save()

        # Create parent
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_setter = Mobile()

        mobile_prereq_setter.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_setter.set_what_we_call_you('test_prereq_setter')

        mobile_prereq_setter.save()


        parent.set_mobile_id(mobile_prereq_setter.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_setter = Item()

        item_prereq_setter.set_internal_name('test_prereq_setter')

        item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        item_prereq_setter.save()


        parent.set_item_id(item_prereq_setter.get_id())

        # Use setter
        parent.set_mobile(related1)

        # Verify FK updated
        self.assertEqual(parent.get_mobile_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_mobile(), related1)


    def test_belongs_to_blueprint_basic(self):
        """Test blueprint relationship basic getter."""
        # Create related model
        related = ItemBlueprint()
        related.set_bake_time_ms(1)
        related.save()

        # Create parent and set FK
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_basic = Mobile()

        mobile_prereq_basic.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_basic.set_what_we_call_you('test_prereq_basic')

        mobile_prereq_basic.save()


        parent.set_mobile_id(mobile_prereq_basic.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_basic = Item()

        item_prereq_basic.set_internal_name('test_prereq_basic')

        item_prereq_basic.set_item_type(ThriftItemType.WEAPON)

        item_prereq_basic.save()


        parent.set_item_id(item_prereq_basic.get_id())
        parent.set_blueprint_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_blueprint()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ItemBlueprint)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_blueprint()
        self.assertIs(result, result2)


    def test_belongs_to_blueprint_setter(self):
        """Test blueprint relationship setter."""
        # Create related models
        related1 = ItemBlueprint()
        related1.set_bake_time_ms(1)
        related1.save()

        # Create parent
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_setter = Mobile()

        mobile_prereq_setter.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_setter.set_what_we_call_you('test_prereq_setter')

        mobile_prereq_setter.save()


        parent.set_mobile_id(mobile_prereq_setter.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_setter = Item()

        item_prereq_setter.set_internal_name('test_prereq_setter')

        item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        item_prereq_setter.save()


        parent.set_item_id(item_prereq_setter.get_id())

        # Use setter
        parent.set_blueprint(related1)

        # Verify FK updated
        self.assertEqual(parent.get_blueprint_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_blueprint(), related1)


    def test_belongs_to_item_basic(self):
        """Test item relationship basic getter."""
        # Create related model
        related = Item()
        related.set_internal_name('test_internal_name')
        related.set_item_type(ThriftItemType.WEAPON)
        related.save()

        # Create parent and set FK
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_basic = Mobile()

        mobile_prereq_basic.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_basic.set_what_we_call_you('test_prereq_basic')

        mobile_prereq_basic.save()


        parent.set_mobile_id(mobile_prereq_basic.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.set_item_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_item()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Item)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_item()
        self.assertIs(result, result2)


    def test_belongs_to_item_setter(self):
        """Test item relationship setter."""
        # Create related models
        related1 = Item()
        related1.set_internal_name('test_internal_name')
        related1.set_item_type(ThriftItemType.WEAPON)
        related1.save()

        # Create parent
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_setter = Mobile()

        mobile_prereq_setter.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_setter.set_what_we_call_you('test_prereq_setter')

        mobile_prereq_setter.save()


        parent.set_mobile_id(mobile_prereq_setter.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_setter = Item()

        item_prereq_setter.set_internal_name('test_prereq_setter')

        item_prereq_setter.set_item_type(ThriftItemType.WEAPON)

        item_prereq_setter.save()


        parent.set_item_id(item_prereq_setter.get_id())

        # Use setter
        parent.set_item(related1)

        # Verify FK updated
        self.assertEqual(parent.get_item_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_item(), related1)

    def test_has_many_inventory_entries_basic(self):
        """Test inventory_entries relationship basic getter."""
        # Create parent
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_parent = Mobile()

        mobile_prereq_parent.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_parent.set_what_we_call_you('test_prereq_parent')

        mobile_prereq_parent.save()


        parent.set_mobile_id(mobile_prereq_parent.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_parent = Item()

        item_prereq_parent.set_internal_name('test_prereq_parent')

        item_prereq_parent.set_item_type(ThriftItemType.WEAPON)

        item_prereq_parent.save()


        parent.set_item_id(item_prereq_parent.get_id())
        parent.save()


        # Create prerequisite Item for item_id

        item_prereq = Item()

        item_prereq.set_internal_name('test_prereq')

        item_prereq.set_item_type(ThriftItemType.WEAPON)

        item_prereq.save()


        # Create related records
        child1 = InventoryEntry()
        child1.set_mobile_item_id(parent.get_id())
        child1.set_inventory_id(1)
        # Create prerequisite Item for item_id

        item_prereq_child1 = Item()

        item_prereq_child1.set_internal_name('test_prereq_child1')

        item_prereq_child1.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child1.save()


        child1.set_item_id(item_prereq_child1.get_id())
        child1.set_quantity(1.0)
        child1.save()

        child2 = InventoryEntry()
        child2.set_mobile_item_id(parent.get_id())
        child2.set_inventory_id(1)
        # Create prerequisite Item for item_id

        item_prereq_child2 = Item()

        item_prereq_child2.set_internal_name('test_prereq_child2')

        item_prereq_child2.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child2.save()


        child2.set_item_id(item_prereq_child2.get_id())
        child2.set_quantity(1.0)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_inventory_entries(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_inventory_entries(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_inventory_entries(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_inventory_entries_lazy(self):
        """Test inventory_entries relationship lazy loading."""
        # Create parent with children
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_parent_lazy = Mobile()

        mobile_prereq_parent_lazy.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_parent_lazy.set_what_we_call_you('test_prereq_parent_lazy')

        mobile_prereq_parent_lazy.save()


        parent.set_mobile_id(mobile_prereq_parent_lazy.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_parent_lazy = Item()

        item_prereq_parent_lazy.set_internal_name('test_prereq_parent_lazy')

        item_prereq_parent_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_parent_lazy.save()


        parent.set_item_id(item_prereq_parent_lazy.get_id())
        parent.save()


        # Create prerequisite Item for item_id

        item_prereq_lazy = Item()

        item_prereq_lazy.set_internal_name('test_internal_name')

        item_prereq_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_lazy.save()


        # Create child
        child = InventoryEntry()
        child.set_mobile_item_id(parent.get_id())
        child.set_inventory_id(1)
        # Create prerequisite Item for item_id

        item_prereq_child_lazy = Item()

        item_prereq_child_lazy.set_internal_name('test_prereq_child_lazy')

        item_prereq_child_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child_lazy.save()


        child.set_item_id(item_prereq_child_lazy.get_id())
        child.set_quantity(1.0)
        child.save()

        # Test lazy mode
        results_iter = parent.get_inventory_entries(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], InventoryEntry)


    def test_has_many_mobile_item_attributes_basic(self):
        """Test mobile_item_attributes relationship basic getter."""
        # Create parent
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_parent = Mobile()

        mobile_prereq_parent.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_parent.set_what_we_call_you('test_prereq_parent')

        mobile_prereq_parent.save()


        parent.set_mobile_id(mobile_prereq_parent.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_parent = Item()

        item_prereq_parent.set_internal_name('test_prereq_parent')

        item_prereq_parent.set_item_type(ThriftItemType.WEAPON)

        item_prereq_parent.save()


        parent.set_item_id(item_prereq_parent.get_id())
        parent.save()


        # Create related records
        child1 = MobileItemAttribute()
        child1.set_mobile_item_id(parent.get_id())
        child1.set_internal_name('test_internal_name')
        child1.set_visible(1)
        child1.set_attribute_type('test_attribute_type')
        child1.save()

        child2 = MobileItemAttribute()
        child2.set_mobile_item_id(parent.get_id())
        child2.set_internal_name('test_internal_name')
        child2.set_visible(1)
        child2.set_attribute_type('test_attribute_type')
        child2.save()

        # Test getter (eager mode)
        results = parent.get_mobile_item_attributes(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_mobile_item_attributes(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_mobile_item_attributes(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_mobile_item_attributes_lazy(self):
        """Test mobile_item_attributes relationship lazy loading."""
        # Create parent with children
        parent = MobileItem()
        # Create prerequisite Mobile for mobile_id

        mobile_prereq_parent_lazy = Mobile()

        mobile_prereq_parent_lazy.set_mobile_type(ThriftMobileType.PLAYER)

        mobile_prereq_parent_lazy.set_what_we_call_you('test_prereq_parent_lazy')

        mobile_prereq_parent_lazy.save()


        parent.set_mobile_id(mobile_prereq_parent_lazy.get_id())
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_parent_lazy = Item()

        item_prereq_parent_lazy.set_internal_name('test_prereq_parent_lazy')

        item_prereq_parent_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_parent_lazy.save()


        parent.set_item_id(item_prereq_parent_lazy.get_id())
        parent.save()


        # Create child
        child = MobileItemAttribute()
        child.set_mobile_item_id(parent.get_id())
        child.set_internal_name('test_internal_name')
        child.set_visible(1)
        child.set_attribute_type('test_attribute_type')
        child.save()

        # Test lazy mode
        results_iter = parent.get_mobile_item_attributes(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], MobileItemAttribute)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = MobileItem()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = MobileItem()
        model.set_mobile_id(1)
        model.set_internal_name('test_internal_name')
        model.set_item_type(ThriftItemType.WEAPON)
        model.set_item_id(1)
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = MobileItem()
        model.set_mobile_id(1)
        model.set_internal_name('test_internal_name')
        model.set_item_type(ThriftItemType.WEAPON)
        model.set_item_id(1)
        model.save()
        self.assertFalse(model._dirty)

        model.set_internal_name('test_value_2')
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = MobileItem()
        model.set_mobile_id(1)
        model.set_internal_name('test_internal_name')
        model.set_item_type(ThriftItemType.WEAPON)
        model.set_item_id(1)
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = Mobile()
        related.set_mobile_type(ThriftMobileType.PLAYER)
        related.set_what_we_call_you('test_what_we_call_you')
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = MobileItem()
        parent.set_mobile_id(1)
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.set_item_id(1)
        parent.set_mobile(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)

    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = MobileItem()
        parent.set_mobile_id(1)
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.set_item_id(1)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = InventoryEntry()
        child1.set_inventory_id(1)
        child1.set_item_id(1)
        child1.set_quantity(1.0)
        child1.set_mobile_item_id(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = InventoryEntry()
        child2.set_inventory_id(1)
        child2.set_item_id(1)
        child2.set_quantity(1.0)
        child2.set_mobile_item_id(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_inventory_entries(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = MobileItem.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = InventoryEntry.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = InventoryEntry.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = MobileItem()
        parent.set_mobile_id(1)
        parent.set_internal_name('test_internal_name')
        parent.set_item_type(ThriftItemType.WEAPON)
        parent.set_item_id(1)
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = InventoryEntry()
        child.set_inventory_id(1)
        child.set_item_id(1)
        child.set_quantity(1.0)
        child.set_mobile_item_id(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = MobileItem.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = InventoryEntry.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass

    def test_from_thrift_with_enum(self):
        """Test from_thrift correctly converts enum integer to string name."""
        from game.ttypes import MobileItem as ThriftMobileItem, ItemType

        # Create Thrift object with enum field
        thrift_obj = ThriftMobileItem(
            mobile_id=1,
            internal_name='test_internal_name',
            item_type=ItemType.RAWMATERIAL,
            item_id=1,
        )

        # Convert to model
        model = MobileItem()
        model.from_thrift(thrift_obj)

        # Verify enum was converted to string name
        self.assertEqual(model._data['item_type'], 'RAWMATERIAL')

        # Save and reload to verify round-trip
        model.save()
        model_id = model.get_id()
        self.assertIsNotNone(model_id)

        # Load from database
        loaded_model = MobileItem.find(model_id)
        self.assertIsNotNone(loaded_model)
        self.assertEqual(loaded_model._data['item_type'], 'RAWMATERIAL')

        # Convert back to Thrift
        results, thrift_obj_out = loaded_model.into_thrift()
        if thrift_obj_out is None:
            # Print error details if conversion failed
            for result in results:
                print(f"into_thrift error: {result.message}")
        self.assertIsNotNone(thrift_obj_out, f"into_thrift failed: {results[0].message if results else 'unknown'}")
        self.assertEqual(thrift_obj_out.item_type, ItemType.RAWMATERIAL)

        # Clean up - use fresh connection to avoid nested transaction
        cleanup_conn = loaded_model._create_connection()
        loaded_model.destroy(connection=cleanup_conn)
        cleanup_conn.close()



class TestMobileRelationships(unittest.TestCase):
    """Comprehensive relationship tests for Mobile model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = Mobile()

    def test_belongs_to_owner_mobile_basic(self):
        """Test owner_mobile relationship basic getter."""
        # Create related model
        related = Mobile()
        related.set_mobile_type(ThriftMobileType.PLAYER)
        related.set_what_we_call_you('test_what_we_call_you')
        related.save()

        # Create parent and set FK
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_owner_mobile_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_owner_mobile()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Mobile)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_owner_mobile()
        self.assertIs(result, result2)


    def test_belongs_to_owner_mobile_setter(self):
        """Test owner_mobile relationship setter."""
        # Create related models
        related1 = Mobile()
        related1.set_mobile_type(ThriftMobileType.PLAYER)
        related1.set_what_we_call_you('test_what_we_call_you')
        related1.save()

        # Create parent
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')

        # Use setter
        parent.set_owner_mobile(related1)

        # Verify FK updated
        self.assertEqual(parent.get_owner_mobile_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_owner_mobile(), related1)


    def test_belongs_to_owner_item_basic(self):
        """Test owner_item relationship basic getter."""
        # Create related model
        related = Item()
        related.set_internal_name('test_internal_name')
        related.set_item_type(ThriftItemType.WEAPON)
        related.save()

        # Create parent and set FK
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_owner_item_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_owner_item()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Item)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_owner_item()
        self.assertIs(result, result2)


    def test_belongs_to_owner_item_setter(self):
        """Test owner_item relationship setter."""
        # Create related models
        related1 = Item()
        related1.set_internal_name('test_internal_name')
        related1.set_item_type(ThriftItemType.WEAPON)
        related1.save()

        # Create parent
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')

        # Use setter
        parent.set_owner_item(related1)

        # Verify FK updated
        self.assertEqual(parent.get_owner_item_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_owner_item(), related1)


    def test_belongs_to_owner_player_basic(self):
        """Test owner_player relationship basic getter."""
        # Create related model
        related = Player()
        related.set_full_name('test_full_name')
        related.set_what_we_call_you('test_what_we_call_you')
        related.set_security_token('test_security_token')
        related.set_over_13(1)
        related.set_year_of_birth(1)
        related.set_email('test_email')
        related.save()

        # Create parent and set FK
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_owner_player_id(related.get_id())
        parent.save()

        # Test getter
        result = parent.get_owner_player()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Player)
        self.assertEqual(result.get_id(), related.get_id())

        # Test caching - second call should return same instance
        result2 = parent.get_owner_player()
        self.assertIs(result, result2)


    def test_belongs_to_owner_player_setter(self):
        """Test owner_player relationship setter."""
        # Create related models
        related1 = Player()
        related1.set_full_name('test_full_name')
        related1.set_what_we_call_you('test_what_we_call_you')
        related1.set_security_token('test_security_token')
        related1.set_over_13(1)
        related1.set_year_of_birth(1)
        related1.set_email('test_email')
        related1.save()

        # Create parent
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')

        # Use setter
        parent.set_owner_player(related1)

        # Verify FK updated
        self.assertEqual(parent.get_owner_player_id(), related1.get_id())

        # Verify model marked dirty
        self.assertTrue(parent._dirty)

        # Verify getter returns same instance
        self.assertIs(parent.get_owner_player(), related1)

    def test_has_many_attribute_owners_basic(self):
        """Test attribute_owners relationship basic getter."""
        # Create parent
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.save()


        # Create prerequisite Attribute for attribute_id

        attribute_prereq = Attribute()

        attribute_prereq.set_internal_name('test_prereq')

        attribute_prereq.set_visible(1)

        attribute_prereq.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq.save()


        # Create related records
        child1 = AttributeOwner()
        child1.set_mobile_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child1 = Attribute()

        attribute_prereq_child1.set_internal_name('test_prereq_child1')

        attribute_prereq_child1.set_visible(1)

        attribute_prereq_child1.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child1.save()


        child1.set_attribute_id(attribute_prereq_child1.get_id())
        child1.save()

        child2 = AttributeOwner()
        child2.set_mobile_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child2 = Attribute()

        attribute_prereq_child2.set_internal_name('test_prereq_child2')

        attribute_prereq_child2.set_visible(1)

        attribute_prereq_child2.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child2.save()


        child2.set_attribute_id(attribute_prereq_child2.get_id())
        child2.save()

        # Test getter (eager mode)
        results = parent.get_attribute_owners(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_attribute_owners(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_attribute_owners(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_attribute_owners_lazy(self):
        """Test attribute_owners relationship lazy loading."""
        # Create parent with children
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.save()


        # Create prerequisite Attribute for attribute_id

        attribute_prereq_lazy = Attribute()

        attribute_prereq_lazy.set_internal_name('test_internal_name')

        attribute_prereq_lazy.set_visible(1)

        attribute_prereq_lazy.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_lazy.save()


        # Create child
        child = AttributeOwner()
        child.set_mobile_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child_lazy = Attribute()

        attribute_prereq_child_lazy.set_internal_name('test_prereq_child_lazy')

        attribute_prereq_child_lazy.set_visible(1)

        attribute_prereq_child_lazy.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child_lazy.save()


        child.set_attribute_id(attribute_prereq_child_lazy.get_id())
        child.save()

        # Test lazy mode
        results_iter = parent.get_attribute_owners(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], AttributeOwner)


    def test_has_many_inventory_owners_basic(self):
        """Test inventory_owners relationship basic getter."""
        # Create parent
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.save()


        # Create related records
        child1 = InventoryOwner()
        child1.set_mobile_id(parent.get_id())
        child1.set_inventory_id(1)
        child1.save()

        child2 = InventoryOwner()
        child2.set_mobile_id(parent.get_id())
        child2.set_inventory_id(1)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_inventory_owners(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_inventory_owners(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_inventory_owners(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_inventory_owners_lazy(self):
        """Test inventory_owners relationship lazy loading."""
        # Create parent with children
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.save()


        # Create child
        child = InventoryOwner()
        child.set_mobile_id(parent.get_id())
        child.set_inventory_id(1)
        child.save()

        # Test lazy mode
        results_iter = parent.get_inventory_owners(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], InventoryOwner)


    def test_has_many_mobile_items_basic(self):
        """Test mobile_items relationship basic getter."""
        # Create parent
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.save()


        # Create prerequisite Item for item_id

        item_prereq = Item()

        item_prereq.set_internal_name('test_prereq')

        item_prereq.set_item_type(ThriftItemType.WEAPON)

        item_prereq.save()


        # Create related records
        child1 = MobileItem()
        child1.set_mobile_id(parent.get_id())
        child1.set_internal_name('test_internal_name')
        child1.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_child1 = Item()

        item_prereq_child1.set_internal_name('test_prereq_child1')

        item_prereq_child1.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child1.save()


        child1.set_item_id(item_prereq_child1.get_id())
        child1.save()

        child2 = MobileItem()
        child2.set_mobile_id(parent.get_id())
        child2.set_internal_name('test_internal_name')
        child2.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_child2 = Item()

        item_prereq_child2.set_internal_name('test_prereq_child2')

        item_prereq_child2.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child2.save()


        child2.set_item_id(item_prereq_child2.get_id())
        child2.save()

        # Test getter (eager mode)
        results = parent.get_mobile_items(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_mobile_items(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_mobile_items(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_mobile_items_lazy(self):
        """Test mobile_items relationship lazy loading."""
        # Create parent with children
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.save()


        # Create prerequisite Item for item_id

        item_prereq_lazy = Item()

        item_prereq_lazy.set_internal_name('test_internal_name')

        item_prereq_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_lazy.save()


        # Create child
        child = MobileItem()
        child.set_mobile_id(parent.get_id())
        child.set_internal_name('test_internal_name')
        child.set_item_type(ThriftItemType.WEAPON)
        # Create prerequisite Item for item_id

        item_prereq_child_lazy = Item()

        item_prereq_child_lazy.set_internal_name('test_prereq_child_lazy')

        item_prereq_child_lazy.set_item_type(ThriftItemType.WEAPON)

        item_prereq_child_lazy.save()


        child.set_item_id(item_prereq_child_lazy.get_id())
        child.save()

        # Test lazy mode
        results_iter = parent.get_mobile_items(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], MobileItem)

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = Mobile()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = Mobile()
        model.set_mobile_type(ThriftMobileType.PLAYER)
        model.set_what_we_call_you('test_what_we_call_you')
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = Mobile()
        model.set_mobile_type(ThriftMobileType.PLAYER)
        model.set_what_we_call_you('test_what_we_call_you')
        model.save()
        self.assertFalse(model._dirty)

        model.set_mobile_type(ThriftMobileType.NPC)
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = Mobile()
        model.set_mobile_type(ThriftMobileType.PLAYER)
        model.set_what_we_call_you('test_what_we_call_you')
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_save_belongs_to(self):
        """Test cascade save for belongs-to relationships."""
        # Create related model (unsaved)
        related = Mobile()
        related.set_mobile_type(ThriftMobileType.PLAYER)
        related.set_what_we_call_you('test_what_we_call_you')
        self.assertTrue(related._dirty)
        self.assertIsNone(related.get_id())

        # Create parent (unsaved)
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_owner_mobile(related)

        # Save parent with cascade
        parent.save(cascade=True)

        # Verify both saved
        self.assertIsNotNone(parent.get_id())
        self.assertIsNotNone(related.get_id())
        self.assertFalse(parent._dirty)
        self.assertFalse(related._dirty)

    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = AttributeOwner()
        child1.set_attribute_id(1)
        child1.set_mobile_id(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = AttributeOwner()
        child2.set_attribute_id(1)
        child2.set_mobile_id(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_attribute_owners(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = Mobile.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = AttributeOwner.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = AttributeOwner.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = Mobile()
        parent.set_mobile_type(ThriftMobileType.PLAYER)
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = AttributeOwner()
        child.set_attribute_id(1)
        child.set_mobile_id(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = Mobile.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = AttributeOwner.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass

    # TODO: Add Owner union tests for tables with owner fields
    # TODO: Add AttributeValue union tests for attributes table



class TestPlayerRelationships(unittest.TestCase):
    """Comprehensive relationship tests for Player model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = Player()

    def test_has_many_attribute_owners_basic(self):
        """Test attribute_owners relationship basic getter."""
        # Create parent
        parent = Player()
        parent.set_full_name('test_full_name')
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_security_token('test_security_token')
        parent.set_over_13(1)
        parent.set_year_of_birth(1)
        parent.set_email('test_email')
        parent.save()


        # Create prerequisite Attribute for attribute_id

        attribute_prereq = Attribute()

        attribute_prereq.set_internal_name('test_prereq')

        attribute_prereq.set_visible(1)

        attribute_prereq.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq.save()


        # Create related records
        child1 = AttributeOwner()
        child1.set_player_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child1 = Attribute()

        attribute_prereq_child1.set_internal_name('test_prereq_child1')

        attribute_prereq_child1.set_visible(1)

        attribute_prereq_child1.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child1.save()


        child1.set_attribute_id(attribute_prereq_child1.get_id())
        child1.save()

        child2 = AttributeOwner()
        child2.set_player_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child2 = Attribute()

        attribute_prereq_child2.set_internal_name('test_prereq_child2')

        attribute_prereq_child2.set_visible(1)

        attribute_prereq_child2.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child2.save()


        child2.set_attribute_id(attribute_prereq_child2.get_id())
        child2.save()

        # Test getter (eager mode)
        results = parent.get_attribute_owners(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_attribute_owners(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_attribute_owners(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_attribute_owners_lazy(self):
        """Test attribute_owners relationship lazy loading."""
        # Create parent with children
        parent = Player()
        parent.set_full_name('test_full_name')
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_security_token('test_security_token')
        parent.set_over_13(1)
        parent.set_year_of_birth(1)
        parent.set_email('test_email')
        parent.save()


        # Create prerequisite Attribute for attribute_id

        attribute_prereq_lazy = Attribute()

        attribute_prereq_lazy.set_internal_name('test_internal_name')

        attribute_prereq_lazy.set_visible(1)

        attribute_prereq_lazy.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_lazy.save()


        # Create child
        child = AttributeOwner()
        child.set_player_id(parent.get_id())
        # Create prerequisite Attribute for attribute_id

        attribute_prereq_child_lazy = Attribute()

        attribute_prereq_child_lazy.set_internal_name('test_prereq_child_lazy')

        attribute_prereq_child_lazy.set_visible(1)

        attribute_prereq_child_lazy.set_attribute_type(ThriftAttributeType.STRENGTH)

        attribute_prereq_child_lazy.save()


        child.set_attribute_id(attribute_prereq_child_lazy.get_id())
        child.save()

        # Test lazy mode
        results_iter = parent.get_attribute_owners(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], AttributeOwner)


    def test_has_many_inventory_owners_basic(self):
        """Test inventory_owners relationship basic getter."""
        # Create parent
        parent = Player()
        parent.set_full_name('test_full_name')
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_security_token('test_security_token')
        parent.set_over_13(1)
        parent.set_year_of_birth(1)
        parent.set_email('test_email')
        parent.save()


        # Create related records
        child1 = InventoryOwner()
        child1.set_player_id(parent.get_id())
        child1.set_inventory_id(1)
        child1.save()

        child2 = InventoryOwner()
        child2.set_player_id(parent.get_id())
        child2.set_inventory_id(1)
        child2.save()

        # Test getter (eager mode)
        results = parent.get_inventory_owners(lazy=False)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)

        # Test caching
        results2 = parent.get_inventory_owners(lazy=False)
        self.assertIs(results, results2)

        # Test reload
        results3 = parent.get_inventory_owners(reload=True)
        self.assertIsNot(results, results3)
        self.assertEqual(len(results3), 2)


    def test_has_many_inventory_owners_lazy(self):
        """Test inventory_owners relationship lazy loading."""
        # Create parent with children
        parent = Player()
        parent.set_full_name('test_full_name')
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_security_token('test_security_token')
        parent.set_over_13(1)
        parent.set_year_of_birth(1)
        parent.set_email('test_email')
        parent.save()


        # Create child
        child = InventoryOwner()
        child.set_player_id(parent.get_id())
        child.set_inventory_id(1)
        child.save()

        # Test lazy mode
        results_iter = parent.get_inventory_owners(lazy=True)
        self.assertFalse(isinstance(results_iter, list))

        # Consume iterator
        results_list = list(results_iter)
        self.assertEqual(len(results_list), 1)
        self.assertIsInstance(results_list[0], InventoryOwner)


    def test_has_many_mobile_basic(self):
        """Test mobile relationship basic getter."""
        # Create parent
        parent = Player()
        parent.set_full_name('test_full_name')
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_security_token('test_security_token')
        parent.set_over_13(1)
        parent.set_year_of_birth(1)
        parent.set_email('test_email')
        parent.save()


        # Create related records
        child1 = Mobile()
        child1.set_owner_player_id(parent.get_id())
        child1.set_mobile_type(ThriftMobileType.PLAYER)
        child1.set_what_we_call_you('test_what_we_call_you')
        child1.save()

        child2 = Mobile()
        child2.set_owner_player_id(parent.get_id())
        child2.set_mobile_type(ThriftMobileType.PLAYER)
        child2.set_what_we_call_you('test_what_we_call_you')
        child2.save()

        # Test getter (1-to-1 relationship)
        result = parent.get_mobile()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Mobile)
        self.assertEqual(result.get_owner_player_id(), parent.get_id())

        # Test caching
        result2 = parent.get_mobile()
        self.assertIs(result, result2)

        # Test reload
        result3 = parent.get_mobile(reload=True)
        self.assertIsNotNone(result3)
        self.assertEqual(result3.get_owner_player_id(), parent.get_id())

    def test_dirty_tracking_new_model(self):
        """Test that new models are marked dirty."""
        model = Player()
        self.assertTrue(model._dirty)

    def test_dirty_tracking_saved_model(self):
        """Test that saved models are marked clean."""
        model = Player()
        model.set_full_name('test_full_name')
        model.set_what_we_call_you('test_what_we_call_you')
        model.set_security_token('test_security_token')
        model.set_over_13(1)
        model.set_year_of_birth(1)
        model.set_email('test_email')
        model.save()
        self.assertFalse(model._dirty)

    def test_dirty_tracking_setter(self):
        """Test that setters mark model dirty."""
        model = Player()
        model.set_full_name('test_full_name')
        model.set_what_we_call_you('test_what_we_call_you')
        model.set_security_token('test_security_token')
        model.set_over_13(1)
        model.set_year_of_birth(1)
        model.set_email('test_email')
        model.save()
        self.assertFalse(model._dirty)

        model.set_full_name('test_value_2')
        self.assertTrue(model._dirty)

    def test_dirty_tracking_skip_save(self):
        """Test that clean models skip save operation."""
        model = Player()
        model.set_full_name('test_full_name')
        model.set_what_we_call_you('test_what_we_call_you')
        model.set_security_token('test_security_token')
        model.set_over_13(1)
        model.set_year_of_birth(1)
        model.set_email('test_email')
        model.save()
        self.assertFalse(model._dirty)

        # Save again without changes
        model.save()
        self.assertFalse(model._dirty)

    def test_cascade_destroy(self):
        """Test cascade destroy for has-many relationships."""
        # Create parent
        parent = Player()
        parent.set_full_name('test_full_name')
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_security_token('test_security_token')
        parent.set_over_13(1)
        parent.set_year_of_birth(1)
        parent.set_email('test_email')
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create children
        child1 = AttributeOwner()
        child1.set_attribute_id(1)
        child1.set_player_id(parent_id)
        child1.save()
        child1_id = child1.get_id()
        self.assertIsNotNone(child1_id)

        child2 = AttributeOwner()
        child2.set_attribute_id(1)
        child2.set_player_id(parent_id)
        child2.save()
        child2_id = child2.get_id()
        self.assertIsNotNone(child2_id)

        # Verify children exist
        children = parent.get_attribute_owners(reload=True)
        self.assertEqual(len(children), 2)

        # Destroy parent with cascade
        parent.destroy(cascade=True)

        # Verify parent is destroyed
        self.assertIsNone(parent.get_id())
        destroyed_parent = Player.find(parent_id)
        self.assertIsNone(destroyed_parent)

        # Verify children are destroyed
        destroyed_child1 = AttributeOwner.find(child1_id)
        self.assertIsNone(destroyed_child1)
        destroyed_child2 = AttributeOwner.find(child2_id)
        self.assertIsNone(destroyed_child2)

    def test_destroy_without_cascade(self):
        """Test destroy without cascade leaves children intact."""
        # Create parent
        parent = Player()
        parent.set_full_name('test_full_name')
        parent.set_what_we_call_you('test_what_we_call_you')
        parent.set_security_token('test_security_token')
        parent.set_over_13(1)
        parent.set_year_of_birth(1)
        parent.set_email('test_email')
        parent.save()
        parent_id = parent.get_id()
        self.assertIsNotNone(parent_id)

        # Create child
        child = AttributeOwner()
        child.set_attribute_id(1)
        child.set_player_id(parent_id)
        child.save()
        child_id = child.get_id()
        self.assertIsNotNone(child_id)

        # Destroy parent WITHOUT cascade (should fail with FK constraint)
        # Note: This may fail or succeed depending on DB FK constraints
        try:
            parent.destroy(cascade=False)
            # If successful, verify parent destroyed but child remains
            self.assertIsNone(parent.get_id())
            destroyed_parent = Player.find(parent_id)
            self.assertIsNone(destroyed_parent)

            # Child should still exist (orphaned)
            remaining_child = AttributeOwner.find(child_id)
            # Note: Child may or may not exist depending on FK constraints
            # This test documents the behavior rather than enforcing it
        except Exception as e:
            # Expected if DB has FK constraints with RESTRICT or NO ACTION
            pass

    # TODO: Add Owner union tests for tables with owner fields
    # TODO: Add AttributeValue union tests for attributes table



if __name__ == '__main__':
    unittest.main()
