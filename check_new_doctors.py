#!/usr/bin/env python3
"""
Script to check which scraped doctors are NEW (not in database)
"""

import sqlite3
from collections import defaultdict

# Database path
DB_PATH = '/home/ppaudyal/Documents/drprofile/doctor_directory/instance/doctors.db'

def normalize_name(name):
    """Normalize doctor name for comparison."""
    if not name:
        return ""

    name = name.strip()
    # Remove common prefixes
    prefixes = ['dr.', 'dr', 'prof.', 'prof', 'professor', 'associate prof.', 'asst. prof.', 'assoc. prof.', 'asst.', 'assoc.']
    name_lower = name.lower()

    for prefix in prefixes:
        if name_lower.startswith(prefix + ' '):
            name = name[len(prefix):].strip()
            name_lower = name.lower()

    return name_lower.strip()

def get_existing_doctors():
    """Get all existing doctors from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT d.id, d.name, d.nmc_number, s.name as specialty, d.education, d.workplace, c.name as city
        FROM doctors d
        LEFT JOIN specialties s ON d.specialty_id = s.id
        LEFT JOIN cities c ON d.city_id = c.id
    """)

    doctors = cursor.fetchall()
    conn.close()

    # Create lookup dictionaries
    doctors_by_nmc = {}
    doctors_by_name = {}

    for doc in doctors:
        doc_id, name, nmc, specialty, education, workplace, city = doc

        # Index by NMC number
        if nmc:
            doctors_by_nmc[nmc.strip()] = {
                'id': doc_id,
                'name': name,
                'nmc': nmc,
                'specialty': specialty,
                'education': education,
                'workplace': workplace,
                'city': city
            }

        # Index by normalized name
        normalized = normalize_name(name)
        if normalized:
            doctors_by_name[normalized] = {
                'id': doc_id,
                'name': name,
                'nmc': nmc,
                'specialty': specialty,
                'education': education,
                'workplace': workplace,
                'city': city
            }

    return doctors_by_nmc, doctors_by_name, len(doctors)

def check_doctor(name, nmc, specialty, education, hospital, doctors_by_nmc, doctors_by_name):
    """Check if doctor is in database. Returns (in_db, match_info)"""

    # First check by NMC (most reliable)
    if nmc:
        nmc_clean = str(nmc).strip()
        if nmc_clean in doctors_by_nmc:
            return True, doctors_by_nmc[nmc_clean]

    # Check by name
    normalized = normalize_name(name)
    if normalized in doctors_by_name:
        return True, doctors_by_name[normalized]

    return False, None

# Scraped data from hospitals
stem_center_doctors = [
    {"name": "Dr. Bajarang Kumar Rauniyar", "nmc": "6895", "specialty": "Endocrinology", "education": "MD Endocrinology & Metabolism (BSMMU, Bangladesh); MBBS (Kathmandu University)"},
    {"name": "Dr. Rashmi Bastakoti", "nmc": "5555", "specialty": "Obstetrics & Gynecology", "education": "MD Obstetrics & Gynecology; MBBS"},
    {"name": "Dr. Amrit Rijal", "nmc": "13757", "specialty": "Endocrinology", "education": "MD Internal Medicine & Endocrinology (BSMMU, Dhaka); MBBS (KU)"},
    {"name": "Dr. Deepak Raj Pandey", "nmc": "5257", "specialty": "Gastroenterology", "education": "MD Gastroenterology & Hepatology; MD Internal Medicine; MBBS"},
    {"name": "Dr. Bashanta Baral", "nmc": "8232", "specialty": "Urology", "education": "MS Urology (BSMMU, Bangladesh); MBBS (KU)"},
    {"name": "Dr. Samir Keshari Baidya", "nmc": "9101", "specialty": "Nephrology", "education": "DM Nephrology; Internal Medicine residency (Philippines); MBBS (2010)"},
    {"name": "Dr. Saroj Prasad Gaudel", "nmc": "9469", "specialty": "Internal Medicine", "education": "MD Internal Medicine; MBBS"},
    {"name": "Dr. Mitesh Yadav", "nmc": "14526", "specialty": "Pediatrics", "education": "MD Pediatrics (NAMS); MBBS (Nepalgunj Medical College)"},
    {"name": "Dr. Surakshya Joshi", "nmc": "8198", "specialty": "Cardiology", "education": "FCPS Cardiology (Pakistan); MBBS (Liaquat University)"},
    {"name": "Dr. Anzil Mani Singh Maharjan", "nmc": "5614", "specialty": "Neurology", "education": "MD Neurology (BSMMU, Dhaka); MBBS"},
    {"name": "Dr. Niresh Shrestha", "nmc": "10703", "specialty": "Orthopedics", "education": "MS Orthopedic; MBBS; AO Trauma and Hand Surgery fellowships (India)"},
    {"name": "Dr. Dibya Poudel", "nmc": "14243", "specialty": "Obstetrics & Gynecology", "education": "MBBS (KU); MD/MS Obstetrics & Gynecology (NAMS); Reproductive Medicine fellowship"},
    {"name": "Dr. Raskin Shakya", "nmc": "10554", "specialty": "Orthopedics", "education": "MBBS; MS Orthopedic Surgery"},
    {"name": "Dr. MD Sajjad Safi", "nmc": "8628", "specialty": "Cardiology", "education": "MD Cardiology (BSMMU, Bangladesh); MBBS (Manipal, Pokhara)"},
    {"name": "Dr. Manisha Koirala", "nmc": "16383", "specialty": "Dermatology", "education": "MD Dermatology (NAMS); MBBS (UCMS)"},
    {"name": "Dr. Kristi Gupta", "nmc": "30126", "specialty": "Dental", "education": "Bachelor of Dental Surgery (Chitwan Medical College, TU)"},
    {"name": "Dr. Anir Ram Moh Shrestha", "nmc": "2816", "specialty": "General Surgery", "education": ""},
]

bb_hospital_doctors = [
    {"name": "Prof. Dr. Ashok Kumar Banskota", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Babu Kaji Shrestha", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Saroj Rijal", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Ishor Pradhan", "nmc": "", "specialty": "Orthopedic Surgery (Arthroscopic)", "education": ""},
    {"name": "Prof. Dr. Amit Joshi", "nmc": "", "specialty": "Orthopedic Surgery (Arthroscopy)", "education": ""},
    {"name": "Dr. Tarun Rajbhandari", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Om Prasad Shrestha", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Bibek Banskota", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Rajesh K. Chaudhary", "nmc": "", "specialty": "Orthopedic Surgery (Spine)", "education": ""},
    {"name": "Dr. Ram Krishna Barakoti", "nmc": "", "specialty": "Orthopedic Surgery (Spine)", "education": ""},
    {"name": "Dr. Nagmani Singh", "nmc": "", "specialty": "Orthopedic Surgery (Arthroscopy)", "education": ""},
    {"name": "Dr. Bibek Basukala", "nmc": "", "specialty": "Orthopedic Surgery (Arthroscopy)", "education": ""},
    {"name": "Dr. Birendra Bahadur Chand", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Rajendra Aryal", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Rohit Bista", "nmc": "", "specialty": "Orthopedic Surgery (Arthroscopy)", "education": ""},
    {"name": "Dr. Ansul Rajbhandari", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Yam Prakash Gurung", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Deepak Kaucha", "nmc": "", "specialty": "Orthopedic Surgery (Spine)", "education": ""},
    {"name": "Dr. Niresh Shrestha", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Nitesh Raj Pandey", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Rajiv Sharma", "nmc": "", "specialty": "Orthopedic Surgery (Arthroscopic)", "education": ""},
    {"name": "Dr. Santosh Batajoo", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Dr. Subhash Regmi", "nmc": "", "specialty": "Orthopedic Surgery", "education": ""},
    {"name": "Prof. Dr. Jagdish Lal Baidya", "nmc": "", "specialty": "General & Laparoscopic Surgery", "education": ""},
    {"name": "Dr. Niraj Lal Baidya", "nmc": "", "specialty": "General & Laparoscopic Surgery", "education": ""},
    {"name": "Dr. D.V. Karkee", "nmc": "", "specialty": "General & Laparoscopic Surgery", "education": ""},
    {"name": "Dr. Arbin Joshi", "nmc": "", "specialty": "General & Laparoscopic Surgery", "education": ""},
    {"name": "Dr. Paleshwan Joshi Lakhey", "nmc": "", "specialty": "General Surgery (GI/HPB)", "education": ""},
    {"name": "Dr. Ijendra Prajapati", "nmc": "", "specialty": "General/GI Oncosurgery", "education": ""},
    {"name": "Dr. Sudip Ratna Shakya", "nmc": "", "specialty": "Laparoscopic & Oncosurgery", "education": ""},
    {"name": "Dr. Rajesh Batajoo", "nmc": "", "specialty": "Urology (Uro-Oncology)", "education": ""},
    {"name": "Dr. Binod Shrestha", "nmc": "", "specialty": "Urology", "education": ""},
    {"name": "Dr. Anil Shrestha", "nmc": "", "specialty": "Urology (Kidney Transplant)", "education": ""},
    {"name": "Dr. Saroj Baidya", "nmc": "", "specialty": "General & Urology", "education": ""},
    {"name": "Dr. Atul Kasaju", "nmc": "", "specialty": "Urology", "education": ""},
    {"name": "Dr. Sanjay Lakhey", "nmc": "", "specialty": "Internal Medicine", "education": ""},
    {"name": "Dr. Om Prakash Adhikari", "nmc": "", "specialty": "Internal Medicine", "education": ""},
    {"name": "Dr. Ramesh Basnyat", "nmc": "", "specialty": "Pulmonology", "education": ""},
    {"name": "Dr. Sarita Pandey", "nmc": "", "specialty": "Internal Medicine", "education": ""},
    {"name": "Dr. Philip Shyam Ranjit", "nmc": "", "specialty": "Internal Medicine & Gastroenterology", "education": ""},
    {"name": "Dr. Deependra Karki", "nmc": "", "specialty": "Internal Medicine & Endocrinology", "education": ""},
    {"name": "Dr. Amit Man Joshi", "nmc": "", "specialty": "Gastroenterology", "education": ""},
    {"name": "Dr. Sanu Raja Amatya", "nmc": "", "specialty": "Internal Medicine", "education": ""},
    {"name": "Dr. Arbindra Pokhrel", "nmc": "", "specialty": "Hepatology", "education": ""},
    {"name": "Dr. Ajit Shrestha", "nmc": "", "specialty": "Internal Medicine", "education": ""},
    {"name": "Dr. Shikher Shrestha", "nmc": "", "specialty": "Neurosurgery", "education": ""},
    {"name": "Dr. Dinuj Shrestha", "nmc": "", "specialty": "Neurosurgery", "education": ""},
    {"name": "Dr. Naresh Kharbuja", "nmc": "", "specialty": "Neurology", "education": ""},
    {"name": "Prof. Dr. Kundu Yangzom", "nmc": "", "specialty": "Obstetrics & Gynecology", "education": ""},
    {"name": "Dr. Anjana Karki", "nmc": "", "specialty": "Obstetrics & Gynecology", "education": ""},
    {"name": "Dr. Nutan Sharma", "nmc": "", "specialty": "IVF & Reproductive Medicine", "education": ""},
    {"name": "Dr. Sangita Shakya", "nmc": "", "specialty": "Pediatrics", "education": ""},
    {"name": "Dr. Sushil Dhungel", "nmc": "", "specialty": "Pediatrics (Laparoscopic)", "education": ""},
    {"name": "Dr. Anwesh Bhatta", "nmc": "", "specialty": "Pediatrics", "education": ""},
    {"name": "Dr. Rajib Rajbhandari", "nmc": "", "specialty": "Cardiology", "education": ""},
    {"name": "Dr. Jageshwar Prasad Shah", "nmc": "", "specialty": "Cardiology", "education": ""},
    {"name": "Dr. Ananda Khanal", "nmc": "", "specialty": "Cardiology", "education": ""},
    {"name": "Dr. Kishan Kumar Kushwaha", "nmc": "", "specialty": "Internal Medicine & Cardiology", "education": ""},
    {"name": "Dr. Prashant Bajracharya", "nmc": "", "specialty": "Cardiology", "education": ""},
    {"name": "Dr. Sanjay Singh K.C", "nmc": "", "specialty": "Cardiology", "education": ""},
    {"name": "Dr. Rajan Poudel", "nmc": "", "specialty": "Cardiology", "education": ""},
    {"name": "Dr. Inku Shrestha Basnet", "nmc": "", "specialty": "ENT (Head & Neck)", "education": ""},
    {"name": "Dr. Asbina K.C", "nmc": "", "specialty": "ENT (Head & Neck, Vertigo)", "education": ""},
    {"name": "Dr. Luna Mathema Shrestha", "nmc": "", "specialty": "ENT (Head & Neck, Allergy)", "education": ""},
    {"name": "Dr. Chetana Pathak", "nmc": "", "specialty": "ENT", "education": ""},
    {"name": "Dr. Rishikesh Narayan Shrestha", "nmc": "", "specialty": "Surgical Oncology", "education": ""},
    {"name": "Dr. Sristee Shrestha Prajapati", "nmc": "", "specialty": "Gynecologic Oncology", "education": ""},
    {"name": "Dr. Roshan Prajapati", "nmc": "", "specialty": "Medical Oncology", "education": ""},
    {"name": "Dr. Niraj Kumar Singh", "nmc": "", "specialty": "Hematology", "education": ""},
    {"name": "Dr. Deep Lamichhane", "nmc": "", "specialty": "Surgical Oncology", "education": ""},
    {"name": "Dr. Archana Amatya", "nmc": "", "specialty": "Surgical Oncology", "education": ""},
    {"name": "Dr. Sudip Thapa", "nmc": "", "specialty": "Medical Oncology", "education": ""},
    {"name": "Dr. Bibek Khanal", "nmc": "", "specialty": "Surgical Oncology", "education": ""},
    {"name": "Dr. Suraj Suwal", "nmc": "", "specialty": "Surgical Oncology", "education": ""},
    {"name": "Dr. Mipsang Lama", "nmc": "", "specialty": "Hematology", "education": ""},
    {"name": "Dr. Sudhir Raj Silwal", "nmc": "", "specialty": "Radiation Oncology", "education": ""},
    {"name": "Dr. Mahendra Maharjan", "nmc": "", "specialty": "Oral & Maxillofacial Surgery", "education": ""},
    {"name": "Dr. Krishna Manandhar", "nmc": "", "specialty": "Plastic & Reconstructive Surgery", "education": ""},
    {"name": "Dr. Anoj Rajkarnikar", "nmc": "", "specialty": "Plastic & Reconstructive Surgery", "education": ""},
    {"name": "Dr. Juna Gurung", "nmc": "", "specialty": "Plastic & Reconstructive Surgery", "education": ""},
    {"name": "Prof. Dr. Sudarshan Narsingh Pradhan", "nmc": "", "specialty": "Neuropsychiatry", "education": ""},
    {"name": "Dr. Surendra Sherchan", "nmc": "", "specialty": "Psychiatry", "education": ""},
    {"name": "Dr. Namrata Pradhan", "nmc": "", "specialty": "Psychiatry", "education": ""},
    {"name": "Dr. Supriya Sherchan", "nmc": "", "specialty": "Psychiatry", "education": ""},
    {"name": "Prof. Dr. Dwarika Prasad Shrestha", "nmc": "", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Parash Shrestha", "nmc": "", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Shailendra Shrestha", "nmc": "", "specialty": "Nephrology", "education": ""},
    {"name": "Dr. Kajan Raj Shrestha", "nmc": "", "specialty": "Cardio-Thoracic & Vascular Surgery", "education": ""},
    {"name": "Dr. Prasiddha Bikram Kadel", "nmc": "", "specialty": "Cardio-Thoracic & Vascular Surgery", "education": ""},
    {"name": "Dr. Satish Vaidya", "nmc": "", "specialty": "Cardio-Thoracic & Vascular Surgery", "education": ""},
    {"name": "Dr. Rajat Pradhan", "nmc": "", "specialty": "Cardio-Thoracic & Vascular Surgery", "education": ""},
    {"name": "Dr. Deepa Shah", "nmc": "", "specialty": "Rheumatology", "education": ""},
    {"name": "Dr. Prabhat Ranjan Baral", "nmc": "", "specialty": "Anesthesiology", "education": ""},
    {"name": "Dr. Bhakta Bahadur Burathoki", "nmc": "", "specialty": "Anesthesiology", "education": ""},
    {"name": "Dr. Ramnath Dhoan Shrestha", "nmc": "", "specialty": "Anesthesiology", "education": ""},
    {"name": "Dr. Meena Kunwar", "nmc": "", "specialty": "Ophthalmology", "education": ""},
]

kantipur_doctors = [
    {"name": "Dr. Kiran Manandhar", "nmc": "2193", "specialty": "", "education": ""},
    {"name": "Dr. Mukesh Sharma", "nmc": "7539", "specialty": "", "education": ""},
    {"name": "Dr. Pankaj Deo", "nmc": "14814", "specialty": "", "education": ""},
    {"name": "Dr. Srijan Malla", "nmc": "2649", "specialty": "", "education": ""},
    {"name": "Dr. Dipesh Shrestha", "nmc": "6609", "specialty": "", "education": ""},
    {"name": "Dr. Bikash Sahani", "nmc": "12825", "specialty": "", "education": ""},
    {"name": "Dr. Jay Dev Yadav", "nmc": "10845", "specialty": "", "education": ""},
    {"name": "Dr. R.K Singh", "nmc": "703", "specialty": "", "education": ""},
    {"name": "Dr. Yagya Bahadur Bhandari", "nmc": "968", "specialty": "", "education": ""},
    {"name": "Dr. Rabin Joshi", "nmc": "2839", "specialty": "", "education": ""},
    {"name": "Dr. Uday Raj Upadhayay", "nmc": "783", "specialty": "", "education": ""},
    {"name": "Dr. Merina Manandhar", "nmc": "11039", "specialty": "", "education": ""},
    {"name": "Dr. Boblin Raj Shakya", "nmc": "4785", "specialty": "", "education": ""},
    {"name": "Dr. Avesh Koirala", "nmc": "", "specialty": "", "education": ""},
    {"name": "Dr. Rohit Chaudhary", "nmc": "", "specialty": "", "education": ""},
    {"name": "Dr. Ajay Kumar Jha", "nmc": "3021", "specialty": "", "education": ""},
    {"name": "Dr. Roshan Prajapati", "nmc": "3520", "specialty": "", "education": ""},
    {"name": "Dr. Sristee Prajapati", "nmc": "3492", "specialty": "", "education": ""},
    {"name": "Dr. Neeyaj Kausar", "nmc": "4784", "specialty": "", "education": ""},
    {"name": "Dr. Mukunda Sharma", "nmc": "1859", "specialty": "", "education": ""},
]

disharc_doctors = [
    {"name": "Prof. Dr. Anil Kumar Jha", "nmc": "1032", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Mahesh Shah", "nmc": "1780", "specialty": "Dermatology", "education": ""},
    {"name": "Prof. Dr. Ram Chandra Adhikari", "nmc": "2367", "specialty": "Pathology", "education": ""},
    {"name": "Prof. Dr. Sagar Mani Jha", "nmc": "2699", "specialty": "Dermatology", "education": ""},
    {"name": "Prof. Dr. Shristi Shrestha", "nmc": "3297", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Bijay Shrestha", "nmc": "3547", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Padma Tuladhar", "nmc": "4462", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Smita Joshi", "nmc": "5666", "specialty": "Pediatric Dermatology", "education": ""},
    {"name": "Asst. Prof. Dr. Bishal Karki", "nmc": "6863", "specialty": "Plastic & Cosmetic Surgery", "education": ""},
    {"name": "Dr. Utsav Sharma", "nmc": "7619", "specialty": "Dermatology", "education": ""},
    {"name": "Assoc. Prof. Dr. Suchana Marahatta", "nmc": "8368", "specialty": "Aesthetic Dermatology", "education": ""},
    {"name": "Dr. Subekcha Karki", "nmc": "8909", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Siree Thapa", "nmc": "8038", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Prarthana Adhikari", "nmc": "12420", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Kamal Raj Pathak", "nmc": "10277", "specialty": "Plastic & Cosmetic Surgery", "education": ""},
    {"name": "Dr. Megha Dev", "nmc": "17270", "specialty": "Dermatology", "education": ""},
    {"name": "Dr. Shraddha Shrestha", "nmc": "17597", "specialty": "Dermatology", "education": ""},
]

def main():
    print("="*100)
    print("CHECKING NEW DOCTORS FROM HOSPITAL WEBSITES")
    print("="*100)
    print()

    # Load database
    doctors_by_nmc, doctors_by_name, total_in_db = get_existing_doctors()
    print(f"Total doctors in database: {total_in_db}")
    print()

    hospitals_data = [
        ("STEM Center KTM", stem_center_doctors),
        ("B&B Hospital", bb_hospital_doctors),
        ("Kantipur Hospital", kantipur_doctors),
        ("DISHARC (DI Skin Hospital)", disharc_doctors),
    ]

    all_new_doctors = []

    for hospital_name, doctors in hospitals_data:
        print("="*100)
        print(f"HOSPITAL: {hospital_name}")
        print("="*100)

        new_doctors = []
        existing_count = 0

        for doc in doctors:
            in_db, match = check_doctor(
                doc['name'],
                doc['nmc'],
                doc['specialty'],
                doc['education'],
                hospital_name,
                doctors_by_nmc,
                doctors_by_name
            )

            if in_db:
                existing_count += 1
            else:
                new_doctors.append(doc)
                all_new_doctors.append({
                    'hospital': hospital_name,
                    **doc
                })

        print(f"Total doctors scraped: {len(doctors)}")
        print(f"Already in database: {existing_count}")
        print(f"NEW doctors found: {len(new_doctors)}")
        print()

        if new_doctors:
            print("NEW DOCTORS:")
            print("-" * 100)
            for i, doc in enumerate(new_doctors, 1):
                print(f"{i}. {doc['name']}")
                if doc['nmc']:
                    print(f"   NMC: {doc['nmc']}")
                if doc['specialty']:
                    print(f"   Specialty: {doc['specialty']}")
                if doc['education']:
                    print(f"   Education: {doc['education']}")
                print()
        print()

    # Summary
    print("="*100)
    print("OVERALL SUMMARY")
    print("="*100)
    print(f"Total NEW doctors discovered: {len(all_new_doctors)}")
    print()

    # Group by hospital
    by_hospital = defaultdict(int)
    for doc in all_new_doctors:
        by_hospital[doc['hospital']] += 1

    print("Breakdown by hospital:")
    for hospital, count in by_hospital.items():
        print(f"  - {hospital}: {count} new doctors")
    print()

    # Doctors with NMC numbers (higher quality data)
    with_nmc = [d for d in all_new_doctors if d.get('nmc')]
    print(f"New doctors with NMC numbers: {len(with_nmc)}")
    print(f"New doctors without NMC numbers: {len(all_new_doctors) - len(with_nmc)}")
    print()

    print("="*100)
    print("NOTES:")
    print("- Om Hospital: Website lists 150+ doctors but doesn't show NMC numbers")
    print("- Norvic Hospital: Website requires JavaScript - couldn't fetch (shows location.reload())")
    print("- Grande Hospital: SSL certificate error - couldn't fetch")
    print("- Doctors without NMC numbers require manual verification before adding to database")
    print("="*100)

if __name__ == '__main__':
    main()
