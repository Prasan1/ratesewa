#!/usr/bin/env python3
"""
Migrate Doctor Locations from Cities to Local Levels

This script maps the messy 4890 cities to the canonical 753 local levels
using the location alias system, then updates doctors with proper local_level_id.

Usage:
    python migrate_doctor_locations.py           # Dry run - analyze only
    python migrate_doctor_locations.py --execute # Actually migrate
"""

import re
import argparse
from collections import defaultdict
from difflib import SequenceMatcher

from app import app, db
from models import City, Doctor, LocalLevel, LocationAlias


def normalize_name(name):
    """Normalize a name for matching"""
    if not name:
        return ''
    # Lowercase, strip, remove common suffixes
    name = name.lower().strip()
    name = re.sub(r'\s*(municipality|rural municipality|metropolitan|sub-metropolitan|city|nagarpalika|gaupalika|gaunpalika|mahanagarpalika|upamahanagarpalika)\s*$', '', name, flags=re.IGNORECASE).strip()
    return name


def build_lookup():
    """Build lookup table from aliases to local levels"""
    lookup = {}

    # Add local level names directly
    for ll in LocalLevel.query.all():
        lookup[normalize_name(ll.name)] = ll
        lookup[ll.name.lower()] = ll

    # Add aliases
    for alias in LocationAlias.query.all():
        lookup[alias.alias.lower()] = alias.local_level
        lookup[normalize_name(alias.alias)] = alias.local_level

    return lookup


def find_local_level(city_name, lookup, local_levels):
    """Find matching local level for a city name"""
    if not city_name:
        return None, 'empty', 0

    city_norm = normalize_name(city_name)
    city_lower = city_name.lower().strip()

    # Exact match on normalized name
    if city_norm in lookup:
        return lookup[city_norm], 'exact', 1.0

    # Exact match on lowercase
    if city_lower in lookup:
        return lookup[city_lower], 'exact', 1.0

    # Fuzzy match on local level names
    best_match = None
    best_score = 0
    for ll in local_levels:
        score = SequenceMatcher(None, city_norm, normalize_name(ll.name)).ratio()
        if score > best_score:
            best_score = score
            best_match = ll

    if best_score >= 0.85:
        return best_match, 'fuzzy', best_score

    return None, 'no_match', best_score


def migrate_doctor_locations(dry_run=True):
    """Migrate doctor locations from cities to local levels"""
    print("\n" + "=" * 70)
    print(f"  DOCTOR LOCATION MIGRATION {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print("=" * 70)

    with app.app_context():
        # Build lookup
        print("\n  Building alias lookup...")
        lookup = build_lookup()
        local_levels = LocalLevel.query.all()
        print(f"  Lookup has {len(lookup)} entries")

        # Get all cities
        cities = City.query.all()
        print(f"  Processing {len(cities)} cities...")

        # Map cities to local levels
        city_to_ll = {}  # city_id -> local_level
        stats = {
            'exact': 0,
            'fuzzy': 0,
            'no_match': 0,
            'empty': 0,
        }
        no_match_cities = []

        for city in cities:
            ll, match_type, score = find_local_level(city.name, lookup, local_levels)
            stats[match_type] += 1

            if ll:
                city_to_ll[city.id] = ll
            else:
                no_match_cities.append((city.id, city.name, score))

        print(f"\n  City mapping results:")
        print(f"    Exact matches: {stats['exact']}")
        print(f"    Fuzzy matches: {stats['fuzzy']}")
        print(f"    No matches: {stats['no_match']}")
        print(f"    Empty: {stats['empty']}")

        # Count doctors affected
        doctors_by_city = defaultdict(int)
        total_doctors = 0
        for d in Doctor.query.all():
            doctors_by_city[d.city_id] += 1
            total_doctors += 1

        doctors_mappable = sum(doctors_by_city[cid] for cid in city_to_ll.keys())
        doctors_unmapped = total_doctors - doctors_mappable

        print(f"\n  Doctor impact:")
        print(f"    Total doctors: {total_doctors}")
        print(f"    Can be mapped: {doctors_mappable} ({100*doctors_mappable/total_doctors:.1f}%)")
        print(f"    Cannot be mapped: {doctors_unmapped} ({100*doctors_unmapped/total_doctors:.1f}%)")

        # Show top unmapped cities by doctor count
        unmapped_with_counts = [
            (cid, name, score, doctors_by_city[cid])
            for cid, name, score in no_match_cities
        ]
        unmapped_with_counts.sort(key=lambda x: -x[3])

        print(f"\n  Top 30 unmapped cities by doctor count:")
        for cid, name, score, doc_count in unmapped_with_counts[:30]:
            print(f"    {doc_count:4d} doctors - '{name}'")

        if dry_run:
            print("\n  This was a DRY RUN. Run with --execute to migrate.")
            return

        # Actually migrate
        print("\n  Migrating doctors...")
        updated = 0
        batch_size = 1000

        doctors = Doctor.query.filter(Doctor.local_level_id.is_(None)).all()
        for i, doctor in enumerate(doctors):
            if doctor.city_id in city_to_ll:
                doctor.local_level_id = city_to_ll[doctor.city_id].id
                updated += 1

            if (i + 1) % batch_size == 0:
                db.session.commit()
                print(f"    Processed {i + 1} doctors...")

        db.session.commit()
        print(f"  Updated {updated} doctors with local_level_id!")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Migrate doctor locations')
    parser.add_argument('--execute', action='store_true', help='Actually migrate (default is dry run)')
    args = parser.parse_args()

    migrate_doctor_locations(dry_run=not args.execute)


if __name__ == '__main__':
    main()
