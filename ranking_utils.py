"""
Doctor Ranking Score Utilities

Calculates composite ranking scores for verified doctors based on:
- Reviews & Rating (50%) - Bayesian weighted rating
- Profile Completion (25%) - Percentage of filled profile fields
- Review Response Rate (15%) - % of reviews doctor has responded to
- Account Age Bonus (10%) - Small boost for established accounts, capped at 2 years
"""
from datetime import datetime


# Profile completion fields and their weights (total = 100)
PROFILE_FIELDS = {
    'photo_url': 20,        # Most visible - patients want to see who they're visiting
    'description': 20,      # Tells patients about the doctor
    'education': 15,        # Credentials (MBBS, MD, etc.)
    'college': 10,          # Where they studied
    'experience': 10,       # Years of experience
    'workplace': 10,        # Current workplace
    'phone_number': 10,     # Contact information
    'working_hours': 5,     # Schedule availability
}

# Ranking weights (Balanced distribution)
WEIGHT_RATING = 0.50
WEIGHT_PROFILE = 0.25
WEIGHT_RESPONSE = 0.15
WEIGHT_AGE = 0.10

# Account age cap (2 years = 730 days)
MAX_ACCOUNT_AGE_DAYS = 730


def calculate_profile_completion(doctor):
    """
    Calculate profile completion score for a doctor.

    Args:
        doctor: Doctor model instance

    Returns:
        float: Score between 0.0 and 1.0
    """
    score = 0
    for field, weight in PROFILE_FIELDS.items():
        value = getattr(doctor, field, None)
        # Check for truthy value (not None, not empty string)
        if value:
            score += weight
    return score / 100.0


def calculate_profile_completion_details(doctor):
    """
    Get detailed breakdown of profile completion.

    Args:
        doctor: Doctor model instance

    Returns:
        dict: {field: {'filled': bool, 'weight': int}, 'total': float}
    """
    details = {}
    total = 0
    for field, weight in PROFILE_FIELDS.items():
        value = getattr(doctor, field, None)
        filled = bool(value)
        details[field] = {'filled': filled, 'weight': weight}
        if filled:
            total += weight
    details['total_score'] = total / 100.0
    details['total_percent'] = total
    return details


def calculate_response_rate(total_reviews, total_responses):
    """
    Calculate review response rate.

    Args:
        total_reviews: Total number of reviews for the doctor
        total_responses: Total number of doctor responses

    Returns:
        float: Rate between 0.0 and 1.0
    """
    if total_reviews == 0:
        return 0.0
    return min(total_responses / total_reviews, 1.0)


def calculate_account_age_bonus(created_at):
    """
    Calculate account age bonus (capped at 2 years).

    Args:
        created_at: datetime when doctor account was created

    Returns:
        float: Bonus between 0.0 and 1.0
    """
    if not created_at:
        return 0.0

    days_old = (datetime.utcnow() - created_at).days
    # Cap at MAX_ACCOUNT_AGE_DAYS (2 years)
    return min(days_old / MAX_ACCOUNT_AGE_DAYS, 1.0)


def calculate_composite_score(rating_score, profile_completion, response_rate, account_age_bonus):
    """
    Calculate the final composite ranking score.

    Args:
        rating_score: Bayesian weighted rating (0.0 to 5.0, normalized to 0-1)
        profile_completion: Profile completion score (0.0 to 1.0)
        response_rate: Review response rate (0.0 to 1.0)
        account_age_bonus: Account age bonus (0.0 to 1.0)

    Returns:
        float: Composite score between 0.0 and 1.0
    """
    # Normalize rating score from 0-5 scale to 0-1
    normalized_rating = rating_score / 5.0 if rating_score else 0.0

    return (
        normalized_rating * WEIGHT_RATING +
        profile_completion * WEIGHT_PROFILE +
        response_rate * WEIGHT_RESPONSE +
        account_age_bonus * WEIGHT_AGE
    )


def get_ranking_breakdown(doctor, rating_score, total_reviews, total_responses):
    """
    Get a detailed breakdown of all ranking factors for a doctor.
    Useful for displaying on doctor dashboard.

    Args:
        doctor: Doctor model instance
        rating_score: Bayesian weighted rating
        total_reviews: Total number of reviews
        total_responses: Total number of responses

    Returns:
        dict: Breakdown of all ranking factors and final score
    """
    profile_completion = calculate_profile_completion(doctor)
    response_rate = calculate_response_rate(total_reviews, total_responses)
    account_age_bonus = calculate_account_age_bonus(doctor.created_at)

    composite = calculate_composite_score(
        rating_score, profile_completion, response_rate, account_age_bonus
    )

    return {
        'rating': {
            'score': rating_score,
            'normalized': rating_score / 5.0 if rating_score else 0.0,
            'weight': WEIGHT_RATING,
            'contribution': (rating_score / 5.0 if rating_score else 0.0) * WEIGHT_RATING
        },
        'profile_completion': {
            'score': profile_completion,
            'percent': int(profile_completion * 100),
            'weight': WEIGHT_PROFILE,
            'contribution': profile_completion * WEIGHT_PROFILE
        },
        'response_rate': {
            'score': response_rate,
            'percent': int(response_rate * 100),
            'reviews': total_reviews,
            'responses': total_responses,
            'weight': WEIGHT_RESPONSE,
            'contribution': response_rate * WEIGHT_RESPONSE
        },
        'account_age': {
            'score': account_age_bonus,
            'days': (datetime.utcnow() - doctor.created_at).days if doctor.created_at else 0,
            'weight': WEIGHT_AGE,
            'contribution': account_age_bonus * WEIGHT_AGE
        },
        'composite_score': composite,
        'composite_percent': int(composite * 100)
    }
