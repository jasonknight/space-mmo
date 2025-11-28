#!/usr/bin/env python3
"""
Simple test to verify mobile endpoint functionality after refactoring.
"""

import sys
sys.path.append("../gen-py")
sys.path.append("../py")

import os

# Set environment variables for database connection
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'admin'
os.environ['DB_PASSWORD'] = 'minda'
os.environ['DB_DATABASE'] = 'gamedb'

# Import the MobileModel to test
from db_models.models import Mobile as MobileModel

def test_mobile_model_find():
    """Test that MobileModel.find() works."""
    print("Testing MobileModel.find()...")
    try:
        # Try to find a mobile by ID (this will fail if table is empty, but that's ok)
        mobile = MobileModel.find(1)
        if mobile:
            print(f"  ✓ Found mobile: id={mobile.get_id()}, name={mobile.get_what_we_call_you()}")
        else:
            print("  ✓ MobileModel.find() executed successfully (no mobile with id=1 found, which is expected)")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_mobile_model_create():
    """Test that we can create a mobile using ActiveRecord pattern."""
    print("\nTesting MobileModel creation...")
    try:
        # Create a test mobile
        mobile = MobileModel()
        mobile.set_mobile_type('NPC')
        mobile.set_what_we_call_you('Test Mobile')
        mobile.set_owner_player_id(1)

        # Save it
        mobile.save()

        print(f"  ✓ Created mobile: id={mobile.get_id()}, name={mobile.get_what_we_call_you()}")

        # Clean up: delete the test mobile
        import mysql.connector
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='minda',
            database='gamedb',
            auth_plugin='mysql_native_password',
            ssl_disabled=True,
            use_pure=True,
        )
        cursor = connection.cursor()
        cursor.execute("DELETE FROM mobiles WHERE id = %s", (mobile.get_id(),))
        connection.commit()
        cursor.close()
        connection.close()

        print("  ✓ Cleaned up test mobile")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_import():
    """Test that app.py can be imported without errors."""
    print("\nTesting app.py import...")
    try:
        import app
        print("  ✓ app.py imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Error importing app.py: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Mobile Endpoints Refactoring Tests")
    print("=" * 60)

    results = []
    results.append(test_mobile_model_find())
    results.append(test_mobile_model_create())
    results.append(test_app_import())

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
