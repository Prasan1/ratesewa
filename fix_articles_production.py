#!/usr/bin/env python3
"""
Fix article specialty links - Production version
Uses actual production specialty IDs from DO database
"""

from app import app, db
from models import Article, Specialty

with app.app_context():
    print("=" * 60)
    print("FIXING ARTICLE SPECIALTIES (Production)")
    print("=" * 60)

    # Article title → Correct Specialty ID mapping
    # Based on actual production specialty IDs
    ARTICLE_FIXES = {
        'cholesterol': 15,  # Cardiology
        'heart health': 15,  # Cardiology
        'blood pressure': 15,  # Cardiology
        'mental health': 22,  # Psychiatry
        'women\'s health': 43,  # Obstetrics & Gynecology
        'diabetes': 13,  # General Physician (if exists, otherwise use another)
        'nutrition': 13,  # General Physician
    }

    fixed_count = 0

    # Get all articles
    articles = Article.query.all()

    for article in articles:
        title_lower = article.title.lower()

        # Check which specialty this article should have
        target_specialty_id = None

        if 'cholesterol' in title_lower or 'heart' in title_lower or 'blood pressure' in title_lower:
            target_specialty_id = 15  # Cardiology
        elif 'mental health' in title_lower or 'mental' in title_lower:
            target_specialty_id = 22  # Psychiatry
        elif 'women' in title_lower or 'gynecology' in title_lower:
            target_specialty_id = 43  # Obstetrics & Gynecology
        elif 'diabetes' in title_lower or 'nutrition' in title_lower:
            target_specialty_id = 13  # General Physician (assuming ID 13 exists)

        if target_specialty_id:
            # Check if it needs fixing
            if article.related_specialty_id != target_specialty_id:
                old_id = article.related_specialty_id

                # Verify target specialty exists
                target_spec = Specialty.query.get(target_specialty_id)
                if target_spec:
                    article.related_specialty_id = target_specialty_id
                    fixed_count += 1

                    print(f"✓ {article.title}")
                    print(f"  Changed: {old_id} → {target_specialty_id} ({target_spec.name})")
                else:
                    print(f"⚠ {article.title}")
                    print(f"  ERROR: Target specialty {target_specialty_id} not found!")
            else:
                print(f"✓ {article.title} - Already correct ({target_specialty_id})")

    if fixed_count > 0:
        db.session.commit()
        print("\n" + "=" * 60)
        print(f"✅ Fixed {fixed_count} article(s)")
        print("=" * 60)
    else:
        print("\n✅ All articles already have correct specialties")

    # Show final state
    print("\n" + "=" * 60)
    print("FINAL STATE:")
    print("=" * 60)

    for article in Article.query.all():
        spec_name = "None"
        if article.related_specialty_id:
            spec = Specialty.query.get(article.related_specialty_id)
            spec_name = spec.name if spec else f"BROKEN ({article.related_specialty_id})"

        print(f"{article.title[:45]:45s} → {spec_name}")
