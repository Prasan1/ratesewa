#!/usr/bin/env python3
"""
TEMPLATE: How to create your own doctor import script

STEPS TO USE THIS TEMPLATE:
1. Copy this file and rename it (e.g., import_hospital_name.py)
2. Update DOCTORS_DATA with your doctors
3. Update the hospital/clinic name in descriptions
4. Add a route in app.py (see instructions below)
5. Add a button in admin_import_doctors.html
6. Commit, push, and run from admin panel

"""

from app import app, db
from models import Doctor, Specialty, City
from slugify import slugify

# ============================================================
# STEP 1: ADD YOUR DOCTORS HERE
# ============================================================
DOCTORS_DATA = [
    # Example doctors - replace with your own data
    {"name": "Dr. John Doe", "specialty": "Cardiologist", "city": "Kathmandu"},
    {"name": "Dr. Jane Smith", "specialty": "Pediatrician", "city": "Pokhara"},
    {"name": "Dr. Ram Sharma", "specialty": "Dermatologist", "city": "Lalitpur"},
    # Add more doctors here...
]

# ============================================================
# STEP 2: UPDATE THIS FUNCTION NAME AND DESCRIPTION
# ============================================================
def import_your_hospital_doctors():
    """Import doctors from [YOUR HOSPITAL NAME]"""

    with app.app_context():
        print("=" * 70)
        print("Importing [YOUR HOSPITAL NAME] Doctors")  # Update this
        print("=" * 70)

        imported = 0
        skipped = 0
        errors = 0

        for doctor_data in DOCTORS_DATA:
            name = doctor_data['name']

            try:
                # Check if doctor already exists
                slug = slugify(name)
                existing = Doctor.query.filter_by(slug=slug).first()

                if existing:
                    print(f"⏭️  Skipping {name} - already exists")
                    skipped += 1
                    continue

                # Get or create specialty
                specialty_name = doctor_data['specialty']
                specialty = Specialty.query.filter(
                    Specialty.name.ilike(specialty_name)
                ).first()

                if not specialty:
                    specialty = Specialty(name=specialty_name)
                    db.session.add(specialty)
                    db.session.flush()
                    print(f"   ✨ Created specialty: {specialty_name}")

                # Get or create city
                city_name = doctor_data['city']
                city = City.query.filter(City.name.ilike(city_name)).first()

                if not city:
                    city = City(name=city_name)
                    db.session.add(city)
                    db.session.flush()
                    print(f"   ✨ Created city: {city_name}")

                # Create description (update hospital name here)
                description = f"{name} is a {specialty_name} practicing at [YOUR HOSPITAL NAME], {city_name}, Nepal."

                # Create doctor
                doctor = Doctor(
                    name=name,
                    specialty_id=specialty.id,
                    city_id=city.id,
                    description=description,
                    education=None,  # Will be filled when doctor claims profile (e.g., "MBBS, MD")
                    college=None,  # Will be filled when doctor claims profile (e.g., "Tribhuvan University")
                    workplace="[YOUR HOSPITAL/CLINIC NAME], [CITY]",  # Update this (e.g., "Grande Hospital, Kathmandu")
                    experience=5,  # Default years of experience
                    photo_url=None,
                    slug=slug,
                    is_active=True  # Important: Make them visible on homepage!
                )

                db.session.add(doctor)
                print(f"✅ Added: {name} - {specialty_name}")
                imported += 1

            except Exception as e:
                print(f"❌ Error adding {name}: {str(e)}")
                errors += 1
                continue

        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "=" * 70)
            print(f"✅ Import Complete!")
            print(f"   Imported: {imported}")
            print(f"   Skipped:  {skipped}")
            print(f"   Errors:   {errors}")
            print("=" * 70)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing to database: {str(e)}")
            print("   All changes have been rolled back.")

if __name__ == '__main__':
    import_your_hospital_doctors()


# ============================================================
# STEP 3: ADD A ROUTE IN app.py
# ============================================================
# Add this code to app.py after the other import routes:
"""
@app.route('/admin/import-your-hospital/run', methods=['POST'])
@admin_required
def run_import_your_hospital():
    \"\"\"Import doctors from [YOUR HOSPITAL NAME]\"\"\"
    try:
        # Import the function from your script
        from import_your_hospital import import_your_hospital_doctors

        # Capture output
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        # Run the import
        import_your_hospital_doctors()

        # Get the output
        output = buffer.getvalue()
        sys.stdout = old_stdout

        flash('[YOUR HOSPITAL] doctors import completed!', 'success')
        return render_template('admin_import_result.html', output=output)

    except Exception as e:
        flash(f'Error during import: {str(e)}', 'danger')
        return redirect(url_for('import_doctors_page'))
"""

# ============================================================
# STEP 4: ADD A BUTTON IN admin_import_doctors.html
# ============================================================
# Add this HTML in templates/admin_import_doctors.html:
"""
<!-- Your Hospital Import -->
<div class="card shadow-sm mb-4">
    <div class="card-body">
        <h5 class="card-title">Import [YOUR HOSPITAL NAME] Doctors</h5>
        <p class="text-muted">
            Import doctors from [YOUR HOSPITAL NAME], [CITY].
        </p>

        <div class="alert alert-info">
            <i class="fas fa-hospital me-2"></i>
            <strong>Source:</strong> [YOUR HOSPITAL] Website
            <br>
            <strong>City:</strong> [CITY NAME]
            <br>
            <strong>Doctors to import:</strong> XX doctors across X departments
        </div>

        <form method="POST" action="{{ url_for('run_import_your_hospital') }}" class="d-inline" onsubmit="return confirm('Import [YOUR HOSPITAL] doctors?');">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            <button type="submit" class="btn btn-primary btn-lg mt-3">
                <i class="fas fa-hospital me-2"></i>Import [YOUR HOSPITAL] Doctors
            </button>
        </form>
    </div>
</div>
"""
