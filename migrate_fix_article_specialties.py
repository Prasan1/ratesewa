#!/usr/bin/env python3
"""
Migration: Fix broken article specialty links after specialization cleanup

This fixes articles that reference old deleted specialty IDs from the
specialty cleanup migration. Articles were missed in the original cleanup.

Run this on production after deploying.
"""

from app import app, db
from models import Article, Specialty

def fix_article_specialties():
    """Fix articles with broken specialty links"""

    # Mapping of old deleted IDs to new correct IDs
    SPECIALTY_FIXES = {
        1: 37,  # General Practitioner → General Physician
        2: 18,  # Cardiologist → Cardiology
        3: 13,  # Dermatologist → Dermatology
        4: 26,  # Pediatrician → Pediatrics
        5: 21,  # Gynecologist → Obstetrics & Gynecology
        8: 19,  # Psychiatrist → Psychiatry
        10: 23, # ENT Specialist → ENT
        24: 35, # Urology | Andrology → Urology
        25: 37, # General Physician | Endocrinology → General Physician
        33: 21, # Obs. Gynaecology → Obstetrics & Gynecology
        34: 23, # ENT, HNS → ENT
    }

    print("=" * 60)
    print("MIGRATION: Fix Article Specialty Links")
    print("=" * 60)

    with app.app_context():
        fixed_count = 0

        for article in Article.query.all():
            if article.related_specialty_id in SPECIALTY_FIXES:
                old_id = article.related_specialty_id
                new_id = SPECIALTY_FIXES[old_id]

                # Verify new specialty exists
                new_specialty = Specialty.query.get(new_id)
                if new_specialty:
                    article.related_specialty_id = new_id
                    fixed_count += 1

                    print(f"✓ {article.title}")
                    print(f"  Changed: {old_id} → {new_id} ({new_specialty.name})")
                else:
                    print(f"⚠ {article.title}")
                    print(f"  ERROR: Target specialty {new_id} not found!")

        if fixed_count > 0:
            db.session.commit()
            print("\n" + "=" * 60)
            print(f"✅ Fixed {fixed_count} article(s)")
            print("=" * 60)
        else:
            print("\n✅ No articles needed fixing")

        # Verify all articles now have valid specialty links
        print("\n" + "=" * 60)
        print("VERIFICATION")
        print("=" * 60)

        broken = []
        for article in Article.query.all():
            if article.related_specialty_id:
                specialty = Specialty.query.get(article.related_specialty_id)
                if not specialty:
                    broken.append(f"{article.title} (ID: {article.related_specialty_id})")

        if broken:
            print("❌ Still broken:")
            for b in broken:
                print(f"  - {b}")
        else:
            print("✅ All articles have valid specialty links")

        print("=" * 60)


if __name__ == '__main__':
    fix_article_specialties()
