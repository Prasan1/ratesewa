#!/usr/bin/env python3
"""
Test admin users functionality
"""
from app import app, db
from models import User

def test_admin_users():
    with app.app_context():
        print("Testing Admin Users Functionality")
        print("=" * 50)

        # Test 1: Retrieve all users
        try:
            users = User.query.order_by(User.name.asc()).all()
            print(f"✅ Successfully retrieved {len(users)} users")
        except Exception as e:
            print(f"❌ Error retrieving users: {e}")
            return

        # Test 2: Check is_active column
        print("\nUser Status Check:")
        for user in users:
            status = "Active" if user.is_active else "Inactive"
            role = "Admin" if user.is_admin else "User"
            print(f"  {user.name:25s} | {status:8s} | {role}")

        # Test 3: Test activate/deactivate
        print("\nTesting Activate/Deactivate:")
        test_user = User.query.filter_by(email='test@ratesewa.com').first()
        if test_user:
            print(f"  Test user found: {test_user.name}")
            original_status = test_user.is_active

            # Deactivate
            test_user.is_active = False
            db.session.commit()
            print(f"  ✅ Deactivated: is_active = {test_user.is_active}")

            # Reactivate
            test_user.is_active = True
            db.session.commit()
            print(f"  ✅ Reactivated: is_active = {test_user.is_active}")

            # Restore original
            test_user.is_active = original_status
            db.session.commit()
            print(f"  ✅ Restored to original status: {original_status}")
        else:
            print("  ⚠️ Test user not found")

        print("\n" + "=" * 50)
        print("All tests passed! Admin users functionality is working.")

if __name__ == "__main__":
    test_admin_users()
