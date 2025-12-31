"""
Seed script to populate Kathmandu doctors from 3 hospitals/clinics:
1. Metro Kathmandu Hospital (Narayan Gopal Chowk, Maharajgunj)
2. Clinic One Kathmandu
3. Kathmandu Medical College (Sinamangal)
"""

import os
import sys
from datetime import datetime

# Ensure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Doctor, City, Specialty, User
import re


def generate_slug(name):
    """Generate URL-friendly slug from name"""
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name).strip()
    slug = re.sub(r'[-\s]+', '-', name)
    return slug


def ensure_specialty_exists(specialty_name):
    """Get or create specialty"""
    specialty = Specialty.query.filter_by(name=specialty_name).first()
    if not specialty:
        specialty = Specialty(name=specialty_name, description=f"{specialty_name} specialist")
        db.session.add(specialty)
        db.session.flush()
    return specialty


def ensure_city_exists(city_name):
    """Get or create city"""
    city = City.query.filter_by(name=city_name).first()
    if not city:
        city = City(name=city_name, description=f"{city_name}, Nepal")
        db.session.add(city)
        db.session.flush()
    return city


# Metro Kathmandu Hospital Doctors (Narayan Gopal Chowk, Maharajgunj)
METRO_HOSPITAL_DOCTORS = [
    {"name": "Dr. Sweta Agrawal", "specialty": "General Physician", "education": "MBBS"},
    {"name": "Dr. Jyoti Bhattarai", "specialty": "Endocrinology", "education": "MBBS, MD"},
    {"name": "Dr. Madhu Pandey", "specialty": "Endocrinology", "education": "MBBS, MD"},
    {"name": "Dr. Binay Bhattarai", "specialty": "Endocrinology", "education": "MBBS, MD"},
    {"name": "Dr. Birat Krishna Timalsina", "specialty": "Cardiology", "education": "MBBS, MD, DM"},
    {"name": "Dr. Dipendra Lal Shrestha", "specialty": "General Medicine", "education": "MBBS, MD"},
    {"name": "Dr. Bikal Ghimire", "specialty": "Gastroenterology", "education": "MBBS, MS"},
    {"name": "Dr. Prasan Bir Singh Kansakar", "specialty": "Gastroenterology", "education": "MBBS, MS"},
    {"name": "Dr. Sangam Rayamajhi", "specialty": "Plastic Surgery", "education": "MBBS, MS, MCh"},
    {"name": "Dr. Ajay Rana", "specialty": "Orthopedics", "education": "MBBS, MS"},
    {"name": "Dr. Sumit Agrawal", "specialty": "Orthopedics", "education": "MBBS, MS"},
    {"name": "Dr. Gyanendra Shah", "specialty": "Orthopedics", "education": "MBBS, MS"},
    {"name": "Dr. Sagun Joshi", "specialty": "Orthopedics", "education": "MBBS, MS"},
    {"name": "Dr. Shankar Thapa", "specialty": "Orthopedics", "education": "MBBS, MS"},
    {"name": "Dr. Pramila Pradhan", "specialty": "Gynecology", "education": "MBBS, MD"},
    {"name": "Dr. Amrita Giri", "specialty": "Gynecology", "education": "MBBS, MD"},
    {"name": "Dr. Kavita Adhikari", "specialty": "Gynecology", "education": "MBBS, MD"},
    {"name": "Dr. Jasma Mally", "specialty": "Gynecology", "education": "MBBS, MD"},
    {"name": "Dr. Sujan Pradhan", "specialty": "Radiology", "education": "MBBS, MD"},
    {"name": "Prof. Dr. Desh Raj Kunwar", "specialty": "Psychiatry", "education": "MBBS, MD"},
    {"name": "Dr. Arun Raj Kunwar", "specialty": "Psychiatry", "education": "MBBS, MD, DM"},
    {"name": "Dr. Rishav Koirala", "specialty": "Psychiatry", "education": "MBBS, MD"},
    {"name": "Dr. Gunjan Dhoju", "specialty": "Psychiatry", "education": "MA Psychology"},
    {"name": "Dr. Krishna Sharma", "specialty": "Neurosurgery", "education": "MBBS, MS"},
    {"name": "Dr. Sanjesh Bhakta Shrestha", "specialty": "Urology", "education": "MBBS, MS"},
    {"name": "Dr. Ghanashyam Sigdel", "specialty": "Urology", "education": "MBBS, MS"},
    {"name": "Dr. Diwas Gnyawali", "specialty": "Urology", "education": "MBBS, MS"},
    {"name": "Dr. Surendra Bikram Adhikari", "specialty": "Urology", "education": "MBBS, MS"},
    {"name": "Dr. Kunjan Acharya", "specialty": "ENT", "education": "MBBS, MS"},
    {"name": "Dr. Bimal Lal Karn", "specialty": "Pediatrics", "education": "MBBS, MD"},
    {"name": "Dr. Suman Bikram Adhikari", "specialty": "Pediatrics", "education": "MBBS, MS"},
    {"name": "Dr. Diba Sharma", "specialty": "Nephrology", "education": "MBBS, MD, DM"},
    {"name": "Dr. Anurag Jha", "specialty": "Gastroenterology", "education": "MBBS, MD, DM"},
    {"name": "Dr. Tshering Wangdi Sherpa", "specialty": "Gastroenterology", "education": "MBBS, MD, DM"},
    {"name": "Dr. Sabina Shrestha", "specialty": "Pathology", "education": "MBBS, MD"},
    {"name": "Dr. Rajesh Bhurtel", "specialty": "Ophthalmology", "education": "MBBS, MS"},
    {"name": "Dr. Antiba Karki", "specialty": "Dentistry", "education": "BDS"},
    {"name": "Dr. Medina Shakya", "specialty": "Dermatology", "education": "MBBS, MD"},
    {"name": "Dr. Deependra Shrestha", "specialty": "ENT", "education": "MBBS, MS"},
    {"name": "Dr. Riskey Dev", "specialty": "ENT", "education": "MBBS, MS"},
    {"name": "Dr. Bijaya Kharel", "specialty": "ENT", "education": "MBBS, MS"},
    {"name": "Mr. Ishwor Budhathoki", "specialty": "Physiotherapy", "education": "BPT"},
]

# Clinic One Doctors (Multiple branches in Kathmandu)
CLINIC_ONE_DOCTORS = [
    {"name": "Dr. Rajesh Kumar Mandal", "specialty": "General Surgery", "education": "MBBS, MS, MCh", "nmc": "8325"},
    {"name": "Dr. Prerna Jha", "specialty": "Psychiatry", "education": "MBBS, MD", "nmc": "16964"},
    {"name": "Dr. Vijay Bhushan Dutta", "specialty": "ENT", "education": "MS (ENT)", "nmc": "8605"},
    {"name": "Dr. Jit Prakash Shrestha", "specialty": "Urology", "education": "MBBS, MS", "nmc": "6515"},
    {"name": "Dr. Mahesh Dahal", "specialty": "Endocrinology", "education": "MBBS, MD", "nmc": "6173"},
    {"name": "Dr. Tulika Dubey", "specialty": "ENT", "education": "MS (ENT)", "nmc": "10304"},
    {"name": "Dr. Yesha Amatya", "specialty": "Pediatrics", "education": "MBBS, MD", "nmc": "9006"},
    {"name": "Dr. Nabin Bahadur Basnet", "specialty": "Nephrology", "education": "MBBS, PhD", "nmc": "5559"},
    {"name": "Dr. Kabita Keyal", "specialty": "Pediatrics", "education": "MBBS, MD", "nmc": "4967"},
    {"name": "Dr. Banira Karki", "specialty": "Oncology", "education": "Fellowship Breast Oncosurgery", "nmc": "7625"},
    {"name": "Dr. Tseten Yonjen Tamang", "specialty": "General Surgery", "education": "MBBS, MS", "nmc": "6137"},
    {"name": "Dr. Pawan Singh Bhat", "specialty": "General Surgery", "education": "MS", "nmc": "7961"},
    {"name": "Dr. Dikshya Neupane", "specialty": "Psychiatry", "education": "MBBS, MD", "nmc": "26204"},
    {"name": "Dr. Punyaram Kharbuja", "specialty": "Gastroenterology", "education": "MBBS, MS", "nmc": "7240"},
    {"name": "Dr. Nipun Shrestha", "specialty": "Pediatrics", "education": "MBBS, PG", "nmc": "9771"},
    {"name": "Dr. Rupak Khadka", "specialty": "ENT", "education": "MBBS, MS", "nmc": "15976"},
    {"name": "Dr. Naresh Kharbuja", "specialty": "Neurology", "education": "MBBS, MD"},
    {"name": "Dr. Shri Krishna Awal", "specialty": "Orthopedics", "education": "MBBS, MS", "nmc": "8528"},
    {"name": "Dr. Ram Krishna Shrestha", "specialty": "Orthopedics", "education": "MBBS, MD", "nmc": "2862"},
    {"name": "Dr. Noora Pradhan", "specialty": "Gynecology", "education": "MBBS, MD", "nmc": "5688"},
    {"name": "Dr. Sanjay Shrestha", "specialty": "Cardiology", "education": "MBBS, MD, DM", "nmc": "10941"},
    {"name": "Dr. Shristi Subba Rai", "specialty": "ENT", "education": "MBBS, MS", "nmc": "20642"},
    {"name": "Dr. Wesh Ansari", "specialty": "Urology", "education": "MBBS, MS", "nmc": "13003"},
    {"name": "Dr. Raman Ghimire", "specialty": "Radiology", "education": "MD", "nmc": "16886"},
    {"name": "Dr. Sujan Pradhan", "specialty": "ENT", "education": "MBBS, MS", "nmc": "20642"},
    {"name": "Kusum Shree Niraula", "specialty": "Psychology", "education": "MA"},
]

# Kathmandu Medical College Doctors (Sinamangal)
KMC_DOCTORS = [
    {"name": "Dr. Subash Pant", "specialty": "Internal Medicine", "education": "MBBS, MD", "title": "HOD"},
    {"name": "Dr. Amir Bajracharya", "specialty": "Plastic Surgery", "education": "MBBS, MS, MCh", "title": "HOD"},
    {"name": "Dr. Ashish Kumar Ray", "specialty": "Pediatrics", "education": "MBBS, MD", "title": "HOD"},
    {"name": "Dr. Dipty Shrestha", "specialty": "Gynecology", "education": "MD, MS", "title": "Associate Professor"},
    {"name": "Dr. Rabin Maharjan", "specialty": "Internal Medicine", "education": "MBBS, MD", "title": "Lecturer"},
    {"name": "Dr. Nitesh Paudel", "specialty": "Internal Medicine", "education": "MBBS, MD", "title": "Lecturer"},
    {"name": "Dr. Pawana Kayastha", "specialty": "Pediatrics", "education": "MBBS, MD", "title": "Associate Professor"},
    {"name": "Dr. Ajay Sah", "specialty": "Internal Medicine", "education": "MBBS, MD", "title": "Lecturer"},
    {"name": "Dr. Prabin Khatri", "specialty": "Rheumatology", "education": "MBBS, MD", "title": "Associate Professor"},
    {"name": "Dr. Aabishkar Subedi", "specialty": "Internal Medicine", "education": "MBBS, MD", "title": "Lecturer"},
    {"name": "Dr. Parash Rayamajhi", "specialty": "Neurology", "education": "MBBS, MD, DM", "title": "HOD"},
    {"name": "Dr. Navin Kumar Mishra", "specialty": "Pulmonology", "education": "BS, MPH, MD", "title": "HOD"},
]


def estimate_experience(education):
    """Estimate years of experience based on education level"""
    if "DM" in education or "MCh" in education or "PhD" in education:
        return 15  # Super specialty
    elif "MD" in education or "MS" in education:
        return 10  # Specialty
    elif "Fellowship" in education or "PG" in education:
        return 8
    elif "MBBS" in education or "BDS" in education:
        return 5
    else:
        return 3


def seed_doctors():
    """Seed database with Kathmandu doctors"""

    with app.app_context():
        print("🏥 Starting Kathmandu Doctors Database Seeding...")

        # Get or create Kathmandu city
        kathmandu = ensure_city_exists("Kathmandu")
        print(f"✅ City: {kathmandu.name}")

        doctors_added = 0
        doctors_skipped = 0

        # Process Metro Hospital Doctors
        print("\n📍 Processing Metro Kathmandu Hospital doctors...")
        for doctor_data in METRO_HOSPITAL_DOCTORS:
            try:
                slug = generate_slug(doctor_data['name'])

                # Check if doctor already exists
                existing = Doctor.query.filter_by(slug=slug).first()
                if existing:
                    print(f"   ⚠️  Skipping {doctor_data['name']} (already exists)")
                    doctors_skipped += 1
                    continue

                # Get or create specialty
                specialty = ensure_specialty_exists(doctor_data['specialty'])

                # Create doctor
                doctor = Doctor(
                    name=doctor_data['name'],
                    slug=slug,
                    city_id=kathmandu.id,
                    specialty_id=specialty.id,
                    education=doctor_data.get('education', 'Not specified'),
                    experience=estimate_experience(doctor_data.get('education', '')),
                    description=f"{doctor_data['specialty']} at Metro Kathmandu Hospital, Narayan Gopal Chowk, Maharajgunj",
                    practice_address="Metro Kathmandu Hospital, Narayan Gopal Chowk, Maharajgunj, Kathmandu 44600, Nepal",
                    is_active=True,
                    is_featured=False,
                    is_verified=False
                )
                db.session.add(doctor)
                doctors_added += 1
                print(f"   ✅ Added: {doctor.name} ({doctor_data['specialty']})")

            except Exception as e:
                print(f"   ❌ Error adding {doctor_data['name']}: {e}")
                continue

        # Process Clinic One Doctors
        print("\n📍 Processing Clinic One doctors...")
        for doctor_data in CLINIC_ONE_DOCTORS:
            try:
                slug = generate_slug(doctor_data['name'])

                # Check if doctor already exists
                existing = Doctor.query.filter_by(slug=slug).first()
                if existing:
                    print(f"   ⚠️  Skipping {doctor_data['name']} (already exists)")
                    doctors_skipped += 1
                    continue

                # Get or create specialty
                specialty = ensure_specialty_exists(doctor_data['specialty'])

                # Create doctor
                doctor = Doctor(
                    name=doctor_data['name'],
                    slug=slug,
                    city_id=kathmandu.id,
                    specialty_id=specialty.id,
                    education=doctor_data.get('education', 'Not specified'),
                    experience=estimate_experience(doctor_data.get('education', '')),
                    description=f"{doctor_data['specialty']} at Clinic One Kathmandu",
                    practice_address="Clinic One, Multiple locations in Kathmandu Valley",
                    nmc_number=doctor_data.get('nmc'),
                    is_active=True,
                    is_featured=False,
                    is_verified=False
                )
                db.session.add(doctor)
                doctors_added += 1
                print(f"   ✅ Added: {doctor.name} ({doctor_data['specialty']}) - NMC: {doctor_data.get('nmc', 'N/A')}")

            except Exception as e:
                print(f"   ❌ Error adding {doctor_data['name']}: {e}")
                continue

        # Process KMC Doctors
        print("\n📍 Processing Kathmandu Medical College doctors...")
        for doctor_data in KMC_DOCTORS:
            try:
                slug = generate_slug(doctor_data['name'])

                # Check if doctor already exists
                existing = Doctor.query.filter_by(slug=slug).first()
                if existing:
                    print(f"   ⚠️  Skipping {doctor_data['name']} (already exists)")
                    doctors_skipped += 1
                    continue

                # Get or create specialty
                specialty = ensure_specialty_exists(doctor_data['specialty'])

                # Create doctor
                college_desc = f"{doctor_data.get('title', '')} - {doctor_data['specialty']}" if doctor_data.get('title') else doctor_data['specialty']
                doctor = Doctor(
                    name=doctor_data['name'],
                    slug=slug,
                    city_id=kathmandu.id,
                    specialty_id=specialty.id,
                    education=doctor_data.get('education', 'Not specified'),
                    college="Kathmandu Medical College",
                    experience=estimate_experience(doctor_data.get('education', '')),
                    description=f"{college_desc} at Kathmandu Medical College",
                    practice_address="Kathmandu Medical College, Sinamangal, Kathmandu",
                    is_active=True,
                    is_featured=False,
                    is_verified=False
                )
                db.session.add(doctor)
                doctors_added += 1
                print(f"   ✅ Added: {doctor.name} ({doctor_data['specialty']}) - {doctor_data.get('title', '')}")

            except Exception as e:
                print(f"   ❌ Error adding {doctor_data['name']}: {e}")
                continue

        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "="*60)
            print("✅ Database seeding completed successfully!")
            print(f"📊 Summary:")
            print(f"   - Doctors added: {doctors_added}")
            print(f"   - Doctors skipped (already exist): {doctors_skipped}")
            print(f"   - Total: {doctors_added + doctors_skipped}")
            print(f"   - City: Kathmandu")
            print(f"   - Sources: Metro Hospital (42), Clinic One (26), KMC (12)")
            print("="*60)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing to database: {e}")
            return False

        return True


if __name__ == '__main__':
    seed_doctors()
