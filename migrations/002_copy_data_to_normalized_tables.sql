-- Migration: Copy Data from doctors table to normalized tables
-- Date: 2026-01-08
-- Safe: This script ONLY copies data, does NOT delete or modify source data
-- Run AFTER: 001_create_normalized_tables.sql

-- ============================================================================
-- IMPORTANT: This is a COPY operation, NOT a move
-- The original doctors table remains completely unchanged
-- ============================================================================

-- ============================================================================
-- 1. COPY CONTACT & LOCATION DATA
-- ============================================================================
INSERT INTO doctor_contact (doctor_id, phone_number, practice_address, workplace, latitude, longitude, created_at, updated_at)
SELECT
    id,
    phone_number,
    practice_address,
    workplace,
    latitude,
    longitude,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM doctors
WHERE id NOT IN (SELECT doctor_id FROM doctor_contact);

-- ============================================================================
-- 2. COPY SUBSCRIPTION & BILLING DATA
-- ============================================================================
INSERT INTO doctor_subscription (doctor_id, subscription_tier, subscription_expires_at, trial_ends_at, stripe_customer_id, profile_views, created_at, updated_at)
SELECT
    id,
    COALESCE(subscription_tier, 'free'),
    subscription_expires_at,
    trial_ends_at,
    stripe_customer_id,
    COALESCE(profile_views, 0),
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM doctors
WHERE id NOT IN (SELECT doctor_id FROM doctor_subscription);

-- ============================================================================
-- 3. COPY CREDENTIALS DATA
-- ============================================================================
INSERT INTO doctor_credentials (doctor_id, nmc_number, external_clinic_url, created_at, updated_at)
SELECT
    id,
    nmc_number,
    external_clinic_url,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM doctors
WHERE id NOT IN (SELECT doctor_id FROM doctor_credentials);

-- ============================================================================
-- 4. COPY SETTINGS & PREFERENCES
-- ============================================================================
INSERT INTO doctor_settings (doctor_id, photo_url, working_hours, clinic_id, created_at, updated_at)
SELECT
    id,
    photo_url,
    working_hours,
    clinic_id,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM doctors
WHERE id NOT IN (SELECT doctor_id FROM doctor_settings);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these after migration to verify success:

-- Check row counts match:
-- SELECT 'doctors' as table_name, COUNT(*) as count FROM doctors
-- UNION ALL
-- SELECT 'doctor_contact', COUNT(*) FROM doctor_contact
-- UNION ALL
-- SELECT 'doctor_subscription', COUNT(*) FROM doctor_subscription
-- UNION ALL
-- SELECT 'doctor_credentials', COUNT(*) FROM doctor_credentials
-- UNION ALL
-- SELECT 'doctor_settings', COUNT(*) FROM doctor_settings;

-- Sample comparison (pick a random doctor):
-- SELECT d.id, d.name, d.phone_number as old_phone, dc.phone_number as new_phone
-- FROM doctors d
-- LEFT JOIN doctor_contact dc ON d.id = dc.doctor_id
-- LIMIT 5;

-- Verify no data loss:
-- SELECT COUNT(*) as doctors_with_phone FROM doctors WHERE phone_number IS NOT NULL;
-- SELECT COUNT(*) as contact_with_phone FROM doctor_contact WHERE phone_number IS NOT NULL;
-- (These two numbers should match)
