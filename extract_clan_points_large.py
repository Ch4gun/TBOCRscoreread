#!/usr/bin/env python3
"""
Large Image Clan Points OCR Extractor
Enhanced version that handles large clan member lists without size errors
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pandas as pd
import re
import os
import sys
import cv2
import numpy as np
import platform

# Configuration
INPUT_IMAGE = "points.jpg"
OUTPUT_CSV = "clan_points.csv"
DEBUG_MODE = True

# Tesseract size limits (approximate)
MAX_TESSERACT_WIDTH = 8000
MAX_TESSERACT_HEIGHT = 8000
MAX_TESSERACT_PIXELS = 40000000  # ~40 megapixels

def configure_tesseract():
    """Configure Tesseract executable path based on the operating system"""
    system = platform.system().lower()
    
    if system == "windows":
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
            r"C:\tesseract\tesseract.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"🔧 Found Tesseract at: {path}")
                return True
        
        try:
            pytesseract.get_tesseract_version()
            print("🔧 Using Tesseract from system PATH")
            return True
        except:
            print("❌ Tesseract not found. Please install Tesseract OCR")
            return False
    
    else:  # Linux/Mac
        try:
            pytesseract.get_tesseract_version()
            print("🔧 Using Tesseract from system PATH")
            return True
        except:
            print("❌ Tesseract not found. Install with: sudo apt install tesseract-ocr")
            return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    missing = []
    try:
        import cv2
        print("✅ OpenCV available")
    except ImportError:
        missing.append("opencv-python")
    
    try:
        import pandas
        print("✅ Pandas available")
    except ImportError:
        missing.append("pandas")
    
    try:
        from PIL import Image
        print("✅ PIL available")
    except ImportError:
        missing.append("pillow")
    
    if not configure_tesseract():
        missing.append("tesseract-ocr")
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        return False
    
    return True

def calculate_safe_scaling(width, height):
    """Calculate safe scaling factor to avoid Tesseract size limits"""
    print(f"📏 Original image size: {width}x{height}")
    
    # Calculate different scaling factors
    scale_factors = [4, 3, 2, 1.5, 1]
    
    for scale in scale_factors:
        new_width = int(width * scale)
        new_height = int(height * scale)
        total_pixels = new_width * new_height
        
        if (new_width <= MAX_TESSERACT_WIDTH and 
            new_height <= MAX_TESSERACT_HEIGHT and 
            total_pixels <= MAX_TESSERACT_PIXELS):
            print(f"🔧 Using {scale}x scaling -> {new_width}x{new_height}")
            return scale
    
    print("⚠️ Image too large even at 1x - will use chunk processing")
    return 1

def enhanced_preprocess_image(image_path):
    """Enhanced image preprocessing with automatic size management"""
    print(f"📷 Processing image: {image_path}")
    
    # Load with OpenCV
    img_cv = cv2.imread(image_path)
    if img_cv is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Get original dimensions
    original_height, original_width = img_cv.shape[:2]
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Apply preprocessing techniques
    # 1. Denoise
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # 2. Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # 3. Apply adaptive threshold
    thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Convert to PIL
    pil_image = Image.fromarray(thresh)
    width, height = pil_image.size
    
    # Calculate safe scaling factor
    scale_factor = calculate_safe_scaling(width, height)
    
    # Apply scaling
    if scale_factor > 1:
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"✅ Image scaled to: {new_width}x{new_height}")
    
    # Apply sharpening only if image isn't too large
    if scale_factor >= 2:
        pil_image = pil_image.filter(ImageFilter.SHARPEN)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(2.5)
    else:
        # For large images, use lighter processing
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.8)
    
    if DEBUG_MODE:
        pil_image.save("debug_processed.png")
        print("🔧 Saved processed image as debug_processed.png")
    
    return pil_image

def extract_with_chunking(img):
    """Process large images in chunks if necessary"""
    width, height = img.size
    total_pixels = width * height
    
    # If image is still too large, process in horizontal chunks
    if total_pixels > MAX_TESSERACT_PIXELS or height > MAX_TESSERACT_HEIGHT:
        print(f"🔄 Image too large ({width}x{height}), processing in chunks...")
        return extract_in_chunks(img)
    else:
        return extract_with_multiple_configs(img)

def extract_in_chunks(img):
    """Extract text by processing image in horizontal chunks"""
    width, height = img.size
    chunk_height = min(MAX_TESSERACT_HEIGHT - 100, height // 3)  # Process in 3 chunks with overlap
    overlap = 50  # Overlap between chunks to avoid cutting words
    
    all_text = []
    y_pos = 0
    
    while y_pos < height:
        # Calculate chunk boundaries
        chunk_start = max(0, y_pos - overlap)
        chunk_end = min(height, y_pos + chunk_height + overlap)
        
        # Extract chunk
        chunk = img.crop((0, chunk_start, width, chunk_end))
        
        print(f"🔍 Processing chunk: y={chunk_start}-{chunk_end}")
        
        # Process chunk with simpler config to avoid issues
        try:
            config = r'--oem 3 --psm 4'
            text = pytesseract.image_to_string(chunk, config=config)
            all_text.append(text)
            if DEBUG_MODE:
                print(f"   Chunk text length: {len(text)} chars")
        except Exception as e:
            print(f"   ⚠️ Chunk failed: {e}")
            # Try with even simpler config
            try:
                config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(chunk, config=config)
                all_text.append(text)
            except:
                print(f"   ❌ Chunk completely failed")
        
        y_pos += chunk_height
    
    combined_text = '\n'.join(all_text)
    print(f"✅ Processed {len(all_text)} chunks, total text: {len(combined_text)} chars")
    return combined_text

def extract_with_multiple_configs(img):
    """Try multiple OCR configurations for normal-sized images"""
    configs = [
        r'--oem 3 --psm 4',  # Assume a single column of text of variable sizes
        r'--oem 3 --psm 6',  # Uniform block of text
        r'--oem 1 --psm 4',  # LSTM engine
    ]
    
    all_text = []
    for config in configs:
        try:
            text = pytesseract.image_to_string(img, config=config)
            all_text.append(text)
            if DEBUG_MODE:
                print(f"✅ Config {config}: {len(text)} chars extracted")
        except Exception as e:
            if DEBUG_MODE:
                print(f"⚠️ Config {config} failed: {e}")
            continue
    
    if not all_text:
        print("❌ All OCR configurations failed!")
        return ""
    
    # Combine all results
    combined_text = '\n'.join(all_text)
    return combined_text

def extract_all_players_and_points(img):
    """Extract all players and points from potentially large clan list"""
    print("🔍 Running OCR extraction for large clan list...")
    
    # Get OCR text (with chunking if necessary)
    text = extract_with_chunking(img)
    
    if not text.strip():
        print("❌ No text extracted from image")
        return []
    
    if DEBUG_MODE:
        print("----- COMBINED OCR OUTPUT -----")
        print(text[:1000] + ("..." if len(text) > 1000 else ""))  # Show first 1000 chars
        print("-------------------------------")
    
    # Find all potential player names and points
    results = []
    
    # Enhanced point extraction with multiple patterns
    found_points = set()
    
    # Pattern 1: Standard comma-separated numbers
    pattern1 = r'(\d{1,3}[,\.]\d{3}[,\.]*\d{0,3})'
    for match in re.finditer(pattern1, text):
        clean = re.sub(r'[^\d]', '', match.group(1))
        if clean and len(clean) >= 4:  # At least 4 digits
            try:
                num = int(clean)
                if 1000 <= num <= 999999:  # Broader range for clan points
                    found_points.add(num)
            except ValueError:
                pass
    
    # Pattern 2: Just numbers
    pattern2 = r'\b(\d{4,7})\b'
    for match in re.finditer(pattern2, text):
        try:
            num = int(match.group(1))
            if 1000 <= num <= 999999:
                found_points.add(num)
        except ValueError:
            pass
    
    found_points = sorted(list(found_points), reverse=True)  # Sort highest to lowest
    
    if DEBUG_MODE:
        print(f"📊 Found {len(found_points)} potential point values")
        print(f"Top 10 points: {found_points[:10]}")
    
    # Extract player names - look for lines that contain both name and points
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for lines with both text and numbers
        numbers_in_line = re.findall(r'\d{4,7}', line)
        if numbers_in_line:
            # Extract the name part (text before/after numbers)
            name_part = re.sub(r'\d+[,\.\s]*\d*', '', line).strip()
            name_part = re.sub(r'[^\w\s]', ' ', name_part).strip()
            
            if name_part and len(name_part) > 2:  # Valid name
                # Find the best matching points for this line
                line_numbers = [int(re.sub(r'[^\d]', '', num)) for num in numbers_in_line 
                              if re.sub(r'[^\d]', '', num).isdigit()]
                
                for num in line_numbers:
                    if 1000 <= num <= 999999:
                        results.append((name_part, f"{num:,}"))
                        if DEBUG_MODE:
                            print(f"✅ Found: {name_part} -> {num:,}")
                        break
    
    # Remove duplicates while preserving order
    seen_names = set()
    unique_results = []
    for name, points in results:
        if name.lower() not in seen_names:
            seen_names.add(name.lower())
            unique_results.append((name, points))
    
    print(f"📋 Extracted {len(unique_results)} unique player records")
    return unique_results

def save_to_csv(data, filename):
    """Save extracted data to CSV file"""
    if not data:
        print("❌ No data to save")
        return False
    
    try:
        df = pd.DataFrame(data, columns=["Name", "Points"])
        df.to_csv(filename, index=False)
        print(f"✅ Successfully saved {len(data)} entries to '{filename}'")
        return True
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
        return False

def main():
    """Main execution function"""
    print("🎯 LARGE IMAGE Clan Points OCR Extractor")
    print("=" * 50)
    
    if not check_dependencies():
        print("❌ Please install missing dependencies and try again")
        sys.exit(1)
    
    try:
        # Check if input image exists
        if not os.path.exists(INPUT_IMAGE):
            print(f"❌ Image file '{INPUT_IMAGE}' not found")
            print("💡 Make sure the image file is in the current directory")
            sys.exit(1)
        
        # Process image and extract data
        processed_img = enhanced_preprocess_image(INPUT_IMAGE)
        extracted_data = extract_all_players_and_points(processed_img)
        
        if extracted_data:
            print(f"\n📊 Extracted {len(extracted_data)} player records:")
            for i, (name, points) in enumerate(extracted_data[:10]):  # Show first 10
                print(f"  {i+1:2d}. {name}: {points}")
            
            if len(extracted_data) > 10:
                print(f"  ... and {len(extracted_data) - 10} more players")
            
            if save_to_csv(extracted_data, OUTPUT_CSV):
                print(f"\n🎉 Process completed successfully!")
                print(f"📄 Results saved to: {OUTPUT_CSV}")
                print(f"📊 Total players extracted: {len(extracted_data)}")
            else:
                print("\n❌ Failed to save results")
        else:
            print("\n⚠️ No player data found. Possible issues:")
            print("  • Image quality might be too low")
            print("  • Text format doesn't match expected patterns")
            print("  • Try adjusting the DEBUG_MODE to see OCR output")
            print(f"\n💡 Check the 'debug_processed.png' file to see how the image was processed")
    
    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
        print(f"💡 Make sure '{INPUT_IMAGE}' exists in the current directory")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n📄 Check '{OUTPUT_CSV}' for results!")
        print(f"🔧 Check 'debug_processed.png' to see how the image was processed")

if __name__ == "__main__":
    main()