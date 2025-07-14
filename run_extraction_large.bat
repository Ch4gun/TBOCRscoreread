@echo off
echo ==========================================
echo    LARGE IMAGE Clan Points OCR Extractor  
echo ==========================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking/installing dependencies...
pip install pytesseract pillow pandas opencv-python 2>nul

REM Check if points.jpg exists
if not exist "points.jpg" (
    echo.
    echo ERROR: points.jpg not found!
    echo Please place your clan points image in this folder and rename it to "points.jpg"
    echo.
    echo This version handles LARGE images with many clan members!
    echo.
    pause
    exit /b 1
)

REM Run the large image extraction script
echo.
echo Running LARGE IMAGE OCR extraction...
echo This version can handle images with many clan members!
echo ==========================================
python extract_clan_points_large.py

REM Check if CSV was created
if exist "clan_points.csv" (
    echo.
    echo ==========================================
    echo SUCCESS! Results saved to clan_points.csv
    echo ==========================================
    echo.
    echo Opening CSV file...
    start "" clan_points.csv
) else (
    echo.
    echo WARNING: No CSV file was created
    echo Check the output above for errors
)

echo.
echo Press any key to close...
pause >nul