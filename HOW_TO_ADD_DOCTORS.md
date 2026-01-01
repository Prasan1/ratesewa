# How to Add Doctors to RankSewa

This guide explains how to add doctors yourself without needing help from Claude.

## Quick Summary

1. **Create/edit a Python import script** with doctor data
2. **Add a route in app.py** to handle the import
3. **Add a button in admin panel** to trigger the import
4. **Commit and push to GitHub** (auto-deploys to production)
5. **Click the import button** in the admin panel

---

## Method 1: Add to Existing Import (Easiest)

If you just want to add a few more doctors to an existing hospital:

### Example: Adding doctors to B&C Medical College

```bash
# 1. Edit the existing file
nano import_bnc_doctors.py

# 2. Add new doctors to the DOCTORS_DATA list:
DOCTORS_DATA = [
    # ... existing doctors ...

    # Add your new doctors here:
    {"name": "Dr. New Doctor Name", "specialty": "Cardiologist", "city": "Birtamod"},
    {"name": "Dr. Another Doctor", "specialty": "Neurologist", "city": "Birtamod"},
]

# 3. Save and exit (Ctrl+X, then Y, then Enter)

# 4. Commit and push
git add import_bnc_doctors.py
git commit -m "Add new doctors to B&C Medical College"
git push

# 5. Go to admin panel → Import Doctors → Click "Import B&C Doctors"
```

---

## Method 2: Create New Import for a Different Hospital

### Step 1: Copy the Template

```bash
cp EXAMPLE_import_template.py import_kmc_doctors.py
```

### Step 2: Edit Your New File

```bash
nano import_kmc_doctors.py
```

Replace:
- `DOCTORS_DATA` - Add all your doctors
- `[YOUR HOSPITAL NAME]` - e.g., "Kathmandu Medical College"
- `[YOUR HOSPITAL/COLLEGE NAME]` - e.g., "KMC"
- Function name: `import_your_hospital_doctors` → `import_kmc_doctors`

**Example:**

```python
DOCTORS_DATA = [
    {"name": "Dr. Suresh Adhikari", "specialty": "Cardiologist", "city": "Kathmandu"},
    {"name": "Dr. Anita Gurung", "specialty": "Pediatrician", "city": "Kathmandu"},
    {"name": "Dr. Prakash Thapa", "specialty": "Orthopedic Surgeon", "city": "Kathmandu"},
]

def import_kmc_doctors():
    """Import doctors from Kathmandu Medical College"""
    # ... rest of the code ...
    description = f"{name} is a {specialty_name} practicing at Kathmandu Medical College, {city_name}, Nepal."
    # ...
    college="Kathmandu Medical College",
```

### Step 3: Add Route in app.py

```bash
nano app.py
```

Find the section with other import routes (search for `run_import_bnc_doctors`), and add:

```python
@app.route('/admin/import-kmc-doctors/run', methods=['POST'])
@admin_required
def run_import_kmc_doctors():
    """Import doctors from KMC"""
    try:
        from import_kmc_doctors import import_kmc_doctors

        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        import_kmc_doctors()

        output = buffer.getvalue()
        sys.stdout = old_stdout

        flash('KMC doctors import completed!', 'success')
        return render_template('admin_import_result.html', output=output)

    except Exception as e:
        flash(f'Error during KMC import: {str(e)}', 'danger')
        return redirect(url_for('import_doctors_page'))
```

### Step 4: Add Button in Admin Panel

```bash
nano templates/admin_import_doctors.html
```

Add this HTML before the "Troubleshooting" card:

```html
<!-- KMC Import -->
<div class="card shadow-sm mb-4">
    <div class="card-body">
        <h5 class="card-title">Import Kathmandu Medical College Doctors</h5>
        <p class="text-muted">
            Import doctors from KMC, Kathmandu.
        </p>

        <div class="alert alert-info">
            <i class="fas fa-hospital me-2"></i>
            <strong>Source:</strong> Kathmandu Medical College
            <br>
            <strong>City:</strong> Kathmandu
            <br>
            <strong>Doctors to import:</strong> 3 doctors
        </div>

        <form method="POST" action="{{ url_for('run_import_kmc_doctors') }}" class="d-inline" onsubmit="return confirm('Import KMC doctors?');">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            <button type="submit" class="btn btn-primary btn-lg mt-3">
                <i class="fas fa-hospital me-2"></i>Import KMC Doctors
            </button>
        </form>
    </div>
</div>
```

### Step 5: Commit and Push

```bash
git add import_kmc_doctors.py app.py templates/admin_import_doctors.html
git commit -m "Add KMC doctor import"
git push
```

### Step 6: Run Import

1. Wait ~2 minutes for DigitalOcean to deploy
2. Go to: Admin → Import Doctors
3. Scroll to "Import Kathmandu Medical College Doctors"
4. Click "Import KMC Doctors"
5. See the results!

---

## Understanding the Data Format

### Doctor Data Dictionary

```python
{
    "name": "Dr. John Doe",           # Full name with title
    "specialty": "Cardiologist",       # Medical specialty
    "city": "Kathmandu"                # City name
}
```

### Common Specialties

Use these exact names (the system will match them or create new ones):

- Cardiologist
- Dermatologist
- Pediatrician
- Neurologist
- Orthopedic Surgeon
- General Surgeon
- Psychiatrist
- Anesthesiologist
- Radiologist
- Pathologist
- Obstetrician & Gynecologist (or OB/GYN)
- Pulmonologist
- Nephrologist
- Endocrinologist
- Gastroenterologist
- Urologist
- Ophthalmologist
- ENT Specialist
- Oncologist

### Cities

Common cities already in database:
- Kathmandu
- Lalitpur
- Bhaktapur
- Pokhara
- Biratnagar
- Birtamod

New cities will be created automatically if they don't exist.

---

## Tips & Tricks

### 1. Getting Doctor Data from a Website

If you have a hospital website with doctor listings:

1. Open the page
2. Copy the doctor names
3. Organize in a spreadsheet (Excel/Google Sheets)
4. Convert to Python format:

**Spreadsheet:**
```
Name                    | Specialty      | City
Dr. Ram Sharma          | Cardiologist   | Kathmandu
Dr. Sita Devi          | Pediatrician   | Kathmandu
```

**Python format:**
```python
{"name": "Dr. Ram Sharma", "specialty": "Cardiologist", "city": "Kathmandu"},
{"name": "Dr. Sita Devi", "specialty": "Pediatrician", "city": "Kathmandu"},
```

### 2. Testing Before Production

You can test the import script locally:

```bash
# On your local machine (not production):
python3 import_kmc_doctors.py
```

This will show you what will happen without affecting production.

### 3. Checking for Duplicates

The script automatically skips duplicates based on the doctor's name (converted to a slug).

For example:
- "Dr. Ram Sharma" becomes slug: "dr-ram-sharma"
- "Dr. Ram Sharma" (added again) → Skipped!

### 4. Re-running Imports

It's safe to run the import multiple times:
- Existing doctors are skipped
- Only new doctors are added
- No data is lost

---

## Common Issues

### Issue 1: "Specialty not found"

**Solution:** The script automatically creates missing specialties. This is not an error!

### Issue 2: "City not found"

**Solution:** The script automatically creates missing cities. This is not an error!

### Issue 3: Doctors not showing on homepage

**Check:**
1. Is `is_active=True` in the script? ✅
2. Did you merge duplicate specialties? (Admin → Manage Specialties → Merge Duplicates)
3. Are you searching with the correct specialty name?

### Issue 4: Import button doesn't work

**Check:**
1. Did you add the route in app.py?
2. Did you push to GitHub?
3. Did you wait 2 minutes for deployment?
4. Is the CSRF token in the form?

---

## Need Help?

If you get stuck:

1. Check the error message in the admin panel
2. Look at existing import scripts (import_bnc_doctors.py) as examples
3. Make sure all file names match (import script, route name, function name)
4. Verify you pushed to GitHub and deployment finished

---

## Summary Checklist

- [ ] Create import script with DOCTORS_DATA
- [ ] Update function name and descriptions
- [ ] Add route in app.py
- [ ] Add button in admin_import_doctors.html
- [ ] Commit all files
- [ ] Push to GitHub
- [ ] Wait for deployment (check GitHub Actions or DigitalOcean)
- [ ] Go to Admin → Import Doctors
- [ ] Click your import button
- [ ] Check results!

**You're done!** 🎉
