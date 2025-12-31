"""
Migration script to add appointment_id column to ratings table
"""
import sqlite3
import os

def migrate():
    db_path = os.path.join('instance', 'doctors.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(ratings)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'appointment_id' in columns:
            print("Column 'appointment_id' already exists in ratings table. Skipping migration.")
            return True

        # Add appointment_id column
        print("Adding appointment_id column to ratings table...")
        cursor.execute("""
            ALTER TABLE ratings
            ADD COLUMN appointment_id INTEGER
            REFERENCES appointments(id)
        """)

        conn.commit()
        print("Migration completed successfully!")
        return True

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
