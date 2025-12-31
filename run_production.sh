#!/bin/bash
# Production server runner for RateSewa using Gunicorn

echo "Starting RateSewa Production Server..."
echo "============================================"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn not found. Installing..."
    pip install gunicorn
fi

# Set production environment
export FLASK_ENV=production

# Run Gunicorn with 4 workers
# Adjust the number of workers based on your server's CPU cores
# Formula: (2 x CPU cores) + 1
echo "Starting Gunicorn with 4 worker processes..."
echo "Server running at http://0.0.0.0:8000"
echo "Press CTRL+C to stop the server"
echo "============================================"

gunicorn -w 4 -b 0.0.0.0:8000 --access-logfile - --error-logfile - app:app
