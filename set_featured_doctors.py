#!/usr/bin/env python3
"""
Set Featured tier for premium subscribers
Run this in DigitalOcean Console to activate Featured badges
"""

from app import app, db
from models import Doctor

def set_featured_doctors():
    with app.app_context():
        print("=" * 70)
        print("SETTING FEATURED DOCTORS")
        print("=" * 70)

        # List of Featured doctors
        featured_doctors = [
            'Dr. Bilakshan Mishra',
            'Subin Paudel'
        ]

        updated = []
        not_found = []

        for name in featured_doctors:
            # Try exact match first
            doctor = Doctor.query.filter_by(name=name).first()

            # Try partial match if exact fails
            if not doctor:
                doctor = Doctor.query.filter(Doctor.name.ilike(f'%{name}%')).first()

            if doctor:
                old_tier = doctor.subscription_tier or 'NULL (free)'
                doctor.subscription_tier = 'featured'
                updated.append((doctor.name, old_tier))
                print(f"\n✅ {doctor.name}")
                print(f"   Changed from: {old_tier} → featured")
                print(f"   Profile: https://ranksewa.com/doctor/{doctor.slug}")
            else:
                not_found.append(name)
                print(f"\n❌ NOT FOUND: {name}")

        if updated:
            db.session.commit()
            print("\n" + "=" * 70)
            print(f"✅ SUCCESS - Updated {len(updated)} doctor(s) to Featured tier")
            print("=" * 70)
            print("\nRefresh their profiles to see:")
            print("  - Purple 'Featured' badge with ⭐ star icon")
            print("  - Featured doctor banner at top")
            print("  - All premium features unlocked")

        if not_found:
            print("\n⚠️  NOT FOUND:")
            for name in not_found:
                print(f"   - {name}")
            print("\nCheck the exact name in the database.")

if __name__ == '__main__':
    set_featured_doctors()
