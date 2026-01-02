"""
Database migration script for PostgreSQL - adds Health Digest features
Run this on Heroku: heroku run python migrate_health_digest_postgres.py
"""
from app import app, db
from models import ArticleCategory, Article
from sqlalchemy import text


def run_migration():
    """Run the health digest migration for PostgreSQL"""
    with app.app_context():
        print("🚀 Starting Health Digest migration (PostgreSQL)...")

        # Create all new tables
        print("\n📊 Creating new tables...")
        db.create_all()
        print("✅ Tables created successfully")

        # Initialize article categories
        print("\n📂 Initializing article categories...")
        categories = [
            {'name': 'Heart Health', 'slug': 'heart-health', 'icon': 'fa-heartbeat', 'description': 'Heart disease, blood pressure, and cardiovascular health', 'display_order': 1},
            {'name': 'Diabetes', 'slug': 'diabetes', 'icon': 'fa-syringe', 'description': 'Diabetes management, blood sugar, and insulin', 'display_order': 2},
            {'name': 'Blood Pressure', 'slug': 'blood-pressure', 'icon': 'fa-heart-pulse', 'description': 'Hypertension and blood pressure management', 'display_order': 3},
            {'name': 'Nutrition', 'slug': 'nutrition', 'icon': 'fa-apple-alt', 'description': 'Healthy eating, diet, and nutrition advice', 'display_order': 4},
            {'name': 'Women\'s Health', 'slug': 'womens-health', 'icon': 'fa-venus', 'description': 'Maternal health, pregnancy, and women-specific health topics', 'display_order': 5},
            {'name': 'Mental Health', 'slug': 'mental-health', 'icon': 'fa-brain', 'description': 'Depression, anxiety, stress, and mental wellbeing', 'display_order': 6},
            {'name': 'Child Health', 'slug': 'child-health', 'icon': 'fa-child', 'description': 'Pediatric health, child development, and parenting', 'display_order': 7},
            {'name': 'General Health', 'slug': 'general-health', 'icon': 'fa-notes-medical', 'description': 'General health tips, preventive care, and wellness', 'display_order': 8},
        ]

        created_count = 0
        for cat_data in categories:
            existing = ArticleCategory.query.filter_by(slug=cat_data['slug']).first()
            if not existing:
                category = ArticleCategory(**cat_data)
                db.session.add(category)
                created_count += 1
                print(f"  ✅ Created category: {cat_data['name']}")
            else:
                print(f"  ⏭️  Category already exists: {cat_data['name']}")

        if created_count > 0:
            db.session.commit()
            print(f"\n✅ Created {created_count} categories")
        else:
            print("\nℹ️  All categories already exist")

        print("\n✨ Migration completed successfully!")
        print("\nHealth Digest is now ready!")
        print("Next step: Run seed scripts to add articles")


if __name__ == '__main__':
    run_migration()
