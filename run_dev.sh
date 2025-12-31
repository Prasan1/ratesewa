#!/bin/bash
# Development server runner for RateSewa

echo "Starting RateSewa Development Server..."
echo "============================================"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the Flask development server
echo "Server starting at http://localhost:5000"
echo "Press CTRL+C to stop the server"
echo "============================================"
python3 app.py
