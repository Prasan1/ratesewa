# Database Migrations

This directory contains SQL migration scripts for the doctor directory application.

## Production Deployment

**IMPORTANT:** These migrations have been run in development but NOT in production.

**⚠️  CRITICAL:** Production has real doctors with accounts. Extra care required!

### Safe Migration Procedure (Step-by-Step):

#### Step 1: Pre-Migration Verification
```bash
# Run verification script BEFORE migration
python migrations/verify_migration.py pre

# This will:
# - Count all doctors and their data
# - Identify signed-up doctors (those with user accounts)
# - Save stats to migration_stats.txt for comparison
```

#### Step 2: Create Backup
```bash
# Create timestamped backup
cp instance/doctors.db instance/doctors.db.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup was created
ls -lh instance/doctors.db*
```

#### Step 3: Test Migration on Backup First (Recommended)
```bash
# Copy production database to test location
cp instance/doctors.db instance/doctors_test.db

# Run migration on TEST database
sqlite3 instance/doctors_test.db < migrations/001_create_normalized_tables.sql
sqlite3 instance/doctors_test.db < migrations/002_copy_data_to_normalized_tables.sql

# Verify test migration
python migrations/verify_migration.py post instance/doctors_test.db

# If verification passes, proceed to Step 4
# If verification fails, DO NOT run on production!
```

#### Step 4: Run Production Migration
```bash
# Only run this if Step 3 verification passed!
sqlite3 instance/doctors.db < migrations/001_create_normalized_tables.sql
sqlite3 instance/doctors.db < migrations/002_copy_data_to_normalized_tables.sql
```

#### Step 5: Post-Migration Verification
```bash
# Verify production migration
python migrations/verify_migration.py post

# This will:
# - Check all new tables were created
# - Verify row counts match pre-migration
# - Confirm signed-up doctors' data is intact
# - Report any data loss or mismatches
```

#### Step 6: Manual Check of Signed-Up Doctors
```bash
# After migration, manually verify signed-up doctors can:
# 1. Log in successfully
# 2. See their profile data (photo, phone, etc.)
# 3. Access their dashboard without errors
```

### Rollback Procedure (If Needed)

If migration fails or verification shows errors:

```bash
# Stop the application
# Replace database with backup
cp instance/doctors.db.backup_YYYYMMDD_HHMMSS instance/doctors.db

# Restart application with old database
```

## Migration History

### 001_create_normalized_tables.sql
- Creates 6 new tables for normalized doctor data:
  - `doctor_contact` - Phone, address, location
  - `doctor_subscription` - Billing, tier, profile views
  - `doctor_credentials` - NMC number, external URLs
  - `doctor_settings` - Photo, working hours
  - `doctor_medical_tools` - Medical certificate/prescription templates
  - `doctor_template_usage` - Usage analytics

### 002_copy_data_to_normalized_tables.sql
- Migrates existing data from `doctors` table to new normalized tables
- Maintains backward compatibility (old columns still exist)
- Zero data loss migration

## Development Note

- Local database was migrated on 2026-01-08
- All 24,070 doctors successfully migrated
- Backup: `instance/doctors.db.backup_20260108_133346`
