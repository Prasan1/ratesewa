"""
Database migration script to add gamification features
Run this script to add gamification tables and initialize badges
"""
from app import app, db
from models import User, BadgeDefinition, UserBadge, ReviewHelpful
from gamification import initialize_badges
from sqlalchemy import text


def run_migration():
    """Run the gamification migration"""
    with app.app_context():
        print("🚀 Starting gamification migration...")

        # Create all new tables
        print("\n📊 Creating new tables...")
        db.create_all()
        print("✅ Tables created successfully")

        # Add points column to users table if it doesn't exist
        print("\n➕ Adding points column to users table...")
        try:
            with db.engine.connect() as conn:
                # Check if column exists
                result = conn.execute(text("""
                    SELECT COUNT(*)
                    FROM pragma_table_info('users')
                    WHERE name='points'
                """))
                exists = result.scalar() > 0

                if not exists:
                    conn.execute(text("ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✅ Points column added to users table")
                else:
                    print("ℹ️  Points column already exists")
        except Exception as e:
            print(f"⚠️  Error adding points column: {e}")
            print("   (This is OK if the column already exists)")

        # Initialize badge definitions
        print("\n🏆 Initializing badge definitions...")
        initialize_badges()

        # Update existing users to have 0 points if NULL
        print("\n🔄 Updating existing users...")
        try:
            users = User.query.filter(User.points == None).all()
            for user in users:
                user.points = 0
            db.session.commit()
            print(f"✅ Updated {len(users)} users with default points")
        except Exception as e:
            print(f"⚠️  Error updating users: {e}")

        print("\n✨ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Test the gamification features")
        print("3. Check /leaderboard to see the leaderboard")
        print("4. Check /profile to see user badges and points")


if __name__ == '__main__':
    run_migration()
