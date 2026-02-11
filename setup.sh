#!/bin/bash

echo "🚀 Setting up AI Product Review Generator..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    echo "✅ uv installed successfully!"
else
    echo "✅ uv is already installed"
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
uv venv --python 3.12

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
uv sync

echo ""
echo "✨ Setup complete! ✨"
echo ""
echo "To run the app:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run the app: uv run app.py"
echo ""
echo "You'll need an API key from one of these providers:"
echo "  - OpenAI: https://platform.openai.com/api-keys"
echo "  - Google Gemini: https://aistudio.google.com/apikey"
echo "  - Anthropic Claude: https://console.anthropic.com/"
echo "  - xAI Grok: https://console.x.ai/"
echo ""
