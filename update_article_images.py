"""
Update article images to use local files instead of Unsplash
"""
from app import app, db
from models import Article

def update_images():
    """Update article featured images to local files"""
    with app.app_context():
        print("🖼️  Updating article images...")

        # Map of slugs to local image paths
        image_map = {
            'understanding-type-2-diabetes-nepal': '/static/img/type-2-diabates.jpg',
            'high-blood-pressure-nepal-control': '/static/img/heart-health.jpg',
            'cholesterol-heart-health-nepal': '/static/img/cholesterol.jpg'
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
