"""
Database migration script for PostgreSQL - adds gamification features
Run this on Heroku: heroku run python migrate_gamification_postgres.py
"""
from app import app, db
from models import User, BadgeDefinition, UserBadge, ReviewHelpful
from gamification import initialize_badges
from sqlalchemy import text


def run_migration():
    """Run the gamification migration for PostgreSQL"""
    with app.app_context():
        print("🚀 Starting gamification migration (PostgreSQL)...")

        # Create all new tables
        print("\n📊 Creating new tables...")
        db.create_all()
        print("✅ Tables created successfully")

        # Add points column to users table if it doesn't exist (PostgreSQL syntax)
        print("\n➕ Adding points column to users table...")
        try:
            with db.engine.connect() as conn:
                # Check if column exists (PostgreSQL)
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='users' AND column_name='points'
                """))
                exists = result.fetchone() is not None

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
            with db.engine.connect() as conn:
                result = conn.execute(text("UPDATE users SET points = 0 WHERE points IS NULL"))
                conn.commit()
                print(f"✅ Updated users with default points")
        except Exception as e:
            print(f"⚠️  Error updating users: {e}")

        print("\n✨ Migration completed successfully!")
        print("\nGamification features are now active!")


if __name__ == '__main__':
    run_migration()
