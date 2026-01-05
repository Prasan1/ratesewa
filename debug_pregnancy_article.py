#!/usr/bin/env python3
"""
Debug: Why isn't the pregnancy article being detected?
"""

from app import app, db
from models import Article, Specialty

with app.app_context():
    print("=" * 60)
    print("DEBUGGING PREGNANCY ARTICLE")
    print("=" * 60)

    # Find pregnancy article
    articles = Article.query.all()

    for article in articles:
        title_lower = article.title.lower()

        # Check if it contains pregnancy
        if 'pregn' in title_lower:  # Using shorter match
            print(f"\n🔍 FOUND PREGNANCY ARTICLE:")
            print(f"Title: '{article.title}'")
            print(f"Title (lowercase): '{title_lower}'")
            print(f"Current Specialty ID: {article.related_specialty_id}")

            if article.related_specialty_id:
                spec = Specialty.query.get(article.related_specialty_id)
                print(f"Current Specialty Name: {spec.name if spec else 'NOT FOUND'}")

            # Test keyword matches
            print(f"\nKeyword tests:")
            print(f"  'pregnancy' in title: {'pregnancy' in title_lower}")
            print(f"  'women' in title: {'women' in title_lower}")
            print(f"  'prenatal' in title: {'prenatal' in title_lower}")
            print(f"  'maternal' in title: {'maternal' in title_lower}")

            # What should it be?
            target_id = 43
            target_spec = Specialty.query.get(target_id)
            print(f"\nShould be: {target_id} ({target_spec.name if target_spec else 'NOT FOUND'})")
            print(f"Needs fixing: {article.related_specialty_id != target_id}")

    print("\n" + "=" * 60)
    print("ALL ARTICLE TITLES:")
    print("=" * 60)
    for article in articles:
        print(f"- {article.title}")
