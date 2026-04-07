#!/bin/bash

# BeasiswaKu Team Setup Script
# Run this after cloning the repository

set -e  # Exit on any error

echo "🚀 BeasiswaKu Team Setup Script"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Python version
echo -e "${YELLOW}Step 1: Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
    echo -e "${RED}❌ Python 3.8+ required. Current: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python version OK${NC}"
echo ""

# 2. Create virtual environment
echo -e "${YELLOW}Step 2: Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "venv already exists, skipping..."
else
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi
echo ""

# 3. Activate virtual environment
echo -e "${YELLOW}Step 3: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# 4. Install dependencies
echo -e "${YELLOW}Step 4: Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# 5. Initialize database
echo -e "${YELLOW}Step 5: Initializing database...${NC}"
python -c "from crud import init_db; init_db(); print('Database initialized')" 2>/dev/null
if [ -f "database/beasiswaku.db" ]; then
    echo -e "${GREEN}✅ Database created at database/beasiswaku.db${NC}"
else
    echo -e "${RED}❌ Database creation failed${NC}"
    exit 1
fi
echo ""

# 6. Ask for user name
echo -e "${YELLOW}Step 6: Setup Copilot personalization${NC}"
echo ""
echo "Pilih nama Anda:"
echo "1) Darva (Database & Authentication)"
echo "2) Kyla (UI/UX - Beasiswa Tab)"
echo "3) Aulia (Analytics & Visualization)"
echo "4) Kemal (Scraping & Search)"
echo "5) Richard (Advanced Analytics)"
echo ""
read -p "Pilih 1-5: " CHOICE

case $CHOICE in
    1)
        PERSON="darva"
        ROLE="Darva (Database & Authentication Specialist)"
        ;;
    2)
        PERSON="kyla"
        ROLE="Kyla (UI/UX Specialist)"
        ;;
    3)
        PERSON="aulia"
        ROLE="Aulia (Analytics & Visualization Specialist)"
        ;;
    4)
        PERSON="kemal"
        ROLE="Kemal (Data & Search Specialist)"
        ;;
    5)
        PERSON="richard"
        ROLE="Richard (Advanced Analytics Specialist)"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ Set role: $ROLE${NC}"
echo ""

# 7. Copy prompt to user folder (optional with message)
echo -e "${YELLOW}Step 7: Copilot prompt setup (optional)${NC}"
echo ""
echo "Untuk personalisasi Copilot dengan role Anda:"
echo ""
echo "Copy file ini ke VS Code User Prompts folder:"
echo "  Source: .github/prompts/${PERSON}.prompt.md"
echo "  Destination: ~/.config/Code/User/prompts/${PERSON}.prompt.md"
echo ""
echo "atau jalankan:"
echo "  cp .github/prompts/${PERSON}.prompt.md ~/.config/Code/User/prompts/"
echo ""

read -p "Ingin copy sekarang? (y/n): " COPY_PROMPTS

if [ "$COPY_PROMPTS" = "y" ] || [ "$COPY_PROMPTS" = "Y" ]; then
    PROMPTS_DIR="$HOME/.config/Code/User/prompts"
    
    # Create directory jika belum ada
    mkdir -p "$PROMPTS_DIR"
    
    # Copy file
    cp ".github/prompts/${PERSON}.prompt.md" "$PROMPTS_DIR/${PERSON}.prompt.md"
    
    if [ -f "$PROMPTS_DIR/${PERSON}.prompt.md" ]; then
        echo -e "${GREEN}✅ Prompt copied to $PROMPTS_DIR/${PERSON}.prompt.md${NC}"
    else
        echo -e "${RED}❌ Failed to copy prompt${NC}"
    fi
    echo ""
fi

# 8. Final summary
echo -e "${GREEN}=================================="
echo "✅ Setup Complete!"
echo "==================================${NC}"
echo ""
echo "You are set up as: $ROLE"
echo ""
echo "Next steps:"
echo "1. Open project in VS Code: code ."
echo "2. Restart VS Code to load new prompts"
echo "3. Read ONBOARDING.md for detailed instructions"
echo "4. Check copilot-instructions.md Section 0 for your tasks"
echo ""
echo "Quick test:"
echo "  Ask Copilot: 'Cek Section 0 di copilot-instructions.md'"
echo ""
echo "Happy coding! 🚀"
