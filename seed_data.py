#!/usr/bin/env python3
"""
Seed database with realistic Nepali doctors, cities, and specialties
"""
from app import app, db
from models import City, Specialty, Doctor, User
from werkzeug.security import generate_password_hash
import random

def seed_database():
    with app.app_context():
        print("🌱 Seeding database with Nepali doctor data...")

        # Add more major Nepali cities if they don't exist
        cities_data = [
            {"name": "Kathmandu", "description": "Capital city of Nepal"},
            {"name": "Pokhara", "description": "Tourism capital of Nepal"},
            {"name": "Lalitpur", "description": "City of fine arts"},
            {"name": "Bhaktapur", "description": "City of devotees"},
            {"name": "Biratnagar", "description": "Industrial capital of Nepal"},
            {"name": "Dharan", "description": "Education hub of eastern Nepal"},
            {"name": "Birgunj", "description": "Gateway to Nepal"},
            {"name": "Hetauda", "description": "Capital of Bagmati Pradesh"},
            {"name": "Butwal", "description": "Commercial hub"},
            {"name": "Bharatpur", "description": "Healthcare hub in Chitwan"},
        ]

        cities = {}
        for city_data in cities_data:
            city = City.query.filter_by(name=city_data["name"]).first()
            if not city:
                city = City(**city_data)
                db.session.add(city)
                print(f"  ✓ Added city: {city_data['name']}")
            cities[city_data["name"]] = city

        db.session.commit()

        # Ensure all specialties exist
        specialties_data = [
            {"name": "General Practitioner", "description": "Primary care physician"},
            {"name": "Cardiologist", "description": "Heart specialist"},
            {"name": "Dermatologist", "description": "Skin specialist"},
            {"name": "Pediatrician", "description": "Child healthcare specialist"},
            {"name": "Gynecologist", "description": "Women's health specialist"},
            {"name": "Orthopedic", "description": "Bone and joint specialist"},
            {"name": "Neurologist", "description": "Nervous system specialist"},
            {"name": "Psychiatrist", "description": "Mental health specialist"},
            {"name": "Ophthalmologist", "description": "Eye specialist"},
            {"name": "ENT Specialist", "description": "Ear, Nose, and Throat specialist"},
            {"name": "Dentist", "description": "Dental specialist"},
            {"name": "Ayurvedic Practitioner", "description": "Traditional Ayurvedic medicine"},
        ]

        specialties = {}
        for spec_data in specialties_data:
            specialty = Specialty.query.filter_by(name=spec_data["name"]).first()
            if not specialty:
                specialty = Specialty(**spec_data)
                db.session.add(specialty)
                print(f"  ✓ Added specialty: {spec_data['name']}")
            specialties[spec_data["name"]] = specialty

        db.session.commit()

        # Add realistic doctors
        doctors_data = [
            # Kathmandu doctors
            {
                "name": "Dr. Rajendra Prasad Miya",
                "specialty": "General Practitioner",
                "city": "Kathmandu",
                "experience": 15,
                "education": "MBBS",
                "college": "Institute of Medicine, Tribhuvan University",
                "description": "Experienced general physician specializing in preventive care and chronic disease management. Available for consultations at Naxal Clinic.",
                "is_featured": True,
                "is_verified": True
            },
            {
                "name": "Dr. Shila Rana",
                "specialty": "Pediatrician",
                "city": "Kathmandu",
                "experience": 12,
                "education": "MBBS, MD (Pediatrics)",
                "college": "B.P. Koirala Institute of Health Sciences",
                "description": "Dedicated to child healthcare with expertise in newborn care, vaccinations, and developmental assessments.",
                "is_featured": True,
                "is_verified": True
            },
            {
                "name": "Dr. Pravin Mishra",
                "specialty": "Cardiologist",
                "city": "Kathmandu",
                "experience": 20,
                "education": "MBBS, MD (Cardiology)",
                "college": "Tribhuvan University Teaching Hospital",
                "description": "Senior cardiologist with extensive experience in interventional cardiology and heart disease management.",
                "is_featured": True,
                "is_verified": True
            },
            {
                "name": "Dr. Ranjeeta Karki",
                "specialty": "Gynecologist",
                "city": "Kathmandu",
                "experience": 10,
                "education": "MBBS, MS (Gynecology)",
                "college": "Kathmandu Medical College",
                "description": "Women's health specialist offering comprehensive obstetric and gynecological care.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Ramesh K. Shrestha",
                "specialty": "Orthopedic",
                "city": "Kathmandu",
                "experience": 18,
                "education": "MBBS, MS (Orthopedics)",
                "college": "National Academy of Medical Sciences",
                "description": "Orthopedic surgeon specializing in joint replacement and sports injuries.",
                "is_featured": True,
                "is_verified": True
            },
            {
                "name": "Dr. Binita Sharma",
                "specialty": "Dermatologist",
                "city": "Kathmandu",
                "experience": 8,
                "education": "MBBS, MD (Dermatology)",
                "college": "Nepal Medical College",
                "description": "Skin specialist offering treatment for acne, eczema, and cosmetic dermatology services.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Sanjay Thapa",
                "specialty": "Neurologist",
                "city": "Kathmandu",
                "experience": 14,
                "education": "MBBS, DM (Neurology)",
                "college": "PGIMER, Chandigarh, India",
                "description": "Neurologist with expertise in stroke management, epilepsy, and neurodegenerative diseases.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Anjali Karmacharya",
                "specialty": "Ophthalmologist",
                "city": "Kathmandu",
                "experience": 11,
                "education": "MBBS, MS (Ophthalmology)",
                "college": "Tribhuvan University",
                "description": "Eye specialist providing cataract surgery, LASIK, and general eye care services.",
                "is_featured": False,
                "is_verified": True
            },

            # Pokhara doctors
            {
                "name": "Dr. Binod Dhungana",
                "specialty": "General Practitioner",
                "city": "Pokhara",
                "experience": 13,
                "education": "MBBS",
                "college": "Manipal College of Medical Sciences",
                "description": "Family physician providing comprehensive primary care services in Lakeside area.",
                "is_featured": True,
                "is_verified": True
            },
            {
                "name": "Dr. Sabita Gurung",
                "specialty": "Gynecologist",
                "city": "Pokhara",
                "experience": 9,
                "education": "MBBS, MS (Gynecology)",
                "college": "Manipal Teaching Hospital",
                "description": "Committed to women's reproductive health and safe motherhood practices.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Keshav Poudel",
                "specialty": "Dentist",
                "city": "Pokhara",
                "experience": 7,
                "education": "BDS",
                "college": "Kantipur Dental College",
                "description": "General dentist offering preventive care, root canal treatment, and cosmetic dentistry.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Priya Adhikari",
                "specialty": "Pediatrician",
                "city": "Pokhara",
                "experience": 10,
                "education": "MBBS, MD (Pediatrics)",
                "college": "B.P. Koirala Institute of Health Sciences",
                "description": "Child health expert with special interest in nutrition and growth monitoring.",
                "is_featured": True,
                "is_verified": True
            },

            # Lalitpur doctors
            {
                "name": "Dr. Arjun Shrestha",
                "specialty": "Cardiologist",
                "city": "Lalitpur",
                "experience": 16,
                "education": "MBBS, DM (Cardiology)",
                "college": "All India Institute of Medical Sciences",
                "description": "Heart specialist with expertise in non-invasive cardiology and preventive care.",
                "is_featured": True,
                "is_verified": True
            },
            {
                "name": "Dr. Meera Joshi",
                "specialty": "Psychiatrist",
                "city": "Lalitpur",
                "experience": 12,
                "education": "MBBS, MD (Psychiatry)",
                "college": "National Academy of Medical Sciences",
                "description": "Mental health professional specializing in depression, anxiety, and stress management.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Ramhari Khadka",
                "specialty": "ENT Specialist",
                "city": "Lalitpur",
                "experience": 15,
                "education": "MBBS, MS (ENT)",
                "college": "Tribhuvan University",
                "description": "ENT surgeon offering treatment for sinus problems, hearing loss, and throat disorders.",
                "is_featured": False,
                "is_verified": True
            },

            # Biratnagar doctors
            {
                "name": "Dr. Madan Koirala",
                "specialty": "General Practitioner",
                "city": "Biratnagar",
                "experience": 14,
                "education": "MBBS",
                "college": "B.P. Koirala Institute of Health Sciences",
                "description": "General physician with focus on diabetes and hypertension management.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Ananda Prasad Acharya",
                "specialty": "General Practitioner",
                "city": "Biratnagar",
                "experience": 11,
                "education": "MBBS",
                "college": "Universal College of Medical Sciences",
                "description": "Experienced in treating common ailments and providing preventive healthcare.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Sunita Rai",
                "specialty": "Dermatologist",
                "city": "Biratnagar",
                "experience": 6,
                "education": "MBBS, MD (Dermatology)",
                "college": "Nepal Medical College",
                "description": "Skin care specialist focusing on acne treatment and anti-aging procedures.",
                "is_featured": False,
                "is_verified": True
            },

            # Bharatpur doctors
            {
                "name": "Dr. Krishna Bahadur Thapa",
                "specialty": "Orthopedic",
                "city": "Bharatpur",
                "experience": 17,
                "education": "MBBS, MS (Orthopedics)",
                "college": "Institute of Medicine, Tribhuvan University",
                "description": "Orthopedic surgeon with expertise in fracture management and joint care.",
                "is_featured": True,
                "is_verified": True
            },
            {
                "name": "Dr. Rita Kumari Tharu",
                "specialty": "General Practitioner",
                "city": "Bharatpur",
                "experience": 9,
                "education": "MBBS",
                "college": "Chitwan Medical College",
                "description": "Primary care physician serving the Bharatpur community with dedication.",
                "is_featured": False,
                "is_verified": True
            },

            # Dharan doctors
            {
                "name": "Dr. Bikash Chaudhary",
                "specialty": "General Practitioner",
                "city": "Dharan",
                "experience": 10,
                "education": "MBBS",
                "college": "B.P. Koirala Institute of Health Sciences",
                "description": "General physician with special interest in infectious diseases.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Pooja Limbu",
                "specialty": "Pediatrician",
                "city": "Dharan",
                "experience": 8,
                "education": "MBBS, MD (Pediatrics)",
                "college": "B.P. Koirala Institute of Health Sciences",
                "description": "Child healthcare provider focusing on immunization and developmental care.",
                "is_featured": False,
                "is_verified": True
            },

            # Butwal doctors
            {
                "name": "Dr. Suresh Pandey",
                "specialty": "General Practitioner",
                "city": "Butwal",
                "experience": 12,
                "education": "MBBS",
                "college": "Lumbini Medical College",
                "description": "General physician providing quality healthcare to Butwal residents.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Nirmala Regmi",
                "specialty": "Gynecologist",
                "city": "Butwal",
                "experience": 11,
                "education": "MBBS, MS (Gynecology)",
                "college": "Universal College of Medical Sciences",
                "description": "Women's health specialist with expertise in high-risk pregnancy management.",
                "is_featured": True,
                "is_verified": True
            },

            # Bhaktapur doctors
            {
                "name": "Dr. Dipesh Shrestha",
                "specialty": "Dentist",
                "city": "Bhaktapur",
                "experience": 6,
                "education": "BDS",
                "college": "Nepal Medical College",
                "description": "Dental surgeon offering comprehensive oral healthcare services.",
                "is_featured": False,
                "is_verified": True
            },
            {
                "name": "Dr. Saraswati Maharjan",
                "specialty": "Ayurvedic Practitioner",
                "city": "Bhaktapur",
                "experience": 14,
                "education": "BAMS",
                "college": "Nepal Ayurveda Campus",
                "description": "Traditional Ayurvedic practitioner specializing in holistic wellness and chronic disease management.",
                "is_featured": False,
                "is_verified": True
            },
        ]

        # Add doctors to database
        existing_count = Doctor.query.count()
        added_count = 0

        for doc_data in doctors_data:
            # Create slug from name
            slug = doc_data["name"].lower().replace("dr. ", "").replace(" ", "-")

            # Check if doctor already exists
            if not Doctor.query.filter_by(slug=slug).first():
                doctor = Doctor(
                    name=doc_data["name"],
                    slug=slug,
                    specialty_id=specialties[doc_data["specialty"]].id,
                    city_id=cities[doc_data["city"]].id,
                    experience=doc_data["experience"],
                    education=doc_data["education"],
                    college=doc_data["college"],
                    description=doc_data["description"],
                    is_featured=doc_data.get("is_featured", False),
                    is_verified=doc_data.get("is_verified", True),
                    is_active=True
                )
                db.session.add(doctor)
                added_count += 1
                print(f"  ✓ Added doctor: {doc_data['name']}")

        db.session.commit()

        # Create admin user if doesn't exist
        admin_user = User.query.filter_by(email="admin@ranksewa.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin",
                email="admin@ranksewa.com",
                password=generate_password_hash("admin123"),
                is_admin=True,
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"  ✓ Created admin user (email: admin@ranksewa.com, password: admin123)")

        # Create test user if doesn't exist
        test_user = User.query.filter_by(email="test@ranksewa.com").first()
        if not test_user:
            test_user = User(
                name="Test User",
                email="test@ranksewa.com",
                password=generate_password_hash("test123"),
                is_admin=False,
                is_active=True
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"  ✓ Created test user (email: test@ranksewa.com, password: test123)")

        print(f"\n✅ Database seeding complete!")
        print(f"   Cities: {City.query.count()}")
        print(f"   Specialties: {Specialty.query.count()}")
        print(f"   Doctors: {existing_count} → {Doctor.query.count()} (+{added_count})")
        print(f"   Users: {User.query.count()}")

if __name__ == "__main__":
    seed_database()
