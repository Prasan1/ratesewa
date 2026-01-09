# Production Database Migration Guide

## Overview

This migration adds 6 normalized tables to separate doctor data for better organization:
- `doctor_contact` - Phone, address, location
- `doctor_subscription` - Billing, tier, profile views
- `doctor_credentials` - NMC number, external URLs
- `doctor_settings` - Photo, working hours
- `doctor_medical_tools` - Medical certificate/prescription templates (for future feature)
- `doctor_template_usage` - Usage analytics (for future feature)

## ⚠️ IMPORTANT: Production has PostgreSQL

Production uses **PostgreSQL** (not SQLite), so we're using Flask-Migrate (Alembic) for database migrations.

## Prerequisites

1. Flask-Migrate is now installed (`Flask-Migrate==4.0.5` in requirements.txt)
2. App has been updated with `Migrate(app, db)` initialization
3. Local development (SQLite) has been successfully migrated and tested

## Deployment Steps for DigitalOcean

### Step 1: Deploy Code Changes

Push the latest code to GitHub (already done):
```bash
git push origin main
```

In DigitalOcean App Platform, the app will automatically redeploy with the new code including:
- Flask-Migrate installed
- Migration files in `migrations/` directory
- Updated `app.py` with Migrate initialization

### Step 2: Access Production Shell

In DigitalOcean App Platform Console:
1. Go to your app
2. Click on "Console" tab
3. Select your web component
4. Click "Run Command" or open terminal

### Step 3: Run Database Migration

In the production console, run:

```bash
# Initialize Flask-Migrate (if not already done)
# This stamps the migration tracking table
python -m flask db current

# Run the migration to create new tables
python -m flask db upgrade

# This will create the 6 new tables in PostgreSQL
```

### Step 4: Run Data Migration

Copy data from `doctors` table to the new normalized tables:

```bash
python migrations/data_migration.py
```

This script will:
- Check if data already exists (prevents duplicate migration)
- Copy all doctor data to the 6 new tables
- Show progress every 100 doctors
- Display final verification counts

**Expected output:**
```
Starting data migration...
Database: postgresql://...

Found XXXX doctors to migrate
  Migrated 100/XXXX doctors...
  Migrated 200/XXXX doctors...
  ...

============================================================
✅ Migration complete!
============================================================
  Total doctors: XXXX
  Successfully migrated: XXXX
  Errors: 0

Verification:
  doctor_contact: XXXX records
  doctor_subscription: XXXX records
  doctor_credentials: XXXX records
  doctor_settings: XXXX records
```

### Step 5: Verify Migration Success

Check that the tables were created and populated:

```bash
# Quick verification using psql (if available)
python -c "from app import app, db; from models import DoctorContact, DoctorSubscription; app.app_context().push(); print(f'Contacts: {DoctorContact.query.count()}'); print(f'Subscriptions: {DoctorSubscription.query.count()}')"
```

### Step 6: Test the Application

1. Visit your production URL
2. Test doctor profiles (should work normally)
3. Log in as a doctor with an account
4. Verify their dashboard loads correctly
5. Check that all doctor data is displayed properly

## What If Something Goes Wrong?

### Rollback Migration

If the migration fails or causes issues:

```bash
# Roll back the database migration
python -m flask db downgrade

# This will drop the 6 new tables
```

The app will continue to work with the old schema since:
- Old columns still exist in `doctors` table
- Code has backward compatibility
- Models have fallbacks for old column access

### Contact Support

If migration fails:
1. Check the error message in console
2. Take a screenshot
3. DO NOT run the migration multiple times
4. Contact the development team with the error details

## Verification Checklist

After migration, verify:

- [ ] All 6 new tables created in PostgreSQL
- [ ] Record counts match `doctors` table count
- [ ] Doctors with accounts (signed up) can log in
- [ ] Doctor dashboards load without errors
- [ ] Doctor profiles display correctly
- [ ] No 500 errors in application logs
- [ ] Search and filtering still works

## Technical Notes

### Why These Tables?

The normalized schema separates doctor data into logical groups:
1. **Better organization**: Related data is grouped together
2. **Future features**: Medical tools table is ready for certificate/prescription feature
3. **Performance**: Can query specific subsets without loading all doctor data
4. **Maintainability**: Easier to add new fields to specific categories

### Backward Compatibility

The migration maintains backward compatibility:
- Old columns remain in `doctors` table
- Code can access data both ways:
  - Old: `doctor.phone_number`
  - New: `doctor.contact.phone_number`
- Models have relationships set up with `lazy='joined'` for performance

### Migration is Idempotent

Running the data migration multiple times is safe:
- Script checks if data already exists
- Prompts before re-running
- Won't create duplicate records

## Timeline

- **Local Development**: Migrated successfully on 2026-01-08
- **Production**: Pending deployment
- **Estimated Migration Time**: ~2-3 minutes for data copy (depends on record count)

## Support

For issues or questions:
- Check application logs in DigitalOcean console
- Review migration output for errors
- Verify database connection is working
- Check that Flask-Migrate is properly installed
