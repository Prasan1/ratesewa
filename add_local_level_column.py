#!/usr/bin/env python3
"""
Add local_level_id column to doctors table.
Run this once on production after setting up LocalLevel tables.
"""

from app import app, db

with app.app_context():
    try:
        db.session.execute(db.text('ALTER TABLE doctors ADD COLUMN local_level_id INTEGER REFERENCES local_levels(id)'))
        db.session.commit()
        print('✓ Column local_level_id added to doctors table!')
    except Exception as e:
        if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
            print('✓ Column already exists, skipping.')
        else:
            print(f'✗ Error: {e}')
            raise
