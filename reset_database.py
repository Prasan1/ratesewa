import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE_FILE = 'doctors.db'
SCHEMA_FILE = 'schema.sql'

print("--- Starting Database Reset ---")

# 1. Delete the old database file if it exists
if os.path.exists(DATABASE_FILE):
    os.remove(DATABASE_FILE)
    print(f"Deleted existing database: {DATABASE_FILE}")

# 2. Create a new database and build the schema from the file
print(f"Creating new database from '{SCHEMA_FILE}'...")
connection = sqlite3.connect(DATABASE_FILE)
with open(SCHEMA_FILE, 'r') as f:
    connection.executescript(f.read())
print("Database schema created successfully.")

# 3. Seed the new database with data
cursor = connection.cursor()
print("Seeding database with data...")

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
    ('Neurologist', 'Nervous system specialist'),
    ('General Practitioner', 'Provides primary and continuing medical care'),
    ('Ayurvedic Practitioner', 'Specialist in traditional Ayurvedic medicine')
]
cursor.executemany('INSERT INTO specialties (name, description) VALUES (?, ?)', specialties)

# Add doctors
doctors = [
    # --- Biratnagar Doctors ---
    ('Dr. Madan Koirala', 2, 7, 25, 'MBBS, MD', 'Kathmandu Medical College', 'Specializes in general medicine and has a focus on chronic conditions.', 1),
    ('Dr. Ananda Prasad Acharya', 2, 7, 15, 'MBBS, MD', 'B.P. Koirala Institute of Health Sciences', 'Verified professional with 5.02 reviews. Associated with Birat Medical College Teaching Hospital.', 0),
    ('Dr. Kumar Narayan', 2, 7, 41, 'MBBS', 'Institute of Medicine', 'Established in 1982. Provides general medical services.', 0),
    ('Dr. Malla Mahabir Krishna', 2, 7, 30, 'MBBS', 'Tribhuvan University Teaching Hospital', 'Provides general medical services. Profile available on Nepalyp.com.', 0),
    ('Dr. Upadhyaya C.P.', 2, 7, 20, 'MBBS', 'Kathmandu Medical College', 'Verified professional.', 0),

    # --- Kathmandu Doctors ---
    ('Dr. Rajendra Prasad Miya', 1, 7, 22, 'MBBS, MD', 'Tribhuvan University Teaching Hospital', 'A highly respected General Practitioner with extensive experience in internal medicine.', 1),
    ('Dr. Shila Rana', 1, 4, 18, 'MBBS, MD (Pediatrics)', 'KIST Medical College', 'Known for her compassionate care and expertise in pediatric diseases.', 0),
    ('Dr. Pravin Mishra', 1, 3, 28, 'MBBS, MD, DM (Cardiology)', 'NAMS (National Academy of Medical Sciences)', 'Expert in interventional cardiology and heart failure management.', 1),
    ('Dr. Ranjeeta Karki', 1, 2, 16, 'MBBS, MS (OBGYN)', 'Patan Academy of Health Sciences', 'Specialist in high-risk pregnancy and advanced laparoscopic surgery.', 0),
    ('Dr. Ramesh K. Shrestha', 1, 5, 35, 'MBBS, MS (Ortho), MCh', 'Kathmandu Medical College', 'A leading orthopedic surgeon specializing in joint replacement and trauma.', 0)
]
# This will now work because the column was just created from the new schema
cursor.executemany('INSERT INTO doctors (name, city_id, specialty_id, experience, education, college, description, is_featured) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', doctors)

# Add users
users = [
    ('Amit Singh', 'amit@example.com', generate_password_hash('password123')),
    ('Sita Sharma', 'sita@example.com', generate_password_hash('password123')),
    ('Ramesh Karki', 'ramesh@example.com', generate_password_hash('password123')),
    ('Gita Thapa', 'gita@example.com', generate_password_hash('password123')),
    ('Bikram Lama', 'bikram@example.com', generate_password_hash('password123'))
]
cursor.executemany('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', users)

# Add ratings
ratings = [
    (1, 1, 5, 'Dr. Madan is very thorough and takes time to listen.'),
    (1, 2, 4, 'Excellent GP, diagnosed my condition correctly.'),
    (6, 1, 5, 'Dr. Pravin is a lifesaver! Highly recommended.'),
    (6, 2, 5, 'The best cardiologist in the valley, in my opinion.'),
    (7, 4, 5, 'Dr. Ranjeeta made my pregnancy journey smooth and stress-free.'),
    (7, 5, 4, 'A very skilled and caring gynecologist.'),
    (8, 1, 5, 'Dr. Ramesh performed my knee replacement perfectly. I can walk without pain now!'),
    (8, 2, 4, 'Great experience. Explained everything clearly.')
]
cursor.executemany('INSERT INTO ratings (doctor_id, user_id, rating, comment) VALUES (?, ?, ?, ?)', ratings)

# 4. Commit and close
connection.commit()
connection.close()

print("--- Database Reset Complete ---")
print(f"Database '{DATABASE_FILE}' is ready with new data.")