#!/usr/bin/env python3
"""
Nepal Location Data Setup & Cleanup Script

This script:
1. Creates Province, District, LocalLevel tables
2. Imports official 753 local levels
3. Builds alias mapping for fuzzy matching
4. Maps existing cities to proper local levels
5. Prepares for doctor location cleanup

Usage:
    python nepal_location_setup.py --step 1  # Create tables & import data
    python nepal_location_setup.py --step 2  # Build alias mappings
    python nepal_location_setup.py --step 3  # Analyze existing cities
    python nepal_location_setup.py --step 4  # Map cities to local levels
"""

import json
import re
import argparse
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher

from app import app, db
from models import City, Doctor, Province, District, LocalLevel, LocationAlias
from sqlalchemy import text

# Data files - use relative path for production compatibility
import os
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nepal_admin_data')


# ============================================================
# COMMON ALIASES - Manual mappings for known variations
# ============================================================

KNOWN_ALIASES = {
    # Kathmandu variations
    'kathmandu': ['k.m.c', 'k.m.c.', 'kmc', 'kathmandu metropolitan', 'kathmandu metropolitan city', 'ktm'],
    'lalitpur': ['l.m.c', 'lmc', 'lalitpur metropolitan', 'lalitpur metropolitan city', 'patan'],
    'bhaktapur': ['bhaktapur municipality', 'bhadgaon'],
    'pokhara': ['pokhara metropolitan', 'pokhara metropolitan city', 'pokhara lekhnath'],
    'bharatpur': ['bharatpur metropolitan', 'bharatpur metropolitan city'],
    'biratnagar': ['biratnagar metropolitan', 'biratnagar metropolitan city'],
    'birgunj': ['birgunj metropolitan', 'birgunj metropolitan city'],

    # Common district/city confusions
    'chitwan': ['chitawan'],
    'dharan': ['dharan sub-metropolitan', 'dharan sub metropolitan'],
    'butwal': ['butwal sub-metropolitan', 'butwal sub metropolitan'],
    'hetauda': ['hetauda sub-metropolitan', 'hetauda sub metropolitan'],
    'itahari': ['itahari sub-metropolitan', 'itahari sub metropolitan'],
    'nepalgunj': ['nepalgunj sub-metropolitan', 'nepalgunj sub metropolitan', 'nepalganj'],
    'janakpur': ['janakpurdham', 'janakpur sub-metropolitan', 'janakpurdham sub-metropolitan'],
}


# ============================================================
# STEP 1: Create tables and import official data
# ============================================================

def step1_create_and_import():
    """Create tables and import official Nepal location data"""
    print("\n" + "=" * 60)
    print("STEP 1: Create Tables & Import Official Data")
    print("=" * 60)

    with app.app_context():
        # Create tables
        print("\n1. Creating tables...")
        db.create_all()
        print("   ✓ Tables created")

        # Check if already imported
        if Province.query.count() > 0:
            print("   ⚠ Data already imported. Skipping.")
            return

        # Load JSON data
        print("\n2. Loading JSON data...")
        with open(f'{DATA_DIR}/provinces.json', 'r') as f:
            provinces_data = json.load(f)
        with open(f'{DATA_DIR}/districts.json', 'r') as f:
            districts_data = json.load(f)
        with open(f'{DATA_DIR}/local_levels.json', 'r') as f:
            local_levels_data = json.load(f)
        with open(f'{DATA_DIR}/local_level_type.json', 'r') as f:
            level_types_data = {t['local_level_type_id']: t['name'] for t in json.load(f)}

        print(f"   ✓ Loaded {len(provinces_data)} provinces")
        print(f"   ✓ Loaded {len(districts_data)} districts")
        print(f"   ✓ Loaded {len(local_levels_data)} local levels")

        # Import provinces
        print("\n3. Importing provinces...")
        province_map = {}
        for p in provinces_data:
            province = Province(
                id=p['province_id'],
                name=p['name'],
                nepali_name=p['nepali_name']
            )
            db.session.add(province)
            province_map[p['province_id']] = province
        db.session.flush()
        print(f"   ✓ Imported {len(provinces_data)} provinces")

        # Import districts
        print("\n4. Importing districts...")
        district_map = {}
        for d in districts_data:
            district = District(
                id=d['district_id'],
                name=d['name'],
                nepali_name=d['nepali_name'],
                province_id=d['province_id']
            )
            db.session.add(district)
            district_map[d['district_id']] = district
        db.session.flush()
        print(f"   ✓ Imported {len(districts_data)} districts")

        # Import local levels
        print("\n5. Importing local levels...")
        for ll in local_levels_data:
            local_level = LocalLevel(
                id=ll['municipality_id'],
                name=ll['name'],
                nepali_name=ll['nepali_name'],
                district_id=ll['district_id'],
                level_type=level_types_data.get(ll['local_level_type_id'], 'Unknown')
            )
            db.session.add(local_level)

        db.session.commit()
        print(f"   ✓ Imported {len(local_levels_data)} local levels")

        print("\n" + "=" * 60)
        print("STEP 1 COMPLETE")
        print("=" * 60)


# ============================================================
# STEP 2: Build alias mappings
# ============================================================

def step2_build_aliases():
    """Build alias mappings for fuzzy matching"""
    print("\n" + "=" * 60)
    print("STEP 2: Build Alias Mappings")
    print("=" * 60)

    with app.app_context():
        # Clear existing aliases
        LocationAlias.query.delete()

        local_levels = LocalLevel.query.all()
        ll_by_name = {ll.name.lower(): ll for ll in local_levels}

        aliases_created = 0

        # Add known manual aliases
        print("\n1. Adding known aliases...")
        for canonical, aliases in KNOWN_ALIASES.items():
            ll = ll_by_name.get(canonical)
            if ll:
                for alias in aliases:
                    alias_obj = LocationAlias(
                        alias=alias.lower(),
                        local_level_id=ll.id,
                        alias_type='common_variant'
                    )
                    db.session.add(alias_obj)
                    aliases_created += 1

        # Add district names -> main local level mappings
        print("2. Adding district name mappings...")
        type_priority = {
            'Metropolitan City': 1,
            'Sub-Metropolitan City': 2,
            'Municipality': 3,
            'Rural Municipality': 4,
        }
        districts = District.query.all()
        for d in districts:
            # Find main local level (by type priority)
            local_levels_in_district = LocalLevel.query.filter_by(district_id=d.id).all()
            if local_levels_in_district:
                sorted_lls = sorted(local_levels_in_district, key=lambda x: type_priority.get(x.level_type, 5))
                main_ll = sorted_lls[0]
                # Add district name as alias
                alias_obj = LocationAlias(
                    alias=d.name.lower(),
                    local_level_id=main_ll.id,
                    alias_type='district_name'
                )
                db.session.add(alias_obj)
                aliases_created += 1
                # Also add district nepali name
                if d.nepali_name:
                    alias_obj = LocationAlias(
                        alias=d.nepali_name.lower(),
                        local_level_id=main_ll.id,
                        alias_type='district_nepali'
                    )
                    db.session.add(alias_obj)
                    aliases_created += 1

        # Add Nepali names as aliases
        print("3. Adding Nepali name aliases...")
        for ll in local_levels:
            if ll.nepali_name:
                alias_obj = LocationAlias(
                    alias=ll.nepali_name.lower(),
                    local_level_id=ll.id,
                    alias_type='nepali'
                )
                db.session.add(alias_obj)
                aliases_created += 1

        # Add "Municipality" and "Rural Municipality" suffix variants
        print("4. Adding suffix variants...")
        for ll in local_levels:
            name_lower = ll.name.lower()

            # Add with suffixes - English and Nepali
            if ll.level_type == 'Metropolitan City':
                variants = [
                    f'{name_lower} metropolitan',
                    f'{name_lower} metropolitan city',
                    f'{name_lower} mahanagarpalika',
                    f'{name_lower}mahanagarpalika',  # no space
                    f'{name_lower}metropolitan',
                    f'{name_lower}metropolitancity',
                ]
            elif ll.level_type == 'Sub-Metropolitan City':
                variants = [
                    f'{name_lower} sub-metropolitan',
                    f'{name_lower} sub metropolitan',
                    f'{name_lower} sub-metropolitan city',
                    f'{name_lower} upamahanagarpalika',
                    f'{name_lower}submetropolitan',
                    f'{name_lower}sub-metropolitan',
                ]
            elif ll.level_type == 'Municipality':
                variants = [
                    f'{name_lower} municipality',
                    f'{name_lower} nagarpalika',
                    f'{name_lower}nagarpalika',  # no space
                    f'{name_lower}municipality',
                ]
            elif ll.level_type == 'Rural Municipality':
                variants = [
                    f'{name_lower} rural municipality',
                    f'{name_lower} gaupalika',
                    f'{name_lower} gaunpalika',
                    f'{name_lower}gaupalika',  # no space
                    f'{name_lower}gaunpalika',
                    f'{name_lower} rural',
                ]
            else:
                variants = []

            for v in variants:
                alias_obj = LocationAlias(
                    alias=v,
                    local_level_id=ll.id,
                    alias_type='full_name'
                )
                db.session.add(alias_obj)
                aliases_created += 1

        db.session.commit()
        print(f"\n   ✓ Created {aliases_created} aliases")

        print("\n" + "=" * 60)
        print("STEP 2 COMPLETE")
        print("=" * 60)


# ============================================================
# STEP 3: Analyze existing cities
# ============================================================

def step3_analyze_cities():
    """Analyze existing cities and find matches"""
    print("\n" + "=" * 60)
    print("STEP 3: Analyze Existing Cities")
    print("=" * 60)

    with app.app_context():
        cities = City.query.all()
        local_levels = LocalLevel.query.all()
        aliases = LocationAlias.query.all()

        # Build lookup dictionaries
        ll_by_name = {ll.name.lower(): ll for ll in local_levels}
        ll_by_alias = {a.alias.lower(): a.local_level for a in aliases}

        # Merge lookups
        all_lookups = {**ll_by_name, **ll_by_alias}

        # Categorize cities
        exact_matches = []
        fuzzy_matches = []
        no_matches = []

        print(f"\nAnalyzing {len(cities)} cities...")

        for city in cities:
            city_name = city.name.lower().strip()

            # Remove common suffixes for matching
            clean_name = re.sub(r'\s*(municipality|rural municipality|metropolitan|sub-metropolitan|city|nagarpalika|gaupalika|gaunpalika)\s*$', '', city_name, flags=re.IGNORECASE).strip()

            # Exact match
            if city_name in all_lookups:
                exact_matches.append((city, all_lookups[city_name], 'exact'))
            elif clean_name in all_lookups:
                exact_matches.append((city, all_lookups[clean_name], 'cleaned'))
            else:
                # Fuzzy match
                best_match = None
                best_score = 0

                for ll in local_levels:
                    score = SequenceMatcher(None, clean_name, ll.name.lower()).ratio()
                    if score > best_score:
                        best_score = score
                        best_match = ll

                if best_score >= 0.8:
                    fuzzy_matches.append((city, best_match, best_score))
                else:
                    no_matches.append((city, best_match, best_score))

        # Print results
        print(f"\n=== RESULTS ===")
        print(f"Exact matches:    {len(exact_matches)}")
        print(f"Fuzzy matches:    {len(fuzzy_matches)} (score >= 0.8)")
        print(f"No matches:       {len(no_matches)}")

        # Show sample no-matches
        print(f"\n=== SAMPLE NO-MATCHES (first 30) ===")
        for city, best, score in sorted(no_matches, key=lambda x: -x[2])[:30]:
            print(f"  '{city.name}' -> best: '{best.name if best else 'None'}' (score: {score:.2f})")

        # Save results to file
        with open('/tmp/city_analysis.txt', 'w') as f:
            f.write("=== EXACT MATCHES ===\n")
            for city, ll, match_type in exact_matches:
                f.write(f"{city.id}\t{city.name}\t->\t{ll.name}\t({match_type})\n")

            f.write("\n=== FUZZY MATCHES ===\n")
            for city, ll, score in fuzzy_matches:
                f.write(f"{city.id}\t{city.name}\t->\t{ll.name}\t(score: {score:.2f})\n")

            f.write("\n=== NO MATCHES ===\n")
            for city, best, score in no_matches:
                f.write(f"{city.id}\t{city.name}\t->\tbest: {best.name if best else 'None'}\t(score: {score:.2f})\n")

        print(f"\n   Full analysis saved to /tmp/city_analysis.txt")

        print("\n" + "=" * 60)
        print("STEP 3 COMPLETE")
        print("=" * 60)

        return exact_matches, fuzzy_matches, no_matches


# ============================================================
# STEP 4: Map cities to local levels
# ============================================================

def step4_map_cities(dry_run=True):
    """Map existing cities to local levels"""
    print("\n" + "=" * 60)
    print(f"STEP 4: Map Cities to Local Levels {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print("=" * 60)

    # Run analysis first (just for display)
    exact_matches, fuzzy_matches, no_matches = step3_analyze_cities()

    if dry_run:
        print("\n   This is a DRY RUN. No changes made.")
        print("   Run with --execute to apply mappings.")
        return

    # Re-run mapping within same context to avoid detached object issues
    with app.app_context():
        cities = City.query.all()
        local_levels = LocalLevel.query.all()
        aliases = LocationAlias.query.all()

        # Build lookup dictionaries
        ll_by_name = {ll.name.lower(): ll for ll in local_levels}
        ll_by_alias = {a.alias.lower(): a.local_level for a in aliases}
        all_lookups = {**ll_by_name, **ll_by_alias}

        mapped_count = 0

        for city in cities:
            city_name = city.name.lower().strip()
            clean_name = re.sub(r'\s*(municipality|rural municipality|metropolitan|sub-metropolitan|city|nagarpalika|gaupalika|gaunpalika)\s*$', '', city_name, flags=re.IGNORECASE).strip()

            ll = None
            if city_name in all_lookups:
                ll = all_lookups[city_name]
            elif clean_name in all_lookups:
                ll = all_lookups[clean_name]
            else:
                # Fuzzy match
                best_match = None
                best_score = 0
                for local_level in local_levels:
                    score = SequenceMatcher(None, clean_name, local_level.name.lower()).ratio()
                    if score > best_score:
                        best_score = score
                        best_match = local_level
                if best_score >= 0.85:
                    ll = best_match

            if ll and ll.old_city_id is None:
                ll.old_city_id = city.id
                mapped_count += 1

        db.session.commit()
        print(f"\n   ✓ Mapped {mapped_count} cities to local levels")

    print("\n" + "=" * 60)
    print("STEP 4 COMPLETE")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='Nepal Location Setup')
    parser.add_argument('--step', type=int, choices=[1, 2, 3, 4], required=True,
                        help='Step to run: 1=Create/Import, 2=Aliases, 3=Analyze, 4=Map')
    parser.add_argument('--execute', action='store_true',
                        help='Actually execute changes (for step 4)')
    args = parser.parse_args()

    if args.step == 1:
        step1_create_and_import()
    elif args.step == 2:
        step2_build_aliases()
    elif args.step == 3:
        step3_analyze_cities()
    elif args.step == 4:
        step4_map_cities(dry_run=not args.execute)


if __name__ == '__main__':
    main()
