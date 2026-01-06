#!/usr/bin/env python3
"""
Script to scrape doctor information from hospital websites and check against the database.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Database path
DB_PATH = '/home/ppaudyal/Documents/drprofile/doctor_directory/instance/doctors.db'

def get_existing_doctors():
    """Get all existing doctors from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT d.id, d.name, d.nmc_number, s.name as specialty, d.education, d.workplace
        FROM doctors d
        LEFT JOIN specialties s ON d.specialty_id = s.id
    """)

    doctors = cursor.fetchall()
    conn.close()

    # Create lookup dictionaries for quick checking
    doctors_by_name = {}
    doctors_by_nmc = {}

    for doc in doctors:
        doc_id, name, nmc, specialty, education, workplace = doc
        name_lower = name.lower().strip()
        doctors_by_name[name_lower] = {
            'id': doc_id,
            'name': name,
            'nmc': nmc,
            'specialty': specialty,
            'education': education,
            'workplace': workplace
        }
        if nmc:
            doctors_by_nmc[nmc.strip()] = {
                'id': doc_id,
                'name': name,
                'nmc': nmc,
                'specialty': specialty,
                'education': education,
                'workplace': workplace
            }

    return doctors_by_name, doctors_by_nmc, len(doctors)

def normalize_name(name):
    """Normalize doctor name for comparison."""
    if not name:
        return ""

    name = name.strip()
    # Remove common prefixes
    prefixes = ['dr.', 'dr', 'prof.', 'prof', 'associate prof.', 'asst. prof.']
    name_lower = name.lower()

    for prefix in prefixes:
        if name_lower.startswith(prefix + ' '):
            name = name[len(prefix):].strip()
            break
        elif name_lower.startswith(prefix):
            name = name[len(prefix):].strip()
            break

    return name.lower().strip()

def is_doctor_in_db(doctor_name, nmc_number, doctors_by_name, doctors_by_nmc):
    """Check if a doctor is already in the database."""
    # Check by NMC number first (most reliable)
    if nmc_number and nmc_number.strip() in doctors_by_nmc:
        return True, doctors_by_nmc[nmc_number.strip()]

    # Check by normalized name
    normalized = normalize_name(doctor_name)
    if normalized in doctors_by_name:
        return True, doctors_by_name[normalized]

    # Also check for partial matches (last name matching)
    if ' ' in normalized:
        last_name = normalized.split()[-1]
        for db_name in doctors_by_name.keys():
            if ' ' in db_name and db_name.split()[-1] == last_name:
                # Potential match - be conservative
                pass

    return False, None

def main():
    print("=" * 80)
    print("HOSPITAL DOCTOR SCRAPER - Database Check")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Load existing doctors from database
    print("Loading existing doctors from database...")
    doctors_by_name, doctors_by_nmc, total_in_db = get_existing_doctors()
    print(f"Found {total_in_db} doctors in database")
    print()

    # Hospital websites to scrape
    hospitals = [
        {
            'name': 'STEM Center KTM',
            'url': 'https://stemcenterktm.com/doctors',
            'doctors': []
        },
        {
            'name': 'Om Hospital',
            'url': 'https://omhospitalnepal.com/doctors',
            'doctors': []
        },
        {
            'name': 'B&B Hospital',
            'url': 'https://www.bbhospital.com.np/HomeUI/OurDoctor',
            'doctors': []
        },
        {
            'name': 'Norvic Hospital',
            'url': 'https://norvichospital.com/find-a-doctor',
            'doctors': []
        },
        {
            'name': 'Kantipur Hospital',
            'url': 'https://www.kantipurhospital.com.np/doctors.php',
            'doctors': []
        },
        {
            'name': 'Grande Hospital',
            'url': 'https://www.grandehospital.com/en/find-a-doctor',
            'doctors': []
        },
        {
            'name': 'DISHARC',
            'url': 'https://disharc.org/doctors/',
            'doctors': []
        }
    ]

    print("=" * 80)
    print("NOTE: This script structure is ready. Now scraping each hospital...")
    print("=" * 80)
    print()

    return hospitals, doctors_by_name, doctors_by_nmc

if __name__ == '__main__':
    hospitals, doctors_by_name, doctors_by_nmc = main()
    print("\nScript setup complete. Now proceeding to scrape websites...")
