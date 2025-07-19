#!/usr/bin/env python3
"""
Large Clan Screenshot OCR Extractor
Designed for handling very large screenshots (e.g., 623px × 11302px for 80-100 players)
Processes the image in regions to extract nicknames (left) and points (right) accurately
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import pandas as pd
import re
import os
import sys
import cv2
import numpy as np
import platform
from typing import List, Tuple, Optional
import json

# Configuration
INPUT_IMAGE = "points.jpg"
OUTPUT_CSV = "clan_points.csv"
DEBUG_MODE = True
SAVE_DEBUG_IMAGES = True

# Layout parameters for large screenshots
EXPECTED_PLAYER_HEIGHT = 140  # Approximate height per player row in pixels
LEFT_REGION_WIDTH_RATIO = 0.7  # 70% of width for nickname area
RIGHT_REGION_WIDTH_RATIO = 0.3  # 30% of width for points area
MIN_OVERLAP = 20  # Pixels of overlap between processing chunks

class LargeClanOCR:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.original_image = None
        self.image_width = 0
        self.image_height = 0
        self.players_data = []
        
    def configure_tesseract(self) -> bool:
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
                print("❌ Tesseract not found. Please install Tesseract OCR:")
                print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
                return False
        
        elif system in ["linux", "darwin"]:
            try:
                pytesseract.get_tesseract_version()
                print("🔧 Using Tesseract from system PATH")
                return True
            except:
                if system == "linux":
                    print("❌ Tesseract not found. Install with: sudo apt-get install tesseract-ocr")
                else:
                    print("❌ Tesseract not found. Install with: brew install tesseract")
                return False
        
        return True

    def load_and_analyze_image(self) -> bool:
        """Load the image and analyze its dimensions"""
        if not os.path.exists(self.image_path):
            print(f"❌ Image file '{self.image_path}' not found")
            return False
        
        try:
            self.original_image = Image.open(self.image_path)
            self.image_width, self.image_height = self.original_image.size
            
            print(f"📷 Loaded image: {self.image_width}x{self.image_height} pixels")
            print(f"📊 Estimated players: {self.image_height // EXPECTED_PLAYER_HEIGHT}")
            
            return True
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return False

    def preprocess_region(self, region_image: Image.Image, region_type: str = "general") -> Image.Image:
        """Preprocess a specific region for optimal OCR"""
        # Convert to OpenCV format
        img_array = np.array(region_image)
        if len(img_array.shape) == 3:
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_cv = img_array
        
        # Convert to grayscale
        if len(img_cv.shape) == 3:
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_cv
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Different preprocessing for nicknames vs points
        if region_type == "nickname":
            # For nicknames, use adaptive threshold to handle varying text styles
            thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
        else:  # points
            # For points, use simple threshold as numbers are usually more uniform
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL
        pil_image = Image.fromarray(thresh)
        
        # Scale up for better OCR (2x for large images to avoid memory issues)
        width, height = pil_image.size
        scale_factor = 2
        pil_image = pil_image.resize((width * scale_factor, height * scale_factor), Image.Resampling.LANCZOS)
        
        # Apply sharpening
        pil_image = pil_image.filter(ImageFilter.SHARPEN)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.5)
        
        return pil_image

    def extract_from_region(self, region_image: Image.Image, region_type: str, chunk_index: int = 0) -> List[str]:
        """Extract text from a specific region using appropriate OCR settings"""
        processed_region = self.preprocess_region(region_image, region_type)
        
        if SAVE_DEBUG_IMAGES:
            debug_filename = f"debug_{region_type}_chunk_{chunk_index}.png"
            processed_region.save(debug_filename)
            if DEBUG_MODE:
                print(f"🔧 Saved debug image: {debug_filename}")
        
        # OCR configuration based on region type
        if region_type == "nickname":
            # For nicknames, expect mixed case text with special characters
            config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]{}()_- '
        else:  # points
            # For points, expect numbers, commas, and "points" text
            config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789,points '
        
        try:
            text = pytesseract.image_to_string(processed_region, config=config)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            
            if DEBUG_MODE:
                print(f"\n--- {region_type.upper()} OCR CHUNK {chunk_index} ---")
                for i, line in enumerate(lines):
                    print(f"{i+1}: '{line}'")
                print("---" + "-" * len(f"{region_type.upper()} OCR CHUNK {chunk_index}") + "---")
            
            return lines
        except Exception as e:
            print(f"⚠️ OCR failed for {region_type} chunk {chunk_index}: {e}")
            return []

    def process_large_image(self) -> List[Tuple[str, str]]:
        """Process the large image in chunks to extract player data"""
        print("🔍 Processing large image in chunks...")
        
        # Calculate chunk size (process ~10-15 players at a time to manage memory)
        chunk_height = EXPECTED_PLAYER_HEIGHT * 12
        left_region_width = int(self.image_width * LEFT_REGION_WIDTH_RATIO)
        
        all_nicknames = []
        all_points = []
        
        # Process image in overlapping chunks
        y_position = 0
        chunk_index = 0
        
        while y_position < self.image_height:
            # Calculate chunk boundaries
            chunk_end = min(y_position + chunk_height, self.image_height)
            
            if DEBUG_MODE:
                print(f"\n📍 Processing chunk {chunk_index}: y={y_position} to {chunk_end}")
            
            # Extract nickname region (left side)
            nickname_region = self.original_image.crop((0, y_position, left_region_width, chunk_end))
            nickname_lines = self.extract_from_region(nickname_region, "nickname", chunk_index)
            
            # Extract points region (right side)
            points_region = self.original_image.crop((left_region_width, y_position, self.image_width, chunk_end))
            points_lines = self.extract_from_region(points_region, "points", chunk_index)
            
            # Store results with chunk information
            all_nicknames.extend([(line, chunk_index, y_position) for line in nickname_lines])
            all_points.extend([(line, chunk_index, y_position) for line in points_lines])
            
            # Move to next chunk with overlap
            y_position = chunk_end - MIN_OVERLAP
            chunk_index += 1
            
            # Safety check to prevent infinite loop
            if chunk_index > 100:
                print("⚠️ Too many chunks, stopping to prevent infinite loop")
                break
        
        # Match nicknames with points
        matched_players = self.match_nicknames_with_points(all_nicknames, all_points)
        
        return matched_players

    def clean_nickname(self, raw_name: str) -> Optional[str]:
        """Clean and validate a nickname"""
        # Remove common OCR artifacts and normalize
        cleaned = re.sub(r'[^\w\s\[\]{}()_-]', ' ', raw_name)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Look for clan tag patterns like [K178]
        clan_tag_match = re.search(r'\[K?\d+\]', cleaned)
        if clan_tag_match:
            # Extract everything after the clan tag
            after_tag = cleaned[clan_tag_match.end():].strip()
            if after_tag:
                # Keep only the first 2-3 words as the actual nickname
                words = after_tag.split()
                if len(words) >= 1:
                    return ' '.join(words[:3])
        
        # If no clan tag, look for recognizable nickname patterns
        # Remove numbers at the beginning/end that might be OCR artifacts
        cleaned = re.sub(r'^\d+\s*', '', cleaned)
        cleaned = re.sub(r'\s*\d+$', '', cleaned)
        
        # Must have at least 2 characters and contain letters
        if len(cleaned) >= 2 and re.search(r'[a-zA-Z]', cleaned):
            words = cleaned.split()
            return ' '.join(words[:3])  # Max 3 words
        
        return None

    def clean_points(self, raw_points: str) -> Optional[str]:
        """Clean and validate points value"""
        # Look for number patterns with optional commas
        points_match = re.search(r'(\d{1,3}(?:,\d{3})*)', raw_points)
        if points_match:
            points_str = points_match.group(1)
            try:
                # Validate it's a reasonable points value (1,000 to 999,999)
                points_num = int(points_str.replace(',', ''))
                if 1000 <= points_num <= 999999:
                    return points_str
            except ValueError:
                pass
        return None

    def match_nicknames_with_points(self, nicknames: List[Tuple[str, int, int]], 
                                   points: List[Tuple[str, int, int]]) -> List[Tuple[str, str]]:
        """Match nicknames with their corresponding points based on position"""
        print("🔗 Matching nicknames with points...")
        
        # Clean and organize data
        clean_nicknames = []
        for raw_name, chunk_idx, y_pos in nicknames:
            clean_name = self.clean_nickname(raw_name)
            if clean_name:
                clean_nicknames.append((clean_name, chunk_idx, y_pos))
        
        clean_points = []
        for raw_points, chunk_idx, y_pos in points:
            clean_pts = self.clean_points(raw_points)
            if clean_pts:
                clean_points.append((clean_pts, chunk_idx, y_pos))
        
        if DEBUG_MODE:
            print(f"\n📋 Found {len(clean_nicknames)} valid nicknames and {len(clean_points)} valid points")
            print("Nicknames:", [name for name, _, _ in clean_nicknames[:10]])
            print("Points:", [pts for pts, _, _ in clean_points[:10]])
        
        # Match by proximity (same chunk or adjacent chunks, similar y-position)
        matched_pairs = []
        used_points = set()
        
        for name, name_chunk, name_y in clean_nicknames:
            best_match = None
            best_distance = float('inf')
            
            for i, (points_val, points_chunk, points_y) in enumerate(clean_points):
                if i in used_points:
                    continue
                
                # Calculate distance (prefer same chunk, but allow adjacent chunks)
                chunk_distance = abs(name_chunk - points_chunk)
                y_distance = abs(name_y - points_y)
                
                # Total distance (weight chunk distance more heavily)
                total_distance = (chunk_distance * 1000) + y_distance
                
                # Only consider matches within reasonable range
                if chunk_distance <= 1 and y_distance <= chunk_height:
                    if total_distance < best_distance:
                        best_distance = total_distance
                        best_match = (points_val, i)
            
            if best_match:
                points_val, points_idx = best_match
                matched_pairs.append((name, points_val))
                used_points.add(points_idx)
                
                if DEBUG_MODE:
                    print(f"✅ Matched: {name} -> {points_val}")
        
        return matched_pairs

    def save_results(self, data: List[Tuple[str, str]]) -> bool:
        """Save results to CSV file"""
        if not data:
            print("❌ No data to save")
            return False
        
        try:
            df = pd.DataFrame(data, columns=["Nickname", "Points"])
            df.to_csv(OUTPUT_CSV, index=False)
            print(f"✅ Successfully saved {len(data)} players to '{OUTPUT_CSV}'")
            
            # Display results
            print("\n📊 Extracted Player Data:")
            print(df.to_string(index=False))
            
            return True
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return False

    def run(self) -> bool:
        """Main processing pipeline"""
        print("🎯 Large Clan Screenshot OCR Extractor")
        print("=" * 50)
        
        # Setup
        if not self.configure_tesseract():
            return False
        
        if not self.load_and_analyze_image():
            return False
        
        # Process
        try:
            players_data = self.process_large_image()
            
            if players_data:
                print(f"\n🎉 Successfully extracted {len(players_data)} players!")
                return self.save_results(players_data)
            else:
                print("\n⚠️ No player data extracted. Check:")
                print("  • Image quality and resolution")
                print("  • Player list format (nicknames on left, points on right)")
                print("  • Debug images for OCR issues")
                return False
                
        except Exception as e:
            print(f"❌ Processing error: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Entry point"""
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = INPUT_IMAGE
    
    extractor = LargeClanOCR(image_path)
    success = extractor.run()
    
    if success:
        print(f"\n✨ Process completed! Check '{OUTPUT_CSV}' for results.")
    else:
        print("\n❌ Process failed. Check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())