"""
Migration script to add doctor verification fields and tables
Run this script to upgrade the database schema for doctor verification features
"""
import os
import sys
from sqlalchemy import create_engine, text

# Ensure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Doctor, VerificationRequest, DoctorResponse


def upgrade_database():
    """Add new fields and tables for doctor verification system"""

    with app.app_context():
        engine = db.engine

        print("🔄 Starting database migration...")

        try:
            # Add new columns to users table
            print("   Adding 'role' and 'doctor_id' columns to users table...")
            with engine.connect() as conn:
                # Check if columns exist first
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='users' AND column_name='role'
                """))

                if result.fetchone() is None:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'patient'"))
                    conn.commit()
                    print("   ✅ Added 'role' column to users")
                else:
                    print("   ⚠️  'role' column already exists in users")

                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='users' AND column_name='doctor_id'
                """))

                if result.fetchone() is None:
                    conn.execute(text("ALTER TABLE users ADD COLUMN doctor_id INTEGER REFERENCES doctors(id)"))
                    conn.commit()
                    print("   ✅ Added 'doctor_id' column to users")
                else:
                    print("   ⚠️  'doctor_id' column already exists in users")

            # Add new columns to doctors table
            print("   Adding verification columns to doctors table...")
            with engine.connect() as conn:
                columns_to_add = [
                    ("nmc_number", "VARCHAR(50) UNIQUE"),
                    ("phone_number", "VARCHAR(20)"),
                    ("practice_address", "TEXT"),
                    ("profile_views", "INTEGER DEFAULT 0")
                ]

                for col_name, col_type in columns_to_add:
                    result = conn.execute(text(f"""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name='doctors' AND column_name='{col_name}'
                    """))

                    if result.fetchone() is None:
                        conn.execute(text(f"ALTER TABLE doctors ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        print(f"   ✅ Added '{col_name}' column to doctors")
                    else:
                        print(f"   ⚠️  '{col_name}' column already exists in doctors")

            # Create new tables
            print("   Creating verification_requests and doctor_responses tables...")
            db.create_all()
            print("   ✅ Created new tables")

            print("\n✅ Migration completed successfully!")
            print("\n📝 Summary of changes:")
            print("   - Added 'role' and 'doctor_id' to users table")
            print("   - Added 'nmc_number', 'phone_number', 'practice_address', 'profile_views' to doctors table")
            print("   - Created 'verification_requests' table")
            print("   - Created 'doctor_responses' table")

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print("\nIf you see 'column already exists' errors, you can safely ignore them.")
            print("The migration will only add missing columns.")
            sys.exit(1)


def downgrade_database():
    """Remove doctor verification fields and tables (NOT RECOMMENDED for production)"""

    print("⚠️  WARNING: This will remove all doctor verification data!")
    confirm = input("Are you sure you want to downgrade? Type 'yes' to confirm: ")

    if confirm.lower() != 'yes':
        print("Downgrade cancelled.")
        return

    with app.app_context():
        engine = db.engine

        print("🔄 Starting database downgrade...")

        try:
            with engine.connect() as conn:
                # Drop new tables
                print("   Dropping verification_requests and doctor_responses tables...")
                conn.execute(text("DROP TABLE IF EXISTS doctor_responses CASCADE"))
                conn.execute(text("DROP TABLE IF EXISTS verification_requests CASCADE"))
                conn.commit()

                # Remove columns from users
                print("   Removing columns from users table...")
                conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS doctor_id"))
                conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS role"))
                conn.commit()

                # Remove columns from doctors
                print("   Removing columns from doctors table...")
                conn.execute(text("ALTER TABLE doctors DROP COLUMN IF EXISTS nmc_number"))
                conn.execute(text("ALTER TABLE doctors DROP COLUMN IF EXISTS phone_number"))
                conn.execute(text("ALTER TABLE doctors DROP COLUMN IF EXISTS practice_address"))
                conn.execute(text("ALTER TABLE doctors DROP COLUMN IF EXISTS profile_views"))
                conn.commit()

            print("\n✅ Downgrade completed successfully!")

        except Exception as e:
            print(f"\n❌ Downgrade failed: {e}")
            sys.exit(1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Database migration for doctor verification')
    parser.add_argument('--downgrade', action='store_true', help='Downgrade database (remove changes)')

    args = parser.parse_args()

    if args.downgrade:
        downgrade_database()
    else:
        upgrade_database()
