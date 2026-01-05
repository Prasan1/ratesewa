#!/usr/bin/env python3
"""
Fix doctor names that are in ALL UPPERCASE
Converts them to proper Title Case

Example:
- Dr. ASHWINI GURUNG → Dr. Ashwini Gurung
- DR. RAM PRASAD SHARMA → Dr. Ram Prasad Sharma
"""

from app import app, db
from models import Doctor

def fix_uppercase_names():
    """Convert all uppercase doctor names to title case"""

    with app.app_context():
        print("=" * 60)
        print("FIXING UPPERCASE DOCTOR NAMES")
        print("=" * 60)

        # Get all active doctors
        doctors = Doctor.query.filter_by(is_active=True).all()

        fixed_count = 0

        for doctor in doctors:
            if not doctor.name:
                continue

            # Remove "Dr. " or "Dr " prefix temporarily
            name = doctor.name
            prefix = ""

            if name.startswith("Dr. "):
                prefix = "Dr. "
                name_part = name[4:]
            elif name.startswith("Dr "):
                prefix = "Dr. "  # Standardize to "Dr. " with period
                name_part = name[3:]
            elif name.startswith("DR. "):
                prefix = "Dr. "
                name_part = name[4:]
            elif name.startswith("DR "):
                prefix = "Dr. "
                name_part = name[3:]
            else:
                name_part = name

            # Check if name part is all uppercase
            if name_part and len(name_part) > 1:
                # Check if majority of letters are uppercase
                letters = [c for c in name_part if c.isalpha()]
                if letters:
                    uppercase_count = sum(1 for c in letters if c.isupper())
                    uppercase_ratio = uppercase_count / len(letters)

                    # If 80%+ of letters are uppercase, fix it
                    if uppercase_ratio >= 0.8:
                        old_name = doctor.name

                        # Convert to title case
                        new_name_part = name_part.title()

                        # Handle special cases for Nepali names
                        # (These are common patterns that shouldn't be title-cased)
                        special_words = {
                            'Mc': 'Mc',  # McDonald → McDonald (keep Mc uppercase)
                            'Mac': 'Mac',  # MacLeod → MacLeod
                        }

                        for old, new in special_words.items():
                            new_name_part = new_name_part.replace(old, new)

                        doctor.name = prefix + new_name_part
                        fixed_count += 1

                        print(f"✓ Fixed: {old_name} → {doctor.name}")

        if fixed_count > 0:
            db.session.commit()
            print("\n" + "=" * 60)
            print(f"✅ Fixed {fixed_count} doctor name(s)")
            print("=" * 60)
        else:
            print("\n✅ All doctor names are already properly formatted")

        # Verification
        print("\n" + "=" * 60)
        print("VERIFICATION - Checking for remaining uppercase names:")
        print("=" * 60)

        remaining = []
        for doctor in Doctor.query.filter_by(is_active=True).all():
            if doctor.name:
                name_part = doctor.name.replace('Dr. ', '').replace('Dr ', '')
                if name_part:
                    letters = [c for c in name_part if c.isalpha()]
                    if letters:
                        uppercase_count = sum(1 for c in letters if c.isupper())
                        uppercase_ratio = uppercase_count / len(letters)

                        if uppercase_ratio >= 0.8:
                            remaining.append(doctor.name)

        if remaining:
            print(f"⚠️ Still {len(remaining)} names with uppercase issues:")
            for name in remaining[:10]:
                print(f"  - {name}")
        else:
            print("✅ No uppercase names remaining")

        print("=" * 60)


if __name__ == '__main__':
    fix_uppercase_names()
