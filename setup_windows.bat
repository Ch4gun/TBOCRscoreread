(cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF'
diff --git a/setup_windows.bat b/setup_windows.bat
--- a/setup_windows.bat
+++ b/setup_windows.bat
@@ -0,0 +1,69 @@
+@echo off
+echo 🚀 Clan Points OCR Extractor - Windows Setup
+echo =============================================
+
+REM Check if Python is installed
+python --version >nul 2>&1
+if errorlevel 1 (
+    echo ❌ Python is not installed or not in PATH!
+    echo Please install Python from: https://python.org
+    echo Make sure to check "Add Python to PATH" during installation
+    pause
+    exit /b 1
+)
+
+echo ✅ Python found!
+python --version
+
+REM Check if Tesseract is available
+echo.
+echo 🔍 Checking for Tesseract OCR...
+tesseract --version >nul 2>&1
+if errorlevel 1 (
+    echo ⚠️  Tesseract not found in PATH
+    echo Please install Tesseract OCR:
+    echo    Option 1: winget install UB-Mannheim.Tesseract
+    echo    Option 2: Download from https://github.com/UB-Mannheim/tesseract/wiki
+    echo.
+    echo The script will try to auto-detect Tesseract installation later.
+) else (
+    echo ✅ Tesseract found!
+    tesseract --version
+)
+
+echo.
+echo 📦 Setting up virtual environment...
+
+REM Remove existing venv if it exists
+if exist "venv\" (
+    echo Removing existing virtual environment...
+    rmdir /s /q venv
+)
+
+REM Create new virtual environment
+echo Creating virtual environment...
+python -m venv venv
+
+REM Activate virtual environment
+echo Activating virtual environment...
+call venv\Scripts\activate
+
+REM Upgrade pip
+echo Upgrading pip...
+python -m pip install --upgrade pip
+
+REM Install requirements
+echo Installing dependencies...
+pip install -r requirements.txt
+
+echo.
+echo ✅ Setup completed successfully!
+echo.
+echo 📋 Next steps:
+echo 1. Place your clan points screenshot in this folder
+echo 2. Rename it to 'points.jpg'
+echo 3. Double-click 'run_extraction.bat' to extract points
+echo    OR manually run: python extract_clan_points.py
+echo.
+
+pause
EOF
)
