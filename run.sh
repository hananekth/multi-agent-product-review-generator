#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the app
echo "🚀 Starting AI Product Review Generator..."
uv run app.py
