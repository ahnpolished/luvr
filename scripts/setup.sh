#!/usr/bin/env bash
# ============================================================
# Luvr Setup Script
# One-command setup for Mac development environment
# ============================================================
set -euo pipefail

echo "💝 Setting up Luvr - iMessage Dating Advice Chatbot"
echo "===================================================="
echo ""

# Check Python version
PYTHON=$(which python3 || which python || echo "")
if [ -z "$PYTHON" ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo "✅ Python found: $PYTHON_VERSION"

# Check minimum version (3.12)
MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')
MINOR=$($PYTHON -c 'import sys; print(sys.version_info.minor)')
if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 12 ]; }; then
    echo "❌ Python 3.12+ is required. Found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
$PYTHON -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -e ".[dev]" > /dev/null 2>&1

# Set up .env if not exists
if [ ! -f .env ]; then
    echo ""
    echo "🔑 Setting up configuration..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env with your API keys:"
    echo ""
    echo "   Required:"
    echo "   - BLUEBUBBLES_SERVER_URL  (your BlueBubbles server URL)"
    echo "   - BLUEBUBBLES_PASSWORD    (your BlueBubbles password)"
    echo ""
    echo "   Choose one LLM provider:"
    echo "   - OPENAI_API_KEY          (for OpenAI + Whisper)"
    echo "   - ANTHROPIC_API_KEY       (for Claude)"
    echo ""
    echo "   Edit with: nano .env  or  vim .env"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Create tmp directory
mkdir -p tmp

echo ""
echo "===================================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Install & configure BlueBubbles on your Mac"
echo "     → https://bluebubbles.app"
echo "  3. Start the server:  make run"
echo "  4. Send a test iMessage to your bot!"
echo ""
echo "For detailed instructions, see SETUP.md"
echo "===================================================="
