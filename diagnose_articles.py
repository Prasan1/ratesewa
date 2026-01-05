#!/usr/bin/env python3
"""
Diagnostic script: Show what specialty each article is linked to
"""

from app import app, db
from models import Article, Specialty, Doctor

with app.app_context():
    print("=" * 60)
    print("ARTICLE SPECIALTY DIAGNOSIS")
    print("=" * 60)

    articles = Article.query.all()

    for article in articles:
        print(f"\nArticle: {article.title}")
        print(f"Slug: {article.slug}")

        if article.related_specialty_id:
            specialty = Specialty.query.get(article.related_specialty_id)

            if specialty:
                print(f"Specialty ID: {article.related_specialty_id}")
                print(f"Specialty Name: {specialty.name}")

                # Count doctors in this specialty
                doctor_count = Doctor.query.filter_by(
                    specialty_id=article.related_specialty_id,
                    is_active=True
                ).count()
                print(f"Doctors in specialty: {doctor_count}")

                # Show first 3 doctors
                doctors = Doctor.query.filter_by(
                    specialty_id=article.related_specialty_id,
                    is_active=True
                ).limit(3).all()

                if doctors:
                    print("Sample doctors:")
                    for d in doctors:
                        print(f"  - {d.name}")
                else:
                    print("⚠️ No doctors in this specialty!")
            else:
                print(f"❌ BROKEN: Specialty ID {article.related_specialty_id} not found")
        else:
            print("⚠️ No specialty linked")

    print("\n" + "=" * 60)
    print("ALL SPECIALTIES")
    print("=" * 60)

    specialties = Specialty.query.all()
    for spec in specialties:
        doc_count = Doctor.query.filter_by(specialty_id=spec.id, is_active=True).count()
        print(f"{spec.id:3d}. {spec.name:40s} ({doc_count:,} doctors)")
