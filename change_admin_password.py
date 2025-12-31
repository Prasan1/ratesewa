#!/usr/bin/env python3
"""
Quick script to change admin password
Usage: python3 change_admin_password.py
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash
import getpass

def change_admin_password():
    with app.app_context():
        print("=" * 60)
        print("  CHANGE ADMIN PASSWORD")
        print("=" * 60)
        print()

        # Find admin user
        admin = User.query.filter_by(email='admin@ranksewa.com').first()

        if not admin:
            print("❌ Admin user not found!")
            return

        print(f"Admin user: {admin.name} ({admin.email})")
        print()

        # Get new password
        while True:
            new_password = getpass.getpass("Enter NEW password: ")

            if len(new_password) < 6:
                print("⚠️  Password must be at least 6 characters. Try again.")
                continue

            confirm_password = getpass.getpass("Confirm NEW password: ")

            if new_password != confirm_password:
                print("⚠️  Passwords don't match. Try again.")
                continue

            break

        # Update password
        admin.password = generate_password_hash(new_password)
        db.session.commit()

        print()
        print("=" * 60)
        print("✅ Password changed successfully!")
        print("=" * 60)
        print()
        print(f"You can now login with:")
        print(f"  Email: {admin.email}")
        print(f"  Password: {new_password}")
        print()
        print("⚠️  WRITE THIS DOWN and keep it safe!")
        print()

if __name__ == '__main__':
    change_admin_password()
