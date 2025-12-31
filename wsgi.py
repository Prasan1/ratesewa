"""WSGI entry point for RateSewa"""
import os
import sys

# Ensure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app, db

# Create database tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables ready")
    except Exception as e:
        print(f"⚠️  Database setup: {e}")

# Expose the app for gunicorn
application = app

if __name__ == '__main__':
    app.run()
