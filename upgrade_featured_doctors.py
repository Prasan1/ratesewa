#!/usr/bin/env python3
"""
Upgrade all featured doctors to 'featured' subscription tier
"""

from app import app, db
from models import Doctor

def upgrade_featured():
    with app.app_context():
        # Find all featured doctors
        featured = Doctor.query.filter_by(is_featured=True).all()
        print(f"Found {len(featured)} featured doctors")

        for d in featured:
            print(f"  {d.id}: {d.name} - current tier: {d.subscription_tier}")

        # Update them to featured tier
        updated = Doctor.query.filter_by(is_featured=True).update({'subscription_tier': 'featured'})
        db.session.commit()

        print(f"\nUpdated {updated} doctors to 'featured' tier")

if __name__ == '__main__':
    upgrade_featured()
