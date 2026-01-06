#!/usr/bin/env python3
"""
Script to check Om Hospital doctors against database
"""

import sqlite3

# Database path
DB_PATH = '/home/ppaudyal/Documents/drprofile/doctor_directory/instance/doctors.db'

def normalize_name(name):
    """Normalize doctor name for comparison."""
    if not name:
        return ""

    name = name.strip()
    # Remove common prefixes
    prefixes = ['dr.', 'dr', 'prof.', 'prof', 'professor', 'associate prof.', 'asst. prof.',
                'assoc. prof.', 'asst.', 'assoc.', 'pt.']
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
        SELECT d.id, d.name, d.nmc_number, s.name as specialty
        FROM doctors d
        LEFT JOIN specialties s ON d.specialty_id = s.id
    """)

    doctors = cursor.fetchall()
    conn.close()

    # Create lookup dictionary by normalized name
    doctors_by_name = {}

    for doc in doctors:
        doc_id, name, nmc, specialty = doc
        normalized = normalize_name(name)
        if normalized:
            doctors_by_name[normalized] = {
                'id': doc_id,
                'name': name,
                'nmc': nmc,
                'specialty': specialty
            }

    return doctors_by_name, len(doctors)

# Om Hospital doctors (117 total)
om_hospital_doctors = [
    {"name": "Dr. Ranju Kharel (Sitaula)", "specialty": "Ophthalmology and Uveitis"},
    {"name": "Dr. Pratap Karki", "specialty": "Ophthalmology, Retina"},
    {"name": "Dr. Rita Shrestha", "specialty": "Dermatology"},
    {"name": "Prof. Dr. A.K. Jha", "specialty": "ENT Head and Neck Surgery"},
    {"name": "Prof. Dr. Pushpa Prasad Sharma", "specialty": "Neuropsychiatry"},
    {"name": "Prof. Dr. Rupesh Raj Joshi", "specialty": "ENT Head and Neck Surgery"},
    {"name": "Prof. Dr. Jageshwor Gautam", "specialty": "Gynaecology"},
    {"name": "Prof. Dr. Ugra Narayan Pathak", "specialty": "Internal Medicine"},
    {"name": "Prof. Dr. Pramod K. Chhetri", "specialty": "Nephrology"},
    {"name": "Prof. Dr. Rabindra Shrestha", "specialty": "Neurology"},
    {"name": "Prof. Dr. Pawan Kumar Sultaniya", "specialty": "Neurosurgery"},
    {"name": "Dr. Rajendra Pd. Baral", "specialty": "Oncology"},
    {"name": "Dr. Rita Singh", "specialty": "Pediatrics"},
    {"name": "Prof. Dr. Bhola Raj Joshi", "specialty": "Urology"},
    {"name": "Dr. Sanubhai Khadka", "specialty": "General Practice"},
    {"name": "Prof. Dr. Sunil Kumar Sharma Dhakal", "specialty": "GI Surgery"},
    {"name": "Dr. Samit Sharma", "specialty": "Plastic & Reconstructive Surgery"},
    {"name": "Dr. Subash Chandra Shah", "specialty": "Pediatric Cardiology"},
    {"name": "Bhupal Baniya", "specialty": "Nutrition and Dietetics"},
    {"name": "Prof. Dr. Gaurav Raj Dhakal", "specialty": "Spine Surgery"},
    {"name": "Dr. Shrishti Shrestha", "specialty": "Dermatology"},
    {"name": "Prof. Dr. Kamal Koirala", "specialty": "General & GI Surgery"},
    {"name": "Assoc. Prof. Dr. Krishna Dhungana", "specialty": "Neurology"},
    {"name": "Dr. Uma Gurung", "specialty": "Pediatrics"},
    {"name": "Prof. Dr. Subodh Sagar Dhakal", "specialty": "Pulmonology & Critical Care"},
    {"name": "Dr. Kamal Sharma Lamsal", "specialty": "Cardiology"},
    {"name": "Dr. Suman Bikram Adhikari", "specialty": "Pediatric Surgery & Urology"},
    {"name": "Dr. Saubhagyaman Malla", "specialty": "Anaesthesiology"},
    {"name": "Dr. Shyam Maharjan", "specialty": "Anaesthesiology"},
    {"name": "Dr. Surendra Kumar Shrestha", "specialty": "Anaesthesiology"},
    {"name": "Prof. Dr. Chandramani Poudel", "specialty": "Interventional Cardiology"},
    {"name": "Dr. Kajan Raj Shrestha", "specialty": "Cardiothoracic and Vascular Surgery"},
    {"name": "Dr. Pramesh Sunder Shrestha", "specialty": "Critical Care Medicine"},
    {"name": "Dr. Harish Joshi", "specialty": "Dental Surgery"},
    {"name": "Dr. Sudip Parajuli", "specialty": "Dermatology"},
    {"name": "Dr. Sanjay Kumar Gupta", "specialty": "General Practice"},
    {"name": "Prof. Dr. Rahul Pathak", "specialty": "Gastroenterology"},
    {"name": "Dr. Deepak Raj Pandey", "specialty": "Gastroenterology"},
    {"name": "Dr. Suphatra Koirala", "specialty": "Gynaecology"},
    {"name": "Dr. Louisa Rajput", "specialty": "Gynaecology"},
    {"name": "Dr. Mamata Baral", "specialty": "Gynaecology"},
    {"name": "Dr. Roshan Gongol", "specialty": "Gynaecology"},
    {"name": "Dr. Bishwanath Koirala", "specialty": "Internal Medicine"},
    {"name": "Dr. Dhiraj Manandhar", "specialty": "Nephrology"},
    {"name": "Dr. Prakash Poudel", "specialty": "Nephrology"},
    {"name": "Dr. Chandra Man Prajapati", "specialty": "Neurosurgery"},
    {"name": "Dr. Gisup Prasiko", "specialty": "Oncology"},
    {"name": "Dr. Rajeev Kumar Deo", "specialty": "Medical Oncology"},
    {"name": "Dr. Ujjwal Chalise", "specialty": "Oncology"},
    {"name": "Dr. Ramesh Pradhan", "specialty": "Ophthalmology"},
    {"name": "Dr. Achyut Raj Bhandari", "specialty": "Orthopedic Surgery"},
    {"name": "Prof. Dr. Nabees M.S. Pradhan", "specialty": "Orthopedic Surgery/Sports Medicine"},
    {"name": "Dr. Praphulla Shrestha", "specialty": "Orthopedic Surgery"},
    {"name": "Dr. Prawesh Singh Bhandari", "specialty": "Orthopedic Surgery"},
    {"name": "Dr. Rojan Ghimire", "specialty": "Pathology"},
    {"name": "Dr. Abhimanyu Jha", "specialty": "Pathology"},
    {"name": "Dr. Ritu Amatya", "specialty": "Pathology"},
    {"name": "Dr. Anand Shrestha", "specialty": "Radiology"},
    {"name": "Dr. Hari Kishor Shrestha", "specialty": "Fetal Medicine"},
    {"name": "Prof. Dr. Abhushan S. Tuladhar", "specialty": "Radiology"},
    {"name": "Prof. Dr. Rabin Koirala", "specialty": "GI Surgery"},
    {"name": "Dr. Sarina Rajbhandari", "specialty": "ENT Head and Neck Surgery"},
    {"name": "Dr. Anjan Singh Karki", "specialty": "Neurosurgery"},
    {"name": "Dr. Dharmagat Bhattarai", "specialty": "Pediatric Immunology and Rheumatology"},
    {"name": "Dr. Prakashnidhi Tiwari", "specialty": "Pediatric Oncology"},
    {"name": "Dr. Krishna Prasad Devkota", "specialty": "Pediatric Surgery"},
    {"name": "Pt. Pravin Yadav", "specialty": "Physiotherapy"},
    {"name": "Dr. Praphul Kumar Jha", "specialty": "General Practice"},
    {"name": "Dr. M.P. Shrivastava", "specialty": "Orthopedics"},
    {"name": "Dr. Sushan Vaidya", "specialty": ""},
    {"name": "Pt. Sumi Shakya", "specialty": "Physiotherapy"},
    {"name": "Dr. Bijay Lingden", "specialty": ""},
    {"name": "Dr. Binod Aryal", "specialty": "Gynaecology Oncology"},
    {"name": "Dr. Samir Keshari Baidya", "specialty": "Nephrology"},
    {"name": "Dr. Saroj Sedai", "specialty": "Dermatology"},
    {"name": "Dr. Binod Rajbhandari", "specialty": "Neurosurgery"},
    {"name": "Dr. Astha Singh", "specialty": "Pediatrics"},
    {"name": "Dr. Sulab Basnet", "specialty": "ENT Head and Neck Surgery"},
    {"name": "Dr. Rishabh Dev Tripathee", "specialty": ""},
    {"name": "Dr. Saket Jha", "specialty": "Immunology & Rheumatology"},
    {"name": "Dr. Bajrang Kumar Rauniyar", "specialty": "Endocrinology"},
    {"name": "Dr. Bikal Ghimire", "specialty": "GI and HPB Surgery"},
    {"name": "Dr. Prasan Bir Singh Kansakar", "specialty": "GI and HPB Surgery"},
    {"name": "Dr. Sabina Shrestha", "specialty": "Gynaecology IVF"},
    {"name": "Dr. Sampada Mishra Pathak", "specialty": "Gynaecology IVF"},
    {"name": "Dr. Anjan Shrestha", "specialty": "Hemato-Oncology"},
    {"name": "Dr. Niraj Shrestha", "specialty": "Orthopedic Surgery"},
    {"name": "Dr. Shirish Adhikari", "specialty": "Orthopedic Surgery"},
    {"name": "Prof. Dr. Amit Shrestha", "specialty": "Radiology"},
    {"name": "Dr. Roshani Pathak", "specialty": "Radiology"},
    {"name": "Dr. Ajit Thapa", "specialty": "Interventional Radiology"},
    {"name": "Dr. Jenny Gautam", "specialty": "Radiology"},
    {"name": "Dr. Amir Shrestha", "specialty": "Radiology"},
    {"name": "Dr. Deepa Kumari Shrestha", "specialty": "Pulmonology"},
    {"name": "Dr. Pratik Man Singh Gurung", "specialty": "Urology & Robotic Surgery"},
    {"name": "Dr. Diwakar Parajuli", "specialty": "Emergency Medicine"},
    {"name": "Dr. Abhishek Chaturbedi", "specialty": "Neurosurgery"},
    {"name": "Dr. Anuj Jung Rayamajhi", "specialty": "Pain Medicine"},
    {"name": "Dr. Gargi Bastola", "specialty": "Pathology"},
    {"name": "Dr. Gyanendra Joshi", "specialty": "Orthopedic & Spine Surgery"},
    {"name": "Dr. Nitesh Shrestha", "specialty": "Pediatrics"},
    {"name": "Dr. Shistata Raj Bhandari", "specialty": "Dermatology"},
    {"name": "Dr. Bijan Shrestha", "specialty": "GI and HPB Surgery"},
    {"name": "Dr. Parashu Ram Ghimire", "specialty": "Internal Medicine"},
    {"name": "Dr. Sujan Pandey", "specialty": "Emergency Medicine"},
    {"name": "Dr. Sumit Singh Maharjan", "specialty": "Ophthalmology Anterior Segment"},
    {"name": "Dr. Satyadeep Bhattacharya", "specialty": "Colorectal & Robotic Surgery"},
    {"name": "Dr. Prashun Upadhaya", "specialty": "Hemato Oncology"},
    {"name": "Dr. Paras Panjiyar", "specialty": "Ophthalmology, Pediatric"},
    {"name": "Dr. Pranil Rai", "specialty": "GI Surgery"},
    {"name": "Dr. Saraswati Pandey", "specialty": "Ophthalmology & Pediatric"},
    {"name": "Dr. Subodh Shrestha", "specialty": "Radiology"},
    {"name": "Dr. Sauharda Lohani", "specialty": "Radiation Oncology"},
    {"name": "Dr. Shiwa Upadhayay", "specialty": "Ophthalmology, Neuro-ophthalmology"},
    {"name": "Dr. Nirvan Rai", "specialty": "General Surgery"},
    {"name": "Dr. Rakshya Shrestha", "specialty": "Medical Oncology"},
    {"name": "Dr. Sulabh Kumar Shrestha", "specialty": "Orthopedic Surgery"},
]

def main():
    print("="*100)
    print("OM HOSPITAL DOCTOR CHECK")
    print("="*100)
    print()

    # Load database
    doctors_by_name, total_in_db = get_existing_doctors()
    print(f"Total doctors in database: {total_in_db}")
    print()

    print(f"Total doctors from Om Hospital: {len(om_hospital_doctors)}")
    print()

    new_doctors = []
    existing_count = 0

    for doc in om_hospital_doctors:
        normalized = normalize_name(doc['name'])

        if normalized in doctors_by_name:
            existing_count += 1
        else:
            new_doctors.append(doc)

    print(f"Already in database: {existing_count}")
    print(f"NEW doctors found: {len(new_doctors)}")
    print()

    if new_doctors:
        print("NEW DOCTORS FROM OM HOSPITAL:")
        print("-" * 100)
        for i, doc in enumerate(new_doctors, 1):
            print(f"{i}. {doc['name']}")
            if doc['specialty']:
                print(f"   Specialty: {doc['specialty']}")
            print()

if __name__ == '__main__':
    main()
