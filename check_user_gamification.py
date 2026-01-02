"""
Check a user's gamification status and award retroactive points/badges
Run on DO Console: python check_user_gamification.py
"""
from app import app, db
from models import User, UserBadge, BadgeDefinition, Rating
from gamification import check_and_award_badges, award_points

def check_user(email):
    """Check gamification status for a specific user"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"❌ User not found: {email}")
            return

        print(f"\n👤 User: {user.name} ({user.email})")
        print(f"   Points: {user.points}")
        print(f"   Tier: {user.tier_name} ({user.tier})")
        print(f"   Reviews written: {user.review_count}")
        print(f"   Helpful votes received: {user.helpful_count}")

        # Check badges
        user_badges = UserBadge.query.filter_by(user_id=user.id).all()
        print(f"\n🏆 Badges earned: {len(user_badges)}")
        for ub in user_badges:
            print(f"   - {ub.badge_definition.icon} {ub.badge_definition.name}")

        if not user_badges:
            print("   (No badges yet)")

        # Check available badges
        all_badges = BadgeDefinition.query.filter_by(is_active=True).all()
        print(f"\n📋 Total badges available: {len(all_badges)}")

        # Check if user should have badges
        print(f"\n🔍 Checking if user qualifies for badges...")
        newly_awarded = check_and_award_badges(user, db_commit=True)

        if newly_awarded:
            print(f"✅ Awarded {len(newly_awarded)} new badges:")
            for badge in newly_awarded:
                print(f"   - {badge.badge_definition.icon} {badge.badge_definition.name}")
        else:
            print("ℹ️  No new badges to award (already has all qualifying badges)")

        # Check reviews
        print(f"\n📝 User's reviews:")
        ratings = Rating.query.filter_by(user_id=user.id).all()
        for i, rating in enumerate(ratings, 1):
            print(f"   {i}. Doctor: {rating.doctor.name} (Active: {rating.doctor.is_active})")
            print(f"      Rating: {rating.rating}/5, Comment length: {len(rating.comment or '')} words")
            print(f"      Helpful votes: {rating.helpful_count}")


def award_retroactive_points():
    """Award points to users who wrote reviews before gamification was added"""
    with app.app_context():
        print("\n🔄 Checking for users who need retroactive points...\n")

        # Find users with reviews but 0 points
        users = User.query.filter(User.points == 0).all()

        updated_count = 0
        for user in users:
            if user.review_count > 0:
                # Calculate retroactive points
                points = 0
                for rating in user.ratings:
                    # Base points for review
                    points += 10
                    # Bonus for detailed review
                    if rating.comment and len(rating.comment) >= 100:
                        points += 5
                    # Bonus for helpful votes
                    points += rating.helpful_count * 2

                # Award points
                user.points = points
                updated_count += 1
                print(f"✅ {user.name}: {user.review_count} reviews → {points} points")

                # Check and award badges
                check_and_award_badges(user, db_commit=False)

        if updated_count > 0:
            db.session.commit()
            print(f"\n🎉 Updated {updated_count} users with retroactive points!")
        else:
            print("\nℹ️  No users need retroactive points")


if __name__ == '__main__':
    import sys

    # Check if email provided
    if len(sys.argv) > 1:
        email = sys.argv[1]
        check_user(email)
    else:
        # Award retroactive points to all users
        print("🚀 Running retroactive points award for all users...")
        award_retroactive_points()
        print("\n✅ Done! Run with email to check specific user: python check_user_gamification.py user@example.com")
