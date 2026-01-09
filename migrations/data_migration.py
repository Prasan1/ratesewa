#!/usr/bin/env python3
"""
Data migration script to copy data from doctors table to normalized tables.
Run this AFTER applying the 001_add_normalized_doctor_tables migration.

Works with both SQLite and PostgreSQL.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Doctor, DoctorContact, DoctorSubscription, DoctorCredentials, DoctorSettings
from datetime import datetime

def migrate_data():
    """Copy data from doctors table to normalized tables"""
    with app.app_context():
        print("Starting data migration...")
        print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Check if migration is needed
        contact_count = DoctorContact.query.count()
        if contact_count > 0:
            print(f"\n⚠️  Data already migrated ({contact_count} records in doctor_contact)")
            response = input("Do you want to re-run the migration? This will duplicate data! (yes/no): ")
            if response.lower() != 'yes':
                print("Aborting.")
                return

        # Get all doctors
        doctors = Doctor.query.all()
        print(f"\nFound {len(doctors)} doctors to migrate")

        migrated = 0
        errors = 0

        for doctor in doctors:
            try:
                # Create doctor_contact
                if not DoctorContact.query.filter_by(doctor_id=doctor.id).first():
                    contact = DoctorContact(
                        doctor_id=doctor.id,
                        phone_number=doctor.phone_number,
                        practice_address=doctor.practice_address,
                        workplace=doctor.workplace,
                        latitude=doctor.latitude if hasattr(doctor, 'latitude') else None,
                        longitude=doctor.longitude if hasattr(doctor, 'longitude') else None,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(contact)

                # Create doctor_subscription
                if not DoctorSubscription.query.filter_by(doctor_id=doctor.id).first():
                    subscription = DoctorSubscription(
                        doctor_id=doctor.id,
                        subscription_tier=doctor.subscription_tier or 'free',
                        subscription_expires_at=doctor.subscription_expires_at if hasattr(doctor, 'subscription_expires_at') else None,
                        trial_ends_at=doctor.trial_ends_at if hasattr(doctor, 'trial_ends_at') else None,
                        stripe_customer_id=doctor.stripe_customer_id if hasattr(doctor, 'stripe_customer_id') else None,
                        profile_views=doctor.profile_views or 0,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(subscription)

                # Create doctor_credentials
                if not DoctorCredentials.query.filter_by(doctor_id=doctor.id).first():
                    credentials = DoctorCredentials(
                        doctor_id=doctor.id,
                        nmc_number=doctor.nmc_number if hasattr(doctor, 'nmc_number') else None,
                        external_clinic_url=doctor.external_clinic_url if hasattr(doctor, 'external_clinic_url') else None,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(credentials)

                # Create doctor_settings
                if not DoctorSettings.query.filter_by(doctor_id=doctor.id).first():
                    settings = DoctorSettings(
                        doctor_id=doctor.id,
                        photo_url=doctor.photo_url,
                        working_hours=doctor.working_hours if hasattr(doctor, 'working_hours') else None,
                        clinic_id=doctor.clinic_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(settings)

                migrated += 1

                # Commit every 100 doctors to avoid memory issues
                if migrated % 100 == 0:
                    db.session.commit()
                    print(f"  Migrated {migrated}/{len(doctors)} doctors...")

            except Exception as e:
                print(f"  ❌ Error migrating doctor {doctor.id}: {e}")
                errors += 1
                db.session.rollback()

        # Final commit
        db.session.commit()

        print(f"\n{'='*60}")
        print(f"✅ Migration complete!")
        print(f"{'='*60}")
        print(f"  Total doctors: {len(doctors)}")
        print(f"  Successfully migrated: {migrated}")
        print(f"  Errors: {errors}")

        # Verify
        print(f"\nVerification:")
        print(f"  doctor_contact: {DoctorContact.query.count()} records")
        print(f"  doctor_subscription: {DoctorSubscription.query.count()} records")
        print(f"  doctor_credentials: {DoctorCredentials.query.count()} records")
        print(f"  doctor_settings: {DoctorSettings.query.count()} records")

if __name__ == '__main__':
    migrate_data()
