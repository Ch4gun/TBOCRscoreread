# Large Clan Screenshot OCR Extractor

This tool is specifically designed to extract player nicknames and points from very large clan screenshots (e.g., 623px × 11302px for 80-100 players). It processes images in chunks to handle memory efficiently and accurately match nicknames (left side) with points (right side).

## 🎯 Key Features

- **Large Image Support**: Handles screenshots up to 14,000px height (100 players)
- **Chunk Processing**: Processes images in manageable pieces to avoid memory issues
- **Region-Based OCR**: Separate processing for nicknames (left) and points (right)
- **Auto-Configuration**: Automatically adjusts settings based on clan size
- **Configurable**: JSON-based configuration for easy customization
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Debug Support**: Extensive debugging tools and intermediate image saving

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pytesseract opencv-python Pillow pandas numpy
```

### 2. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Or install with: `winget install UB-Mannheim.Tesseract`

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 3. Run the Extractor

```bash
# Basic usage (processes points.jpg)
python run_large_extraction.py

# Process specific image
python run_large_extraction.py my_clan_screenshot.png

# Quick mode (less debug output)
python run_large_extraction.py --quick my_clan_screenshot.png

# Check if dependencies are installed
python run_large_extraction.py --check-deps
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `extract_clan_points_large.py` | Core OCR processor for large images |
| `extract_clan_points_configurable.py` | Configurable version with JSON settings |
| `run_large_extraction.py` | Simple command-line interface |
| `config.json` | Configuration file for all settings |

## ⚙️ Configuration

The `config.json` file allows you to customize all aspects of the processing:

### Key Settings

```json
{
  "processing_settings": {
    "expected_player_height": 140,     // Pixels per player row
    "players_per_chunk": 12,           // Players processed together
    "chunk_overlap_pixels": 20         // Overlap between chunks
  },
  
  "layout_settings": {
    "left_region_width_ratio": 0.7,    // 70% width for nicknames
    "right_region_width_ratio": 0.3     // 30% width for points
  },
  
  "ocr_settings": {
    "scale_factor": 2,                  // Image scaling for OCR
    "contrast_enhancement": 1.5         // Contrast boost
  }
}
```

### Clan Size Categories

The tool automatically detects and adjusts for different clan sizes:

- **Small**: Up to 30 players (≤4,200px height)
- **Medium**: 30-50 players (≤7,000px height) 
- **Large**: 50-80 players (≤11,200px height)
- **Maximum**: 80-100 players (>11,200px height)

## 🖼️ Image Requirements

### Optimal Screenshot Format

- **Width**: 623px (2K monitor) or similar
- **Height**: Variable (up to ~14,000px for 100 players)
- **Layout**: Nicknames on left, points on right
- **Quality**: High resolution, avoid scaling down
- **Format**: PNG, JPG, JPEG, BMP, or TIFF

### Example Layout

```
[K178] PlayerName1          215,600 points
[K179] PlayerName2          204,205 points
[K180] PlayerName3          196,570 points
...
```

## 🔧 Troubleshooting

### Common Issues

**1. "Tesseract not found"**
- Install Tesseract OCR for your operating system
- Ensure it's in your system PATH

**2. "No player data extracted"**
- Check image layout (nicknames left, points right)
- Verify image quality and resolution
- Enable debug mode to see OCR output
- Adjust `left_region_width_ratio` in config.json

**3. "Memory issues with large images"**
- Reduce `scale_factor` in config.json
- Decrease `players_per_chunk` 
- Ensure you have sufficient RAM (8GB+ recommended)

**4. "Nicknames not recognized correctly"**
- Check debug images to see OCR processing
- Adjust OCR character whitelist in config.json
- Increase `scale_factor` for better text recognition

### Debug Mode

Enable debug mode in config.json to:
- See detailed OCR output for each chunk
- Save intermediate processed images
- Track nickname/point matching process

```json
{
  "processing_settings": {
    "debug_mode": true,
    "save_debug_images": true
  }
}
```

## 📊 Output

The tool generates:
- **CSV file**: Player nicknames and points
- **Debug images** (if enabled): Processed image chunks
- **Console output**: Processing progress and statistics

### Sample CSV Output

```csv
Nickname,Points
Spider Friend,215,600
Violent Violet,204,205
Akshat,196,570
Finde,190,960
```

## 🎛️ Advanced Usage

### Custom Configuration

Create a custom config file:

```bash
python run_large_extraction.py --config my_config.json my_image.png
```

### Batch Processing

Process multiple images:

```bash
for image in *.png; do
    python run_large_extraction.py --quick "$image" --output "${image%.*}_results.csv"
done
```

### Performance Optimization

For very large images (80-100 players):
1. Set `debug_mode: false` for faster processing
2. Reduce `scale_factor` to 1.5 or 2
3. Increase `chunk_overlap_pixels` to 30-40
4. Ensure sufficient system RAM

## 🔄 Comparison with Original Script

| Feature | Original Script | Large Screenshot Script |
|---------|----------------|------------------------|
| Max Image Size | ~2,000px height | ~14,000px height |
| Memory Usage | High (full image) | Low (chunked processing) |
| Processing Speed | Fast for small images | Optimized for large images |
| Accuracy | Good for clear text | Better region-based matching |
| Configuration | Hardcoded | JSON-configurable |
| Debug Support | Basic | Comprehensive |

## 💡 Tips for Best Results

1. **Take high-quality screenshots** - Don't scale down before processing
2. **Ensure clear text** - Avoid blurry or low-contrast images
3. **Check layout consistency** - Nicknames left, points right throughout
4. **Use debug mode first** - Verify OCR accuracy before bulk processing
5. **Adjust for your game** - Clan tag format may need tweaking in regex patterns
6. **Monitor memory usage** - Very large images need sufficient RAM

## 🆘 Support

If you encounter issues:

1. Run with `--check-deps` to verify installation
2. Enable debug mode to see detailed processing
3. Check the generated debug images
4. Adjust config.json settings for your specific image format
5. Ensure your screenshot matches the expected layout

The tool is designed to handle the specific case of very large clan screenshots (623px × 11302px) where traditional OCR approaches fail due to memory constraints or poor region handling.