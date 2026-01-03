#!/usr/bin/env python3
"""
Migration: Add clinics table and clinic_id column to doctors table (SQLite)
"""
import sqlite3


def migrate():
    conn = sqlite3.connect('instance/doctors.db')
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(doctors)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'clinic_id' not in columns:
            cursor.execute('ALTER TABLE doctors ADD COLUMN clinic_id INTEGER')
            conn.commit()
            print("✅ Added 'clinic_id' column to doctors table")
        else:
            print("ℹ️  'clinic_id' column already exists")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clinics'")
        if not cursor.fetchone():
            cursor.execute(
                """
                CREATE TABLE clinics (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    city_id INTEGER NOT NULL,
                    address TEXT,
                    phone_number TEXT,
                    description TEXT,
                    is_featured BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
                """
            )
            conn.commit()
            print("✅ Created 'clinics' table")
        else:
            print("ℹ️  'clinics' table already exists")
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    migrate()
