#!/bin/bash
# Startup script for DigitalOcean App Platform

echo "🚀 Starting RateSewa deployment..."

# Create instance directory if it doesn't exist
mkdir -p instance

# Initialize database if it doesn't exist
if [ ! -f "instance/doctors.db" ]; then
    echo "📊 Creating database..."
    python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database tables created")
EOF
fi

echo "🔥 Starting Gunicorn..."
# Start Gunicorn
exec gunicorn --worker-tmp-dir /dev/shm --workers 2 --bind 0.0.0.0:8080 app:app
