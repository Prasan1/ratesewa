"""
Database Setup Script using SQLAlchemy ORM
Creates all tables and seeds sample data including cities, specialties, doctors, users, ratings, and advertisements.
"""

import os
import re
from datetime import datetime, timedelta
from app import app
from models import db, City, Specialty, Doctor, User, Rating, Advertisement

# Helper function for slugs
def generate_slug(name):
    """Generates a URL-friendly slug from a name."""
    name = name.lower().strip()
    name = re.sub(r'[,\s]+', '-', name)
    name = re.sub(r'\s+', '-', name)
    slug = name.strip('-')
    return slug


def setup_database():
    """Create all tables and seed sample data"""

    with app.app_context():
        # Delete the old database file if it exists
        db_path = 'doctors.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed old database file: {db_path}")

        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully.")

        # Seed data
        print("Seeding data...")

        # Add cities
        cities_data = [
            City(name='Kathmandu', description='Capital of Nepal'),
            City(name='Biratnagar', description='Industrial city'),
            City(name='Chitwan', description='Tourist destination'),
            City(name='Birtamod', description='Eastern city')
        ]
        db.session.add_all(cities_data)
        db.session.commit()
        print(f"Added {len(cities_data)} cities.")

        # Add specialties
        specialties_data = [
            Specialty(name='Dermatologist', description='Skin specialist'),
            Specialty(name='Gynecologist', description='Women health specialist'),
            Specialty(name='Cardiologist', description='Heart specialist'),
            Specialty(name='Pediatrician', description='Child specialist'),
            Specialty(name='Orthopedic', description='Bone specialist'),
            Specialty(name='Neurologist', description='Nervous system specialist'),
            Specialty(name='General Practitioner', description='Provides primary and continuing medical care'),
            Specialty(name='Ayurvedic Practitioner', description='Specialist in traditional Ayurvedic medicine')
        ]
        db.session.add_all(specialties_data)
        db.session.commit()
        print(f"Added {len(specialties_data)} specialties.")

        # Add doctors
        doctors_data = [
            # Biratnagar Doctors
            Doctor(name='Dr. Madan Koirala', city_id=2, specialty_id=7, experience=25,
                   education='MBBS, MD', college='Kathmandu Medical College',
                   description='Specializes in general medicine and has a focus on chronic conditions.',
                   is_featured=True, slug=generate_slug('Dr. Madan Koirala')),

            Doctor(name='Dr. Ananda Prasad Acharya', city_id=2, specialty_id=7, experience=15,
                   education='MBBS, MD', college='B.P. Koirala Institute of Health Sciences',
                   description='Verified professional with 5.02 reviews. Associated with Birat Medical College Teaching Hospital.',
                   is_featured=False, slug=generate_slug('Dr. Ananda Prasad Acharya')),

            Doctor(name='Dr. Kumar Narayan', city_id=2, specialty_id=7, experience=41,
                   education='MBBS', college='Institute of Medicine',
                   description='Established in 1982. Provides general medical services.',
                   is_featured=False, slug=generate_slug('Dr. Kumar Narayan')),

            Doctor(name='Dr. Malla Mahabir Krishna', city_id=2, specialty_id=7, experience=30,
                   education='MBBS', college='Tribhuvan University Teaching Hospital',
                   description='Provides general medical services. Profile available on Nepalyp.com.',
                   is_featured=False, slug=generate_slug('Dr. Malla Mahabir Krishna')),

            Doctor(name='Dr. Upadhyaya C.P.', city_id=2, specialty_id=7, experience=20,
                   education='MBBS', college='Kathmandu Medical College',
                   description='Verified professional.',
                   is_featured=False, slug=generate_slug('Dr. Upadhyaya C.P.')),

            # Kathmandu Doctors
            Doctor(name='Dr. Rajendra Prasad Miya', city_id=1, specialty_id=7, experience=22,
                   education='MBBS, MD', college='Tribhuvan University Teaching Hospital',
                   description='A highly respected General Practitioner with extensive experience in internal medicine.',
                   is_featured=True, slug=generate_slug('Dr. Rajendra Prasad Miya')),

            Doctor(name='Dr. Shila Rana', city_id=1, specialty_id=4, experience=18,
                   education='MBBS, MD (Pediatrics)', college='KIST Medical College',
                   description='Known for her compassionate care and expertise in pediatric diseases.',
                   is_featured=False, slug=generate_slug('Dr. Shila Rana')),

            Doctor(name='Dr. Pravin Mishra', city_id=1, specialty_id=3, experience=28,
                   education='MBBS, MD, DM (Cardiology)', college='NAMS (National Academy of Medical Sciences)',
                   description='Expert in interventional cardiology and heart failure management.',
                   is_featured=True, slug=generate_slug('Dr. Pravin Mishra')),

            Doctor(name='Dr. Ranjeeta Karki', city_id=1, specialty_id=2, experience=16,
                   education='MBBS, MS (OBGYN)', college='Patan Academy of Health Sciences',
                   description='Specialist in high-risk pregnancy and advanced laparoscopic surgery.',
                   is_featured=False, slug=generate_slug('Dr. Ranjeeta Karki')),

            Doctor(name='Dr. Ramesh K. Shrestha', city_id=1, specialty_id=5, experience=35,
                   education='MBBS, MS (Ortho), MCh', college='Kathmandu Medical College',
                   description='A leading orthopedic surgeon specializing in joint replacement and trauma.',
                   is_featured=False, slug=generate_slug('Dr. Ramesh K. Shrestha'))
        ]
        db.session.add_all(doctors_data)
        db.session.commit()
        print(f"Added {len(doctors_data)} doctors.")

        # Add sample users (including one admin)
        admin_user = User(name='Admin User', email='admin@example.com', is_admin=True)
        admin_user.set_password('admin123')  # Change this in production!

        users_data = [
            admin_user,  # First user is admin
            User(name='Amit Singh', email='amit@example.com'),
            User(name='Sita Sharma', email='sita@example.com'),
            User(name='Ramesh Karki', email='ramesh@example.com'),
            User(name='Gita Thapa', email='gita@example.com'),
            User(name='Bikram Lama', email='bikram@example.com')
        ]

        # Set passwords for non-admin users
        for user in users_data[1:]:
            user.set_password('password123')

        db.session.add_all(users_data)
        db.session.commit()
        print(f"Added {len(users_data)} users (1 admin).")

        # Add sample ratings
        ratings_data = [
            Rating(doctor_id=1, user_id=2, rating=5, comment='Dr. Madan is very thorough and takes time to listen.'),
            Rating(doctor_id=1, user_id=3, rating=4, comment='Excellent GP, diagnosed my condition correctly.'),
            Rating(doctor_id=6, user_id=2, rating=5, comment='Dr. Pravin is a lifesaver! Highly recommended.'),
            Rating(doctor_id=6, user_id=3, rating=5, comment='The best cardiologist in the valley, in my opinion.'),
            Rating(doctor_id=7, user_id=5, rating=5, comment='Dr. Ranjeeta made my pregnancy journey smooth and stress-free.'),
            Rating(doctor_id=7, user_id=6, rating=4, comment='A very skilled and caring gynecologist.'),
            Rating(doctor_id=8, user_id=2, rating=5, comment='Dr. Ramesh performed my knee replacement perfectly. I can walk without pain now!'),
            Rating(doctor_id=8, user_id=3, rating=4, comment='Great experience. Explained everything clearly.')
        ]
        db.session.add_all(ratings_data)
        db.session.commit()
        print(f"Added {len(ratings_data)} ratings.")

        # Add sample advertisements
        ads_data = [
            # Homepage sidebar ad
            Advertisement(
                name='Health Insurance Promo',
                ad_type='banner',
                position='homepage_sidebar',
                format='300x250',
                image_url='https://picsum.photos/seed/healthins/300/250',
                link_url='https://example.com/health-insurance',
                alt_text='Get Health Insurance Today',
                is_active=True,
                priority=10,
                weight=5,
                advertiser_name='Nepal Health Insurance Co.'
            ),

            # Profile top banner - targeted to Cardiology
            Advertisement(
                name='Heart Care Center Ad',
                ad_type='banner',
                position='profile_top',
                format='728x90',
                image_url='https://picsum.photos/seed/heartcare/728/90',
                link_url='https://example.com/heart-care',
                alt_text='Advanced Heart Care Services',
                target_specialty_id=3,  # Cardiologist
                is_active=True,
                priority=8,
                weight=3,
                advertiser_name='Nepal Heart Care Center'
            ),

            # Profile inline ad - general
            Advertisement(
                name='Medical Equipment Store',
                ad_type='banner',
                position='profile_inline',
                format='336x280',
                image_url='https://picsum.photos/seed/medequip/336/280',
                link_url='https://example.com/medical-equipment',
                alt_text='Quality Medical Equipment',
                is_active=True,
                priority=5,
                weight=2,
                advertiser_name='MedEquip Nepal'
            ),

            # Footer banner
            Advertisement(
                name='Hospital Services Banner',
                ad_type='banner',
                position='footer_banner',
                format='970x250',
                image_url='https://picsum.photos/seed/hospital/970/250',
                link_url='https://example.com/hospital-services',
                alt_text='24/7 Hospital Services',
                is_active=True,
                priority=6,
                weight=4,
                advertiser_name='Grande International Hospital'
            ),

            # Text ad example
            Advertisement(
                name='Pharmacy Text Ad',
                ad_type='text',
                position='homepage_sidebar',
                format='text',
                link_url='https://example.com/pharmacy',
                html_content='<h4>Online Pharmacy</h4><p>Get medicines delivered to your doorstep. 20% off on first order!</p>',
                is_active=True,
                priority=3,
                weight=2,
                advertiser_name='Nepal Online Pharmacy'
            )
        ]
        db.session.add_all(ads_data)
        db.session.commit()
        print(f"Added {len(ads_data)} sample advertisements.")

        print("\nDatabase setup complete!")
        print("\n=== Login Credentials ===")
        print("Admin User:")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("\nRegular Users:")
        print("  Email: amit@example.com (or others)")
        print("  Password: password123")
        print("==========================")


if __name__ == '__main__':
    setup_database()
