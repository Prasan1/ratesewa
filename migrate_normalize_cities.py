#!/usr/bin/env python3
"""
Migration: Normalize and Deduplicate Cities

This script:
1. Merges city variations (e.g., "Kathmandu Metropolitan City" -> "Kathmandu")
2. Fixes typos and inconsistencies
3. Reduces 1,426 cities to a cleaner set

Run this in production console:
    python3 migrate_normalize_cities.py
"""

from app import app, db
from models import City, Doctor
import re

# City normalization mapping
# Maps variations to canonical city name
CITY_NORMALIZATIONS = {
    # Kathmandu variations
    "kathmandu metropolitan city": "Kathmandu",
    "kathmandu mahanagar palika": "Kathmandu",
    "kathmandu metropolitian city": "Kathmandu",
    "kathmandu metropolitan": "Kathmandu",
    "kathmandu municipality": "Kathmandu",
    "kathmandu metroplolitian city": "Kathmandu",

    # Lalitpur variations
    "lalitpur metropolitan city": "Lalitpur",
    "lalitpur municipality": "Lalitpur",
    "lalitpur sub metropolitan city": "Lalitpur",

    # Bhaktapur variations
    "bhaktapur municipality": "Bhaktapur",
    "bhaktapur metropolitan city": "Bhaktapur",

    # Pokhara variations
    "pokhara metropolitan": "Pokhara",
    "pokhara lekhnath": "Pokhara",
    "pokharalekhnath": "Pokhara",
    "pokhara lekhnath metropolitan city": "Pokhara",
    "pokhara sub metropoliton 17": "Pokhara",
    "pokhara metropolitan city": "Pokhara",
    "pokhara 12": "Pokhara",

    # Biratnagar variations
    "biratnagar metropolitan": "Biratnagar",
    "biratnagar s. mtr. city": "Biratnagar",
    "biratnagar submetropolitan city": "Biratnagar",
    "biratnagar sub-metropolitan city": "Biratnagar",

    # Bharatpur variations
    "bharatpur metropolitan city": "Bharatpur",
    "bharatpur municipality": "Bharatpur",

    # Birgunj/Birganj variations
    "birgunj": "Birgunj",
    "birganj": "Birgunj",
    "birgunj municipality": "Birgunj",
    "birgunj sub-metropolitan city": "Birgunj",

    # Dharan variations
    "dharan municipality": "Dharan",
    "dharan sub-metropolitan city": "Dharan",

    # Butwal variations
    "butwal municipality": "Butwal",
    "butwal sub-metropolitan city": "Butwal",

    # Janakpur variations
    "janakpur municipality": "Janakpur",
    "janakpur sub-metropolitan city": "Janakpur",
    "janakpurdham": "Janakpur",

    # Nepalgunj variations
    "nepalgunj municipality": "Nepalgunj",
    "nepalgunj sub-metropolitan city": "Nepalgunj",

    # Dhangadhi variations
    "dhangadhi municipality": "Dhangadhi",
    "dhangadhi sub-metropolitan city": "Dhangadhi",

    # Hetauda variations
    "hetauda municipality": "Hetauda",
    "hetauda sub-metropolitan city": "Hetauda",

    # Itahari variations
    "itahari municipality": "Itahari",
    "itahari sub-metropolitan city": "Itahari",

    # Birtamod variations (Jhapa district)
    "birtamode": "Birtamod",
    "birtamod municipality": "Birtamod",
}

def normalize_city_name(name):
    """
    Normalize city name by:
    1. Trimming whitespace
    2. Checking mapping table
    3. Removing common suffixes
    """
    if not name:
        return name

    # Trim and normalize
    normalized = name.strip()

    # Check exact match in mapping (case-insensitive)
    lower_name = normalized.lower()
    if lower_name in CITY_NORMALIZATIONS:
        return CITY_NORMALIZATIONS[lower_name]

    # Remove common suffixes if not in mapping
    suffixes_to_remove = [
        " metropolitan city",
        " municipality",
        " sub-metropolitan city",
        " sub metropolitan city",
        " mahanagar palika",
        " nagarpalika",
    ]

    for suffix in suffixes_to_remove:
        if normalized.lower().endswith(suffix):
            base_name = normalized[:-len(suffix)].strip()
            # Only remove if the base name exists or is a known city
            if len(base_name) > 3:  # Avoid removing from very short names
                return base_name.title()

    return normalized

def main():
    print("=" * 70)
    print("Migration: Normalize and Deduplicate Cities")
    print("=" * 70)
    print()

    with app.app_context():
        cities = City.query.all()
        print(f"Total cities before: {len(cities)}")
        print()

        # Step 1: Build normalization plan
        print("Step 1: Analyzing city variations...")
        print("-" * 70)

        city_mapping = {}  # old_city_id -> new_city_id
        canonical_cities = {}  # normalized_name -> City object

        for city in cities:
            normalized_name = normalize_city_name(city.name)

            # Find or create canonical city
            if normalized_name.lower() in canonical_cities:
                # This city should be merged into existing canonical city
                canonical_city = canonical_cities[normalized_name.lower()]
                if city.id != canonical_city.id:
                    city_mapping[city.id] = canonical_city.id
                    print(f"  Merge: '{city.name}' -> '{canonical_city.name}'")
            else:
                # This is the canonical city for this name
                canonical_cities[normalized_name.lower()] = city
                # Update city name to normalized version if different
                if city.name != normalized_name:
                    print(f"  Rename: '{city.name}' -> '{normalized_name}'")
                    city.name = normalized_name

        print()
        print(f"Cities to merge: {len(city_mapping)}")
        print()

        # Step 2: Update doctor records
        print("Step 2: Updating doctor records...")
        print("-" * 70)

        updated_count = 0
        for old_city_id, new_city_id in city_mapping.items():
            doctors = Doctor.query.filter_by(city_id=old_city_id).all()
            for doctor in doctors:
                doctor.city_id = new_city_id
                updated_count += 1

        db.session.commit()
        print(f"Updated {updated_count:,} doctor records")
        print()

        # Step 3: Delete merged cities
        print("Step 3: Removing duplicate cities...")
        print("-" * 70)

        for old_city_id in city_mapping.keys():
            city = City.query.get(old_city_id)
            if city:
                db.session.delete(city)

        db.session.commit()

        # Final count
        final_count = City.query.count()

        print()
        print("=" * 70)
        print("Migration Complete!")
        print("=" * 70)
        print(f"Cities before:  {len(cities):,}")
        print(f"Cities after:   {final_count:,}")
        print(f"Cities removed: {len(cities) - final_count:,}")
        print()

        # Show top cities after cleanup
        print("Top 15 cities after normalization:")
        from sqlalchemy import func
        top_cities = db.session.query(
            City.name,
            func.count(Doctor.id).label('doctor_count')
        ).outerjoin(Doctor).group_by(City.id).order_by(
            func.count(Doctor.id).desc()
        ).limit(15).all()

        for city_name, count in top_cities:
            print(f"  {city_name:30} -> {count:4} doctors")

        print()
        print("✅ Cities normalized and deduplicated!")
        print()

if __name__ == '__main__':
    main()
