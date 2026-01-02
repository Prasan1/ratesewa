"""
Script to retroactively award points and badges to existing reviewers
Run this once after the migration to give credit to early adopters
"""
from app import app, db
from models import User, Rating
from gamification import process_new_review, check_and_award_badges, award_points


def award_retroactive_points():
    """Award points to users who reviewed before gamification was added"""
    with app.app_context():
        print("🔄 Awarding retroactive points to existing reviewers...")

        # Get all users who have written reviews
        users_with_reviews = User.query.join(Rating).distinct().all()

        print(f"Found {len(users_with_reviews)} users with existing reviews\n")

        for user in users_with_reviews:
            print(f"Processing {user.name} ({user.email})...")

            total_points = 0

            # Award points for each review
            for rating in user.ratings:
                points = 10  # Base points

                # Bonus for detailed review
                if rating.comment and len(rating.comment) >= 100:
                    points += 5

                # Check if this was the first review for the doctor
                first_review = Rating.query.filter_by(doctor_id=rating.doctor_id)\
                    .order_by(Rating.created_at).first()
                if first_review.id == rating.id:
                    points += 5

                total_points += points

            # Award the points
            user.points = total_points
            print(f"  → Awarded {total_points} points")

            # Check and award badges
            badges_earned = check_and_award_badges(user, db_commit=False)
            if badges_earned:
                badge_names = [b.badge_definition.name for b in badges_earned]
                print(f"  → Badges unlocked: {', '.join(badge_names)}")

            db.session.commit()

        print("\n✨ Retroactive points awarded successfully!")
        print("\nSummary:")
        print(f"- Total users processed: {len(users_with_reviews)}")
        print(f"- Total points distributed: {sum(u.points for u in users_with_reviews)}")


if __name__ == '__main__':
    award_retroactive_points()
