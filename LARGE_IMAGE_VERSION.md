# Large Image Clan Points OCR Extractor

## Problem Solved
The previous versions failed on large clan member lists with the error:
```
Image too large: (2070, 32982) Error during processing.
```

This happens when images with many clan members become too large for Tesseract after 4x upscaling.

## Solution: Smart Scaling + Chunk Processing

### 1. Automatic Size Detection
The script now checks image dimensions and automatically adjusts:
```python
MAX_TESSERACT_WIDTH = 8000
MAX_TESSERACT_HEIGHT = 8000
MAX_TESSERACT_PIXELS = 40000000  # ~40 megapixels
```

### 2. Dynamic Scaling
Instead of always using 4x scaling, it chooses the best option:
- **4x scaling** - For small images (best quality)
- **3x scaling** - For medium images  
- **2x scaling** - For larger images
- **1.5x scaling** - For very large images
- **1x scaling** - For massive images

### 3. Chunk Processing
For extremely large images that still exceed limits, it processes in horizontal chunks:
```python
def extract_in_chunks(img):
    # Splits image into overlapping chunks
    # Processes each chunk separately
    # Combines results
```

## Key Features

### ✅ Handles Any Size Image
- Small clan lists (4-10 members): Uses 4x scaling for maximum accuracy
- Medium clan lists (10-30 members): Uses 2-3x scaling
- Large clan lists (30+ members): Uses 1x scaling or chunk processing

### ✅ No Size Errors
- Automatically detects if image will be too large
- Reduces scaling to prevent Tesseract errors
- Falls back to chunk processing if needed

### ✅ Maintains Accuracy
- Still uses advanced preprocessing (denoising, contrast enhancement)
- Multiple OCR configurations when possible
- Smart pattern matching for player names and points

### ✅ Universal Player Detection
Instead of specific player names, detects any valid player entry:
```python
# Finds lines like:
# "PlayerName 123,456"
# "Another Player 98765"
# "ClanMember 45,678"
```

## Usage

### For Large Images:
```bash
# Windows
run_extraction_large.bat

# Linux/Mac
python3 extract_clan_points_large.py
```

### For Small Images (4 players):
```bash
# Windows
run_extraction_fixed.bat

# Linux/Mac  
python3 extract_clan_points_fixed.py
```

## Output Format
```csv
Name,Points
PlayerName1,215,600
PlayerName2,204,205
PlayerName3,196,570
PlayerName4,190,960
...and more players
```

## Debug Information
The script provides detailed feedback:
```
📏 Original image size: 517x8245
🔧 Using 1x scaling -> 517x8245
🔄 Image too large (517x8245), processing in chunks...
🔍 Processing chunk: y=0-2766
🔍 Processing chunk: y=2716-5516
🔍 Processing chunk: y=5466-8245
✅ Processed 3 chunks, total text: 15420 chars
📋 Extracted 45 unique player records
```

## When to Use Which Version

### Use `extract_clan_points_fixed.py` when:
- You have 4 specific players (Spider Friend, Violent Violet, Akshat, Finde)
- Small image size
- Want maximum accuracy for known players

### Use `extract_clan_points_large.py` when:
- You have many clan members (10+)
- Large image files
- Want to extract all players automatically
- Getting "Image too large" errors

## Technical Details
- **Chunk overlap**: 50 pixels to avoid cutting words
- **Maximum chunk height**: 7900 pixels (safe for Tesseract)
- **Point range**: 1,000 to 999,999 (broader than fixed version)
- **Name validation**: Minimum 3 characters, excludes pure numbers