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
    # Production: Run migrations for missing tables
    print("Production mode - running table migrations...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, 'fix_clinic_tables.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"Migration warning: {result.stderr}")
    except Exception as e:
        print(f"Migration error (non-fatal): {e}")

# Expose the app for gunicorn
application = app

if __name__ == '__main__':
    app.run()
