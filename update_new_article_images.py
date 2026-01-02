"""
Update new article images to use downloaded local files
"""
from app import app, db
from models import Article

def update_images():
    """Update article featured images to local files"""
    with app.app_context():
        print("🖼️  Updating new article images to local files...")

        # Map of slugs to local image paths
        image_map = {
            'womens-health-nepal-challenges-care': '/static/img/womens-health.jpg',
            'nutrition-essentials-healthy-diet-nepal': '/static/img/nutrition.jpg',
            'understanding-mental-health-nepal': '/static/img/mental-health-understanding.jpg',
            'getting-mental-health-help-nepal': '/static/img/mental-health-help.jpg'
        }

        updated_count = 0
        for slug, image_path in image_map.items():
            article = Article.query.filter_by(slug=slug).first()
            if article:
                old_image = article.featured_image
                article.featured_image = image_path
                print(f"  ✅ Updated {slug}")
                print(f"     Old: {old_image}")
                print(f"     New: {image_path}")
                updated_count += 1
            else:
                print(f"  ⚠️  Article not found: {slug}")

        if updated_count > 0:
            db.session.commit()
            print(f"\n🎉 Successfully updated {updated_count} article images!")
        else:
            print("\n❌ No articles were updated")

if __name__ == '__main__':
    update_images()
