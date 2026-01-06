#!/usr/bin/env python3
"""
Delete the old Biratnagar article so we can republish with updated content
"""

from app import app, db
from models import Article

def delete_article():
    """Delete existing Biratnagar article"""
    with app.app_context():
        print("Searching for existing Biratnagar article...")

        # Find the article
        article = Article.query.filter_by(
            title='Prescription Fraud Alert: Biratnagar Pharmacy Caught Manipulating Dosages - What Patients Must Know'
        ).first()

        if not article:
            # Try finding by slug
            article = Article.query.filter_by(
                slug='biratnagar-pharmacy-fraud-prescription-safety'
            ).first()

        if article:
            print(f"Found article: ID {article.id} - {article.title}")
            db.session.delete(article)
            db.session.commit()
            print("✅ Article deleted successfully!")
            print("   Now run: python3 publish_biratnagar_article.py")
        else:
            print("⚠ No existing article found. You can run publish script directly.")

if __name__ == '__main__':
    delete_article()
