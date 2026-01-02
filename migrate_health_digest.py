"""
Database migration script to add Health Digest feature
Run this script to add article tables and initialize categories
"""
from app import app, db
from models import ArticleCategory, Article
from sqlalchemy import text


def run_migration():
    """Run the health digest migration"""
    with app.app_context():
        print("🚀 Starting Health Digest migration...")

        # Create all new tables
        print("\n📊 Creating article tables...")
        db.create_all()
        print("✅ Tables created successfully")

        # Initialize article categories
        print("\n📑 Initializing article categories...")
        initialize_categories()

        print("\n✨ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Visit /admin/articles to create your first article")
        print("3. Visit /health-digest to see the article listing")


def initialize_categories():
    """Initialize default article categories"""
    categories = [
        {
            'name': 'Heart Health',
            'slug': 'heart-health',
            'description': 'Articles about cardiovascular health, cholesterol, and heart disease prevention',
            'icon': 'fa-heart',
            'display_order': 1
        },
        {
            'name': 'Diabetes',
            'slug': 'diabetes',
            'description': 'Information about diabetes management, blood sugar control, and prevention',
            'icon': 'fa-heartbeat',
            'display_order': 2
        },
        {
            'name': 'Blood Pressure',
            'slug': 'blood-pressure',
            'description': 'Hypertension management, blood pressure control, and cardiovascular health',
            'icon': 'fa-tint',
            'display_order': 3
        },
        {
            'name': 'Nutrition & Diet',
            'slug': 'nutrition-diet',
            'description': 'Healthy eating, nutrition tips, and diet plans',
            'icon': 'fa-apple-alt',
            'display_order': 4
        },
        {
            'name': 'Mental Health',
            'slug': 'mental-health',
            'description': 'Mental wellness, stress management, and psychological health',
            'icon': 'fa-brain',
            'display_order': 5
        },
        {
            'name': 'Womens Health',
            'slug': 'womens-health',
            'description': 'Health topics specific to women including pregnancy, menopause, and reproductive health',
            'icon': 'fa-female',
            'display_order': 6
        },
        {
            'name': 'Child Health',
            'slug': 'child-health',
            'description': 'Pediatric health, child development, and parenting tips',
            'icon': 'fa-baby',
            'display_order': 7
        },
        {
            'name': 'Preventive Care',
            'slug': 'preventive-care',
            'description': 'Disease prevention, vaccinations, and healthy lifestyle tips',
            'icon': 'fa-shield-alt',
            'display_order': 8
        },
    ]

    for cat_data in categories:
        # Check if category already exists
        existing = ArticleCategory.query.filter_by(slug=cat_data['slug']).first()
        if not existing:
            category = ArticleCategory(**cat_data)
            db.session.add(category)

    try:
        db.session.commit()
        print(f"✅ Initialized {len(categories)} article categories")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error initializing categories: {e}")


if __name__ == '__main__':
    run_migration()
