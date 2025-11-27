#!/usr/bin/env python3
"""
Concurrent test runner for database models.

This script runs all model tests in parallel using multiprocessing,
with each test using its own unique database to avoid conflicts.
"""

import sys
import multiprocessing
from typing import Callable, Tuple

sys.path.append("../gen-py")

# Database credentials
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASSWORD = "minda"


def run_test_module(
    test_info: Tuple[str, str, Callable, Callable, Callable],
) -> Tuple[str, bool, str]:
    """
    Run a test module in a separate process.

    Args:
        test_info: Tuple of (test_name, database_name, setup_fn, test_fn, teardown_fn)

    Returns:
        Tuple of (test_name, success, error_message)
    """
    test_name, database_name, setup_fn, test_fn, teardown_fn = test_info

    try:
        print(f"\n{'=' * 60}")
        print(f"Starting: {test_name}")
        print(f"Database: {database_name}")
        print(f"{'=' * 60}\n")

        # Setup database
        setup_fn(DB_HOST, DB_USER, DB_PASSWORD, database_name)

        # Run the test function
        test_fn(DB_HOST, DB_USER, DB_PASSWORD, database_name)

        # Teardown database
        teardown_fn(DB_HOST, DB_USER, DB_PASSWORD, database_name)

        print(f"\n{'=' * 60}")
        print(f"✓ PASSED: {test_name}")
        print(f"{'=' * 60}\n")

        return (test_name, True, "")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n{'=' * 60}")
        print(f"✗ FAILED: {test_name}")
        print(f"Error: {error_msg}")
        print(f"{'=' * 60}\n")

        # Try to cleanup even on failure
        try:
            teardown_fn(DB_HOST, DB_USER, DB_PASSWORD, database_name)
        except:
            pass

        return (test_name, False, error_msg)


def main():
    """Main test runner."""
    print("\n" + "=" * 80)
    print("DATABASE MODEL TEST SUITE - CONCURRENT RUNNER")
    print("=" * 80)
    print(
        f"\nRunning tests in parallel using {multiprocessing.cpu_count()} CPU cores\n"
    )

    # Import test modules
    from dbinc.item_test import (
        setup_database as item_setup,
        teardown_database as item_teardown,
        test_item_blueprint,
        test_item,
        test_search_item,
    )
    from dbinc.mobile_item_test import (
        setup_database as mobile_item_setup,
        teardown_database as mobile_item_teardown,
        test_mobile_item,
        test_search_mobile_item,
    )
    from dbinc.inventory_test import (
        setup_database as inventory_setup,
        teardown_database as inventory_teardown,
        test_inventory,
        test_list_inventory,
    )
    from dbinc.mobile_test import (
        setup_database as mobile_setup,
        teardown_database as mobile_teardown,
        test_mobile,
    )
    from dbinc.player_test import (
        setup_database as player_setup,
        teardown_database as player_teardown,
        test_player,
        test_list_player,
        test_player_with_character_attributes,
    )

    # Define all tests with unique database names
    tests = [
        (
            "ItemBlueprint Tests",
            "test_item_blueprint_db",
            item_setup,
            test_item_blueprint,
            item_teardown,
        ),
        ("Item Tests", "test_item_db", item_setup, test_item, item_teardown),
        (
            "Item Search Tests",
            "test_item_search_db",
            item_setup,
            test_search_item,
            item_teardown,
        ),
        (
            "MobileItem Tests",
            "test_mobile_item_db",
            mobile_item_setup,
            test_mobile_item,
            mobile_item_teardown,
        ),
        (
            "MobileItem Search Tests",
            "test_mobile_item_search_db",
            mobile_item_setup,
            test_search_mobile_item,
            mobile_item_teardown,
        ),
        (
            "Inventory Tests",
            "test_inventory_db",
            inventory_setup,
            test_inventory,
            inventory_teardown,
        ),
        (
            "Inventory List Tests",
            "test_inventory_list_db",
            inventory_setup,
            test_list_inventory,
            inventory_teardown,
        ),
        ("Mobile Tests", "test_mobile_db", mobile_setup, test_mobile, mobile_teardown),
        ("Player Tests", "test_player_db", player_setup, test_player, player_teardown),
        (
            "Player List Tests",
            "test_player_list_db",
            player_setup,
            test_list_player,
            player_teardown,
        ),
        (
            "Player Character Attributes Tests",
            "test_player_char_db",
            player_setup,
            test_player_with_character_attributes,
            player_teardown,
        ),
    ]

    print(f"Running {len(tests)} test suites concurrently...\n")

    # Run all tests in parallel
    with multiprocessing.Pool() as pool:
        results = pool.map(run_test_module, tests)

    # Collect and display results
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80 + "\n")

    passed = []
    failed = []

    for test_name, success, error_msg in results:
        if success:
            passed.append(test_name)
            print(f"✓ PASSED: {test_name}")
        else:
            failed.append((test_name, error_msg))
            print(f"✗ FAILED: {test_name}")
            print(f"  Error: {error_msg}")

    # Final summary
    print("\n" + "=" * 80)
    print(f"Total: {len(tests)} tests")
    print(f"Passed: {len(passed)}")
    print(f"Failed: {len(failed)}")
    print("=" * 80 + "\n")

    if failed:
        print("Failed tests:")
        for test_name, error_msg in failed:
            print(f"  - {test_name}: {error_msg}")
        print()
        sys.exit(1)
    else:
        print("🎉 All tests passed!")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
