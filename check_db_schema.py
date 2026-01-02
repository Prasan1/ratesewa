"""
Check database schema to verify migrations ran successfully
Run this on DO Console: python check_db_schema.py
"""
from app import app, db
from sqlalchemy import text, inspect

def check_schema():
    """Check if all required tables and columns exist"""
    with app.app_context():
        print("🔍 Checking database schema...\n")

        inspector = inspect(db.engine)

        # Check if users.points column exists
        print("1️⃣ Checking users table...")
        users_columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"   Columns: {', '.join(users_columns)}")

        if 'points' in users_columns:
            print("   ✅ users.points column EXISTS")
        else:
            print("   ❌ users.points column MISSING")

        # Check gamification tables
        print("\n2️⃣ Checking gamification tables...")
        all_tables = inspector.get_table_names()

        gamification_tables = ['badge_definitions', 'user_badges', 'review_helpful']
        for table in gamification_tables:
            if table in all_tables:
                print(f"   ✅ {table} table EXISTS")
            else:
                print(f"   ❌ {table} table MISSING")

        # Check health digest tables
        print("\n3️⃣ Checking health digest tables...")
        digest_tables = ['article_categories', 'articles']
        for table in digest_tables:
            if table in all_tables:
                print(f"   ✅ {table} table EXISTS")
            else:
                print(f"   ❌ {table} table MISSING")

        # Check badge count
        if 'badge_definitions' in all_tables:
            print("\n4️⃣ Checking badge definitions...")
            result = db.session.execute(text("SELECT COUNT(*) FROM badge_definitions"))
            badge_count = result.scalar()
            print(f"   Badge definitions: {badge_count}")
            if badge_count == 0:
                print("   ⚠️  No badges found - run initialize_badges()")

        # Check category count
        if 'article_categories' in all_tables:
            print("\n5️⃣ Checking article categories...")
            result = db.session.execute(text("SELECT COUNT(*) FROM article_categories"))
            cat_count = result.scalar()
            print(f"   Article categories: {cat_count}")
            if cat_count == 0:
                print("   ⚠️  No categories found - migration may not have completed")

        # Check if there are any NULL points in users
        print("\n6️⃣ Checking user points...")
        if 'points' in users_columns:
            result = db.session.execute(text("SELECT COUNT(*) FROM users WHERE points IS NULL"))
            null_count = result.scalar()
            print(f"   Users with NULL points: {null_count}")
            if null_count > 0:
                print("   ⚠️  Some users have NULL points - run the UPDATE statement")

        print("\n✅ Schema check complete!")

if __name__ == '__main__':
    check_schema()
