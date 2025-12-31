"""
Migration script to add self-registration and subscription features
Adds fields for:
- Doctor subscription tiers (monetization)
- Self-registration flow (new doctor proposals)
"""
from app import app, db
from sqlalchemy import text
from datetime import datetime


def upgrade_database():
    """Add new fields for self-registration and subscription management"""
    with app.app_context():
        print("Starting migration: add_self_registration")

        try:
            engine = db.engine

            with engine.connect() as conn:
                # Start transaction
                trans = conn.begin()

                try:
                    # ===== Doctor Model Updates =====
                    print("Adding subscription fields to doctors table...")

                    # Add subscription tier field
                    conn.execute(text("""
                        ALTER TABLE doctors
                        ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free'
                    """))
                    print("  ✓ Added subscription_tier")

                    # Add subscription expires at
                    conn.execute(text("""
                        ALTER TABLE doctors
                        ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP
                    """))
                    print("  ✓ Added subscription_expires_at")

                    # Add trial ends at
                    conn.execute(text("""
                        ALTER TABLE doctors
                        ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMP
                    """))
                    print("  ✓ Added trial_ends_at")

                    # Add Stripe customer ID
                    conn.execute(text("""
                        ALTER TABLE doctors
                        ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255)
                    """))
                    print("  ✓ Added stripe_customer_id")

                    # ===== VerificationRequest Model Updates =====
                    print("\nAdding self-registration fields to verification_requests table...")

                    # Make doctor_id nullable for new registrations
                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ALTER COLUMN doctor_id DROP NOT NULL
                    """))
                    print("  ✓ Made doctor_id nullable")

                    # Add is_new_doctor flag
                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ADD COLUMN IF NOT EXISTS is_new_doctor BOOLEAN DEFAULT FALSE
                    """))
                    print("  ✓ Added is_new_doctor")

                    # Add proposed doctor information fields
                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ADD COLUMN IF NOT EXISTS proposed_name VARCHAR(200)
                    """))
                    print("  ✓ Added proposed_name")

                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ADD COLUMN IF NOT EXISTS proposed_specialty_id INTEGER REFERENCES specialties(id)
                    """))
                    print("  ✓ Added proposed_specialty_id")

                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ADD COLUMN IF NOT EXISTS proposed_city_id INTEGER REFERENCES cities(id)
                    """))
                    print("  ✓ Added proposed_city_id")

                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ADD COLUMN IF NOT EXISTS proposed_education TEXT
                    """))
                    print("  ✓ Added proposed_education")

                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ADD COLUMN IF NOT EXISTS proposed_college TEXT
                    """))
                    print("  ✓ Added proposed_college")

                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ADD COLUMN IF NOT EXISTS proposed_experience INTEGER
                    """))
                    print("  ✓ Added proposed_experience")

                    # Commit the transaction
                    trans.commit()
                    print("\n✅ Migration completed successfully!")
                    print("\nNext steps:")
                    print("1. Restart your Flask application")
                    print("2. Test the self-registration flow at /doctor/self-register")
                    print("3. Test admin approval creates new doctor profiles")

                except Exception as e:
                    trans.rollback()
                    print(f"\n❌ Migration failed: {str(e)}")
                    raise

        except Exception as e:
            print(f"\n❌ Error during migration: {str(e)}")
            raise


def downgrade_database():
    """Remove self-registration and subscription fields (rollback migration)"""
    with app.app_context():
        print("Starting rollback: remove_self_registration")

        try:
            engine = db.engine

            with engine.connect() as conn:
                trans = conn.begin()

                try:
                    # Remove fields from doctors table
                    print("Removing subscription fields from doctors table...")
                    conn.execute(text("ALTER TABLE doctors DROP COLUMN IF EXISTS subscription_tier"))
                    conn.execute(text("ALTER TABLE doctors DROP COLUMN IF EXISTS subscription_expires_at"))
                    conn.execute(text("ALTER TABLE doctors DROP COLUMN IF EXISTS trial_ends_at"))

                    # Remove fields from verification_requests table
                    print("Removing self-registration fields from verification_requests table...")
                    conn.execute(text("ALTER TABLE verification_requests DROP COLUMN IF EXISTS is_new_doctor"))
                    conn.execute(text("ALTER TABLE verification_requests DROP COLUMN IF EXISTS proposed_name"))
                    conn.execute(text("ALTER TABLE verification_requests DROP COLUMN IF EXISTS proposed_specialty_id"))
                    conn.execute(text("ALTER TABLE verification_requests DROP COLUMN IF EXISTS proposed_city_id"))
                    conn.execute(text("ALTER TABLE verification_requests DROP COLUMN IF EXISTS proposed_education"))
                    conn.execute(text("ALTER TABLE verification_requests DROP COLUMN IF EXISTS proposed_college"))
                    conn.execute(text("ALTER TABLE verification_requests DROP COLUMN IF EXISTS proposed_experience"))

                    # Make doctor_id NOT NULL again
                    conn.execute(text("""
                        ALTER TABLE verification_requests
                        ALTER COLUMN doctor_id SET NOT NULL
                    """))

                    trans.commit()
                    print("\n✅ Rollback completed successfully!")

                except Exception as e:
                    trans.rollback()
                    print(f"\n❌ Rollback failed: {str(e)}")
                    raise

        except Exception as e:
            print(f"\n❌ Error during rollback: {str(e)}")
            raise


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        print("=" * 60)
        print("ROLLBACK MODE: Removing self-registration features")
        print("=" * 60)
        downgrade_database()
    else:
        print("=" * 60)
        print("Adding Self-Registration and Subscription Features")
        print("=" * 60)
        upgrade_database()
