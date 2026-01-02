"""
Subscription pricing and tier configuration
Centralizes all subscription-related constants and pricing logic
"""

# Subscription tiers
SUBSCRIPTION_TIERS = {
    'free': {
        'name': 'Free',
        'price_usd': 0,
        'price_npr': 0,
        'stripe_price_id': None,
        'features': [
            'Profile listing',
            'Verification badge',
            'Respond to reviews',
            'Basic profile editing',
            'Profile photo upload'  # Updated: Now included in Basic tier
        ],
        'locked_features': [
            'Analytics dashboard',
            'Contact info visible',
            'Photo gallery (multiple photos)',  # Updated: Multiple photos still Premium+
            'Appointment hours',
            'Priority placement',
            'Featured badge'
        ]
    },
    'premium': {
        'name': 'Premium',
        'price_usd': 15,  # ~NPR 1,999 at 135 NPR/USD
        'price_npr': 1999,
        'stripe_price_id': 'price_premium_monthly',  # Will be set from Stripe Dashboard
        'features': [
            'All Free features',
            'Analytics dashboard',
            'Contact info visible on profile',
            'Photo gallery (up to 5 photos)',
            'Display appointment hours',
            'Monthly performance reports',
            'Priority email support'
        ],
        'highlight': 'Most Popular'
    },
    'featured': {
        'name': 'Featured Premium',
        'price_usd': 22,  # ~NPR 2,999 at 135 NPR/USD
        'price_npr': 2999,
        'stripe_price_id': 'price_featured_monthly',  # Will be set from Stripe Dashboard
        'features': [
            'All Premium features',
            'Featured badge on profile',
            'Top of search results',
            '3x priority in listings',
            'Sponsored placement',
            'Unlimited photos',
            'Premium support (24h response)'
        ],
        'highlight': 'Best Value'
    }
}

# Clinic tiers (multi-doctor billing)
CLINIC_TIERS = {
    'clinic_starter': {
        'name': 'Clinic Starter',
        'price_npr': 4999,
        'price_usd': 37,
        'max_doctors': 3,
        'features': [
            'Manage up to 3 doctors',
            'Priority support (48h response)',
            'Featured placement boosts',
            'Enhanced analytics for managed profiles'
        ]
    },
    'clinic_growth': {
        'name': 'Clinic Growth',
        'price_npr': 9999,
        'price_usd': 74,
        'max_doctors': 8,
        'features': [
            'Manage up to 8 doctors',
            'Priority support (24h response)',
            'Featured placement boosts',
            'Enhanced analytics for managed profiles'
        ]
    },
    'clinic_pro': {
        'name': 'Clinic Pro',
        'price_npr': 14999,
        'price_usd': 111,
        'max_doctors': 15,
        'features': [
            'Manage up to 15 doctors',
            'Dedicated priority support',
            'Featured placement boosts',
            'Enhanced analytics for managed profiles'
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
    'enabled': False,  # Set to True when offering trials
    'duration_days': 30,
    'tier': 'premium'  # Which tier to trial
}

# Feature flags for each tier
TIER_FEATURES = {
    'free': {
        'can_view_analytics': False,
        'can_show_contact': False,
        'can_upload_photos': True,  # Updated: Now allowed in Basic tier
        'can_show_hours': False,
        'is_featured': False,
        'search_boost_multiplier': 1.0,
        'max_photos': 1  # Updated: Allow 1 profile photo in Basic tier
    },
    'premium': {
        'can_view_analytics': True,
        'can_show_contact': True,
        'can_upload_photos': True,
        'can_show_hours': True,
        'is_featured': False,
        'search_boost_multiplier': 1.5,
        'max_photos': 5
    },
    'featured': {
        'can_view_analytics': True,
        'can_show_contact': True,
        'can_upload_photos': True,
        'can_show_hours': True,
        'is_featured': True,
        'search_boost_multiplier': 3.0,
        'max_photos': 999  # Unlimited
    }
}


def get_tier_info(tier_name):
    """Get subscription tier information"""
    return SUBSCRIPTION_TIERS.get(tier_name, SUBSCRIPTION_TIERS['free'])


def can_access_feature(tier_name, feature_name):
    """Check if a subscription tier has access to a feature"""
    tier_features = TIER_FEATURES.get(tier_name, TIER_FEATURES['free'])
    return tier_features.get(feature_name, False)


def get_upgrade_options(current_tier):
    """Get available upgrade options for current tier"""
    tier_order = ['free', 'premium', 'featured']
    current_index = tier_order.index(current_tier) if current_tier in tier_order else 0

    return [
        {
            'tier': tier,
            'info': SUBSCRIPTION_TIERS[tier]
        }
        for tier in tier_order[current_index + 1:]
    ]


def calculate_price_npr(price_usd, exchange_rate=135):
    """Convert USD price to NPR (default rate: 135 NPR/USD)"""
    return int(price_usd * exchange_rate)


def get_clinic_tier_info(tier_name):
    """Get clinic tier information"""
    return CLINIC_TIERS.get(tier_name, CLINIC_TIERS['clinic_starter'])
