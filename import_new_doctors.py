#!/usr/bin/env python3
"""
Import New Doctors from Hospital Scraping
Reads new_doctors.csv and adds all non-duplicate doctors to the database
"""

from app import app, db, generate_unique_slug
from models import Doctor, Specialty, City
import csv
import sys

def normalize_name(name):
    """Normalize doctor name for comparison."""
    if not name:
        return ""

    name = name.strip()
    # Remove common prefixes
    prefixes = ['dr.', 'dr', 'prof.', 'prof', 'professor', 'associate prof.',
                'asst. prof.', 'assoc. prof.', 'asst.', 'assoc.', 'pt.']
    name_lower = name.lower()

    for prefix in prefixes:
        if name_lower.startswith(prefix + ' '):
            name = name[len(prefix):].strip()
            name_lower = name.lower()

    return name_lower.strip()

def get_or_create_specialty(specialty_name):
    """Get existing specialty or create new one."""
    if not specialty_name or specialty_name.strip() == '':
        # Default to General Practice if no specialty
        specialty = Specialty.query.filter_by(name='General Practice').first()
        if not specialty:
            specialty = Specialty(name='General Practice')
            db.session.add(specialty)
            db.session.flush()
        return specialty

    # Clean up specialty name
    specialty_name = specialty_name.strip()

    # Map common variations
    specialty_mapping = {
        'Dental Surgery': 'Dentistry',
        'Dental': 'Dentistry',
        'Plastic & Cosmetic Surgery': 'Plastic Surgery',
        'Aesthetic Dermatology': 'Dermatology',
        'Orthopedic Surgery': 'Orthopedics',
        'Orthopedic Surgery (Spine)': 'Orthopedics',
        'Orthopedic Surgery (Arthroscopy)': 'Orthopedics',
        'Orthopedic Surgery (Arthroscopic)': 'Orthopedics',
        'Orthopedic Surgery (Chief)': 'Orthopedics',
        'Orthopedics': 'Orthopedics',
        'General & Laparoscopic Surgery': 'General Surgery',
        'General Surgery (GI/HPB)': 'General Surgery',
        'General/GI Oncosurgery': 'General Surgery',
        'Laparoscopic & Oncosurgery': 'General Surgery',
        'Urology (Uro-Oncology)': 'Urology',
        'Urology (Kidney Transplant)': 'Urology',
        'General & Urology': 'Urology',
        'Internal Medicine & Gastroenterology': 'Internal Medicine',
        'Internal Medicine & Endocrinology': 'Internal Medicine',
        'Internal Medicine & Cardiology': 'Cardiology',
        'Neurosurgery': 'Neurosurgery',
        'Obstetrics & Gynecology': 'Obstetrics and Gynecology',
        'Gynaecology': 'Obstetrics and Gynecology',
        'Gynaecology (Laparoscopy/Hysteroscopy)': 'Obstetrics and Gynecology',
        'IVF & Reproductive Medicine': 'Obstetrics and Gynecology',
        'IVF & Reproductive Medicine (Robotic & Laparoscopic)': 'Obstetrics and Gynecology',
        'Pediatrics (Laparoscopic)': 'Pediatrics',
        'Pediatric Cardiology': 'Pediatrics',
        'Pediatric Oncology': 'Pediatrics',
        'ENT (Head & Neck)': 'ENT',
        'ENT (Head & Neck, Vertigo)': 'ENT',
        'ENT (Head & Neck, Allergy)': 'ENT',
        'ENT (Head & Neck, Allergy Specialist)': 'ENT',
        'ENT Head and Neck Surgery': 'ENT',
        'Surgical Oncology': 'Oncology',
        'Gynecologic Oncology': 'Oncology',
        'Medical Oncology': 'Oncology',
        'Radiation Oncology': 'Oncology',
        'Hematology': 'Oncology',
        'Oncology': 'Oncology',
        'Oral & Maxillofacial Surgery': 'Dentistry',
        'Plastic & Reconstructive Surgery': 'Plastic Surgery',
        'Neuropsychiatry': 'Psychiatry',
        'Psychiatry': 'Psychiatry',
        'Dermatology': 'Dermatology',
        'Nephrology': 'Nephrology',
        'Cardio-Thoracic & Vascular Surgery': 'Cardiology',
        'Rheumatology': 'Internal Medicine',
        'Anesthesiology': 'Anesthesiology',
        'Anaesthesiology': 'Anesthesiology',
        'Ophthalmology': 'Ophthalmology',
        'Ophthalmology, Neuro-ophthalmology': 'Ophthalmology',
        'Pulmonology': 'Pulmonology',
        'Pulmonology & Critical Care': 'Pulmonology',
        'Hepatology': 'Gastroenterology',
        'GI Surgery': 'Gastroenterology',
        'Gastroenterology': 'Gastroenterology',
        'Endocrinology': 'Endocrinology',
        'Neurology': 'Neurology',
        'Spine Surgery': 'Neurosurgery',
        'Interventional Cardiology': 'Cardiology',
        'Cardiology': 'Cardiology',
        'Urology': 'Urology',
        'Urology & Robotic Surgery': 'Urology',
        'General Practice': 'General Practice',
    }

    # Try to map to standard specialty
    standard_name = specialty_mapping.get(specialty_name, specialty_name)

    # Try to find existing specialty
    specialty = Specialty.query.filter_by(name=standard_name).first()

    if not specialty:
        # Create new specialty
        specialty = Specialty(name=standard_name)
        db.session.add(specialty)
        db.session.flush()
        print(f"  Created new specialty: {standard_name}")

    return specialty

def get_city_for_hospital(hospital_name):
    """Get city based on hospital."""
    # Most hospitals are in Kathmandu
    hospital_city_map = {
        'STEM Center KTM': 'Kathmandu',
        'Om Hospital': 'Chabahil',
        'B&B Hospital': 'Gwarko',
        'Kantipur Hospital': 'Kathmandu',
        'DISHARC': 'Kathmandu',
    }

    city_name = hospital_city_map.get(hospital_name, 'Kathmandu')
    city = City.query.filter_by(name=city_name).first()

    if not city:
        # Fallback to Kathmandu
        city = City.query.filter_by(name='Kathmandu').first()

    return city

def check_if_exists(name, nmc_number):
    """Check if doctor already exists in database."""
    # Check by NMC number first (most reliable)
    if nmc_number and nmc_number.strip():
        existing = Doctor.query.filter_by(nmc_number=nmc_number.strip()).first()
        if existing:
            return True, existing, 'NMC'

    # Check by normalized name
    normalized = normalize_name(name)
    if normalized:
        all_doctors = Doctor.query.all()
        for doc in all_doctors:
            if normalize_name(doc.name) == normalized:
                return True, doc, 'Name'

    return False, None, None

def import_doctors(csv_file, dry_run=False):
    """Import doctors from CSV file."""

    with app.app_context():
        print("="*100)
        print("IMPORTING NEW DOCTORS FROM HOSPITAL SCRAPING")
        print("="*100)
        print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (will add to database)'}")
        print()

        # Read CSV
        doctors_to_import = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                doctors_to_import.append(row)

        print(f"Total doctors in CSV: {len(doctors_to_import)}")
        print()

        # Check each doctor
        added = []
        skipped = []
        excluded = []  # Non-doctors (physiotherapists, nutritionists)

        for i, row in enumerate(doctors_to_import, 1):
            name = row['Name'].strip()
            nmc = row['NMC Number'].strip() if row['NMC Number'] else ''
            specialty_name = row['Specialty'].strip() if row['Specialty'] else ''
            education = row['Education'].strip() if row['Education'] else ''
            hospital = row['Hospital'].strip()
            notes = row.get('Notes', '').strip()

            # Skip non-doctors (physiotherapists, nutritionists)
            if 'not a medical doctor' in notes.lower() or 'physiotherapist' in notes.lower() or 'nutritionist' in notes.lower():
                excluded.append({'name': name, 'reason': notes})
                continue

            # Check if exists
            exists, existing_doc, match_type = check_if_exists(name, nmc)

            if exists:
                skipped.append({
                    'name': name,
                    'nmc': nmc,
                    'match_type': match_type,
                    'existing': existing_doc
                })
                continue

            # Add to database
            if not dry_run:
                try:
                    specialty = get_or_create_specialty(specialty_name)
                    city = get_city_for_hospital(hospital)
                    slug = generate_unique_slug(name)

                    doctor = Doctor(
                        name=name,
                        slug=slug,
                        specialty_id=specialty.id,
                        city_id=city.id,
                        nmc_number=nmc if nmc else None,
                        education=education if education else None,
                        workplace=hospital,
                        is_verified=False,
                        is_featured=False
                    )

                    db.session.add(doctor)
                    db.session.flush()

                    added.append({
                        'name': name,
                        'nmc': nmc,
                        'specialty': specialty.name,
                        'hospital': hospital,
                        'id': doctor.id
                    })

                except Exception as e:
                    print(f"ERROR adding {name}: {e}")
                    db.session.rollback()
            else:
                # Dry run - just record what would be added
                specialty = get_or_create_specialty(specialty_name)
                added.append({
                    'name': name,
                    'nmc': nmc,
                    'specialty': specialty.name,
                    'hospital': hospital
                })

        # Commit all changes
        if not dry_run:
            db.session.commit()
            print("✅ All changes committed to database")

        # Print summary
        print()
        print("="*100)
        print("IMPORT SUMMARY")
        print("="*100)
        print(f"Total in CSV: {len(doctors_to_import)}")
        print(f"Added: {len(added)}")
        print(f"Skipped (already in DB): {len(skipped)}")
        print(f"Excluded (non-doctors): {len(excluded)}")
        print()

        if added:
            print("="*100)
            print(f"ADDED DOCTORS ({len(added)})")
            print("="*100)

            by_hospital = {}
            for doc in added:
                if doc['hospital'] not in by_hospital:
                    by_hospital[doc['hospital']] = []
                by_hospital[doc['hospital']].append(doc)

            for hospital, docs in sorted(by_hospital.items()):
                print(f"\n{hospital} ({len(docs)} doctors):")
                print("-" * 100)
                for doc in docs:
                    print(f"  {doc['name']}")
                    if doc['nmc']:
                        print(f"    NMC: {doc['nmc']}")
                    print(f"    Specialty: {doc['specialty']}")
                    if not dry_run:
                        print(f"    ID: {doc['id']}")
            print()

        if skipped:
            print("="*100)
            print(f"SKIPPED (Already in Database): {len(skipped)}")
            print("="*100)
            for doc in skipped[:10]:  # Show first 10
                print(f"  {doc['name']} - matched by {doc['match_type']}")
            if len(skipped) > 10:
                print(f"  ... and {len(skipped) - 10} more")
            print()

        if excluded:
            print("="*100)
            print(f"EXCLUDED (Non-doctors): {len(excluded)}")
            print("="*100)
            for doc in excluded:
                print(f"  {doc['name']} - {doc['reason']}")
            print()

        print("="*100)

if __name__ == '__main__':
    import_mode = '--live' in sys.argv

    if not import_mode:
        print("Running in DRY RUN mode. Use --live to actually add doctors to database.")
        print()

    import_doctors('new_doctors.csv', dry_run=not import_mode)
