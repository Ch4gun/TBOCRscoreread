# Clan Points OCR Extractor

A Python script that uses Tesseract OCR to extract player names and points from clan screenshots and saves them to CSV format.

## Features

- ✅ Advanced image preprocessing for better OCR accuracy
- ✅ Intelligent pattern matching for player names and points
- ✅ Robust error handling and validation
- ✅ Debug mode for troubleshooting OCR issues
- ✅ CSV export with proper formatting
- ✅ Cross-platform support (Linux, Windows, macOS)

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

### Prerequisites

1. **Install Tesseract OCR**
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

2. **Install Python Dependencies**
   ```bash
   # Create virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

## Usage

1. **Place your screenshot** in the same directory as the script and name it `points.jpg`

2. **Run the script**:
   ```bash
   python extract_clan_points.py
   ```

3. **Check the output**:
   - Results will be saved to `clan_points.csv`
   - Debug information will be displayed in the console
   - A processed image (`debug_processed.png`) will be saved for troubleshooting

## Configuration

You can modify these settings at the top of the script:

```python
INPUT_IMAGE = "points.jpg"     # Change input filename
OUTPUT_CSV = "clan_points.csv" # Change output filename
DEBUG_MODE = True              # Set to False to reduce console output
```

## Troubleshooting

### OCR Not Working Well?

1. **Check image quality**: Ensure the screenshot is clear and high resolution
2. **Adjust preprocessing**: The script applies denoising and contrast enhancement
3. **Enable debug mode**: Set `DEBUG_MODE = True` to see OCR output and processing steps
4. **Check processed image**: Look at `debug_processed.png` to see how the image was processed

### Missing Players?

The script looks for specific player names. If a player is missing, you can:

1. Check the debug output to see what OCR detected
2. Modify the `expected_names` list in the `parse_ocr_text()` function
3. Adjust the `expected_ranges` dictionary for point validation

### Wrong Points Values?

The script validates points within expected ranges. You can modify these in the `expected_ranges` dictionary:

```python
expected_ranges = {
    'spider friend': (210000, 220000),
    'violent violet': (200000, 210000), 
    'akshat': (190000, 200000),
    'finde': (185000, 195000)
}
```

## Example Output

```
🎯 Clan Points OCR Extractor
========================================
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

## Technical Details

The script uses several advanced techniques for better OCR accuracy:

1. **Image Preprocessing**:
   - Grayscale conversion
   - Denoising with OpenCV
   - Adaptive thresholding
   - Image upscaling (3x)
   - Contrast enhancement

2. **OCR Processing**:
   - Multiple Tesseract configurations
   - Best result selection
   - Text cleaning and normalization

3. **Data Extraction**:
   - Pattern matching for player names
   - Point range validation
   - Duplicate removal
   - Fallback extraction methods

## License

This project is open source and available under the MIT License.