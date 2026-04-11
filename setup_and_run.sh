#!/bin/bash
# setup_and_run.sh - BeasiswaKu Setup & Run Script
# Automatically installs dependencies and runs the application

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                   BeasiswaKu - Setup & Installation               ║"
echo "║                  Sistem Manajemen Beasiswa Desktop                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
ENV_PATH="$HOME/.local/share/beasiswa/env"

if [ -d "$ENV_PATH" ]; then
    echo "   Virtual environment already exists at $ENV_PATH"
else
    python3 -m venv "$ENV_PATH"
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔓 Activating virtual environment..."
source "$ENV_PATH/bin/activate"
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Install requirements
echo "📥 Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "✅ All dependencies installed"
else
    echo "⚠️  requirements.txt not found, installing essential packages..."
    pip install PyQt6 bcrypt requests beautifulsoup4 matplotlib lxml --quiet
    echo "✅ Essential packages installed"
fi
echo ""

# Create database folder
echo "📁 Creating database folder..."
mkdir -p database
echo "✅ Database folder ready"
echo ""

# Verify installation
echo "🧪 Verifying installation..."
python3 -c "
import sys
try:
    import PyQt6
    print('   ✅ PyQt6 imported successfully')
except ImportError:
    print('   ❌ PyQt6 import failed')
    sys.exit(1)

try:
    import bcrypt
    print('   ✅ bcrypt imported successfully')
except ImportError:
    print('   ❌ bcrypt import failed')
    sys.exit(1)

try:
    import crud
    print('   ✅ crud.py module found')
except ImportError:
    print('   ❌ crud.py import failed')
    sys.exit(1)

print('')
print('✅ All verifications passed!')
"

if [ $? -ne 0 ]; then
    echo "❌ Verification failed"
    exit 1
fi

# Show startup menu
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                        Setup Complete! 🎉                         ║"
echo "╠════════════════════════════════════════════════════════════════════╣"
echo "║                        Choose an option:                          ║"
echo "║                                                                    ║"
echo "║  1) Run Application         (python3 main.py)                     ║"
echo "║  2) Run Tests               (python3 comprehensive_analysis.py)   ║"
echo "║  3) View Documentation      (open DOCUMENTATION.md)              ║"
echo "║  4) Exit                    (close this window)                  ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting BeasiswaKu application..."
        echo ""
        python3 main.py
        ;;
    2)
        echo ""
        echo "🧪 Running comprehensive tests and analysis..."
        echo ""
        python3 comprehensive_analysis.py
        ;;
    3)
        echo ""
        echo "📖 Opening documentation..."
        if command -v xdg-open &> /dev/null; then
            xdg-open DOCUMENTATION.md
        elif command -v open &> /dev/null; then
            open DOCUMENTATION.md
        else
            cat DOCUMENTATION.md | less
        fi
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
