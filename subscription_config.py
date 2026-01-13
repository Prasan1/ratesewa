"""
Subscription pricing and tier configuration
Centralizes all subscription-related constants and pricing logic

NEW 3-TIER MODEL:
- User: Free (browse, review, book, health tracker)
- Doctor: Free but NMC verification required (profile, reviews, stats, verified badge)
- Clinic: NPR 4,999/month (Availability & Flow Engine)
"""

# User tier (patients/public users)
USER_TIER = {
    'name': 'User',
    'price_npr': 0,
    'price_usd': 0,
    'features': [
        'Search and browse doctors',
        'Read and write reviews',
        'Book appointments at clinics',
        'Appointment history & reminders',
        'Save favorite doctors'
    ],
    'privacy_note': 'We collect only what\'s needed for bookings and reviews. We do not sell personal data.'
}

# Doctor tier (verified medical professionals)
DOCTOR_TIER = {
    'name': 'Doctor',
    'price_npr': 0,
    'price_usd': 0,
    'requirements': [
        'Valid NMC registration number',
        'Government-issued ID',
        'NMC certificate document'
    ],
    'features': [
        'Verified badge on profile',
        'Edit and manage your profile',
        'Respond to patient reviews',
        'Profile analytics dashboard',
        'SEO-optimized profile page',
        'Google search visibility',
        'Profile photo upload',
        'Join clinic affiliations'
    ],
    'notes': [
        'Verification required within 30 days',
        'Certificate expiry tracking',
        'Re-verification required on expiry'
    ]
}

# Clinic tier (hospitals, clinics, practices)
CLINIC_TIER = {
    'name': 'Clinic',
    'price_npr': 4999,
    'price_usd': 37,
    'stripe_price_id': 'price_clinic_monthly',
    'features': [
        'Availability & Flow Engine access',
        'Add verified doctors',
        'Online appointment booking',
        'Patient queue management',
        'Doctor schedule management',
        'Unavailability/leave management',
        'Daily appointment tracking',
        'Public clinic page'
    ],
    'highlight': 'For Clinics & Hospitals'
}

# Legacy subscription tiers (for backward compatibility during transition)
# These will be deprecated after April 25, 2026
SUBSCRIPTION_TIERS = {
    'free': {
        'name': 'Free',
        'price_usd': 0,
        'price_npr': 0,
        'stripe_price_id': None,
        'features': [
            'Profile listing (unverified)',
            'Receive patient reviews',
            'Basic visibility'
        ],
        'locked_features': [
            'Verified badge (requires NMC verification)',
            'Profile editing',
            'Analytics dashboard',
            'Respond to reviews'
        ]
    },
    'verified': {
        'name': 'Verified Doctor',
        'price_usd': 0,
        'price_npr': 0,
        'stripe_price_id': None,
        'features': [
            'Verified badge',
            'Edit profile details',
            'Respond to reviews',
            'Analytics dashboard',
            'Profile photo upload',
            'Google search visibility',
            'Join clinic affiliations'
        ],
        'requirements': [
            'Valid NMC registration',
            'Government ID verification'
        ]
    }
}

# Stripe configuration
STRIPE_CONFIG = {
    'currency': 'usd',
    'payment_method_types': ['card'],
    'success_url_path': '/subscription/success',
    'cancel_url_path': '/subscription/cancel',
}

# Trial configuration (for future use)
TRIAL_CONFIG = {
    'enabled': False,
    'duration_days': 30,
    'tier': 'clinic'
}

# Feature flags for doctor profiles
# NOTE: Rankings are based ONLY on reviews and verified status - NOT subscription tier
# We do not sell visibility or ranking positions
DOCTOR_FEATURES = {
    'unverified': {
        'can_view_analytics': False,
        'can_show_contact': False,
        'can_upload_photos': False,
        'can_edit_profile': False,
        'can_respond_reviews': False,
        'is_verified': False,
        'max_photos': 0
    },
    'verified': {
        'can_view_analytics': True,
        'can_show_contact': True,
        'can_upload_photos': True,
        'can_edit_profile': True,
        'can_respond_reviews': True,
        'is_verified': True,
        'max_photos': 1
    }
}

# Legacy tier features (for backward compatibility)
TIER_FEATURES = {
    'free': {
        'can_view_analytics': False,
        'can_show_contact': False,
        'can_upload_photos': False,
        'can_show_hours': False,
        'is_featured': False,
        'max_photos': 0
    },
    'premium': {
        'can_view_analytics': True,
        'can_show_contact': True,
        'can_upload_photos': True,
        'can_show_hours': True,
        'is_featured': False,
        'max_photos': 1
    },
    'featured': {
        'can_view_analytics': True,
        'can_show_contact': True,
        'can_upload_photos': True,
        'can_show_hours': True,
        'is_featured': False,  # Featured badge removed
        'max_photos': 1
    },
    'verified': {
        'can_view_analytics': True,
        'can_show_contact': True,
        'can_upload_photos': True,
        'can_show_hours': True,
        'is_featured': False,
        'max_photos': 1
    }
}


def get_user_tier_info():
    """Get user tier information"""
    return USER_TIER


def get_doctor_tier_info():
    """Get doctor tier information"""
    return DOCTOR_TIER


def get_clinic_tier_info():
    """Get clinic tier information"""
    return CLINIC_TIER


def get_tier_info(tier_name):
    """Get subscription tier information (legacy support)"""
    return SUBSCRIPTION_TIERS.get(tier_name, SUBSCRIPTION_TIERS['free'])


def can_access_feature(tier_name, feature_name):
    """Check if a subscription tier has access to a feature"""
    tier_features = TIER_FEATURES.get(tier_name, TIER_FEATURES['free'])
    return tier_features.get(feature_name, False)


def is_doctor_verified(doctor):
    """Check if a doctor is verified"""
    if not doctor:
        return False
    return doctor.is_verified if hasattr(doctor, 'is_verified') else False


def get_doctor_features(doctor):
    """Get feature access for a doctor based on verification status"""
    if is_doctor_verified(doctor):
        return DOCTOR_FEATURES['verified']
    return DOCTOR_FEATURES['unverified']


def calculate_price_npr(price_usd, exchange_rate=135):
    """Convert USD price to NPR (default rate: 135 NPR/USD)"""
    return int(price_usd * exchange_rate)
