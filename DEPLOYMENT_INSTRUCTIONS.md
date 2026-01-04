# Deployment Instructions - 24K Doctors Update

## What's Changed
- ✅ NMC# display on doctor cards and profiles
- ✅ Fixed critical bug: doctors can't rate themselves
- ✅ Cleaned duplicate specializations (37→25)
- ✅ Added pagination to all admin pages
- ✅ Ready to import 24K doctors

## Step 1: Push Code to Git

```bash
# Add all changes
git add .

# Commit
git commit -m "Add NMC#, fix self-rating, optimize for 24K doctors

- Display NMC registration numbers on cards/profiles
- Prevent doctors from rating themselves
- Clean duplicate specializations (37→25)
- Add pagination to admin panels
- Import 24K doctors from NMC dataset"

# Push to trigger DigitalOcean deployment
git push origin main
```

## Step 2: Wait for Deployment

1. Go to your DigitalOcean App Platform dashboard
2. Wait for deployment to complete (usually 3-5 minutes)
3. Check deployment logs for any errors

## Step 3: Run Migrations in Console

1. In DigitalOcean App Platform, go to your app
2. Click on **Console** tab
3. Run these commands **in order**:

```bash
# First, clean up city data
python migrate_cleanup_cities.py

# Then, import doctors
python migrate_import_24k_doctors.py
```

**migrate_cleanup_cities.py** will:
- Remove invalid city names (house numbers, typos)
- Consolidate neighborhoods into parent cities
- Standardize city name cases
- Take ~1 minute

**migrate_import_24k_doctors.py** will:
- Clean duplicate specializations
- Import ~24K doctors from nmc_doctors_complete.csv
- Skip existing doctors (safe to re-run)
- Take about 5-10 minutes

## Step 4: Verify

Check your app:
- Homepage should show "24,000+ Doctors Listed"
- Search should return results from all cities
- Doctor cards should show NMC# numbers
- Doctors can't rate themselves (test this!)

## Troubleshooting

**If migration fails:**
```bash
# Check if CSV file exists
ls -la nmc_doctors_complete.csv

# Check database connection
python -c "from app import app, db; print('DB OK')"

# Re-run migration (it's safe)
python migrate_import_24k_doctors.py
```

**If CSV is missing:**
The file should be in Git. If not, you may need to re-push:
```bash
git add nmc_doctors_complete.csv
git commit -m "Add NMC complete dataset"
git push
```

## Expected Results

**Before:**
- ~3,000 doctors
- Manual specializations
- Doctors could rate themselves

**After:**
- ~24,000 doctors
- 25 clean specializations
- Self-rating prevented
- NMC# displayed everywhere
