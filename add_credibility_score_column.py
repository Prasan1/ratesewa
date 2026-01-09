#!/usr/bin/env python3
"""
Add credibility_score column to ratings table
"""

import os
import sys
from sqlalchemy import create_engine, text

# Database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/doctors.db')

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("Adding credibility_score column to ratings table...")
print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            # Add column (safe - won't fail if column exists)
            print("Adding credibility_score column...")
            conn.execute(text("""
                ALTER TABLE ratings
                ADD COLUMN IF NOT EXISTS credibility_score INTEGER DEFAULT 0
            """))

            trans.commit()
            print("✅ Column added successfully!")

        except Exception as e:
            trans.rollback()
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("✓ Column already exists, skipping")
            else:
                print(f"❌ Error: {e}")
                sys.exit(1)

    # Now calculate credibility scores for existing reviews
    print("\nCalculating credibility scores for existing reviews...")
    print("This may take a few minutes...")

    from app import app
    from credibility import recalculate_all_credibility_scores

    with app.app_context():
        stats = recalculate_all_credibility_scores()

        print("\n" + "="*60)
        print("✅ Credibility scores calculated!")
        print("="*60)
        print(f"Total reviews: {stats['total']}")
        print(f"  Verified Patient (40+): {stats['verified_patient']}")
        print(f"  Trusted (20-39): {stats['trusted']}")
        print(f"  Neutral (0-19): {stats['neutral']}")
        print(f"  Suspicious (<0): {stats['suspicious']}")

except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
