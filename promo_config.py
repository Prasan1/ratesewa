"""
Promotional campaign configuration
Manages time-limited promotions and free tier upgrades
"""
from datetime import datetime, timedelta

# Launch Promotion (ends April 25, 2026)
CURRENT_PROMOTION = {
    'enabled': True,
    'name': 'Launch Special 2026',
    'description': 'All featured features FREE until April 25, 2026!',
    'start_date': datetime(2026, 1, 1),
    'end_date': datetime(2026, 4, 25),
    'auto_upgrade_to': 'featured',  # Auto-grant this tier to all doctors
    'show_pricing': True,  # Still show pricing to build anticipation
    'banner_message': '🎉 Launch Special: All Featured Features FREE until Apr 25, 2026!',
    'banner_color': '#10b981',  # Green
}

# Payment system control
PAYMENT_SYSTEM = {
    'enabled': False,  # Set to True when ready to charge
    'test_mode': True,  # Stripe test mode
    'launch_date': None,  # When payments will start
}


def is_promotion_active():
    """Check if current promotion is active"""
    if not CURRENT_PROMOTION['enabled']:
        return False

    now = datetime.utcnow()
    start = CURRENT_PROMOTION['start_date']
    end = CURRENT_PROMOTION['end_date']

    return start <= now <= end


def get_promotional_tier():
    """Get the tier to auto-grant during promotion"""
    if is_promotion_active():
        return CURRENT_PROMOTION['auto_upgrade_to']
    return None


def should_charge_payment():
    """Determine if we should actually process payments"""
    return PAYMENT_SYSTEM['enabled'] and not is_promotion_active()


def get_promotion_banner():
    """Get promotional banner message if active"""
    if is_promotion_active():
        days_left = (CURRENT_PROMOTION['end_date'] - datetime.utcnow()).days
        return {
            'message': CURRENT_PROMOTION['banner_message'],
            'days_left': days_left,
            'color': CURRENT_PROMOTION['banner_color']
        }
    return None
