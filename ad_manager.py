"""
Advertisement Manager
Handles ad selection, rotation, and tracking logic for the doctor directory app.
Implements a hybrid approach: database ads first, AdSense fallback.
"""

from models import db, Advertisement
from datetime import datetime
import random


def get_ad_for_position(position, specialty_id=None, city_id=None):
    """
    Get an advertisement for a specific position with targeting support.

    Priority waterfall:
    1. Targeted direct ads (matching specialty_id or city_id)
    2. General direct ads (no targeting)
    3. AdSense fallback
    4. None (no ad)

    Args:
        position (str): Ad position (e.g., 'homepage_sidebar', 'profile_top')
        specialty_id (int, optional): Target specialty ID for contextual ads
        city_id (int, optional): Target city ID for location-based ads

    Returns:
        Advertisement object or None
    """
    now = datetime.utcnow()

    # Try to get targeted ads first (specialty or city match)
    if specialty_id or city_id:
        targeted_query = Advertisement.query.filter(
            Advertisement.position == position,
            Advertisement.is_active == True
        ).filter(
            db.or_(
                db.and_(
                    Advertisement.start_date.is_(None) | (Advertisement.start_date <= now),
                    Advertisement.end_date.is_(None) | (Advertisement.end_date >= now)
                )
            )
        )

        # Filter by targeting
        if specialty_id and city_id:
            targeted_query = targeted_query.filter(
                db.or_(
                    Advertisement.target_specialty_id == specialty_id,
                    Advertisement.target_city_id == city_id
                )
            )
        elif specialty_id:
            targeted_query = targeted_query.filter(
                Advertisement.target_specialty_id == specialty_id
            )
        elif city_id:
            targeted_query = targeted_query.filter(
                Advertisement.target_city_id == city_id
            )

        targeted_ads = targeted_query.all()

        if targeted_ads:
            return _weighted_random_selection(targeted_ads)

    # Try general ads (no targeting)
    general_ads = Advertisement.query.filter(
        Advertisement.position == position,
        Advertisement.is_active == True,
        Advertisement.target_specialty_id.is_(None),
        Advertisement.target_city_id.is_(None)
    ).filter(
        db.or_(
            db.and_(
                Advertisement.start_date.is_(None) | (Advertisement.start_date <= now),
                Advertisement.end_date.is_(None) | (Advertisement.end_date >= now)
            )
        )
    ).all()

    if general_ads:
        return _weighted_random_selection(general_ads)

    # Return AdSense fallback
    return get_adsense_fallback(position)


def _weighted_random_selection(ads):
    """
    Select an ad using weighted random selection based on priority and weight.
    Higher priority and weight values increase selection probability.

    Args:
        ads (list): List of Advertisement objects

    Returns:
        Advertisement object
    """
    if not ads:
        return None

    # Calculate weights: priority * weight for each ad
    weighted_ads = [(ad, ad.priority * ad.weight) for ad in ads]
    total_weight = sum(weight for _, weight in weighted_ads)

    if total_weight == 0:
        # If all weights are 0, select randomly
        return random.choice(ads)

    # Weighted random selection
    rand = random.uniform(0, total_weight)
    cumulative = 0

    for ad, weight in weighted_ads:
        cumulative += weight
        if rand <= cumulative:
            return ad

    # Fallback (shouldn't reach here)
    return ads[0]


def get_adsense_fallback(position):
    """
    Returns a placeholder AdSense ad configuration for a position.
    In production, this would contain actual AdSense ad unit codes.

    Args:
        position (str): Ad position identifier

    Returns:
        dict with AdSense configuration or None
    """
    adsense_units = {
        'homepage_sidebar': {
            'type': 'adsense',
            'format': '300x250',
            'slot': 'ADSENSE_SLOT_ID_1',  # Replace with actual AdSense slot ID
            'client': 'ca-pub-XXXXXXXXXXXXXXXX'  # Replace with your AdSense publisher ID
        },
        'profile_top': {
            'type': 'adsense',
            'format': '728x90',
            'slot': 'ADSENSE_SLOT_ID_2',
            'client': 'ca-pub-XXXXXXXXXXXXXXXX'
        },
        'profile_inline': {
            'type': 'adsense',
            'format': '336x280',
            'slot': 'ADSENSE_SLOT_ID_3',
            'client': 'ca-pub-XXXXXXXXXXXXXXXX'
        },
        'footer_banner': {
            'type': 'adsense',
            'format': '970x250',
            'slot': 'ADSENSE_SLOT_ID_4',
            'client': 'ca-pub-XXXXXXXXXXXXXXXX'
        },
        'mobile_bottom': {
            'type': 'adsense',
            'format': '320x50',
            'slot': 'ADSENSE_SLOT_ID_5',
            'client': 'ca-pub-XXXXXXXXXXXXXXXX'
        }
    }

    # Return None for now (AdSense integration can be added later)
    # Uncomment the line below when you have AdSense configured:
    # return adsense_units.get(position)
    return None


def get_in_feed_ads(specialty_id=None, city_id=None, count=5):
    """
    Get multiple ads for in-feed native ad placements.
    Used to inject ads between doctor cards in search results.

    Args:
        specialty_id (int, optional): Target specialty ID
        city_id (int, optional): Target city ID
        count (int): Maximum number of ads to return

    Returns:
        list of Advertisement objects
    """
    now = datetime.utcnow()

    query = Advertisement.query.filter(
        Advertisement.position == 'in_feed',
        Advertisement.is_active == True
    ).filter(
        db.or_(
            db.and_(
                Advertisement.start_date.is_(None) | (Advertisement.start_date <= now),
                Advertisement.end_date.is_(None) | (Advertisement.end_date >= now)
            )
        )
    )

    # Prioritize targeted ads
    if specialty_id:
        query = query.filter(
            db.or_(
                Advertisement.target_specialty_id == specialty_id,
                Advertisement.target_specialty_id.is_(None)
            )
        )
    if city_id:
        query = query.filter(
            db.or_(
                Advertisement.target_city_id == city_id,
                Advertisement.target_city_id.is_(None)
            )
        )

    ads = query.order_by(Advertisement.priority.desc()).limit(count).all()
    return ads


def track_ad_impression(ad_id):
    """
    Track an ad impression by incrementing the impressions counter.

    Args:
        ad_id (int): Advertisement ID

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ad = Advertisement.query.get(ad_id)
        if ad:
            ad.impressions += 1
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking impression: {e}")
        return False


def track_ad_click(ad_id):
    """
    Track an ad click by incrementing the clicks counter.

    Args:
        ad_id (int): Advertisement ID

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ad = Advertisement.query.get(ad_id)
        if ad:
            ad.clicks += 1
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking click: {e}")
        return False


def get_ad_stats(ad_id):
    """
    Get performance statistics for an advertisement.

    Args:
        ad_id (int): Advertisement ID

    Returns:
        dict with stats (impressions, clicks, CTR) or None
    """
    ad = Advertisement.query.get(ad_id)
    if not ad:
        return None

    return {
        'id': ad.id,
        'name': ad.name,
        'impressions': ad.impressions,
        'clicks': ad.clicks,
        'ctr': ad.ctr,
        'position': ad.position,
        'is_active': ad.is_active
    }
