#!/usr/bin/env python3
"""
After running the workplace migration, run this to update B&C doctors with their workplace
"""

from app import app, db
from models import Doctor

def update_bnc_workplace():
    """Update B&C Medical College doctors with workplace info"""

    with app.app_context():
        print("=" * 70)
        print("Updating B&C Medical College Doctors with Workplace")
        print("=" * 70)

        # Find doctors from B&C Medical College based on description
        bnc_doctors = Doctor.query.filter(
            Doctor.description.ilike('%B&C Medical College%')
        ).all()

        updated = 0

        for doctor in bnc_doctors:
            if not doctor.workplace:
                doctor.workplace = "B&C Medical College, Birtamod"
                updated += 1
                print(f"✅ Updated: {doctor.name}")

        try:
            db.session.commit()
            print("\n" + "=" * 70)
            print(f"✅ Update Complete!")
            print(f"   Updated {updated} doctors with workplace info")
            print("=" * 70)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    update_bnc_workplace()
