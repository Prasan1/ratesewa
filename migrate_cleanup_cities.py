#!/usr/bin/env python3
"""
Migration: Clean up invalid city names and consolidate neighborhoods

This fixes:
1. House numbers mistaken as cities (e.g. "3/302", "21/430")
2. Pure numbers (e.g. "12", "155")
3. Common neighborhoods → parent city
4. Typos and invalid entries

Run BEFORE migrate_import_24k_doctors.py
"""

from app import app, db
from models import City, Doctor
from sqlalchemy import func, or_
import re


# Neighborhood → Parent City mapping
NEIGHBORHOOD_CONSOLIDATION = {
    # Kathmandu Valley neighborhoods
    'Baneshwor': 'Kathmandu',
    'Thamel': 'Kathmandu',
    'Naxal': 'Kathmandu',
    'Maitidevi': 'Kathmandu',
    'Gyaneshwor': 'Kathmandu',
    'GYANESHWOR': 'Kathmandu',
    'Kupondol': 'Kathmandu',
    'Sanepa': 'Kathmandu',
    'Jwalakhel': 'Kathmandu',
    'Sundhara': 'Kathmandu',
    'Tahachal': 'Kathmandu',
    'Baluwatar': 'Kathmandu',
    'Maharajgunj': 'Kathmandu',
    'Budhanilkantha': 'Kathmandu',
    'Koteshwor': 'Kathmandu',
    'Kalanki': 'Kathmandu',
    'Chabahil': 'Kathmandu',
    'Chabhil': 'Kathmandu',
    'Bansbari': 'Kathmandu',
    'Basundhara': 'Kathmandu',
    'kalimati': 'Kathmandu',
    'Gairidhara': 'Kathmandu',

    # Lalitpur neighborhoods
    'Patan': 'Lalitpur',
    'Patan-Dhoka': 'Lalitpur',
    'Patan dhoka': 'Lalitpur',
    'Pulchowk': 'Lalitpur',
    'Kupondole': 'Lalitpur',
    'Jawalakhel': 'Lalitpur',

    # Bhaktapur neighborhoods
    'Thimi': 'Bhaktapur',

    # Common variations
    'Birganj': 'Birgunj',
    'TUTH': 'Kathmandu',  # Teaching hospital
    'Bal Mandir': 'Kathmandu',
}


def is_invalid_city_name(name):
    """Check if city name is invalid (number, house address, etc.)"""
    name = name.strip()

    # Empty or too short
    if not name or len(name) < 2:
        return True

    # Pure numbers
    if name.isdigit():
        return True

    # House numbers (e.g., "3/302", "21/430", "1/753")
    if re.match(r'^\d+/\d+', name):
        return True

    # Mostly numbers (e.g., "01 bara", "04 syangja")
    if re.match(r'^\d+\s', name):
        return True

    # Single characters
    if len(name) <= 2 and not name.isalpha():
        return True

    # Just a comma
    if name == ',':
        return True

    return False


def cleanup_cities():
    """Clean up and consolidate city data"""
    print("="*60)
    print("CITY CLEANUP MIGRATION")
    print("="*60)

    with app.app_context():
        total_cities_before = City.query.count()
        print(f"\nCities before cleanup: {total_cities_before:,}")

        # Step 1: Delete invalid cities with no doctors
        print("\nStep 1: Removing invalid/empty cities...")
        invalid_count = 0

        for city in City.query.all():
            if is_invalid_city_name(city.name):
                doctor_count = Doctor.query.filter_by(city_id=city.id).count()

                if doctor_count == 0:
                    # Safe to delete - no doctors
                    db.session.delete(city)
                    invalid_count += 1
                else:
                    # Has doctors - need to reassign
                    print(f"  ⚠️  '{city.name}' has {doctor_count} doctors - setting to 'Unknown'")

                    # Get or create "Unknown" city
                    unknown = City.query.filter_by(name='Unknown').first()
                    if not unknown:
                        unknown = City(name='Unknown')
                        db.session.add(unknown)
                        db.session.flush()

                    # Move doctors
                    Doctor.query.filter_by(city_id=city.id).update({'city_id': unknown.id})
                    db.session.delete(city)
                    invalid_count += 1

        db.session.commit()
        print(f"  ✓ Removed {invalid_count} invalid cities")

        # Step 2: Consolidate neighborhoods into parent cities
        print("\nStep 2: Consolidating neighborhoods...")
        consolidated_count = 0

        for neighborhood, parent_city_name in NEIGHBORHOOD_CONSOLIDATION.items():
            neighborhood_city = City.query.filter_by(name=neighborhood).first()
            if not neighborhood_city:
                continue

            # Get or create parent city
            parent_city = City.query.filter_by(name=parent_city_name).first()
            if not parent_city:
                parent_city = City(name=parent_city_name)
                db.session.add(parent_city)
                db.session.flush()

            # Move doctors from neighborhood to parent
            doctor_count = Doctor.query.filter_by(city_id=neighborhood_city.id).count()
            if doctor_count > 0:
                Doctor.query.filter_by(city_id=neighborhood_city.id).update({'city_id': parent_city.id})
                print(f"  ✓ {neighborhood} → {parent_city_name} ({doctor_count} doctors)")
                consolidated_count += 1

            # Delete neighborhood city
            db.session.delete(neighborhood_city)

        db.session.commit()
        print(f"  ✓ Consolidated {consolidated_count} neighborhoods")

        # Step 3: Standardize case (fix duplicates like "kathmandu" vs "Kathmandu")
        print("\nStep 3: Standardizing city name cases...")
        case_fixes = 0

        # Get all cities
        cities = City.query.all()
        city_map = {}  # lowercase -> proper case City object

        for city in cities:
            lower_name = city.name.lower()

            if lower_name in city_map:
                # Duplicate! Merge into the first one
                primary_city = city_map[lower_name]
                doctor_count = Doctor.query.filter_by(city_id=city.id).count()

                if doctor_count > 0:
                    Doctor.query.filter_by(city_id=city.id).update({'city_id': primary_city.id})
                    print(f"  ✓ Merged '{city.name}' → '{primary_city.name}' ({doctor_count} doctors)")
                    case_fixes += 1

                db.session.delete(city)
            else:
                city_map[lower_name] = city

        db.session.commit()
        print(f"  ✓ Fixed {case_fixes} case duplicates")

        # Final stats
        total_cities_after = City.query.count()
        doctors_with_unknown = Doctor.query.join(City).filter(City.name == 'Unknown').count()

        print("\n" + "="*60)
        print("CLEANUP SUMMARY")
        print("="*60)
        print(f"Cities before: {total_cities_before:,}")
        print(f"Cities after:  {total_cities_after:,}")
        print(f"Cleaned up:    {total_cities_before - total_cities_after:,}")
        print(f"Doctors in 'Unknown': {doctors_with_unknown:,}")
        print("="*60)

        # Show top cities
        print("\nTop 15 cities by doctor count:")
        from sqlalchemy import func
        top_cities = db.session.query(
            City.name,
            func.count(Doctor.id).label('count')
        ).join(Doctor).group_by(City.name).order_by(func.count(Doctor.id).desc()).limit(15).all()

        for city, count in top_cities:
            print(f"  {city:30s}: {count:5d} doctors")

        print("\n✅ City cleanup completed!\n")


if __name__ == '__main__':
    cleanup_cities()
