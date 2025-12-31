import sqlite3
from flask import current_app, g
import os

# This function gets the database connection.
# It connects to the database specified in the app config.
def get_db():
    if 'db' not in g:
        # g is a special object that is unique for each request.
        # We use it to store our database connection.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# This function is called when the application context ends.
# It closes the database connection.
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """Create the database tables."""
    # Ensure the instance folder exists
    os.makedirs(current_app.instance_path, exist_ok=True)
    
    db = get_db()

    # current_app.open_resource opens a file relative to the flaskr package.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def seed_data():
    """Populate the database with initial data."""
    db = get_db()
    cursor = db.cursor()
    
    # Add cities
    cities = [
        ('Kathmandu', 'Capital of Nepal'),
        ('Biratnagar', 'Industrial city'),
        ('Chitwan', 'Tourist destination'),
        ('Birtamod', 'Eastern city')
    ]
    cursor.executemany('INSERT INTO cities (name, description) VALUES (?, ?)', cities)
    
    # Add specialties
    specialties = [
        ('Dermatologist', 'Skin specialist'),
        ('Gynecologist', 'Women health specialist'),
        ('Cardiologist', 'Heart specialist'),
        ('Pediatrician', 'Child specialist'),
        ('Orthopedic', 'Bone specialist'),
        ('Neurologist', 'Nervous system specialist')
    ]
    cursor.executemany('INSERT INTO specialties (name, description) VALUES (?, ?)', specialties)
    
    # Add doctors
    doctors = [
        ('Dr. Rajesh Sharma', 1, 1, 15, 'MBBS, MD', 'Kathmandu Medical College', 'Experienced dermatologist with expertise in skin cancer treatment'),
        ('Dr. Maya Gurung', 1, 2, 12, 'MBBS, MS', 'Tribhuvan University Teaching Hospital', 'Specialist in high-risk pregnancy and infertility'),
        ('Dr. Prakash Thapa', 1, 3, 20, 'MBBS, MD, DM', 'National Medical College', 'Expert in interventional cardiology and heart failure management'),
        ('Dr. Anisha Karki', 2, 1, 8, 'MBBS, MD', 'B.P. Koirala Institute of Health Sciences', 'Specializes in cosmetic dermatology and laser treatments'),
        ('Dr. Sanjay Mishra', 2, 2, 10, 'MBBS, MS', 'Birat Medical College', 'Expert in laparoscopic gynecological surgeries'),
        ('Dr. Sunita Rai', 3, 3, 18, 'MBBS, MD, DM', 'Chitwan Medical College', 'Specializes in pediatric cardiology'),
        ('Dr. Bimal Lama', 3, 4, 14, 'MBBS, MD', 'Institute of Medicine', 'Expert in pediatric infectious diseases'),
        ('Dr. Ramesh Adhikari', 4, 5, 22, 'MBBS, MS, MCh', 'Koshi Medical College', 'Specialist in joint replacement surgery'),
        ('Dr. Pooja Shrestha', 4, 6, 11, 'MBBS, MD', 'National Academy of Medical Sciences', 'Expert in epilepsy and movement disorders')
    ]
    cursor.executemany('INSERT INTO doctors (name, city_id, specialty_id, experience, education, college, description) VALUES (?, ?, ?, ?, ?, ?, ?)', doctors)
    
    # Add some sample users for ratings
    users = [
        ('Amit Singh', 'amit@example.com'),
        ('Sita Sharma', 'sita@example.com'),
        ('Ramesh Karki', 'ramesh@example.com'),
        ('Gita Thapa', 'gita@example.com'),
        ('Bikram Lama', 'bikram@example.com')
    ]
    cursor.executemany('INSERT INTO users (name, email) VALUES (?, ?)', users)

    # Add some sample ratings
    ratings = [
        (1, 1, 5, 'Excellent doctor! Very knowledgeable and caring.'),
        (1, 2, 4, 'Dr. Rajesh is very professional and provided great treatment.'),
        (2, 3, 5, 'Dr. Maya is the best gynecologist I have ever visited.'),
        (3, 4, 5, 'Dr. Prakash saved my father\'s life. Highly recommended.'),
        (4, 5, 4, 'Good doctor with modern techniques.'),
        (5, 1, 5, 'Very professional and caring doctor.'),
        (6, 2, 4, 'Dr. Sunita is great with children.'),
        (7, 3, 5, 'Very knowledgeable and friendly.'),
        (8, 4, 4, 'Good experience with Dr. Ramesh.'),
        (9, 5, 5, 'Dr. Pooja is an excellent neurologist.')
    ]
    cursor.executemany('INSERT INTO ratings (doctor_id, user_id, rating, comment) VALUES (?, ?, ?, ?)', ratings)
    
    db.commit()