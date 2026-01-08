#!/usr/bin/env python3
"""
Check Featured doctors configuration in production
"""

from app import app, db
from models import Doctor

def check_featured_doctors():
    with app.app_context():
        print("=" * 70)
        print("CHECKING FEATURED DOCTORS IN DATABASE")
        print("=" * 70)

        # Check specific doctor
        bilakshan = Doctor.query.filter_by(name='Dr. Bilakshan Mishra').first()
        if bilakshan:
            print(f"\n1. Dr. Bilakshan Mishra (ID: {bilakshan.id})")
            print(f"   subscription_tier: {bilakshan.subscription_tier or 'NULL (defaults to free)'}")
            print(f"   is_verified: {bilakshan.is_verified}")
            print(f"   is_featured: {bilakshan.is_featured}")
            print(f"   Slug: {bilakshan.slug}")
        else:
            print("\n❌ Dr. Bilakshan Mishra not found")

        # Check all featured doctors
        print("\n" + "=" * 70)
        print("ALL DOCTORS WITH subscription_tier = 'featured':")
        print("=" * 70)
        featured = Doctor.query.filter_by(subscription_tier='featured').all()
        if featured:
            for doc in featured:
                print(f"   - {doc.name} (ID: {doc.id})")
        else:
            print("   ⚠️  No doctors with subscription_tier='featured' found")

        # Check all doctors with is_featured flag
        print("\n" + "=" * 70)
        print("ALL DOCTORS WITH is_featured = True:")
        print("=" * 70)
        featured_flag = Doctor.query.filter_by(is_featured=True).all()
        if featured_flag:
            for doc in featured_flag:
                print(f"   - {doc.name} (ID: {doc.id}, tier: {doc.subscription_tier or 'NULL'})")
        else:
            print("   ⚠️  No doctors with is_featured=True found")

        # Suggest fix
        print("\n" + "=" * 70)
        print("FIX: Update Dr. Bilakshan Mishra to Featured tier:")
        print("=" * 70)
        if bilakshan and bilakshan.subscription_tier != 'featured':
            print(f"python3 -c \"from app import app, db; from models import Doctor; \\")
            print(f"with app.app_context(): \\")
            print(f"    d = Doctor.query.get({bilakshan.id}); \\")
            print(f"    d.subscription_tier = 'featured'; \\")
            print(f"    db.session.commit(); \\")
            print(f"    print('✅ Updated to Featured')\"")

if __name__ == '__main__':
    check_featured_doctors()
