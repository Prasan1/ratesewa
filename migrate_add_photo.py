#!/usr/bin/env python3
"""
Migration: Add photo_url column to doctors table
"""
import sqlite3

def add_photo_column():
    conn = sqlite3.connect('instance/doctors.db')
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(doctors)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'photo_url' not in columns:
            cursor.execute('ALTER TABLE doctors ADD COLUMN photo_url TEXT')
            conn.commit()
            print("✅ Added 'photo_url' column to doctors table")
        else:
            print("ℹ️  'photo_url' column already exists")

    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_photo_column()
