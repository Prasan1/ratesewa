#!/usr/bin/env python3
"""Initialize database tables for RateSewa"""

import os
from app import app, db

def init_database():
    """Create all database tables"""
    with app.app_context():
        # Create instance directory if it doesn't exist
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(instance_path, exist_ok=True)

        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")

if __name__ == '__main__':
    init_database()
