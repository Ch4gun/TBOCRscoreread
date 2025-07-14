@echo off
echo 🎯 Clan Points OCR Extractor - Windows Launcher
echo ===============================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo Please run setup first:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if points.jpg exists
if not exist "points.jpg" (
    echo ❌ Image file 'points.jpg' not found!
    echo Please place your clan points screenshot in this folder and rename it to 'points.jpg'
    pause
    exit /b 1
)

echo ✅ Activating virtual environment...
call venv\Scripts\activate

echo ✅ Running OCR extraction...
python extract_clan_points.py

echo.
echo 📄 Check 'clan_points.csv' for results!
echo 🔧 Check 'debug_processed.png' to see how the image was processed
echo.

pause