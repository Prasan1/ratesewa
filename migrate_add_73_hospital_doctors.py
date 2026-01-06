#!/usr/bin/env python3
"""
Migration: Import 73 new doctors from hospital website scraping (Jan 2026)
Run this in DigitalOcean App Platform Console after deploying code

This migration:
1. Imports 73 doctors from Om Hospital, B&B Hospital, DISHARC, STEM Center, and Kantipur Hospital
2. Automatically skips duplicates (safe to run multiple times)
3. Creates necessary specialties if they don't exist
4. Only adds doctors that don't already exist in production

Scraped from:
- Om Hospital (45 doctors)
- B&B Hospital (23 doctors)
- DISHARC (2 doctors with NMC)
- STEM Center (1 doctor with NMC)
- Kantipur Hospital (2 doctors)

Total: 73 doctors (3 with NMC numbers, 70 without)
"""

from app import app, db, generate_unique_slug
from models import Doctor, Specialty, City
import sys

# Embedded CSV data (from new_doctors.csv)
DOCTORS_DATA = [
    {"name": "Dr. Kristi Gupta", "nmc": "30126", "specialty": "Dental Surgery", "education": "Bachelor of Dental Surgery (Chitwan Medical College, TU)", "hospital": "STEM Center KTM"},
    {"name": "Asst. Prof. Dr. Bishal Karki", "nmc": "6863", "specialty": "Plastic & Cosmetic Surgery", "education": "", "hospital": "DISHARC"},
    {"name": "Assoc. Prof. Dr. Suchana Marahatta", "nmc": "8368", "specialty": "Aesthetic Dermatology", "education": "", "hospital": "DISHARC"},
    {"name": "Prof. Dr. A.K. Jha", "nmc": "", "specialty": "ENT Head and Neck Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Pushpa Prasad Sharma", "nmc": "", "specialty": "Neuropsychiatry", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Rupesh Raj Joshi", "nmc": "", "specialty": "ENT Head and Neck Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Jageshwor Gautam", "nmc": "", "specialty": "Gynaecology (Laparoscopy/Hysteroscopy)", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Ugra Narayan Pathak", "nmc": "", "specialty": "Internal Medicine", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Pramod K. Chhetri", "nmc": "", "specialty": "Nephrology", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Rabindra Shrestha", "nmc": "", "specialty": "Neurology", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Pawan Kumar Sultaniya", "nmc": "", "specialty": "Neurosurgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Bhola Raj Joshi", "nmc": "", "specialty": "Urology", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Sunil Kumar Sharma Dhakal", "nmc": "", "specialty": "GI Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Gaurav Raj Dhakal", "nmc": "", "specialty": "Spine Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Kamal Koirala", "nmc": "", "specialty": "General & GI Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Subodh Sagar Dhakal", "nmc": "", "specialty": "Pulmonology & Critical Care", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Chandramani Poudel", "nmc": "", "specialty": "Interventional Cardiology", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Rahul Pathak", "nmc": "", "specialty": "Gastroenterology", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Nabees M.S. Pradhan", "nmc": "", "specialty": "Orthopedic Surgery/Sports Medicine & Shoulder Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Abhushan S. Tuladhar", "nmc": "", "specialty": "Radiology", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Rabin Koirala", "nmc": "", "specialty": "GI Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Amit Shrestha", "nmc": "", "specialty": "Radiology", "education": "", "hospital": "Om Hospital"},
    {"name": "Assoc. Prof. Dr. Krishna Dhungana", "nmc": "", "specialty": "Neurology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Rajendra Pd. Baral", "nmc": "", "specialty": "Oncology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Rita Singh", "nmc": "", "specialty": "Pediatrics", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Sanubhai Khadka", "nmc": "", "specialty": "General Practice", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Subash Chandra Shah", "nmc": "", "specialty": "Pediatric Cardiology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Shrishti Shrestha", "nmc": "", "specialty": "Dermatology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Saubhagyaman Malla", "nmc": "", "specialty": "Anaesthesiology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Shyam Maharjan", "nmc": "", "specialty": "Anaesthesiology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Deepak Raj Pandey", "nmc": "", "specialty": "Gastroenterology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Suphatra Koirala", "nmc": "", "specialty": "Gynaecology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Louisa Rajput", "nmc": "", "specialty": "Gynaecology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Mamata Baral", "nmc": "", "specialty": "Gynaecology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Roshan Gongol", "nmc": "", "specialty": "Gynaecology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Dhiraj Manandhar", "nmc": "", "specialty": "Nephrology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Gisup Prasiko", "nmc": "", "specialty": "Oncology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Rajeev Kumar Deo", "nmc": "", "specialty": "Medical Oncology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Achyut Raj Bhandari", "nmc": "", "specialty": "Orthopedic Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Prakashnidhi Tiwari", "nmc": "", "specialty": "Pediatric Oncology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. M.P. Shrivastava", "nmc": "", "specialty": "Orthopedics", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Bijay Lingden", "nmc": "", "specialty": "", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Saroj Sedai", "nmc": "", "specialty": "Dermatology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Bajrang Kumar Rauniyar", "nmc": "", "specialty": "Endocrinology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Pratik Man Singh Gurung", "nmc": "", "specialty": "Urology & Robotic Surgery", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Shistata Raj Bhandari", "nmc": "", "specialty": "Dermatology", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Parashu Ram Ghimire", "nmc": "", "specialty": "Internal Medicine", "education": "", "hospital": "Om Hospital"},
    {"name": "Dr. Shiwa Upadhayay", "nmc": "", "specialty": "Ophthalmology, Neuro-ophthalmology", "education": "", "hospital": "Om Hospital"},
    {"name": "Prof. Dr. Ashok Kumar Banskota", "nmc": "", "specialty": "Orthopedic Surgery (Chief)", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Saroj Rijal", "nmc": "", "specialty": "Orthopedic Surgery", "education": "", "hospital": "B&B Hospital"},
    {"name": "Prof. Dr. Amit Joshi", "nmc": "", "specialty": "Orthopedic Surgery (Arthroscopy)", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Rajesh K. Chaudhary", "nmc": "", "specialty": "Orthopedic Surgery (Spine)", "education": "", "hospital": "B&B Hospital"},
    {"name": "Prof. Dr. Jagdish Lal Baidya", "nmc": "", "specialty": "General & Laparoscopic Surgery (Chief)", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. D.V. Karkee", "nmc": "", "specialty": "General & Laparoscopic Surgery", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Paleshwan Joshi Lakhey", "nmc": "", "specialty": "General Surgery (GI/HPB)", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Ijendra Prajapati", "nmc": "", "specialty": "General/GI Oncosurgery", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Ramesh Basnyat", "nmc": "", "specialty": "Pulmonology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Arbindra Pokhrel", "nmc": "", "specialty": "Hepatology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Prof. Dr. Kundu Yangzom", "nmc": "", "specialty": "Obstetrics & Gynecology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Nutan Sharma", "nmc": "", "specialty": "IVF & Reproductive Medicine (Robotic & Laparoscopic)", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Kishan Kumar Kushwaha", "nmc": "", "specialty": "Internal Medicine & Cardiology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Sanjay Singh K.C", "nmc": "", "specialty": "Cardiology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Inku Shrestha Basnet", "nmc": "", "specialty": "ENT (Head & Neck)", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Luna Mathema Shrestha", "nmc": "", "specialty": "ENT (Head & Neck/Allergy Specialist)", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Sristee Shrestha Prajapati", "nmc": "", "specialty": "Gynecologic Oncology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Roshan Prajapati", "nmc": "", "specialty": "Medical Oncology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Anoj Rajkarnikar", "nmc": "", "specialty": "Plastic & Reconstructive Surgery", "education": "", "hospital": "B&B Hospital"},
    {"name": "Prof. Dr. Sudarshan Narsingh Pradhan", "nmc": "", "specialty": "Neuropsychiatry", "education": "", "hospital": "B&B Hospital"},
    {"name": "Prof. Dr. Dwarika Prasad Shrestha", "nmc": "", "specialty": "Dermatology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Prasiddha Bikram Kadel", "nmc": "", "specialty": "Cardio-Thoracic & Vascular Surgery", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Ramnath Dhoan Shrestha", "nmc": "", "specialty": "Anesthesiology", "education": "", "hospital": "B&B Hospital"},
    {"name": "Dr. Avesh Koirala", "nmc": "", "specialty": "", "education": "", "hospital": "Kantipur Hospital"},
    {"name": "Dr. Rohit Chaudhary", "nmc": "", "specialty": "", "education": "", "hospital": "Kantipur Hospital"},
]


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

    # Map common variations to standard specialties
    specialty_mapping = {
        'Dental Surgery': 'Dentistry',
        'Dental': 'Dentistry',
        'Plastic & Cosmetic Surgery': 'Plastic Surgery',
        'Plastic & Reconstructive Surgery': 'Plastic Surgery',
        'Aesthetic Dermatology': 'Dermatology',
        'Orthopedic Surgery': 'Orthopedics',
        'Orthopedic Surgery (Spine)': 'Orthopedics',
        'Orthopedic Surgery (Arthroscopy)': 'Orthopedics',
        'Orthopedic Surgery (Chief)': 'Orthopedics',
        'Orthopedics': 'Orthopedics',
        'General & Laparoscopic Surgery': 'General Surgery',
        'General & Laparoscopic Surgery (Chief)': 'General Surgery',
        'General Surgery (GI/HPB)': 'General Surgery',
        'General/GI Oncosurgery': 'General Surgery',
        'Internal Medicine & Cardiology': 'Cardiology',
        'Interventional Cardiology': 'Cardiology',
        'Cardio-Thoracic & Vascular Surgery': 'Cardiology',
        'Obstetrics & Gynecology': 'Obstetrics and Gynecology',
        'Gynaecology': 'Obstetrics and Gynecology',
        'Gynaecology (Laparoscopy/Hysteroscopy)': 'Obstetrics and Gynecology',
        'IVF & Reproductive Medicine (Robotic & Laparoscopic)': 'Obstetrics and Gynecology',
        'Pediatric Cardiology': 'Pediatrics',
        'Pediatric Oncology': 'Pediatrics',
        'ENT (Head & Neck)': 'ENT',
        'ENT (Head & Neck/Allergy Specialist)': 'ENT',
        'ENT Head and Neck Surgery': 'ENT',
        'Medical Oncology': 'Oncology',
        'Gynecologic Oncology': 'Oncology',
        'Neuropsychiatry': 'Psychiatry',
        'Anaesthesiology': 'Anesthesiology',
        'Anesthesiology': 'Anesthesiology',
        'Ophthalmology, Neuro-ophthalmology': 'Ophthalmology',
        'Pulmonology & Critical Care': 'Pulmonology',
        'Hepatology': 'Gastroenterology',
        'GI Surgery': 'Gastroenterology',
        'General & GI Surgery': 'Gastroenterology',
        'Spine Surgery': 'Neurosurgery',
        'Urology & Robotic Surgery': 'Urology',
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

    return specialty


def get_city_for_hospital(hospital_name):
    """Get city based on hospital."""
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


def check_if_exists(name, nmc_number, nmc_cache, name_cache):
    """Check if doctor already exists in database using pre-built caches."""
    # Check by NMC number first (most reliable)
    if nmc_number and nmc_number.strip():
        if nmc_number.strip() in nmc_cache:
            return True, nmc_cache[nmc_number.strip()]

    # Check by normalized name
    normalized = normalize_name(name)
    if normalized and normalized in name_cache:
        return True, name_cache[normalized]

    return False, None


def main():
    with app.app_context():
        print("="*100)
        print("MIGRATION: Import 73 Hospital Doctors (Jan 2026)")
        print("="*100)
        print()
        print("This will import doctors from:")
        print("  - Om Hospital (45 doctors)")
        print("  - B&B Hospital (23 doctors)")
        print("  - DISHARC (2 doctors with NMC)")
        print("  - STEM Center (1 doctor with NMC)")
        print("  - Kantipur Hospital (2 doctors)")
        print()
        print("Total: 73 doctors")
        print()

        # Check current database state
        current_count = Doctor.query.count()
        print(f"Current doctors in database: {current_count}")
        print()

        # Build cache of existing doctors ONCE (efficient for large databases)
        print("Building cache of existing doctors...")
        nmc_cache = {}
        name_cache = {}

        all_doctors = Doctor.query.all()
        for doc in all_doctors:
            if doc.nmc_number:
                nmc_cache[doc.nmc_number] = doc
            normalized = normalize_name(doc.name)
            if normalized:
                name_cache[normalized] = doc

        print(f"Cache built: {len(nmc_cache)} doctors with NMC, {len(name_cache)} total doctors")
        print()

        # Process each doctor
        added = []
        skipped = []

        for i, row in enumerate(DOCTORS_DATA, 1):
            name = row['name'].strip()
            nmc = row['nmc'].strip() if row['nmc'] else ''
            specialty_name = row['specialty'].strip() if row['specialty'] else ''
            education = row['education'].strip() if row['education'] else ''
            hospital = row['hospital'].strip()

            # Check if exists using cache
            exists, existing_doc = check_if_exists(name, nmc, nmc_cache, name_cache)

            if exists:
                skipped.append(name)
                continue

            # Add to database
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

                if len(added) % 10 == 0:
                    print(f"  Added {len(added)} doctors so far...")

            except Exception as e:
                print(f"ERROR adding {name}: {e}")
                db.session.rollback()
                return

        # Commit all changes
        db.session.commit()
        print()
        print("✅ All changes committed to database")
        print()

        # Print summary
        print("="*100)
        print("MIGRATION SUMMARY")
        print("="*100)
        print(f"Doctors before migration: {current_count}")
        print(f"Doctors added: {len(added)}")
        print(f"Doctors skipped (already exist): {len(skipped)}")
        print(f"Doctors after migration: {Doctor.query.count()}")
        print()

        if added:
            print("="*100)
            print(f"ADDED DOCTORS ({len(added)})")
            print("="*100)

            # Group by hospital
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
                        print(f"    NMC: {doc['nmc']} ✅")
                    print(f"    Specialty: {doc['specialty']}")
                    print(f"    ID: {doc['id']}")

        if skipped:
            print()
            print("="*100)
            print(f"SKIPPED (Already in Database): {len(skipped)}")
            print("="*100)
            for name in skipped[:10]:
                print(f"  {name}")
            if len(skipped) > 10:
                print(f"  ... and {len(skipped) - 10} more")

        print()
        print("="*100)
        print("MIGRATION COMPLETE!")
        print("="*100)


if __name__ == '__main__':
    print("\n⚠️  WARNING: This will modify the production database!")
    print("Make sure you're running this in the correct environment.")
    print()

    response = input("Continue with migration? (yes/no): ")
    if response.lower() == 'yes':
        main()
    else:
        print("Migration cancelled.")
        sys.exit(0)
