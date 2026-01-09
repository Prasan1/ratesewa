"""
Credibility scoring system for reviews
Based on community signals to identify authentic patient experiences
"""
from datetime import datetime, timedelta
from models import Rating, User
import re


# Scoring matrix based on community signals
CREDIBILITY_POINTS = {
    'verified_interaction': 30,      # Has appointment_id
    'account_history_3plus': 15,     # User has 3+ reviews
    'content_specificity': 10,       # Detailed review with specifics
    'account_age_6months': 10,       # Account older than 6 months
    'review_length_50plus': 5,       # Review longer than 50 characters

    # Negative signals
    'first_time_reviewer': -10,      # User's first review
    'unverified_interaction': -20,   # No appointment_id
    'new_account_24h': -15,          # Account created < 24 hours ago
    'duplicate_content': -50,        # Similar to existing reviews
}

# Thresholds for credibility tiers
CREDIBILITY_TIERS = {
    'verified_patient': 40,   # High credibility - show badge
    'trusted': 20,            # Good credibility
    'neutral': 0,             # Neutral
    'suspicious': -15,        # Flag for review
}


def calculate_credibility_score(review, user):
    """
    Calculate credibility score for a review

    Args:
        review: Rating object
        user: User object who wrote the review

    Returns:
        int: Credibility score (-100 to 100+)
    """
    score = 0
    signals = []

    # 1. Verified Interaction (+30)
    if review.appointment_id:
        score += CREDIBILITY_POINTS['verified_interaction']
        signals.append('verified_interaction')
    else:
        # Unverified Interaction (-20)
        score += CREDIBILITY_POINTS['unverified_interaction']
        signals.append('unverified_interaction')

    # 2. Account History (>3 reviews) (+15)
    review_count = Rating.query.filter_by(user_id=user.id).count()
    if review_count >= 3:
        score += CREDIBILITY_POINTS['account_history_3plus']
        signals.append('account_history_3plus')

    # 3. First-Time Reviewer (-10)
    if review_count == 1:
        score += CREDIBILITY_POINTS['first_time_reviewer']
        signals.append('first_time_reviewer')

    # 4. Account Age (>6 months) (+10)
    account_age = datetime.utcnow() - user.created_at
    if account_age > timedelta(days=180):  # 6 months
        score += CREDIBILITY_POINTS['account_age_6months']
        signals.append('account_age_6months')

    # 5. New Account (<24h) (-15)
    if account_age < timedelta(hours=24):
        score += CREDIBILITY_POINTS['new_account_24h']
        signals.append('new_account_24h')

    # 6. Review Length (>50 chars) (+5)
    if review.comment and len(review.comment.strip()) > 50:
        score += CREDIBILITY_POINTS['review_length_50plus']
        signals.append('review_length_50plus')

    # 7. Content Specificity (+10)
    # Check for specific medical terms, visit details, or personal experience markers
    if review.comment and has_specific_content(review.comment):
        score += CREDIBILITY_POINTS['content_specificity']
        signals.append('content_specificity')

    # 8. Duplicate Content (-50)
    if is_duplicate_content(review):
        score += CREDIBILITY_POINTS['duplicate_content']
        signals.append('duplicate_content')

    return score, signals


def has_specific_content(comment):
    """
    Check if review contains specific details that indicate first-hand experience

    Args:
        comment: Review text

    Returns:
        bool: True if content appears specific/detailed
    """
    if not comment:
        return False

    comment_lower = comment.lower()

    # Indicators of specific, detailed reviews
    specificity_indicators = [
        # Medical terms
        r'\b(diagnosis|treatment|medication|prescription|symptoms?|test|x-ray|scan|surgery)\b',
        # Time references
        r'\b(minutes?|hours?|days?|weeks?|months?|waited|appointment)\b',
        # Personal experience markers
        r'\b(i|my|me|felt|experienced|visited|went|saw|told)\b',
        # Specific details
        r'\b(staff|nurse|reception|clinic|office|waiting room|consultation)\b',
        # Numbers/measurements
        r'\d+\s*(minutes?|hours?|rupees?|days?)',
    ]

    # Count how many types of indicators are present
    indicator_count = 0
    for pattern in specificity_indicators:
        if re.search(pattern, comment_lower):
            indicator_count += 1

    # If 3+ different types of indicators, consider it specific
    return indicator_count >= 3


def is_duplicate_content(review):
    """
    Check if review content is very similar to existing reviews

    Args:
        review: Rating object

    Returns:
        bool: True if appears to be duplicate content
    """
    if not review.comment or len(review.comment.strip()) < 20:
        return False

    # Get other reviews for the same doctor
    other_reviews = Rating.query.filter(
        Rating.doctor_id == review.doctor_id,
        Rating.id != review.id,
        Rating.comment.isnot(None)
    ).limit(50).all()

    # Simple similarity check - normalize and compare
    review_normalized = normalize_text(review.comment)

    for other in other_reviews:
        other_normalized = normalize_text(other.comment)

        # If 80%+ of text is identical, flag as duplicate
        similarity = calculate_similarity(review_normalized, other_normalized)
        if similarity > 0.8:
            return True

    return False


def normalize_text(text):
    """Normalize text for comparison"""
    if not text:
        return ""
    # Remove extra whitespace, convert to lowercase
    return re.sub(r'\s+', ' ', text.lower().strip())


def calculate_similarity(text1, text2):
    """
    Calculate simple text similarity ratio

    Args:
        text1, text2: Normalized text strings

    Returns:
        float: Similarity ratio (0.0 to 1.0)
    """
    if not text1 or not text2:
        return 0.0

    # Simple character-based similarity
    # For production, consider using libraries like difflib or fuzzywuzzy
    words1 = set(text1.split())
    words2 = set(text2.split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union) if union else 0.0


def get_credibility_tier(score):
    """
    Get credibility tier based on score

    Args:
        score: Credibility score

    Returns:
        str: Tier name ('verified_patient', 'trusted', 'neutral', 'suspicious')
    """
    if score >= CREDIBILITY_TIERS['verified_patient']:
        return 'verified_patient'
    elif score >= CREDIBILITY_TIERS['trusted']:
        return 'trusted'
    elif score >= CREDIBILITY_TIERS['neutral']:
        return 'neutral'
    else:
        return 'suspicious'


def update_review_credibility(review_id):
    """
    Calculate and update credibility score for a specific review

    Args:
        review_id: ID of the review to update

    Returns:
        dict: Updated score and tier
    """
    from app import db

    review = Rating.query.get(review_id)
    if not review:
        return None

    score, signals = calculate_credibility_score(review, review.user)
    tier = get_credibility_tier(score)

    # Update the review
    review.credibility_score = score

    # Auto-flag suspicious reviews
    if tier == 'suspicious':
        review.is_suspected = True

    db.session.commit()

    return {
        'score': score,
        'tier': tier,
        'signals': signals
    }


def recalculate_all_credibility_scores():
    """
    Recalculate credibility scores for all existing reviews
    Useful for initial migration or periodic updates

    Returns:
        dict: Statistics about the update
    """
    from app import db, app

    with app.app_context():
        reviews = Rating.query.all()

        stats = {
            'total': len(reviews),
            'verified_patient': 0,
            'trusted': 0,
            'neutral': 0,
            'suspicious': 0,
        }

        for review in reviews:
            score, signals = calculate_credibility_score(review, review.user)
            tier = get_credibility_tier(score)

            review.credibility_score = score

            if tier == 'suspicious':
                review.is_suspected = True

            stats[tier] += 1

            # Commit every 100 reviews
            if stats['total'] > 0 and stats['total'] % 100 == 0:
                db.session.commit()

        db.session.commit()

        return stats
