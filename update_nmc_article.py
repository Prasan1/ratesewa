#!/usr/bin/env python3
"""
Update NMC article with more natural, less AI-sounding content
"""

from app import app, db, Article
from datetime import datetime

def update_nmc_article():
    with app.app_context():
        # Read the natural version
        with open('article_nmc_verification_natural.md', 'r') as f:
            content = f.read()

        # Find the article
        article = Article.query.filter_by(slug='verify-doctor-nmc-number-online').first()

        if not article:
            print("❌ Article not found!")
            return

        # Update with new content
        article.content = content
        article.updated_at = datetime.utcnow()

        db.session.commit()

        print("✅ Article updated with more natural content!")
        print(f"   URL: /health-digest/{article.slug}")
        print()
        print("🔗 Refresh: http://localhost:5000/health-digest/verify-doctor-nmc-number-online")

if __name__ == '__main__':
    update_nmc_article()
