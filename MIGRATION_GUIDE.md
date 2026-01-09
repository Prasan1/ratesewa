# Production Migration Guide - Normalized Doctor Tables

## Quick Summary

Run this single command in DigitalOcean console:

```bash
python run_migration_production.py
```

That's it! The script will:
- Check if tables already exist (safe to run multiple times)
- Create 6 new tables
- Copy all doctor data automatically
- Show verification counts

## What This Migration Does

Creates 6 normalized tables to better organize doctor data:
- `doctor_contact` - Phone, address, location
- `doctor_subscription` - Billing, tier, profile views
- `doctor_credentials` - NMC number, external URLs
- `doctor_settings` - Photo, working hours
- `doctor_medical_tools` - Medical certificate templates (future feature)
- `doctor_template_usage` - Usage analytics (future feature)

## Running in Production (DigitalOcean)

### Step 1: Access Console

1. Go to your DigitalOcean App Platform
2. Click on your app
3. Go to "Console" tab
4. Click "Run Command"

### Step 2: Run Migration

In the console, run:

```bash
python run_migration_production.py
```

You'll see:
- What tables will be created
- Confirmation prompt: type `yes` to proceed
- Progress as tables are created and data is copied
- Final verification showing record counts

### Expected Output

```
======================================================================
DATABASE MIGRATION: Add Normalized Doctor Tables
======================================================================

Database: postgresql://...

Tables to create: doctor_contact, doctor_subscription, doctor_credentials, doctor_settings, doctor_medical_tools, doctor_template_usage

Proceed with migration? (yes/no): yes

Starting migration...
Creating doctor_contact table...
  ✓ doctor_contact created
Creating doctor_subscription table...
  ✓ doctor_subscription created
...

Copying data from doctors table...
Found XXXX doctors to migrate
Copying to doctor_contact...
  ✓ XXXX records copied
...

======================================================================
✅ MIGRATION COMPLETED SUCCESSFULLY!
======================================================================

Final verification:
  doctor_contact: XXXX records
  doctor_subscription: XXXX records
  doctor_credentials: XXXX records
  doctor_settings: XXXX records
  doctor_medical_tools: 0 records
  doctor_template_usage: 0 records
```

## Safety Features

- ✅ **Idempotent**: Safe to run multiple times, skips if tables exist
- ✅ **Transaction-based**: Rolls back on any error
- ✅ **Verification**: Shows final counts to confirm success
- ✅ **Confirmation prompt**: Won't proceed without explicit "yes"
- ✅ **Backward compatible**: App works before and after migration

## If Something Goes Wrong

The migration script uses transactions, so if anything fails it automatically rolls back.

If you need to manually rollback:

```bash
python -c "
from sqlalchemy import create_engine, text
import os
db_url = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://', 1)
engine = create_engine(db_url)
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS doctor_template_usage CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS doctor_medical_tools CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS doctor_settings CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS doctor_credentials CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS doctor_subscription CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS doctor_contact CASCADE'))
    conn.commit()
print('Tables dropped')
"
```

## Testing Locally First

To test on your local development database:

```bash
python run_migration_production.py
```

It will use your local SQLite database and you can verify everything works.

## After Migration

The app will continue working normally. The old columns still exist in the `doctors` table for backward compatibility.

You can verify the app is working by:
1. Visiting your site
2. Searching for doctors
3. Logging in as a doctor
4. Checking the dashboard

## Timeline

- **Estimated time**: 2-3 minutes total
- **Downtime**: None (app keeps running)
- **Risk level**: Low (rollback available, backward compatible)

## Questions?

If the migration fails, check:
1. Database connection is working
2. Console has network access
3. Error message in output
4. Take screenshot and review with team
