#!/usr/bin/env python3
"""
Simple diagnostic: Just show article specialty links
"""

from app import app, db
from models import Article, Specialty

with app.app_context():
    print("=" * 60)
    print("ARTICLE SPECIALTY LINKS")
    print("=" * 60)

    # Find cholesterol article specifically
    cholesterol = Article.query.filter(
        Article.title.ilike('%cholesterol%')
    ).first()

    if cholesterol:
        print(f"\n🔍 CHOLESTEROL ARTICLE:")
        print(f"Title: {cholesterol.title}")
        print(f"Specialty ID: {cholesterol.related_specialty_id}")

        if cholesterol.related_specialty_id:
            spec = Specialty.query.get(cholesterol.related_specialty_id)
            if spec:
                print(f"Specialty Name: {spec.name}")
                print(f"✅ Link is valid")
            else:
                print(f"❌ Specialty ID {cholesterol.related_specialty_id} does NOT exist")
        else:
            print("⚠️ No specialty linked")

    print("\n" + "=" * 60)
    print("ALL ARTICLES:")
    print("=" * 60)

    for article in Article.query.all():
        specialty_name = "None"
        if article.related_specialty_id:
            spec = Specialty.query.get(article.related_specialty_id)
            specialty_name = spec.name if spec else f"BROKEN ID {article.related_specialty_id}"

        print(f"{article.title[:50]:50s} → {specialty_name}")

    print("\n" + "=" * 60)
    print("SPECIALTIES THAT EXIST:")
    print("=" * 60)

    for spec in Specialty.query.order_by(Specialty.id).all():
        print(f"{spec.id:3d}. {spec.name}")
