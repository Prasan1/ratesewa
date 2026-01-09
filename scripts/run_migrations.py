#!/usr/bin/env python3
import os
import sys

from flask_migrate import upgrade

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app, db
from models import Doctor, DoctorContact, DoctorSubscription, DoctorCredentials, DoctorSettings
from datetime import datetime


def copy_data_to_normalized_tables():
    """Copy data from doctors table to new normalized tables"""
    print("\nChecking if data migration is needed...")

    # Check if tables already have data
    contact_count = DoctorContact.query.count()
    if contact_count > 0:
        print(f"✓ Data already migrated ({contact_count} records in doctor_contact)")
        return

    print("Starting data migration...")
    doctors = Doctor.query.all()
    print(f"Found {len(doctors)} doctors to migrate")

    migrated = 0
    for doctor in doctors:
        try:
            # Create doctor_contact
            if not DoctorContact.query.filter_by(doctor_id=doctor.id).first():
                contact = DoctorContact(
                    doctor_id=doctor.id,
                    phone_number=doctor.phone_number,
                    practice_address=doctor.practice_address,
                    workplace=doctor.workplace,
                    latitude=getattr(doctor, 'latitude', None),
                    longitude=getattr(doctor, 'longitude', None),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(contact)

            # Create doctor_subscription
            if not DoctorSubscription.query.filter_by(doctor_id=doctor.id).first():
                subscription = DoctorSubscription(
                    doctor_id=doctor.id,
                    subscription_tier=doctor.subscription_tier or 'free',
                    subscription_expires_at=getattr(doctor, 'subscription_expires_at', None),
                    trial_ends_at=getattr(doctor, 'trial_ends_at', None),
                    stripe_customer_id=getattr(doctor, 'stripe_customer_id', None),
                    profile_views=doctor.profile_views or 0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(subscription)

            # Create doctor_credentials
            if not DoctorCredentials.query.filter_by(doctor_id=doctor.id).first():
                credentials = DoctorCredentials(
                    doctor_id=doctor.id,
                    nmc_number=getattr(doctor, 'nmc_number', None),
                    external_clinic_url=getattr(doctor, 'external_clinic_url', None),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(credentials)

            # Create doctor_settings
            if not DoctorSettings.query.filter_by(doctor_id=doctor.id).first():
                settings = DoctorSettings(
                    doctor_id=doctor.id,
                    photo_url=doctor.photo_url,
                    working_hours=getattr(doctor, 'working_hours', None),
                    clinic_id=doctor.clinic_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(settings)

            migrated += 1
            if migrated % 100 == 0:
                db.session.commit()
                print(f"  Migrated {migrated}/{len(doctors)} doctors...")

        except Exception as e:
            print(f"  ❌ Error migrating doctor {doctor.id}: {e}")
            db.session.rollback()

    db.session.commit()
    print(f"\n✅ Data migration complete! Migrated {migrated} doctors")

    # Verify
    print(f"\nVerification:")
    print(f"  doctor_contact: {DoctorContact.query.count()} records")
    print(f"  doctor_subscription: {DoctorSubscription.query.count()} records")
    print(f"  doctor_credentials: {DoctorCredentials.query.count()} records")
    print(f"  doctor_settings: {DoctorSettings.query.count()} records")


def main():
    with app.app_context():
        print("Running database schema migration...")
        upgrade()
        print("✓ Schema migration complete")

        # Copy data to normalized tables
        copy_data_to_normalized_tables()


if __name__ == "__main__":
    main()
