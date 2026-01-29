#!/usr/bin/env python3
"""
SAFE Import Script for New NMC Doctors

SAFETY FEATURES:
1. DRY RUN by default - shows what would happen without changes
2. INSERT ONLY - never updates existing records
3. Double-checks NMC number before every insert
4. Verified doctors explicitly protected
5. Detailed logging of every action
6. Batch commits with rollback on error

Usage:
    # Test first (dry run - DEFAULT):
    python import_new_doctors_safe.py

    # Actually import (requires explicit flag):
    python import_new_doctors_safe.py --execute

    # Limit rows for testing:
    python import_new_doctors_safe.py --limit 100
"""

import csv
import sys
import os
from datetime import datetime

from app import app, db
from models import Doctor, City, Specialty
from slugify import slugify
from difflib import SequenceMatcher
import re

# Import location models from setup script
from nepal_location_setup import LocalLevel, LocationAlias, District

# ============================================================
# SAFETY CONFIGURATION - DO NOT MODIFY
# ============================================================

# Verified doctors - NEVER touch these
VERIFIED_NMC_NUMBERS = frozenset(['20912', '23561', '29527', '20158'])

# Input file (deduplicated)
INPUT_FILE = '/home/ppaudyal/Documents/scraper/doctors-28660-to-40000/new_doctors_to_import.csv'

# Default specialty for doctors without one
DEFAULT_SPECIALTY = 'General Physician'

# Batch size for commits
BATCH_SIZE = 500

# ============================================================
# IMPORT LOGIC
# ============================================================

class SafeDoctorImporter:
    def __init__(self, dry_run=True, limit=None):
        self.dry_run = dry_run
        self.limit = limit
        self.stats = {
            'total_rows': 0,
            'skipped_verified': 0,
            'skipped_exists': 0,
            'skipped_invalid': 0,
            'created': 0,
            'errors': 0,
        }
        self.city_cache = {}
        self.specialty_cache = {}
        self.errors = []

    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        prefix = {'INFO': ' ', 'WARN': '⚠', 'ERROR': '✗', 'OK': '✓'}
        print(f"[{timestamp}] {prefix.get(level, ' ')} {message}")

    def load_caches(self):
        """Load existing cities and specialties"""
        self.log("Loading cities and specialties...")

        cities = City.query.all()
        for city in cities:
            # Store multiple lookup keys
            self.city_cache[city.name.lower().strip()] = city

        specialties = Specialty.query.all()
        for specialty in specialties:
            self.specialty_cache[specialty.name.lower().strip()] = specialty

        self.log(f"Loaded {len(self.city_cache)} cities, {len(self.specialty_cache)} specialties", 'OK')

        # Load location lookup (local levels + aliases)
        self.log("Loading location aliases...")
        self.local_level_lookup = {}

        # Add local level names
        local_levels = LocalLevel.query.all()
        for ll in local_levels:
            self.local_level_lookup[ll.name.lower()] = ll.name

        # Add aliases
        aliases = LocationAlias.query.all()
        for a in aliases:
            self.local_level_lookup[a.alias.lower()] = a.local_level.name

        self.log(f"Loaded {len(self.local_level_lookup)} location lookups", 'OK')

    def normalize_location(self, raw_location):
        """Normalize a location string to a proper local level name"""
        if not raw_location:
            return 'Kathmandu'

        location = raw_location.lower().strip()

        # Remove common suffixes for matching
        clean_location = re.sub(
            r'\s*(municipality|rural municipality|metropolitan|sub-metropolitan|city|nagarpalika|gaupalika|gaunpalika|vdc|mahanagarpalika)\s*$',
            '', location, flags=re.IGNORECASE
        ).strip()

        # Try exact match
        if location in self.local_level_lookup:
            return self.local_level_lookup[location]
        if clean_location in self.local_level_lookup:
            return self.local_level_lookup[clean_location]

        # Try fuzzy match
        best_match = None
        best_score = 0
        for key, value in self.local_level_lookup.items():
            score = SequenceMatcher(None, clean_location, key).ratio()
            if score > best_score:
                best_score = score
                best_match = value

        if best_score >= 0.8:
            return best_match

        # No good match - return original (title case)
        return raw_location.strip().title()

    def get_or_create_city(self, city_name):
        """Get city or create if not exists - uses normalized location"""
        if not city_name:
            return None

        # Normalize to proper local level name
        normalized = self.normalize_location(city_name)
        key = normalized.lower().strip()

        if key in self.city_cache:
            return self.city_cache[key]

        if not self.dry_run:
            city = City(name=normalized)
            db.session.add(city)
            db.session.flush()
            self.city_cache[key] = city
            if normalized.lower() != city_name.lower():
                self.log(f"Created city: {normalized} (from '{city_name}')")
            else:
                self.log(f"Created city: {city.name}")
            return city
        else:
            if normalized.lower() != city_name.lower():
                self.log(f"[DRY RUN] Would create city: {normalized} (from '{city_name}')")
            else:
                self.log(f"[DRY RUN] Would create city: {city_name}")
            return None

    def get_or_create_specialty(self, specialty_name):
        """Get specialty or create if not exists"""
        if not specialty_name:
            specialty_name = DEFAULT_SPECIALTY

        key = specialty_name.lower().strip()
        if key in self.specialty_cache:
            return self.specialty_cache[key]

        if not self.dry_run:
            specialty = Specialty(name=specialty_name.strip())
            db.session.add(specialty)
            db.session.flush()
            self.specialty_cache[key] = specialty
            self.log(f"Created specialty: {specialty.name}")
            return specialty
        else:
            self.log(f"[DRY RUN] Would create specialty: {specialty_name}")
            return None

    def extract_city_from_address(self, address):
        """Extract city name from NMC address format"""
        if not address:
            return 'Kathmandu'  # Default

        parts = [p.strip() for p in address.split(',') if p.strip()]
        if len(parts) >= 2:
            return parts[1].title()  # District/City is usually second
        elif len(parts) == 1:
            return parts[0].title()
        return 'Kathmandu'

    def map_degree_to_specialty(self, degree):
        """Map medical degree to specialty"""
        degree_map = {
            'mbbs': 'General Physician',
            'md': 'General Physician',
            'bds': 'Dentist',
            'mds': 'Dentist',
            'b.sc nursing': 'Nursing',
            'bsc nursing': 'Nursing',
        }
        if degree:
            return degree_map.get(degree.lower().strip(), DEFAULT_SPECIALTY)
        return DEFAULT_SPECIALTY

    def generate_unique_slug(self, name, existing_slugs):
        """Generate unique slug for doctor"""
        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        while slug in existing_slugs or Doctor.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        existing_slugs.add(slug)
        return slug

    def doctor_exists(self, nmc_number):
        """Check if doctor already exists - SAFETY CHECK"""
        return Doctor.query.filter_by(nmc_number=str(nmc_number)).first() is not None

    def run(self):
        """Run the import"""
        mode = "DRY RUN" if self.dry_run else "🔴 LIVE MODE"

        print("\n" + "=" * 70)
        print(f"  SAFE DOCTOR IMPORT - {mode}")
        print("=" * 70)

        if not self.dry_run:
            print("\n  ⚠️  WARNING: This will INSERT records into the database!")
            print("  ⚠️  Verified doctors are protected and will be skipped.\n")
            confirm = input("  Type 'yes' to continue: ")
            if confirm.lower() != 'yes':
                print("\n  Aborted.")
                return

        print(f"\n  Input file: {INPUT_FILE}")
        print(f"  Limit: {self.limit or 'None (all records)'}")
        print(f"  Protected NMCs: {', '.join(VERIFIED_NMC_NUMBERS)}")
        print()

        with app.app_context():
            self.load_caches()

            existing_slugs = set()
            batch = []

            with open(INPUT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    self.stats['total_rows'] += 1

                    # Check limit
                    if self.limit and self.stats['total_rows'] > self.limit:
                        break

                    # Progress
                    if self.stats['total_rows'] % 1000 == 0:
                        self.log(f"Processed {self.stats['total_rows']} rows...")

                    nmc_no = row.get('nmc_no', '').strip()
                    name = row.get('full_name', '').strip()
                    address = row.get('address', '').strip()
                    degree = row.get('degree', '').strip()

                    # SAFETY: Skip verified doctors
                    if nmc_no in VERIFIED_NMC_NUMBERS:
                        self.stats['skipped_verified'] += 1
                        self.log(f"PROTECTED: Skipping verified doctor NMC {nmc_no}", 'WARN')
                        continue

                    # SAFETY: Double-check if exists
                    if self.doctor_exists(nmc_no):
                        self.stats['skipped_exists'] += 1
                        continue

                    # Validate
                    if not nmc_no or not name:
                        self.stats['skipped_invalid'] += 1
                        continue

                    # Get city and specialty
                    city_name = self.extract_city_from_address(address)
                    specialty_name = self.map_degree_to_specialty(degree)

                    city = self.get_or_create_city(city_name)
                    specialty = self.get_or_create_specialty(specialty_name)

                    if self.dry_run:
                        self.stats['created'] += 1
                        continue

                    if not city or not specialty:
                        self.stats['skipped_invalid'] += 1
                        continue

                    # Create doctor
                    slug = self.generate_unique_slug(name, existing_slugs)

                    doctor = Doctor(
                        name=name,
                        slug=slug,
                        nmc_number=nmc_no,
                        city_id=city.id,
                        specialty_id=specialty.id,
                        education=degree or None,
                        is_verified=False,
                        is_active=True,
                        experience=0
                    )

                    batch.append(doctor)
                    self.stats['created'] += 1

                    # Batch commit
                    if len(batch) >= BATCH_SIZE:
                        try:
                            for doc in batch:
                                db.session.add(doc)
                            db.session.commit()
                            self.log(f"Committed batch of {len(batch)} doctors", 'OK')
                            batch = []
                        except Exception as e:
                            db.session.rollback()
                            self.stats['errors'] += len(batch)
                            self.stats['created'] -= len(batch)
                            self.errors.append(str(e))
                            self.log(f"Batch failed: {e}", 'ERROR')
                            batch = []

                # Final batch
                if batch and not self.dry_run:
                    try:
                        for doc in batch:
                            db.session.add(doc)
                        db.session.commit()
                        self.log(f"Committed final batch of {len(batch)} doctors", 'OK')
                    except Exception as e:
                        db.session.rollback()
                        self.stats['errors'] += len(batch)
                        self.stats['created'] -= len(batch)
                        self.errors.append(str(e))
                        self.log(f"Final batch failed: {e}", 'ERROR')

        # Print summary
        self.print_summary()

    def print_summary(self):
        print("\n" + "=" * 70)
        print("  IMPORT SUMMARY")
        print("=" * 70)
        print(f"""
  Total rows processed:    {self.stats['total_rows']}

  Skipped (verified):      {self.stats['skipped_verified']}
  Skipped (already exists):{self.stats['skipped_exists']}
  Skipped (invalid):       {self.stats['skipped_invalid']}

  {'Would create' if self.dry_run else 'Created'}:              {self.stats['created']}
  Errors:                  {self.stats['errors']}
""")

        if self.dry_run:
            print("  ℹ️  This was a DRY RUN. No changes were made.")
            print("  ℹ️  Run with --execute to actually import.\n")
        else:
            print("  ✅ Import complete!\n")

        if self.errors:
            print("  ERRORS:")
            for err in self.errors[:5]:
                print(f"    - {err}")
            if len(self.errors) > 5:
                print(f"    ... and {len(self.errors) - 5} more")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Safe doctor import script')
    parser.add_argument('--execute', action='store_true',
                        help='Actually execute import (default is dry run)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of rows to process')
    args = parser.parse_args()

    importer = SafeDoctorImporter(
        dry_run=not args.execute,
        limit=args.limit
    )
    importer.run()


if __name__ == '__main__':
    main()
