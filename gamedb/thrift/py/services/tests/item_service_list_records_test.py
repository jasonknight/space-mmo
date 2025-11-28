#!/usr/bin/env python3
"""
Comprehensive test suite for ItemService.list_records() method.
Tests all code paths including pagination, search, and error conditions.
"""

import sys
import os
import uuid

thrift_gen_path = "/vagrant/gamedb/thrift/gen-py"
if thrift_gen_path not in sys.path:
    sys.path.insert(0, thrift_gen_path)

py_path = "/vagrant/gamedb/thrift/py"
if py_path not in sys.path:
    sys.path.insert(0, py_path)

from dotenv import load_dotenv

load_dotenv()

import mysql.connector
from services.item_service import ItemServiceHandler
from game.ttypes import (
    ItemRequest,
    ItemRequestData,
    CreateItemRequestData,
    ListItemRequestData,
    Item,
    ItemType,
    StatusType,
    GameError,
)
from common import is_ok
from db_models.models import (
    Item as ItemModel,
    Attribute,
    AttributeOwner,
)
import db_models.models

TEST_DATABASE = None


def setUpModule():
    """Set up test database before running tests."""
    global TEST_DATABASE
    TEST_DATABASE = f"gamedb_test_{uuid.uuid4().hex[:8]}"

    connection = mysql.connector.connect(
        host="localhost",
        user="admin",
        password="minda",
        auth_plugin="mysql_native_password",
        ssl_disabled=True,
        use_pure=True,
    )
    cursor = connection.cursor()

    cursor.execute(f"CREATE DATABASE `{TEST_DATABASE}`")
    connection.database = TEST_DATABASE

    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.execute(ItemModel.CREATE_TABLE_STATEMENT)
    cursor.execute(Attribute.CREATE_TABLE_STATEMENT)
    cursor.execute(AttributeOwner.CREATE_TABLE_STATEMENT)
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")

    connection.commit()
    cursor.close()
    connection.close()

    os.environ["DB_DATABASE"] = TEST_DATABASE
    db_models.models.DB_DATABASE = TEST_DATABASE
    print(f"\n✓ Test database '{TEST_DATABASE}' created")


def tearDownModule():
    """Tear down test database after running tests."""
    global TEST_DATABASE

    if TEST_DATABASE:
        connection = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="minda",
            auth_plugin="mysql_native_password",
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DATABASE}`")
        connection.commit()
        cursor.close()
        connection.close()
        print(f"\n✓ Test database '{TEST_DATABASE}' dropped")


def create_test_item(service, internal_name, item_type=ItemType.RAWMATERIAL):
    """Helper function to create a test item."""
    item = Item(
        id=None,
        internal_name=internal_name,
        attributes={},
        max_stack_size=1000,
        item_type=item_type,
    )

    create_request = ItemRequest(
        data=ItemRequestData(
            create_item=CreateItemRequestData(item=item),
        ),
    )

    create_response = service.create(create_request)
    assert is_ok(create_response.results), (
        f"Create failed: {create_response.results[0].message}"
    )
    return create_response.response_data.create_item.item.id


def test_missing_list_item_field():
    """Test validation error when list_item field is missing."""
    print("\nTest 1: Missing list_item field")
    service = ItemServiceHandler()

    request = ItemRequest(
        data=ItemRequestData(),
    )

    response = service.list_records(request)

    assert response.results[0].status == StatusType.FAILURE, (
        "Expected FAILURE status"
    )
    assert response.results[0].error_code == GameError.DB_INVALID_DATA, (
        "Expected DB_INVALID_DATA error code"
    )
    assert response.response_data is None, (
        "Expected no response data"
    )
    assert "must contain list_item" in response.results[0].message, (
        "Expected error message about missing list_item"
    )
    print("✓ Missing list_item field correctly returns validation error")


def test_empty_database_listing():
    """Test listing when database is empty."""
    print("\nTest 2: Empty database listing")
    service = ItemServiceHandler()

    request = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=0,
                results_per_page=10,
            ),
        ),
    )

    response = service.list_records(request)

    assert is_ok(response.results), (
        f"List failed: {response.results[0].message}"
    )
    assert response.response_data is not None, (
        "Expected response data"
    )
    assert response.response_data.list_item.total_count == 0, (
        "Expected total_count to be 0"
    )
    assert len(response.response_data.list_item.items) == 0, (
        "Expected empty items list"
    )
    print("✓ Empty database returns 0 items correctly")


def test_normal_listing_without_search():
    """Test normal listing without search string."""
    print("\nTest 3: Normal listing without search (page 0)")
    service = ItemServiceHandler()

    create_test_item(service, "copper_ore", ItemType.RAWMATERIAL)
    create_test_item(service, "iron_ore", ItemType.RAWMATERIAL)
    create_test_item(service, "gold_ore", ItemType.RAWMATERIAL)

    request = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=0,
                results_per_page=10,
            ),
        ),
    )

    response = service.list_records(request)

    assert is_ok(response.results), (
        f"List failed: {response.results[0].message}"
    )
    assert response.response_data is not None, (
        "Expected response data"
    )
    assert response.response_data.list_item.total_count == 3, (
        f"Expected total_count to be 3, got {response.response_data.list_item.total_count}"
    )
    assert len(response.response_data.list_item.items) == 3, (
        f"Expected 3 items, got {len(response.response_data.list_item.items)}"
    )

    internal_names = [item.internal_name for item in response.response_data.list_item.items]
    assert "copper_ore" in internal_names, (
        "Expected copper_ore in results"
    )
    assert "iron_ore" in internal_names, (
        "Expected iron_ore in results"
    )
    assert "gold_ore" in internal_names, (
        "Expected gold_ore in results"
    )
    print(f"✓ Listed all 3 items correctly: {internal_names}")


def test_pagination():
    """Test pagination with multiple pages."""
    print("\nTest 4: Pagination (page > 0)")
    service = ItemServiceHandler()

    for i in range(15):
        create_test_item(service, f"item_{i:02d}", ItemType.RAWMATERIAL)

    request_page_0 = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=0,
                results_per_page=5,
            ),
        ),
    )

    response_page_0 = service.list_records(request_page_0)
    assert is_ok(response_page_0.results), (
        f"Page 0 list failed: {response_page_0.results[0].message}"
    )
    assert response_page_0.response_data.list_item.total_count == 18, (
        f"Expected total_count to be 18 (3 from previous test + 15 new), got {response_page_0.response_data.list_item.total_count}"
    )
    assert len(response_page_0.response_data.list_item.items) == 5, (
        f"Expected 5 items on page 0, got {len(response_page_0.response_data.list_item.items)}"
    )
    page_0_names = [item.internal_name for item in response_page_0.response_data.list_item.items]
    print(f"✓ Page 0 (5 items): {page_0_names}")

    request_page_1 = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=1,
                results_per_page=5,
            ),
        ),
    )

    response_page_1 = service.list_records(request_page_1)
    assert is_ok(response_page_1.results), (
        f"Page 1 list failed: {response_page_1.results[0].message}"
    )
    assert len(response_page_1.response_data.list_item.items) == 5, (
        f"Expected 5 items on page 1, got {len(response_page_1.response_data.list_item.items)}"
    )
    page_1_names = [item.internal_name for item in response_page_1.response_data.list_item.items]
    print(f"✓ Page 1 (5 items): {page_1_names}")

    for name in page_0_names:
        assert name not in page_1_names, (
            f"Item {name} appears on both page 0 and page 1"
        )
    print("✓ Page 0 and page 1 have different items (no overlap)")

    request_page_3 = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=3,
                results_per_page=5,
            ),
        ),
    )

    response_page_3 = service.list_records(request_page_3)
    assert is_ok(response_page_3.results), (
        f"Page 3 list failed: {response_page_3.results[0].message}"
    )
    assert len(response_page_3.response_data.list_item.items) == 3, (
        f"Expected 3 items on page 3, got {len(response_page_3.response_data.list_item.items)}"
    )
    print(f"✓ Page 3 (last page, 3 items): {[item.internal_name for item in response_page_3.response_data.list_item.items]}")


def test_search_with_matches():
    """Test search with search_string that has matches."""
    print("\nTest 5: Search with matches")
    service = ItemServiceHandler()

    create_test_item(service, "steel_sword", ItemType.WEAPON)
    create_test_item(service, "steel_bar", ItemType.REFINEDMATERIAL)
    create_test_item(service, "wooden_sword", ItemType.WEAPON)

    request = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=0,
                results_per_page=10,
                search_string="steel",
            ),
        ),
    )

    response = service.list_records(request)

    assert is_ok(response.results), (
        f"Search list failed: {response.results[0].message}"
    )
    assert response.response_data is not None, (
        "Expected response data"
    )
    assert response.response_data.list_item.total_count == 2, (
        f"Expected total_count to be 2, got {response.response_data.list_item.total_count}"
    )
    assert len(response.response_data.list_item.items) == 2, (
        f"Expected 2 items, got {len(response.response_data.list_item.items)}"
    )

    internal_names = [item.internal_name for item in response.response_data.list_item.items]
    assert "steel_sword" in internal_names, (
        "Expected steel_sword in search results"
    )
    assert "steel_bar" in internal_names, (
        "Expected steel_bar in search results"
    )
    assert "wooden_sword" not in internal_names, (
        "wooden_sword should not be in search results"
    )
    print(f"✓ Search for 'steel' returned 2 matching items: {internal_names}")


def test_search_with_no_matches():
    """Test search with search_string that has no matches."""
    print("\nTest 6: Search with no matches")
    service = ItemServiceHandler()

    request = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=0,
                results_per_page=10,
                search_string="nonexistent_item_xyz",
            ),
        ),
    )

    response = service.list_records(request)

    assert is_ok(response.results), (
        f"Search list failed: {response.results[0].message}"
    )
    assert response.response_data is not None, (
        "Expected response data"
    )
    assert response.response_data.list_item.total_count == 0, (
        f"Expected total_count to be 0, got {response.response_data.list_item.total_count}"
    )
    assert len(response.response_data.list_item.items) == 0, (
        f"Expected 0 items, got {len(response.response_data.list_item.items)}"
    )
    print("✓ Search with no matches returns 0 items correctly")


def test_negative_page_number():
    """Test that negative page numbers are converted to 0."""
    print("\nTest 7: Negative page number handling")
    service = ItemServiceHandler()

    request = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=-5,
                results_per_page=10,
            ),
        ),
    )

    response = service.list_records(request)

    assert is_ok(response.results), (
        f"List with negative page failed: {response.results[0].message}"
    )
    assert response.response_data is not None, (
        "Expected response data"
    )
    print("✓ Negative page number handled correctly (converted to 0)")


def test_exception_handling():
    """Test exception handling when database operation fails."""
    print("\nTest 8: Exception handling")
    service = ItemServiceHandler()

    original_create_connection = ItemModel._create_connection

    def mock_failing_connection():
        raise Exception("Simulated database connection failure")

    try:
        ItemModel._create_connection = mock_failing_connection

        request = ItemRequest(
            data=ItemRequestData(
                list_item=ListItemRequestData(
                    page=0,
                    results_per_page=10,
                ),
            ),
        )

        response = service.list_records(request)

        assert response.results[0].status == StatusType.FAILURE, (
            "Expected FAILURE status on exception"
        )
        assert response.results[0].error_code == GameError.DB_QUERY_FAILED, (
            "Expected DB_QUERY_FAILED error code"
        )
        assert response.response_data is None, (
            "Expected no response data on exception"
        )
        assert "Failed to list items" in response.results[0].message, (
            "Expected error message about listing failure"
        )
        print("✓ Exception correctly caught and returned as FAILURE response")

    finally:
        ItemModel._create_connection = original_create_connection


def test_search_with_pagination():
    """Test search with pagination to ensure search and pagination work together."""
    print("\nTest 9: Search with pagination")
    service = ItemServiceHandler()

    for i in range(10):
        create_test_item(service, f"crystal_gem_{i:02d}", ItemType.RAWMATERIAL)

    request_page_0 = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=0,
                results_per_page=3,
                search_string="crystal",
            ),
        ),
    )

    response_page_0 = service.list_records(request_page_0)
    assert is_ok(response_page_0.results), (
        f"Search with pagination page 0 failed: {response_page_0.results[0].message}"
    )
    assert response_page_0.response_data.list_item.total_count == 10, (
        f"Expected total_count to be 10, got {response_page_0.response_data.list_item.total_count}"
    )
    assert len(response_page_0.response_data.list_item.items) == 3, (
        f"Expected 3 items on page 0, got {len(response_page_0.response_data.list_item.items)}"
    )
    print(f"✓ Search 'crystal' page 0: {[item.internal_name for item in response_page_0.response_data.list_item.items]}")

    request_page_2 = ItemRequest(
        data=ItemRequestData(
            list_item=ListItemRequestData(
                page=2,
                results_per_page=3,
                search_string="crystal",
            ),
        ),
    )

    response_page_2 = service.list_records(request_page_2)
    assert is_ok(response_page_2.results), (
        f"Search with pagination page 2 failed: {response_page_2.results[0].message}"
    )
    assert len(response_page_2.response_data.list_item.items) == 3, (
        f"Expected 3 items on page 2, got {len(response_page_2.response_data.list_item.items)}"
    )
    print(f"✓ Search 'crystal' page 2: {[item.internal_name for item in response_page_2.response_data.list_item.items]}")


def test_list_records_comprehensive():
    """Run all comprehensive tests for list_records method."""
    print("=" * 60)
    print("ItemService.list_records() Comprehensive Test Suite")
    print("=" * 60)

    test_missing_list_item_field()
    test_empty_database_listing()
    test_normal_listing_without_search()
    test_pagination()
    test_search_with_matches()
    test_search_with_no_matches()
    test_negative_page_number()
    test_exception_handling()
    test_search_with_pagination()

    print("\n" + "=" * 60)
    print("All list_records tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    setUpModule()
    try:
        test_list_records_comprehensive()
    finally:
        tearDownModule()
