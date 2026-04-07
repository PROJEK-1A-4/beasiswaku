@echo off
REM BeasiswaKu Team Setup Script for Windows
REM Run this after cloning the repository

setlocal enabledelayedexpansion

echo.
echo 🚀 BeasiswaKu Team Setup Script (Windows)
echo ==========================================
echo.

REM 1. Check Python version
echo Step 1: Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
echo ✅ Python found
echo.

REM 2. Create virtual environment
echo Step 2: Creating virtual environment...
if exist venv (
    echo venv already exists, skipping...
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)
echo.

REM 3. Activate virtual environment
echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM 4. Install dependencies
echo Step 4: Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo ✅ Dependencies installed
echo.

REM 5. Initialize database
echo Step 5: Initializing database...
python -c "from crud import init_db; init_db(); print('Database initialized')" 2>nul
if exist database\beasiswaku.db (
    echo ✅ Database created at database\beasiswaku.db
) else (
    echo ❌ Database creation failed
    pause
    exit /b 1
)
echo.

REM 6. Ask for user name
echo Step 6: Setup Copilot personalization
echo.
echo Pilih nama Anda:
echo 1) Darva (Database ^& Authentication)
echo 2) Kyla (UI/UX - Beasiswa Tab)
echo 3) Aulia (Analytics ^& Visualization)
echo 4) Kemal (Scraping ^& Search)
echo 5) Richard (Advanced Analytics)
echo.

set /p CHOICE="Pilih 1-5: "

if "%CHOICE%"=="1" (
    set PERSON=darva
    set ROLE=Darva (Database ^& Authentication Specialist)
) else if "%CHOICE%"=="2" (
    set PERSON=kyla
    set ROLE=Kyla (UI/UX Specialist)
) else if "%CHOICE%"=="3" (
    set PERSON=aulia
    set ROLE=Aulia (Analytics ^& Visualization Specialist)
) else if "%CHOICE%"=="4" (
    set PERSON=kemal
    set ROLE=Kemal (Data ^& Search Specialist)
) else if "%CHOICE%"=="5" (
    set PERSON=richard
    set ROLE=Richard (Advanced Analytics Specialist)
) else (
    echo ❌ Invalid choice
    pause
    exit /b 1
)

echo ✅ Set role: %ROLE%
echo.

REM 7. Copy prompt (optional)
echo Step 7: Copilot prompt setup (optional)
echo.
echo Untuk personalisasi Copilot dengan role Anda:
echo   Source: .github\prompts\%PERSON%.prompt.md
echo   Destination: %%APPDATA%%\Code\User\prompts\%PERSON%.prompt.md
echo.

set /p COPY_PROMPTS="Ingin copy sekarang? (y/n): "

if /i "%COPY_PROMPTS%"=="y" (
    set PROMPTS_DIR=%APPDATA%\Code\User\prompts
    
    if not exist "!PROMPTS_DIR!" mkdir "!PROMPTS_DIR!"
    
    copy ".github\prompts\%PERSON%.prompt.md" "!PROMPTS_DIR!\%PERSON%.prompt.md" >nul
    
    if exist "!PROMPTS_DIR!\%PERSON%.prompt.md" (
        echo ✅ Prompt copied to !PROMPTS_DIR!\%PERSON%.prompt.md
    ) else (
        echo ❌ Failed to copy prompt
    )
    echo.
)

REM 8. Final summary
echo.
echo ==========================================
echo ✅ Setup Complete!
echo ==========================================
echo.
echo You are set up as: %ROLE%
echo.
echo Next steps:
echo 1. Open project in VS Code: code .
echo 2. Restart VS Code to load new prompts
echo 3. Read ONBOARDING.md for detailed instructions
echo 4. Check copilot-instructions.md Section 0 for your tasks
echo.
echo Quick test:
echo   Ask Copilot: "Cek Section 0 di copilot-instructions.md"
echo.
echo Happy coding! 🚀
echo.
pause
