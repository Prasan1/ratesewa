# Database Migrations

This directory contains SQL migration scripts for the doctor directory application.

## Production Deployment

**IMPORTANT:** These migrations have been run in development but NOT in production.

### Before deploying the latest code to production:

1. **Backup the production database:**
   ```bash
   cp instance/doctors.db instance/doctors.db.backup_$(date +%Y%m%d_%H%M%S)
   ```

2. **Run migrations in order:**
   ```bash
   sqlite3 instance/doctors.db < migrations/001_create_normalized_tables.sql
   sqlite3 instance/doctors.db < migrations/002_copy_data_to_normalized_tables.sql
   ```

3. **Verify migration success:**
   ```bash
   sqlite3 instance/doctors.db "SELECT COUNT(*) FROM doctor_contact;"
   sqlite3 instance/doctors.db "SELECT COUNT(*) FROM doctor_subscription;"
   ```
   Both should return the same count as the doctors table.

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
