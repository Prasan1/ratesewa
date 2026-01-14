"""
Fix duplicate Kathmandu city entries
Run this script in production console
"""
from app import app, db
from models import City, Doctor, Clinic

with app.app_context():
    # Find the duplicate
    dup = City.query.filter(City.name.ilike('%metropolitian%')).first()

    if not dup:
        print("No duplicate found. Already fixed!")
    else:
        print(f"Found duplicate: ID={dup.id}, Name={dup.name}")

        # Update any doctors using duplicate
        doctors = Doctor.query.filter_by(city_id=dup.id).all()
        print(f"Updating {len(doctors)} doctors...")
        for d in doctors:
            d.city_id = 1

        # Update any clinics using duplicate
        clinics = Clinic.query.filter_by(city_id=dup.id).all()
        print(f"Updating {len(clinics)} clinics...")
        for c in clinics:
            c.city_id = 1

        # Delete duplicate
        db.session.delete(dup)
        db.session.commit()
        print("Done! Duplicate city deleted.")
