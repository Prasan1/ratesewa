#!/usr/bin/env python3
"""
NMC Number Verification Tool
Check if an NMC number is already assigned to another doctor before verification
"""

from app import app, db
from models import Doctor
import sys

def verify_nmc_number(nmc_number, doctor_name=None):
    """Check if NMC number is already assigned"""

    with app.app_context():
        print("=" * 70)
        print(f"CHECKING NMC NUMBER: {nmc_number}")
        print("=" * 70)

        # Find doctor with this NMC number
        existing = Doctor.query.filter_by(nmc_number=nmc_number).first()

        if existing:
            print(f"⚠️  NMC# {nmc_number} is ALREADY ASSIGNED to:")
            print(f"    Name: {existing.name}")
            print(f"    City: {existing.city.name}")
            print(f"    Specialty: {existing.specialty.name}")
            print(f"    Workplace: {existing.workplace or 'Not specified'}")
            print(f"    Verified: {'Yes' if existing.is_verified else 'No'}")
            print(f"    Profile: https://ranksewa.com/doctor/{existing.slug}")
            print()

            if doctor_name:
                print(f"❌ CANNOT assign to: {doctor_name}")
                print(f"   Reason: NMC# already belongs to {existing.name}")
                print()
                print("RECOMMENDATION:")
                print("  1. Double-check the NMC number (might be a typo)")
                print("  2. Verify with NMC website: https://www.nmc.org.np/")
                print("  3. Contact the doctor to confirm correct NMC#")
                print("  4. DO NOT verify without confirmed NMC number")

            return False
        else:
            print(f"✅ NMC# {nmc_number} is AVAILABLE")
            if doctor_name:
                print(f"   Can be assigned to: {doctor_name}")
                print()
                print("NEXT STEPS:")
                print("  1. Verify on NMC website: https://www.nmc.org.np/")
                print("  2. Confirm name matches exactly")
                print("  3. Check registration date is valid")
                print("  4. Proceed with verification if everything matches")

            return True

        print("=" * 70)

def search_doctor_by_name(name):
    """Search for doctors by name"""

    with app.app_context():
        doctors = Doctor.query.filter(
            Doctor.name.ilike(f'%{name}%')
        ).limit(10).all()

        print()
        print("=" * 70)
        print(f"SEARCH RESULTS for '{name}':")
        print("=" * 70)

        if doctors:
            for d in doctors:
                print(f"Name: {d.name}")
                print(f"  NMC#: {d.nmc_number or 'Not assigned'}")
                print(f"  City: {d.city.name}")
                print(f"  Specialty: {d.specialty.name}")
                print(f"  Verified: {'Yes' if d.is_verified else 'No'}")
                print(f"  ID: {d.id}")
                print("-" * 70)
        else:
            print("No doctors found with that name")

        print("=" * 70)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 verify_nmc_number.py <nmc_number> [doctor_name]")
        print("  python3 verify_nmc_number.py search <doctor_name>")
        print()
        print("Examples:")
        print("  python3 verify_nmc_number.py 6479 'Dr. Shesh Kanta Aryal'")
        print("  python3 verify_nmc_number.py search 'Arya Karki'")
        sys.exit(1)

    if sys.argv[1].lower() == 'search':
        if len(sys.argv) < 3:
            print("Please provide a doctor name to search")
            sys.exit(1)
        search_doctor_by_name(' '.join(sys.argv[2:]))
    else:
        nmc = sys.argv[1]
        doctor_name = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else None
        verify_nmc_number(nmc, doctor_name)
