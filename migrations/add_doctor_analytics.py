#!/usr/bin/env python3
"""
Migration: Add doctor_analytics table
Tracks daily analytics for each doctor profile
"""

import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import DoctorAnalytics

def upgrade():
    """Create doctor_analytics table"""
    with app.app_context():
        print("Creating doctor_analytics table...")
        db.create_all()  # Creates only tables that don't exist
        print("✅ doctor_analytics table created successfully!")

def downgrade():
    """Drop doctor_analytics table"""
    with app.app_context():
        print("Dropping doctor_analytics table...")
        DoctorAnalytics.__table__.drop(db.engine)
        print("✅ doctor_analytics table dropped!")

if __name__ == '__main__':
    upgrade()
