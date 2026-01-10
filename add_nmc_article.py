#!/usr/bin/env python3
"""
Script to add NMC verification article to database
"""

from app import app, db, Article, ArticleCategory
from datetime import datetime

def add_nmc_article():
    with app.app_context():
        # Read article content
        with open('docs/article_nmc_verification.md', 'r') as f:
            content = f.read()

        # Get or create category
        category = ArticleCategory.query.filter_by(name='Healthcare Tips').first()
        if not category:
            # Create category if it doesn't exist
            category = ArticleCategory(
                name='Healthcare Tips',
                slug='healthcare-tips',
                description='Practical health and healthcare guidance',
                display_order=2
            )
            db.session.add(category)
            db.session.commit()

        # Check if article already exists
        existing = Article.query.filter_by(slug='verify-doctor-nmc-number-online').first()
        if existing:
            print(f"Article already exists (ID: {existing.id}). Updating instead...")
            existing.content = content
            existing.summary = "Learn how to verify your doctor's Nepal Medical Council (NMC) registration number online. Complete guide with step-by-step instructions to check doctor credentials and avoid unregistered practitioners."
            existing.meta_description = "Complete guide to verifying doctors' NMC numbers in Nepal. Learn how to check doctor credentials online, understand NMC registration, and identify red flags. Protect yourself with verified information."
            existing.meta_keywords = "verify doctor nmc nepal, check doctor credentials nepal, nmc number lookup, nmc registration verification, verify medical license nepal, doctor verification nepal, nmc database search"
            existing.updated_at = datetime.utcnow()
            db.session.commit()
            print(f"✅ Article updated successfully!")
            print(f"URL: /health-digest/{existing.slug}")
            return

        # Create new article
        article = Article(
            title="How to Verify Your Doctor's NMC Number Online: A Complete Guide for Patients",
            slug="verify-doctor-nmc-number-online",
            category_id=category.id,
            summary="Learn how to verify your doctor's Nepal Medical Council (NMC) registration number online. Complete guide with step-by-step instructions to check doctor credentials and avoid unregistered practitioners.",
            content=content,
            meta_description="Complete guide to verifying doctors' NMC numbers in Nepal. Learn how to check doctor credentials online, understand NMC registration, and identify red flags. Protect yourself with verified information.",
            meta_keywords="verify doctor nmc nepal, check doctor credentials nepal, nmc number lookup, nmc registration verification, verify medical license nepal, doctor verification nepal, nmc database search",
            related_specialty_id=None,  # General article, not specialty-specific
            is_published=True,  # Publish immediately
            is_featured=True,  # Feature this article
            published_at=datetime.utcnow(),
            featured_image=None  # Can add image later via admin panel
        )

        db.session.add(article)
        db.session.commit()

        print("✅ NMC verification article created successfully!")
        print(f"   ID: {article.id}")
        print(f"   Slug: {article.slug}")
        print(f"   URL: /health-digest/{article.slug}")
        print(f"   Published: {article.is_published}")
        print(f"   Featured: {article.is_featured}")
        print()
        print("🔗 View it at: http://localhost:5000/health-digest/verify-doctor-nmc-number-online")

if __name__ == '__main__':
    add_nmc_article()
