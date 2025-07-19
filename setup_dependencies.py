#!/usr/bin/env python3
"""
Setup script for Large Clan Screenshot OCR Extractor
Installs all required dependencies and checks Tesseract installation
"""

import sys
import subprocess
import platform
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_python_version():
    """Check if Python version is sufficient"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.6+")
        return False

def install_python_packages():
    """Install required Python packages"""
    packages = [
        "pytesseract",
        "opencv-python", 
        "Pillow",
        "pandas",
        "numpy"
    ]
    
    print("\n📦 Installing Python packages...")
    
    success = True
    for package in packages:
        cmd = f"{sys.executable} -m pip install {package}"
        if not run_command(cmd, f"Installing {package}"):
            success = False
    
    return success

def check_tesseract_installation():
    """Check if Tesseract OCR is installed"""
    print("\n🔍 Checking Tesseract OCR installation...")
    
    system = platform.system().lower()
    
    # Try to run tesseract command
    if run_command("tesseract --version", "Checking Tesseract in PATH"):
        return True
    
    # System-specific installation instructions
    print("\n❌ Tesseract OCR not found!")
    print("📋 Installation instructions:")
    
    if system == "linux":
        print("   Ubuntu/Debian: sudo apt-get update && sudo apt-get install tesseract-ocr")
        print("   CentOS/RHEL:   sudo yum install tesseract")
        print("   Arch:          sudo pacman -S tesseract")
    elif system == "darwin":  # macOS
        print("   Homebrew:      brew install tesseract")
        print("   MacPorts:      sudo port install tesseract")
    elif system == "windows":
        print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Or use winget: winget install UB-Mannheim.Tesseract")
    
    return False

def create_test_script():
    """Create a simple test script to verify installation"""
    test_script = """#!/usr/bin/env python3
# Test script for Large Clan Screenshot OCR Extractor

def test_imports():
    try:
        import pytesseract
        print("✅ pytesseract imported successfully")
    except ImportError as e:
        print(f"❌ pytesseract import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ opencv-python imported successfully")
    except ImportError as e:
        print(f"❌ opencv-python import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    return True

def test_tesseract():
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Large Clan Screenshot OCR Extractor Dependencies")
    print("=" * 60)
    
    imports_ok = test_imports()
    tesseract_ok = test_tesseract()
    
    if imports_ok and tesseract_ok:
        print("\\n🎉 All dependencies are working correctly!")
        print("💡 You can now run: python3 run_large_extraction.py")
    else:
        print("\\n❌ Some dependencies are missing or not working")
        print("💡 Please install missing components and run this test again")
"""
    
    with open("test_dependencies.py", "w") as f:
        f.write(test_script)
    
    print("📝 Created test_dependencies.py for verification")

def main():
    """Main setup function"""
    print("🎯 Large Clan Screenshot OCR Extractor - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version incompatible")
        return 1
    
    # Install Python packages
    if not install_python_packages():
        print("\n⚠️ Some Python packages failed to install")
        print("💡 You may need to install them manually")
    
    # Check Tesseract
    tesseract_ok = check_tesseract_installation()
    
    # Create test script
    create_test_script()
    
    # Final status
    print("\n" + "=" * 60)
    if tesseract_ok:
        print("✅ Setup completed successfully!")
        print("🚀 Ready to use Large Clan Screenshot OCR Extractor")
        print("\n💡 Quick test: python3 test_dependencies.py")
        print("💡 Run extractor: python3 run_large_extraction.py")
    else:
        print("⚠️ Setup partially completed")
        print("📋 Please install Tesseract OCR manually (see instructions above)")
        print("🧪 Test after installation: python3 test_dependencies.py")
    
    return 0 if tesseract_ok else 1

if __name__ == "__main__":
    sys.exit(main())