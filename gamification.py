"""
Gamification system for RankSewa
Handles badge awards and point calculations
"""
from models import db, User, UserBadge, BadgeDefinition, Rating, ReviewHelpful
from sqlalchemy.exc import IntegrityError


# Point values for different actions
POINTS = {
    'review': 10,
    'detailed_review': 5,  # Bonus for 100+ words
    'helpful_vote': 2,  # When your review gets marked helpful
    'doctor_response': 3,  # When doctor responds to your review
    'first_review_bonus': 5,  # Bonus for being first to review a doctor
}


def award_points(user, points, db_commit=True):
    """
    Award points to a user

    Args:
        user: User object
        points: Number of points to award
        db_commit: Whether to commit the transaction (default True)
    """
    if points <= 0:
        return

    user.points += points

    if db_commit:
        db.session.commit()


def award_badge(user, badge_slug, db_commit=True):
    """
    Award a badge to a user

    Args:
        user: User object
        badge_slug: Slug of the badge to award (e.g., 'first_review')
        db_commit: Whether to commit the transaction (default True)

    Returns:
        UserBadge object if awarded, None if already has badge or badge doesn't exist
    """
    # Get badge definition
    badge = BadgeDefinition.query.filter_by(slug=badge_slug, is_active=True).first()
    if not badge:
        return None

    # Check if user already has this badge
    existing = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
    if existing:
        return None

    # Award the badge
    user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
    db.session.add(user_badge)

    if db_commit:
        try:
            db.session.commit()
            return user_badge
        except IntegrityError:
            db.session.rollback()
            return None

    return user_badge


def check_and_award_badges(user, db_commit=True):
    """
    Check user's stats and award any badges they've earned

    Args:
        user: User object
        db_commit: Whether to commit the transaction (default True)

    Returns:
        List of newly awarded badges
    """
    newly_awarded = []

    # Get user stats
    review_count = user.review_count
    helpful_count = user.helpful_count

    # Count specialties and cities reviewed
    specialties = set()
    cities = set()
    for rating in user.ratings:
        if rating.doctor.specialty_id:
            specialties.add(rating.doctor.specialty_id)
        if rating.doctor.city_id:
            cities.add(rating.doctor.city_id)

    # Check for "First Review" badge
    if review_count >= 1:
        badge = award_badge(user, 'first_review', db_commit=False)
        if badge:
            newly_awarded.append(badge)

    # Check for "Helpful Reviewer" badge
    if helpful_count >= 5:
        badge = award_badge(user, 'helpful_reviewer', db_commit=False)
        if badge:
            newly_awarded.append(badge)

    # Check for "Detailed Reviewer" badge
    # (At least one review with 100+ words)
    has_detailed = any(len(r.comment or '') >= 100 for r in user.ratings)
    if has_detailed:
        badge = award_badge(user, 'detailed_reviewer', db_commit=False)
        if badge:
            newly_awarded.append(badge)

    # Check for "Community Champion" badges (5, 10, 25 reviews)
    if review_count >= 25:
        badge = award_badge(user, 'champion_25', db_commit=False)
        if badge:
            newly_awarded.append(badge)
    elif review_count >= 10:
        badge = award_badge(user, 'champion_10', db_commit=False)
        if badge:
            newly_awarded.append(badge)
    elif review_count >= 5:
        badge = award_badge(user, 'champion_5', db_commit=False)
        if badge:
            newly_awarded.append(badge)

    # Check for "Specialty Explorer" badge (3+ specialties)
    if len(specialties) >= 3:
        badge = award_badge(user, 'specialty_explorer', db_commit=False)
        if badge:
            newly_awarded.append(badge)

    # Check for "City Guide" badge (3+ cities)
    if len(cities) >= 3:
        badge = award_badge(user, 'city_guide', db_commit=False)
        if badge:
            newly_awarded.append(badge)

    if db_commit and newly_awarded:
        db.session.commit()

    return newly_awarded


def process_new_review(user, rating, is_first_for_doctor=False):
    """
    Process a new review submission and award points/badges

    Args:
        user: User who wrote the review
        rating: Rating object
        is_first_for_doctor: Whether this is the first review for this doctor

    Returns:
        dict with points awarded and badges earned
    """
    total_points = 0

    # Base points for writing a review
    total_points += POINTS['review']

    # Bonus for detailed review (100+ words)
    if rating.comment and len(rating.comment) >= 100:
        total_points += POINTS['detailed_review']

    # Bonus for first review on this doctor
    if is_first_for_doctor:
        total_points += POINTS['first_review_bonus']

    # Award points
    award_points(user, total_points, db_commit=False)

    # Check and award badges
    badges_earned = check_and_award_badges(user, db_commit=False)

    # Commit all changes together
    db.session.commit()

    return {
        'points': total_points,
        'badges': badges_earned,
        'new_tier': user.tier
    }


def process_helpful_vote(review_author, rating):
    """
    Process when someone marks a review as helpful
    Award points to the review author

    Args:
        review_author: User who wrote the review
        rating: Rating that was marked helpful

    Returns:
        dict with points awarded and badges earned
    """
    # Award points to review author
    award_points(review_author, POINTS['helpful_vote'], db_commit=False)

    # Check if this unlocks any badges
    badges_earned = check_and_award_badges(review_author, db_commit=False)

    # Commit changes
    db.session.commit()

    return {
        'points': POINTS['helpful_vote'],
        'badges': badges_earned,
        'new_tier': review_author.tier
    }


def process_doctor_response(review_author):
    """
    Process when a doctor responds to a user's review
    Award points to the review author

    Args:
        review_author: User who wrote the review

    Returns:
        dict with points awarded
    """
    # Award points
    award_points(review_author, POINTS['doctor_response'], db_commit=True)

    return {
        'points': POINTS['doctor_response'],
        'new_tier': review_author.tier
    }


def initialize_badges():
    """
    Initialize the badge definitions in the database
    This should be run once during setup or migration
    """
    badges = [
        {
            'name': 'First Review',
            'slug': 'first_review',
            'description': 'Write your first review',
            'icon': '⭐',
            'tier': 'bronze',
            'display_order': 1
        },
        {
            'name': 'Helpful Reviewer',
            'slug': 'helpful_reviewer',
            'description': 'Get 5 helpful votes on your reviews',
            'icon': '👍',
            'tier': 'silver',
            'display_order': 2
        },
        {
            'name': 'Detailed Reviewer',
            'slug': 'detailed_reviewer',
            'description': 'Write a comprehensive review (100+ words)',
            'icon': '📝',
            'tier': 'bronze',
            'display_order': 3
        },
        {
            'name': 'Community Champion - 5',
            'slug': 'champion_5',
            'description': 'Write 5 reviews',
            'icon': '🏆',
            'tier': 'silver',
            'display_order': 4
        },
        {
            'name': 'Community Champion - 10',
            'slug': 'champion_10',
            'description': 'Write 10 reviews',
            'icon': '🏆',
            'tier': 'gold',
            'display_order': 5
        },
        {
            'name': 'Community Champion - 25',
            'slug': 'champion_25',
            'description': 'Write 25 reviews',
            'icon': '🏆',
            'tier': 'platinum',
            'display_order': 6
        },
        {
            'name': 'Specialty Explorer',
            'slug': 'specialty_explorer',
            'description': 'Review doctors in 3+ different specialties',
            'icon': '🔍',
            'tier': 'gold',
            'display_order': 7
        },
        {
            'name': 'City Guide',
            'slug': 'city_guide',
            'description': 'Review doctors in 3+ different cities',
            'icon': '🗺️',
            'tier': 'gold',
            'display_order': 8
        },
    ]

    for badge_data in badges:
        # Check if badge already exists
        existing = BadgeDefinition.query.filter_by(slug=badge_data['slug']).first()
        if not existing:
            badge = BadgeDefinition(**badge_data)
            db.session.add(badge)

    try:
        db.session.commit()
        print(f"✅ Initialized {len(badges)} badge definitions")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error initializing badges: {e}")
