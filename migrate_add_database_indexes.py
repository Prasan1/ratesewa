#!/usr/bin/env python3
"""
Migration: Add Database Indexes for Performance

This script adds critical indexes to handle 20K+ doctors efficiently:
- nmc_number: for duplicate detection and lookups
- city_id: for city filtering
- specialty_id: for specialty filtering
- name: for name search
- is_active: for filtering active doctors

Run this in production console:
    python3 migrate_add_database_indexes.py
"""

from app import app, db
from sqlalchemy import text, inspect

def index_exists(inspector, table_name, index_name):
    """Check if an index already exists"""
    indexes = inspector.get_indexes(table_name)
    return any(idx['name'] == index_name for idx in indexes)

def main():
    print("=" * 70)
    print("Migration: Add Database Indexes for Performance")
    print("=" * 70)
    print()

    with app.app_context():
        inspector = inspect(db.engine)

        # Define indexes to create
        indexes_to_create = [
            {
                'name': 'ix_doctors_nmc_number',
                'table': 'doctors',
                'column': 'nmc_number',
                'unique': True,
                'description': 'For duplicate detection and NMC lookups'
            },
            {
                'name': 'ix_doctors_city_id',
                'table': 'doctors',
                'column': 'city_id',
                'unique': False,
                'description': 'For filtering by city'
            },
            {
                'name': 'ix_doctors_specialty_id',
                'table': 'doctors',
                'column': 'specialty_id',
                'unique': False,
                'description': 'For filtering by specialty'
            },
            {
                'name': 'ix_doctors_name',
                'table': 'doctors',
                'column': 'name',
                'unique': False,
                'description': 'For name search'
            },
            {
                'name': 'ix_doctors_is_active',
                'table': 'doctors',
                'column': 'is_active',
                'unique': False,
                'description': 'For filtering active doctors'
            },
            {
                'name': 'ix_doctors_is_verified',
                'table': 'doctors',
                'column': 'is_verified',
                'unique': False,
                'description': 'For filtering verified doctors'
            },
        ]

        created_count = 0
        skipped_count = 0

        print("Creating indexes...")
        print("-" * 70)

        for idx_config in indexes_to_create:
            idx_name = idx_config['name']
            table = idx_config['table']
            column = idx_config['column']
            unique = idx_config['unique']
            description = idx_config['description']

            # Check if index already exists
            if index_exists(inspector, table, idx_name):
                print(f"⏭️  SKIP: {idx_name} (already exists)")
                skipped_count += 1
                continue

            # Create index
            try:
                unique_clause = "UNIQUE" if unique else ""
                sql = f"CREATE {unique_clause} INDEX {idx_name} ON {table}({column})"

                db.session.execute(text(sql))
                db.session.commit()

                print(f"✅ CREATED: {idx_name}")
                print(f"   Column: {table}.{column}")
                print(f"   Purpose: {description}")
                created_count += 1
            except Exception as e:
                print(f"❌ ERROR: {idx_name}")
                print(f"   {str(e)}")
                db.session.rollback()

        print()
        print("=" * 70)
        print("Migration Complete!")
        print("=" * 70)
        print(f"Indexes created: {created_count}")
        print(f"Indexes skipped: {skipped_count}")
        print()

        # Show all indexes on doctors table
        print("All indexes on doctors table:")
        indexes = inspector.get_indexes('doctors')
        for idx in indexes:
            unique_str = "UNIQUE" if idx.get('unique') else "NON-UNIQUE"
            columns = ', '.join(idx['column_names'])
            print(f"  {idx['name']:35} {unique_str:12} ({columns})")

        print()
        print("✅ Database is now optimized for 20K+ doctors!")
        print()

if __name__ == '__main__':
    main()
