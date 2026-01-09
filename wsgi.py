"""WSGI entry point for RateSewa"""
import os
import sys

# Ensure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app, db

# Only create tables in development (SQLite), not in production
# Production should use migrations instead
if os.environ.get('DATABASE_URL') is None:
    # Local development only
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables ready (development)")
        except Exception as e:
            print(f"⚠️  Database setup: {e}")
else:
    print("Production mode - skipping db.create_all(), use migrations instead")

# Expose the app for gunicorn
application = app

if __name__ == '__main__':
    app.run()
