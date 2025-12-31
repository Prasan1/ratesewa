#!/usr/bin/env python3
"""
Migration: Add review_flags table for content moderation
This is for flagging inappropriate content, NOT for removing negative reviews
"""

from app import app, db
from sqlalchemy import text

def upgrade_database():
    """Add review_flags table"""
    with app.app_context():
        engine = db.engine
        with engine.connect() as conn:
            trans = conn.begin()

            print("Creating review_flags table...")

            # Create review_flags table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS review_flags (
                    id SERIAL PRIMARY KEY,
                    rating_id INTEGER NOT NULL REFERENCES ratings(id),
                    reporter_user_id INTEGER REFERENCES users(id),
                    reason VARCHAR(50) NOT NULL,
                    additional_details TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    admin_notes TEXT,
                    reviewed_by INTEGER REFERENCES users(id),
                    reviewed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create indexes for performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_review_flags_rating
                ON review_flags(rating_id)
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_review_flags_status
                ON review_flags(status)
            """))

            trans.commit()
            print("✅ Migration completed successfully!")

if __name__ == '__main__':
    print("=" * 60)
    print("Migration: Add Review Flags Table")
    print("=" * 60)
    upgrade_database()
    print("=" * 60)
