#!/usr/bin/env python3
"""
Import Rough Mapping CSV into Location Aliases

This script reads the rough-mapping-of-address.csv file and creates
location aliases that map NMC area names to canonical local levels.

Usage:
    python import_rough_mapping.py           # Dry run
    python import_rough_mapping.py --execute # Actually import
"""

import csv
import argparse
from difflib import SequenceMatcher

from app import app, db
from models import District, LocalLevel, LocationAlias

CSV_FILE = '/home/ppaudyal/Documents/rough-mapping-of-address.csv'


def normalize_name(name):
    """Normalize a name for matching"""
    if not name:
        return ''
    return name.lower().strip().replace('-', ' ').replace('_', ' ')


def find_best_local_level(area_name, district):
    """Find best matching local level in district for an area name"""
    if not district:
        return None

    local_levels = LocalLevel.query.filter_by(district_id=district.id).all()
    if not local_levels:
        return None

    area_norm = normalize_name(area_name)

    # Try exact match first
    for ll in local_levels:
        if normalize_name(ll.name) == area_norm:
            return ll

    # Try prefix/contains match
    for ll in local_levels:
        ll_norm = normalize_name(ll.name)
        if area_norm.startswith(ll_norm) or ll_norm.startswith(area_norm):
            return ll

    # Fuzzy match
    best_match = None
    best_score = 0
    for ll in local_levels:
        score = SequenceMatcher(None, area_norm, normalize_name(ll.name)).ratio()
        if score > best_score:
            best_score = score
            best_match = ll

    # If good enough fuzzy match, use it
    if best_score >= 0.6:
        return best_match

    # Default: return main local level (metro > sub-metro > municipality > rural)
    type_priority = {
        'Metropolitan City': 1,
        'Sub-Metropolitan City': 2,
        'Municipality': 3,
        'Rural Municipality': 4,
    }
    sorted_lls = sorted(local_levels, key=lambda x: type_priority.get(x.level_type, 5))
    return sorted_lls[0] if sorted_lls else None


def import_rough_mapping(dry_run=True):
    """Import rough mapping CSV into location aliases"""
    print("\n" + "=" * 70)
    print(f"  IMPORT ROUGH MAPPING {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print("=" * 70)

    with app.app_context():
        # Load district lookup
        districts = District.query.all()
        district_lookup = {normalize_name(d.name): d for d in districts}

        # Also add common variations
        district_lookup['sindhulpalchok'] = district_lookup.get('sindhupalchok')
        district_lookup['kapilvastu'] = district_lookup.get('kapilbastu')
        district_lookup['dang'] = district_lookup.get('dang')
        district_lookup['panchthar'] = district_lookup.get('pachthar')
        # Nawalparasi was split - default to West (Lumbini) for old references
        district_lookup['nawalparasi'] = district_lookup.get('nawalparasi west')
        district_lookup['nawalpur'] = district_lookup.get('nawalparari east')
        district_lookup['nawalparasi east'] = district_lookup.get('nawalparari east')  # Handle typo in DB
        district_lookup['tehrathum'] = district_lookup.get('terhathum')

        # Get existing aliases to avoid duplicates
        existing_aliases = {a.alias.lower() for a in LocationAlias.query.all()}

        stats = {
            'total': 0,
            'skipped_unknown': 0,
            'skipped_exists': 0,
            'skipped_district_not_found': 0,
            'skipped_no_match': 0,
            'created': 0,
        }

        new_aliases = []

        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                stats['total'] += 1

                area_name = row.get('Area Name', '').strip()
                district_name = row.get('District', '').strip()

                # Skip unknown/empty
                if not area_name or area_name.lower() == 'unknown':
                    stats['skipped_unknown'] += 1
                    continue

                # Skip if already exists
                if area_name.lower() in existing_aliases:
                    stats['skipped_exists'] += 1
                    continue

                # Find district
                district = district_lookup.get(normalize_name(district_name))
                if not district:
                    stats['skipped_district_not_found'] += 1
                    if stats['skipped_district_not_found'] <= 10:
                        print(f"  District not found: '{district_name}' for area '{area_name}'")
                    continue

                # Find local level
                local_level = find_best_local_level(area_name, district)
                if not local_level:
                    stats['skipped_no_match'] += 1
                    continue

                # Create alias
                new_aliases.append({
                    'alias': area_name.lower(),
                    'local_level_id': local_level.id,
                    'alias_type': 'nmc_area',
                    'local_level_name': local_level.name,
                    'district_name': district.name,
                })
                existing_aliases.add(area_name.lower())
                stats['created'] += 1

        # Print summary
        print(f"\n  Total rows: {stats['total']}")
        print(f"  Skipped (unknown/empty): {stats['skipped_unknown']}")
        print(f"  Skipped (already exists): {stats['skipped_exists']}")
        print(f"  Skipped (district not found): {stats['skipped_district_not_found']}")
        print(f"  Skipped (no local level match): {stats['skipped_no_match']}")
        print(f"  Would create: {stats['created']}")

        # Show sample of new aliases
        print(f"\n  Sample new aliases (first 20):")
        for a in new_aliases[:20]:
            print(f"    '{a['alias']}' -> {a['local_level_name']} ({a['district_name']})")

        if dry_run:
            print("\n  This was a DRY RUN. Run with --execute to import.")
        else:
            # Actually create aliases
            print("\n  Creating aliases...")
            for a in new_aliases:
                alias = LocationAlias(
                    alias=a['alias'],
                    local_level_id=a['local_level_id'],
                    alias_type=a['alias_type']
                )
                db.session.add(alias)

            db.session.commit()
            print(f"  Created {len(new_aliases)} new aliases!")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Import rough mapping CSV')
    parser.add_argument('--execute', action='store_true', help='Actually import (default is dry run)')
    args = parser.parse_args()

    import_rough_mapping(dry_run=not args.execute)


if __name__ == '__main__':
    main()
