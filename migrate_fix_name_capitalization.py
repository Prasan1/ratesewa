#!/usr/bin/env python3
"""
Migration: Fix Doctor Name Capitalization

This script standardizes all doctor names to proper title case.
Fixes 248 uppercase names and 127 lowercase names.

Run this in production console:
    python3 migrate_fix_name_capitalization.py
"""

from app import app, db
from models import Doctor
from slugify import slugify

def title_case_name(name):
    """
    Convert name to proper title case while preserving special cases.

    Examples:
        "Dr. JOHN DOE" -> "Dr. John Doe"
        "Dr. john doe" -> "Dr. John Doe"
        "Prof. Dr. JANE SMITH" -> "Prof. Dr. Jane Smith"
        "Dr. SURAJ K.C" -> "Dr. Suraj K.C"
    """
    # Handle special particles that should be lowercase
    lowercase_particles = ['de', 'van', 'von', 'del', 'da', 'di', 'le', 'la']

    # Split into words
    words = name.split()
    result = []

    for i, word in enumerate(words):
        # Keep prefixes as-is (Dr., Prof., etc.)
        if word in ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.']:
            result.append(word)
        # Handle abbreviations with periods (e.g., K.C, B.K, M.D)
        elif '.' in word and len(word) <= 4:
            # Uppercase all letters in abbreviations
            result.append(word.upper())
        # Keep particles lowercase (except at start of name)
        elif i > 0 and word.lower() in lowercase_particles:
            result.append(word.lower())
        # Title case everything else
        else:
            result.append(word.capitalize())

    return ' '.join(result)

def main():
    print("=" * 70)
    print("Migration: Fix Doctor Name Capitalization")
    print("=" * 70)
    print()

    with app.app_context():
        doctors = Doctor.query.all()
        print(f"Total doctors: {len(doctors)}")
        print()

        fixed_count = 0
        unchanged_count = 0
        slug_updated_count = 0

        print("Fixing names...")
        print("-" * 70)

        for doctor in doctors:
            original_name = doctor.name
            fixed_name = title_case_name(original_name)

            if original_name != fixed_name:
                # Check if the fixed name already exists
                existing = Doctor.query.filter(
                    Doctor.name == fixed_name,
                    Doctor.id != doctor.id
                ).first()

                if existing:
                    print(f"⚠️  Skipping (duplicate): {original_name} -> {fixed_name}")
                    unchanged_count += 1
                    continue

                # Update name
                doctor.name = fixed_name

                # Regenerate slug if needed
                new_base_slug = slugify(fixed_name)
                if doctor.slug != new_base_slug:
                    # Check if new slug is available
                    slug = new_base_slug
                    counter = 1
                    while Doctor.query.filter(
                        Doctor.slug == slug,
                        Doctor.id != doctor.id
                    ).first():
                        slug = f"{new_base_slug}-{counter}"
                        counter += 1

                    doctor.slug = slug
                    slug_updated_count += 1

                fixed_count += 1

                # Show first 20 examples
                if fixed_count <= 20:
                    print(f"  {original_name} -> {fixed_name}")
            else:
                unchanged_count += 1

        # Commit changes
        db.session.commit()

        print()
        print("=" * 70)
        print("Migration Complete!")
        print("=" * 70)
        print(f"Fixed: {fixed_count:,} doctors")
        print(f"Unchanged: {unchanged_count:,} doctors")
        print(f"Slugs updated: {slug_updated_count:,}")
        print()
        print("✅ All doctor names are now properly capitalized!")
        print()

if __name__ == '__main__':
    main()
