#!/usr/bin/env python3
"""
Migrate existing workplace text data to structured DoctorWorkplace records.
This script parses the text-based workplace field and creates proper records.

Run: python migrate_workplaces.py
"""

import os
import sys
import re
from sqlalchemy import create_engine, text

# Database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/doctors.db')

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 60)
print("MIGRATING WORKPLACE DATA TO STRUCTURED FORMAT")
print("=" * 60)
print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}\n")

engine = create_engine(DATABASE_URL)

# First ensure the table exists
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS doctor_workplaces (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(300),
    city_id INTEGER,
    city_name VARCHAR(100),
    phone VARCHAR(20),
    display_order INTEGER DEFAULT 1,
    is_primary BOOLEAN DEFAULT FALSE,
    clinic_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

try:
    # Create table if not exists
    with engine.connect() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
        conn.commit()
    print("✓ Table doctor_workplaces ready\n")

    # Get all cities for matching
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM cities"))
        cities = {row[1].lower().strip(): row[0] for row in result.fetchall()}
    print(f"Loaded {len(cities)} cities for matching\n")

    # Get all clinics for matching
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM clinics WHERE is_active = true"))
        clinics = {row[1].lower().strip(): row[0] for row in result.fetchall()}
    print(f"Loaded {len(clinics)} clinics for matching\n")

    # Get doctors with workplace data but no structured workplaces yet
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT d.id, d.workplace
            FROM doctors d
            WHERE d.workplace IS NOT NULL
              AND d.workplace != ''
              AND NOT EXISTS (
                  SELECT 1 FROM doctor_workplaces dw WHERE dw.doctor_id = d.id
              )
        """))
        doctors = list(result.fetchall())

    print(f"Found {len(doctors)} doctors with workplace data to migrate\n")

    total_workplaces = 0
    total_doctors = 0

    for doctor_id, workplace_text in doctors:
        if not workplace_text or not workplace_text.strip():
            continue

        # Split by periods (each period-separated part is a location)
        locations = workplace_text.split('.')

        order = 1
        workplaces_created = 0

        for loc in locations:
            loc = loc.strip()
            if not loc:
                continue

            # Split by comma to get name and address parts
            parts = [p.strip() for p in loc.split(',')]

            if not parts or not parts[0]:
                continue

            clinic_name = parts[0]
            address_parts = parts[1:] if len(parts) > 1 else []

            # Try to identify city from address parts
            city_id = None
            city_name = None
            address = None

            if address_parts:
                # Last part is often the city
                for i, part in enumerate(reversed(address_parts)):
                    part_lower = part.lower().strip()
                    if part_lower in cities:
                        city_id = cities[part_lower]
                        # Everything before this is the address
                        if i > 0:
                            address = ', '.join(address_parts[:-i-1]) if len(address_parts) > i+1 else None
                        else:
                            address = ', '.join(address_parts[:-1]) if len(address_parts) > 1 else None
                        break
                else:
                    # No city match found, use all parts as address
                    address = ', '.join(address_parts)
                    # Try to extract city name from last part
                    if address_parts:
                        city_name = address_parts[-1]

            # Try to match clinic name to registered clinics
            clinic_id = None
            clinic_name_lower = clinic_name.lower().strip()
            if clinic_name_lower in clinics:
                clinic_id = clinics[clinic_name_lower]

            # Insert the workplace record
            try:
                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO doctor_workplaces
                        (doctor_id, name, address, city_id, city_name, display_order, is_primary, clinic_id)
                        VALUES (:doctor_id, :name, :address, :city_id, :city_name, :display_order, :is_primary, :clinic_id)
                    """), {
                        'doctor_id': doctor_id,
                        'name': clinic_name,
                        'address': address,
                        'city_id': city_id,
                        'city_name': city_name if not city_id else None,
                        'display_order': order,
                        'is_primary': order == 1,
                        'clinic_id': clinic_id
                    })
                    conn.commit()
                workplaces_created += 1
                order += 1
            except Exception as e:
                print(f"  Error creating workplace for doctor {doctor_id}: {e}")

        if workplaces_created > 0:
            total_workplaces += workplaces_created
            total_doctors += 1
            print(f"  Doctor {doctor_id}: Created {workplaces_created} workplace(s)")

    print(f"\n{'=' * 60}")
    print("MIGRATION COMPLETED!")
    print(f"{'=' * 60}")
    print(f"Doctors processed: {total_doctors}")
    print(f"Workplaces created: {total_workplaces}")

except Exception as e:
    print(f"\nMIGRATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
