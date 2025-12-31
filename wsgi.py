"""WSGI entry point for RateSewa"""
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"🔍 Loading RateSewa from: {current_dir}")
print(f"🔍 Python path: {sys.path[:3]}")

try:
    # Import the Flask app
    from app import app
    print("✅ Flask app imported successfully")

    # Expose the app for gunicorn
    application = app

    print(f"✅ Application ready: {app.name}")
except Exception as e:
    print(f"❌ Error loading application: {e}")
    import traceback
    traceback.print_exc()
    raise

if __name__ == '__main__':
    app.run()
