#!/usr/bin/env python3
"""
Import 40K doctors from NMC scraper data into RankSewa database.

This script:
1. Reads NMC scraper data (CSV/JSON)
2. Skips doctors already in database (by NMC number)
3. Creates missing cities/specialties
4. Batch imports new doctors
5. Provides progress reporting

Usage:
    python import_nmc_doctors.py --file /path/to/nmc_data.csv --batch-size 500 --dry-run
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from app import app, db
from models import Doctor, City, Specialty
from sqlalchemy import text
from slugify import slugify


class NMCImporter:
    def __init__(self, file_path, batch_size=500, dry_run=False):
        self.file_path = file_path
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.stats = {
            'total_rows': 0,
            'skipped_existing': 0,
            'skipped_invalid': 0,
            'created': 0,
            'cities_created': 0,
            'specialties_created': 0
        }

        # Cache for cities and specialties to avoid repeated queries
        self.city_cache = {}
        self.specialty_cache = {}

    def load_caches(self):
        """Load existing cities and specialties into cache"""
        print("Loading cities and specialties into cache...")

        with app.app_context():
            cities = City.query.all()
            for city in cities:
                self.city_cache[city.name.lower()] = city

            specialties = Specialty.query.all()
            for specialty in specialties:
                self.specialty_cache[specialty.name.lower()] = specialty

        print(f"  ✓ Loaded {len(self.city_cache)} cities")
        print(f"  ✓ Loaded {len(self.specialty_cache)} specialties")

    def get_or_create_city(self, city_name):
        """Get existing city or create new one"""
        if not city_name or city_name.strip() == '':
            return None

        city_name_lower = city_name.strip().lower()

        if city_name_lower in self.city_cache:
            return self.city_cache[city_name_lower]

        # Create new city
        if not self.dry_run:
            city = City(name=city_name.strip())
            db.session.add(city)
            db.session.flush()  # Get ID without committing
            self.city_cache[city_name_lower] = city
            self.stats['cities_created'] += 1
            return city
        else:
            print(f"  [DRY RUN] Would create city: {city_name}")
            return None

    def get_or_create_specialty(self, specialty_name):
        """Get existing specialty or create new one"""
        if not specialty_name or specialty_name.strip() == '':
            return None

        specialty_name_lower = specialty_name.strip().lower()

        if specialty_name_lower in self.specialty_cache:
            return self.specialty_cache[specialty_name_lower]

        # Create new specialty
        if not self.dry_run:
            specialty = Specialty(name=specialty_name.strip())
            db.session.add(specialty)
            db.session.flush()  # Get ID without committing
            self.specialty_cache[specialty_name_lower] = specialty
            self.stats['specialties_created'] += 1
            return specialty
        else:
            print(f"  [DRY RUN] Would create specialty: {specialty_name}")
            return None

    def doctor_exists(self, nmc_number, name):
        """Check if doctor with NMC number or similar name already exists"""
        # Check by NMC number (most reliable)
        if Doctor.query.filter_by(nmc_number=nmc_number).first():
            return True

        # Check by exact name match (case-insensitive)
        # This catches duplicates where NMC number wasn't filled in
        if Doctor.query.filter(Doctor.name.ilike(name)).first():
            return True

        return False

    def parse_csv_row(self, row):
        """
        Parse a CSV row into doctor data.
        NMC CSV columns:
        - nmc_no (required)
        - full_name (required)
        - address (contains city - format: "Place , District," OR "City,")
        - gender (not used)
        - degree (maps to education)
        """
        # Extract city from address field
        # Formats: "Place, District," OR "City," OR "Place, District"
        address = row.get('address', '').strip()
        city_name = ''
        if address:
            parts = [p.strip() for p in address.split(',') if p.strip()]
            if len(parts) >= 2:
                # Format: "Place, District" - use district
                city_name = parts[1]
            elif len(parts) == 1:
                # Format: "City," or "City" - use first part
                city_name = parts[0]

        return {
            'nmc_number': row.get('nmc_no', '').strip(),
            'name': row.get('full_name', '').strip(),
            'city': city_name,
            'specialty': row.get('specialty', '').strip(),  # Will be empty for NMC data
            'education': row.get('degree', '').strip(),
            'workplace': row.get('workplace', '').strip(),
            'phone_number': row.get('phone', '').strip(),
        }

    def validate_doctor_data(self, data):
        """Validate required fields"""
        if not data['nmc_number']:
            return False, "Missing NMC number"
        if not data['name']:
            return False, "Missing name"
        if not data['city']:
            return False, "Missing city"
        # Specialty is optional for NMC data (will default to General Physician)
        return True, None

    def create_doctor(self, data, city, specialty):
        """Create a new doctor record"""
        # Generate unique slug
        base_slug = slugify(data['name'])
        slug = base_slug
        counter = 1

        while Doctor.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        doctor = Doctor(
            name=data['name'],
            slug=slug,
            nmc_number=data['nmc_number'],
            city_id=city.id,
            specialty_id=specialty.id,
            education=data.get('education') or None,
            workplace=data.get('workplace') or None,
            phone_number=data.get('phone_number') or None,
            is_verified=False,  # NMC scraped but not self-verified
            is_active=True,
            experience=0  # Unknown, can be updated later
        )

        return doctor

    def import_from_csv(self):
        """Import doctors from CSV file"""
        print(f"\n{'='*60}")
        print(f"NMC Doctor Import - {'DRY RUN' if self.dry_run else 'LIVE MODE'}")
        print(f"{'='*60}\n")
        print(f"Reading from: {self.file_path}")
        print(f"Batch size: {self.batch_size}\n")

        self.load_caches()

        doctors_batch = []
        batch_slugs = set()  # Track slugs in current batch to avoid duplicates
        batch_nmc_numbers = set()  # Track NMC numbers in current batch

        with app.app_context():
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    self.stats['total_rows'] += 1

                    # Progress indicator
                    if self.stats['total_rows'] % 1000 == 0:
                        print(f"  Processed {self.stats['total_rows']} rows...")

                    # Parse row
                    data = self.parse_csv_row(row)

                    # Validate
                    is_valid, error = self.validate_doctor_data(data)
                    if not is_valid:
                        self.stats['skipped_invalid'] += 1
                        if self.stats['total_rows'] <= 10:  # Show first few errors
                            print(f"  ⚠ Row {self.stats['total_rows']}: {error}")
                        continue

                    # Check if exists (by NMC number or name)
                    if self.doctor_exists(data['nmc_number'], data['name']):
                        self.stats['skipped_existing'] += 1
                        continue

                    # Check for duplicates in current batch (by NMC number)
                    if data['nmc_number'] in batch_nmc_numbers:
                        self.stats['skipped_existing'] += 1
                        continue

                    # Get or create city and specialty
                    city = self.get_or_create_city(data['city'])
                    specialty = self.get_or_create_specialty(data['specialty'])

                    # If specialty is missing (common for NMC data), default to General Physician
                    if not specialty:
                        specialty = self.get_or_create_specialty('General Physician')

                    if not city:
                        self.stats['skipped_invalid'] += 1
                        if self.stats['total_rows'] <= 10:  # Show first few errors
                            print(f"  ⚠ Row {self.stats['total_rows']}: Invalid city: {data['city']}")
                        continue

                    # Create doctor
                    if not self.dry_run:
                        doctor = self.create_doctor(data, city, specialty)
                        db.session.add(doctor)  # Regular add instead of bulk
                        batch_nmc_numbers.add(data['nmc_number'])  # Track in batch
                        self.stats['created'] += 1

                        # Batch commit (commit after accumulating batch_size records)
                        if self.stats['created'] % self.batch_size == 0:
                            db.session.commit()
                            print(f"  ✓ Committed {self.stats['created']} doctors so far...")
                            batch_slugs = set()  # Clear batch tracking
                            batch_nmc_numbers = set()  # Clear batch tracking
                    else:
                        self.stats['created'] += 1
                        if self.stats['total_rows'] <= 10:
                            print(f"  [DRY RUN] Would create: {data['name']} ({data['nmc_number']})")

                # Commit any remaining doctors
                if not self.dry_run and self.stats['created'] > 0:
                    db.session.commit()
                    print(f"  ✓ Final commit completed!")

        self.print_summary()

    def print_summary(self):
        """Print import summary"""
        print(f"\n{'='*60}")
        print("Import Summary")
        print(f"{'='*60}")
        print(f"Total rows processed:     {self.stats['total_rows']:,}")
        print(f"Skipped (already exists): {self.stats['skipped_existing']:,}")
        print(f"Skipped (invalid data):   {self.stats['skipped_invalid']:,}")
        print(f"Doctors created:          {self.stats['created']:,}")
        print(f"Cities created:           {self.stats['cities_created']:,}")
        print(f"Specialties created:      {self.stats['specialties_created']:,}")
        print(f"{'='*60}\n")

        if self.dry_run:
            print("⚠️  This was a DRY RUN - no data was actually imported.")
            print("   Run without --dry-run to perform actual import.\n")


def main():
    parser = argparse.ArgumentParser(description='Import NMC doctors into RankSewa')
    parser.add_argument('--file', required=True, help='Path to CSV file with NMC data')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for inserts (default: 500)')
    parser.add_argument('--dry-run', action='store_true', help='Run without actually importing (test mode)')

    args = parser.parse_args()

    importer = NMCImporter(
        file_path=args.file,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )

    importer.import_from_csv()


if __name__ == '__main__':
    main()
