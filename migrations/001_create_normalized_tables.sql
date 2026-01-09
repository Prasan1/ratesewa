-- Migration: Create Normalized Tables for Doctor Data
-- Date: 2026-01-08
-- Safe: This script ONLY creates new tables, does NOT modify existing tables
-- Compatible with: SQLite (local) and PostgreSQL (production)

-- ============================================================================
-- 1. DOCTOR CONTACT & LOCATION
-- ============================================================================
CREATE TABLE IF NOT EXISTS doctor_contact (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    practice_address TEXT,
    workplace TEXT,
    latitude FLOAT,
    longitude FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_doctor_contact_doctor_id ON doctor_contact(doctor_id);

-- ============================================================================
-- 2. DOCTOR SUBSCRIPTION & BILLING
-- ============================================================================
CREATE TABLE IF NOT EXISTS doctor_subscription (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL UNIQUE,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_expires_at DATETIME,
    trial_ends_at DATETIME,
    stripe_customer_id VARCHAR(255),
    profile_views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_doctor_subscription_doctor_id ON doctor_subscription(doctor_id);
CREATE INDEX IF NOT EXISTS idx_doctor_subscription_tier ON doctor_subscription(subscription_tier);

-- ============================================================================
-- 3. DOCTOR CREDENTIALS
-- ============================================================================
CREATE TABLE IF NOT EXISTS doctor_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL UNIQUE,
    nmc_number VARCHAR(50),
    external_clinic_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_doctor_credentials_doctor_id ON doctor_credentials(doctor_id);
CREATE INDEX IF NOT EXISTS idx_doctor_credentials_nmc ON doctor_credentials(nmc_number);

-- ============================================================================
-- 4. DOCTOR SETTINGS & PREFERENCES
-- ============================================================================
CREATE TABLE IF NOT EXISTS doctor_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL UNIQUE,
    photo_url TEXT,
    working_hours TEXT,
    clinic_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_doctor_settings_doctor_id ON doctor_settings(doctor_id);

-- ============================================================================
-- 5. MEDICAL TOOLS (NEW FEATURE)
-- ============================================================================
CREATE TABLE IF NOT EXISTS doctor_medical_tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL UNIQUE,

    -- Signature & Branding
    signature_image TEXT,
    clinic_letterhead TEXT,

    -- Default Values
    default_clinic_name VARCHAR(255),
    default_clinic_address TEXT,
    default_consultation_fee INTEGER,

    -- Preferences (JSON)
    certificate_settings TEXT,
    prescription_settings TEXT,

    -- Access Control
    tools_enabled BOOLEAN DEFAULT 1,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_doctor_medical_tools_doctor_id ON doctor_medical_tools(doctor_id);

-- ============================================================================
-- 6. TEMPLATE USAGE TRACKING (Analytics)
-- ============================================================================
CREATE TABLE IF NOT EXISTS doctor_template_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    template_type VARCHAR(50),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    patient_name VARCHAR(100),

    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_template_usage_doctor_id ON doctor_template_usage(doctor_id);
CREATE INDEX IF NOT EXISTS idx_template_usage_type ON doctor_template_usage(template_type);
CREATE INDEX IF NOT EXISTS idx_template_usage_date ON doctor_template_usage(generated_at);

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Check that tables were created successfully
-- Run after migration:
-- SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'doctor_%';
