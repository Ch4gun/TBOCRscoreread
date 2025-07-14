# Clan Points OCR Extractor

A Python script that uses Tesseract OCR to extract player names and points from clan screenshots and saves them to CSV format.

## Features

- ✅ Advanced image preprocessing for better OCR accuracy
- ✅ Intelligent pattern matching for player names and points
- ✅ Robust error handling and validation
- ✅ Debug mode for troubleshooting OCR issues
- ✅ CSV export with proper formatting
- ✅ **Cross-platform support (Windows 11, Linux, macOS)**
- ✅ **Automatic Tesseract path detection**

## Expected Output Format

The script extracts data in the following CSV format:

```csv
Name,Points
Spider Friend,215600
Violent Violet,204205
Akshat,196570
Finde,190960
```

## Installation

### Option 1: Windows 11 Installation (Recommended)

#### Method A: Easy Setup (Using Batch Files)

1. **Download all files** to a folder (e.g., `C:\clan-ocr\`)

2. **Install Tesseract OCR** (choose one):
   ```cmd
   # Option 1: Using Windows Package Manager
   winget install UB-Mannheim.Tesseract
   
   # Option 2: Manual download from:
   # https://github.com/UB-Mannheim/tesseract/wiki
   ```

3. **Run the automatic setup**:
   - Double-click `setup_windows.bat`
   - This will automatically install Python dependencies and set up the virtual environment

4. **Use the extractor**:
   - Place your screenshot as `points.jpg` in the folder
   - Double-click `run_extraction.bat`
   - Your results will be saved to `clan_points.csv`

#### Method B: Manual Setup

#### Step 1: Install Tesseract OCR

**Method A: Using Windows Package Manager (Recommended)**
```cmd
# Open Command Prompt or PowerShell as Administrator
winget install UB-Mannheim.Tesseract
```

**Method B: Manual Download**
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
3. Run the installer and follow the setup wizard
4. **Important**: During installation, note the installation path (usually `C:\Program Files\Tesseract-OCR\`)

#### Step 2: Install Python Dependencies
```cmd
# Open Command Prompt or PowerShell
# Navigate to your project folder
cd /path/to/your/project

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Verify Installation
```cmd
# Test Tesseract installation
tesseract --version

# If the above doesn't work, the script will auto-detect Tesseract location
python extract_clan_points.py
```

### Option 2: Linux Installation

```bash
# Install Tesseract OCR
sudo apt-get update
sudo apt-get install tesseract-ocr

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 3: macOS Installation

```bash
# Install Tesseract OCR
brew install tesseract

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Windows 11 Usage

1. **Prepare your screenshot**:
   - Take a screenshot of your clan points
   - Save it as `points.jpg` in the same folder as the script

2. **Run the script**:
   ```cmd
   # Make sure virtual environment is activated
   venv\Scripts\activate
   
   # Run the extraction script
   python extract_clan_points.py
   ```

3. **Check results**:
   - Open `clan_points.csv` in Excel or any text editor
   - Debug image will be saved as `debug_processed.png`

### Linux/macOS Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run the script
python extract_clan_points.py
```

## Configuration

You can modify these settings at the top of the script:

```python
INPUT_IMAGE = "points.jpg"     # Change input filename
OUTPUT_CSV = "clan_points.csv" # Change output filename
DEBUG_MODE = True              # Set to False to reduce console output
```

## Troubleshooting

### Windows 11 Specific Issues

#### "Tesseract not found" Error
1. **Check installation**: Open Command Prompt and run `tesseract --version`
2. **Manual path**: If auto-detection fails, the script will show common installation paths
3. **Reinstall**: Try uninstalling and reinstalling Tesseract
4. **Add to PATH**: Add Tesseract to your Windows PATH environment variable

#### Python/pip not recognized
1. **Install Python**: Download from https://python.org (make sure to check "Add to PATH")
2. **Restart Command Prompt** after Python installation

#### Permission Issues
1. **Run as Administrator**: Right-click Command Prompt and select "Run as administrator"
2. **Check folder permissions**: Make sure you have write access to the project folder

### General Troubleshooting

#### OCR Not Working Well?
1. **Check image quality**: Ensure the screenshot is clear and high resolution
2. **Try different image formats**: Convert to PNG if JPG isn't working well
3. **Enable debug mode**: Set `DEBUG_MODE = True` to see OCR output
4. **Check processed image**: Look at `debug_processed.png` to see preprocessing results

#### Missing Players?
1. **Check debug output**: See what names the OCR detected
2. **Modify expected names**: Update the `expected_names` list in the script
3. **Adjust point ranges**: Modify the `expected_ranges` dictionary

#### Wrong Points Values?
```python
# Modify these ranges in the script
expected_ranges = {
    'spider friend': (210000, 220000),
    'violent violet': (200000, 210000), 
    'akshat': (190000, 200000),
    'finde': (185000, 195000)
}
```

## Example Output

### Windows Command Prompt
```cmd
C:\Users\YourName\clan-ocr> python extract_clan_points.py
🎯 Clan Points OCR Extractor
========================================
🔧 Found Tesseract at: C:\Program Files\Tesseract-OCR\tesseract.exe
✅ All dependencies are available
📷 Processing image: points.jpg
🔧 Saved processed image as debug_processed.png
🔍 Running OCR extraction...

📊 Extracted 4 player records:
  • Spider Friend: 215,600
  • Violent Violet: 204,205
  • Akshat: 196,570
  • Finde: 190,960

🎉 Process completed successfully!
📄 Results saved to: clan_points.csv
```

## File Structure

Your project folder should look like this:
```
clan-ocr/
│
├── extract_clan_points.py    # Main script
├── requirements.txt          # Dependencies
├── README.md                # This file
├── setup_windows.bat        # Windows auto-setup script
├── run_extraction.bat       # Windows launcher script
├── points.jpg               # Your input image
├── clan_points.csv          # Output file (generated)
├── debug_processed.png      # Processed image (generated)
└── venv/                    # Virtual environment folder
```

### Windows Users
- **First time**: Double-click `setup_windows.bat`
- **Regular use**: Double-click `run_extraction.bat`

### Linux/macOS Users
- Use terminal commands as shown in the usage section

## Technical Details

The script automatically detects your operating system and configures Tesseract accordingly:

- **Windows**: Searches common installation paths and system PATH
- **Linux**: Uses system PATH (typically `/usr/bin/tesseract`)
- **macOS**: Uses Homebrew installation path

### Advanced Processing Pipeline:
1. **OS Detection**: Automatically configures Tesseract for your system
2. **Image Preprocessing**: Denoising, thresholding, upscaling, contrast enhancement
3. **Multi-Config OCR**: Tests multiple Tesseract settings for best results
4. **Smart Extraction**: Pattern matching with validation and fallback methods
5. **Data Validation**: Point range checking and duplicate removal

## License

This project is open source and available under the MIT License.