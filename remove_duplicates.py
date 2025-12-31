#!/usr/bin/env python3
"""
Remove duplicate doctor entries
Keeps the newer entries from seed_data.py and removes old ones
Transfers ratings and appointments to new doctor IDs
"""
from app import app, db
from models import Doctor, Rating, Appointment, ContactMessage

def remove_duplicates():
    with app.app_context():
        print("🧹 Removing duplicate doctor entries...")
        print()

        # Mapping of old doctor IDs to new doctor IDs
        id_mapping = {
            1: 26,   # Dr. Madan Koirala
            2: 27,   # Dr. Ananda Prasad Acharya
            6: 11,   # Dr. Rajendra Prasad Miya
            7: 12,   # Dr. Shila Rana
            8: 13,   # Dr. Pravin Mishra
            9: 14,   # Dr. Ranjeeta Karki
            10: 15,  # Dr. Ramesh K. Shrestha
        }

        # First, transfer all related data to new doctor IDs
        print("📦 Transferring related data to new doctor records...")
        for old_id, new_id in id_mapping.items():
            old_doc = db.session.get(Doctor, old_id)
            new_doc = db.session.get(Doctor, new_id)

            if not old_doc or not new_doc:
                continue

            # Transfer ratings
            ratings = Rating.query.filter_by(doctor_id=old_id).all()
            if ratings:
                print(f"  📝 Transferring {len(ratings)} ratings: {old_doc.name} ({old_id} → {new_id})")
                for rating in ratings:
                    rating.doctor_id = new_id

            # Transfer appointments
            appointments = Appointment.query.filter_by(doctor_id=old_id).all()
            if appointments:
                print(f"  📅 Transferring {len(appointments)} appointments: {old_doc.name} ({old_id} → {new_id})")
                for appointment in appointments:
                    appointment.doctor_id = new_id

            # Transfer contact messages
            messages = ContactMessage.query.filter_by(doctor_id=old_id).all()
            if messages:
                print(f"  💬 Transferring {len(messages)} messages: {old_doc.name} ({old_id} → {new_id})")
                for message in messages:
                    message.doctor_id = new_id

        db.session.commit()
        print()

        # Now delete the old duplicate doctors
        print("🗑️  Deleting old duplicate doctor records...")
        removed_count = 0
        for old_id in id_mapping.keys():
            doctor = db.session.get(Doctor, old_id)
            if doctor:
                print(f"  ❌ Removing: {doctor.name} (ID: {old_id}, Slug: {doctor.slug})")
                db.session.delete(doctor)
                removed_count += 1

        db.session.commit()

        print(f"\n✅ Removed {removed_count} duplicate doctors")
        print(f"   Remaining doctors: {Doctor.query.count()}")

        # Show remaining doctors
        print("\n📋 Current doctor list:")
        for doc in Doctor.query.order_by(Doctor.name).all():
            print(f"   {doc.id:3d}. {doc.name:35s} | {doc.city.name}")

if __name__ == "__main__":
    remove_duplicates()
