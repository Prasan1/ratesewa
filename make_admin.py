#!/usr/bin/env python3
"""
Script to make users admin
Usage: python make_admin.py
"""

from app import app, db
from models import User

def make_admin(email):
    """Make a user admin by email"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if user:
            user.is_admin = True
            user.role = 'admin'
            db.session.commit()
            print(f"✅ Successfully made {email} an admin!")
            return True
        else:
            print(f"❌ User not found: {email}")
            print(f"   Please create an account with this email first")
            return False

def list_admins():
    """List all current admins"""
    with app.app_context():
        admins = User.query.filter_by(is_admin=True).all()

        print("\n📋 Current Admins:")
        if admins:
            for admin in admins:
                print(f"   • {admin.name} ({admin.email})")
        else:
            print("   No admins found")
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("RankSewa Admin Setup")
    print("=" * 60)

    # Make these users admin
    admin_emails = [
        'opaltechlab@gmail.com',
        'paul.paudyal@gmail.com'
    ]

    print("\nMaking users admin...\n")
    for email in admin_emails:
        make_admin(email)

    # Show all admins
    list_admins()

    print("=" * 60)
    print("Done!")
    print("=" * 60)
