"""WSGI entry point for RateSewa"""
import os
import sys

# Ensure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app, db

# Only create tables in development (SQLite), not in production
# Production should use migrations instead
if os.environ.get('DATABASE_URL') is None:
    # Local development only
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables ready (development)")
        except Exception as e:
            print(f"⚠️  Database setup: {e}")
else:
    # Production: Run migrations for missing tables directly
    print("Production mode - checking/creating missing tables...")
    try:
        from sqlalchemy import text, inspect

        with app.app_context():
            engine = db.engine
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()

            # Tables to create if missing
            tables_sql = {
                'clinics': """
                    CREATE TABLE IF NOT EXISTS clinics (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        slug VARCHAR(250) UNIQUE NOT NULL,
                        city_id INTEGER,
                        address TEXT,
                        city VARCHAR(100),
                        phone_number VARCHAR(20),
                        phone VARCHAR(20),
                        email VARCHAR(120),
                        website VARCHAR(200),
                        description TEXT,
                        logo_url VARCHAR(500),
                        clinic_type VARCHAR(50) DEFAULT 'clinic',
                        is_featured BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
                        is_verified BOOLEAN DEFAULT FALSE,
                        created_by_user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'clinic_doctors': """
                    CREATE TABLE IF NOT EXISTS clinic_doctors (
                        id SERIAL PRIMARY KEY,
                        clinic_id INTEGER NOT NULL,
                        doctor_id INTEGER NOT NULL,
                        role VARCHAR(50) DEFAULT 'consultant',
                        consultation_fee INTEGER,
                        status VARCHAR(20) DEFAULT 'pending',
                        invited_by_user_id INTEGER,
                        responded_at TIMESTAMP,
                        rejection_reason VARCHAR(500),
                        slot_duration_minutes INTEGER DEFAULT 15,
                        max_patients_per_slot INTEGER DEFAULT 1,
                        accepts_online_booking BOOLEAN DEFAULT TRUE,
                        booking_notice_hours INTEGER DEFAULT 2,
                        cancellation_notice_hours INTEGER DEFAULT 24,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT unique_clinic_doctor UNIQUE (clinic_id, doctor_id)
                    )
                """,
                'clinic_staff': """
                    CREATE TABLE IF NOT EXISTS clinic_staff (
                        id SERIAL PRIMARY KEY,
                        clinic_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        role VARCHAR(50) DEFAULT 'staff',
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT unique_clinic_staff UNIQUE (clinic_id, user_id)
                    )
                """,
                'clinic_schedules': """
                    CREATE TABLE IF NOT EXISTS clinic_schedules (
                        id SERIAL PRIMARY KEY,
                        clinic_doctor_id INTEGER NOT NULL,
                        day_of_week INTEGER NOT NULL,
                        start_time TIME NOT NULL,
                        end_time TIME NOT NULL,
                        max_appointments INTEGER DEFAULT 20,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'schedule_exceptions': """
                    CREATE TABLE IF NOT EXISTS schedule_exceptions (
                        id SERIAL PRIMARY KEY,
                        clinic_doctor_id INTEGER NOT NULL,
                        exception_date DATE NOT NULL,
                        exception_type VARCHAR(20) NOT NULL,
                        start_time TIME,
                        end_time TIME,
                        reason VARCHAR(200),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'clinic_accounts': """
                    CREATE TABLE IF NOT EXISTS clinic_accounts (
                        id SERIAL PRIMARY KEY,
                        manager_user_id INTEGER NOT NULL,
                        name VARCHAR(200),
                        subscription_tier VARCHAR(50) DEFAULT 'clinic_starter',
                        max_doctors INTEGER DEFAULT 3,
                        subscription_expires_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'clinic_manager_doctors': """
                    CREATE TABLE IF NOT EXISTS clinic_manager_doctors (
                        id SERIAL PRIMARY KEY,
                        manager_user_id INTEGER NOT NULL,
                        doctor_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'appointment_reminders': """
                    CREATE TABLE IF NOT EXISTS appointment_reminders (
                        id SERIAL PRIMARY KEY,
                        appointment_id INTEGER NOT NULL,
                        reminder_type VARCHAR(20) NOT NULL,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'sent',
                        response_received BOOLEAN DEFAULT FALSE,
                        response_text VARCHAR(200),
                        response_at TIMESTAMP
                    )
                """,
                'patient_no_show_records': """
                    CREATE TABLE IF NOT EXISTS patient_no_show_records (
                        id SERIAL PRIMARY KEY,
                        patient_phone VARCHAR(20) NOT NULL,
                        patient_user_id INTEGER,
                        appointment_id INTEGER NOT NULL,
                        no_show_date DATE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
            }

            created = 0
            for table_name, create_sql in tables_sql.items():
                if table_name not in existing_tables:
                    try:
                        with engine.connect() as conn:
                            conn.execute(text(create_sql))
                            conn.commit()
                        print(f"  ✅ Created table: {table_name}")
                        created += 1
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            print(f"  ⚠️ {table_name}: {e}")

            if created > 0:
                print(f"✅ Created {created} missing tables")
            else:
                print("✅ All tables exist")

    except Exception as e:
        print(f"⚠️ Migration check (non-fatal): {e}")

# Expose the app for gunicorn
application = app

if __name__ == '__main__':
    app.run()
