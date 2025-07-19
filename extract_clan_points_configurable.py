#!/usr/bin/env python3
"""
Configurable Large Clan Screenshot OCR Extractor
Loads settings from config.json and auto-adjusts for different clan sizes
Designed for handling very large screenshots (e.g., 623px × 11302px for 80-100 players)
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
import json
from typing import List, Tuple, Optional, Dict, Any

class ConfigurableClanOCR:
    def __init__(self, image_path: str, config_path: str = "config.json"):
        self.image_path = image_path
        self.config_path = config_path
        self.config = self.load_config()
        self.original_image = None
        self.image_width = 0
        self.image_height = 0
        self.estimated_players = 0
        self.clan_size_category = "medium"
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Loaded configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            print(f"⚠️ Config file {self.config_path} not found, using defaults")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            print("Using default configuration")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if config file is not available"""
        return {
            "image_settings": {
                "input_image": "points.jpg",
                "output_csv": "clan_points.csv"
            },
            "processing_settings": {
                "debug_mode": True,
                "save_debug_images": True,
                "expected_player_height": 140,
                "chunk_overlap_pixels": 20,
                "players_per_chunk": 12
            },
            "layout_settings": {
                "left_region_width_ratio": 0.7,
                "right_region_width_ratio": 0.3
            },
            "ocr_settings": {
                "nickname_config": "--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]{}()_- ",
                "points_config": "--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789,points ",
                "scale_factor": 2,
                "contrast_enhancement": 1.5
            },
            "validation_settings": {
                "min_points": 1000,
                "max_points": 999999,
                "min_nickname_length": 2,
                "max_nickname_words": 3
            }
        }

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

    def determine_clan_size_category(self) -> str:
        """Determine clan size category based on image dimensions"""
        if "clan_sizes" not in self.config:
            return "large"  # Default fallback
        
        clan_sizes = self.config["clan_sizes"]
        
        if self.image_height <= clan_sizes.get("small", {}).get("expected_height", 4200):
            return "small"
        elif self.image_height <= clan_sizes.get("medium", {}).get("expected_height", 7000):
            return "medium"
        elif self.image_height <= clan_sizes.get("large", {}).get("expected_height", 11200):
            return "large"
        else:
            return "maximum"

    def load_and_analyze_image(self) -> bool:
        """Load the image and analyze its dimensions"""
        if not os.path.exists(self.image_path):
            print(f"❌ Image file '{self.image_path}' not found")
            return False
        
        try:
            self.original_image = Image.open(self.image_path)
            self.image_width, self.image_height = self.original_image.size
            
            # Estimate number of players
            expected_height = self.config["processing_settings"]["expected_player_height"]
            self.estimated_players = self.image_height // expected_height
            
            # Determine clan size category
            self.clan_size_category = self.determine_clan_size_category()
            
            print(f"📷 Loaded image: {self.image_width}x{self.image_height} pixels")
            print(f"📊 Estimated players: {self.estimated_players}")
            print(f"🏆 Clan size category: {self.clan_size_category}")
            
            if "clan_sizes" in self.config and self.clan_size_category in self.config["clan_sizes"]:
                category_info = self.config["clan_sizes"][self.clan_size_category]
                print(f"📋 Category info: {category_info['description']}")
            
            return True
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return False

    def auto_adjust_settings(self):
        """Auto-adjust processing settings based on image size and clan category"""
        # Adjust chunk size based on clan size
        if self.clan_size_category == "small":
            self.config["processing_settings"]["players_per_chunk"] = 15
        elif self.clan_size_category == "medium":
            self.config["processing_settings"]["players_per_chunk"] = 12
        elif self.clan_size_category == "large":
            self.config["processing_settings"]["players_per_chunk"] = 10
        else:  # maximum
            self.config["processing_settings"]["players_per_chunk"] = 8
        
        # Adjust scale factor for very large images to prevent memory issues
        if self.image_height > 10000:
            if self.config["ocr_settings"]["scale_factor"] > 2:
                self.config["ocr_settings"]["scale_factor"] = 2
                print("📉 Reduced scale factor to 2 for large image")
        
        # Adjust overlap for better matching in large clans
        if self.clan_size_category in ["large", "maximum"]:
            self.config["processing_settings"]["chunk_overlap_pixels"] = 30
        
        print(f"⚙️ Auto-adjusted settings for {self.clan_size_category} clan")

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
            thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
        else:  # points
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL
        pil_image = Image.fromarray(thresh)
        
        # Scale up for better OCR
        width, height = pil_image.size
        scale_factor = self.config["ocr_settings"]["scale_factor"]
        pil_image = pil_image.resize((width * scale_factor, height * scale_factor), Image.Resampling.LANCZOS)
        
        # Apply sharpening
        pil_image = pil_image.filter(ImageFilter.SHARPEN)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        contrast_value = self.config["ocr_settings"]["contrast_enhancement"]
        pil_image = enhancer.enhance(contrast_value)
        
        return pil_image

    def extract_from_region(self, region_image: Image.Image, region_type: str, chunk_index: int = 0) -> List[str]:
        """Extract text from a specific region using appropriate OCR settings"""
        processed_region = self.preprocess_region(region_image, region_type)
        
        if self.config["processing_settings"]["save_debug_images"]:
            debug_filename = f"debug_{region_type}_chunk_{chunk_index}.png"
            processed_region.save(debug_filename)
            if self.config["processing_settings"]["debug_mode"]:
                print(f"🔧 Saved debug image: {debug_filename}")
        
        # Get OCR configuration from config
        if region_type == "nickname":
            config = self.config["ocr_settings"]["nickname_config"]
        else:  # points
            config = self.config["ocr_settings"]["points_config"]
        
        try:
            text = pytesseract.image_to_string(processed_region, config=config)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            
            if self.config["processing_settings"]["debug_mode"]:
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
        
        # Get settings from config
        expected_height = self.config["processing_settings"]["expected_player_height"]
        players_per_chunk = self.config["processing_settings"]["players_per_chunk"]
        overlap_pixels = self.config["processing_settings"]["chunk_overlap_pixels"]
        left_width_ratio = self.config["layout_settings"]["left_region_width_ratio"]
        
        chunk_height = expected_height * players_per_chunk
        left_region_width = int(self.image_width * left_width_ratio)
        
        all_nicknames = []
        all_points = []
        
        # Process image in overlapping chunks
        y_position = 0
        chunk_index = 0
        
        while y_position < self.image_height:
            chunk_end = min(y_position + chunk_height, self.image_height)
            
            if self.config["processing_settings"]["debug_mode"]:
                print(f"\n📍 Processing chunk {chunk_index}: y={y_position} to {chunk_end}")
            
            # Extract regions
            nickname_region = self.original_image.crop((0, y_position, left_region_width, chunk_end))
            nickname_lines = self.extract_from_region(nickname_region, "nickname", chunk_index)
            
            points_region = self.original_image.crop((left_region_width, y_position, self.image_width, chunk_end))
            points_lines = self.extract_from_region(points_region, "points", chunk_index)
            
            # Store results with position info
            all_nicknames.extend([(line, chunk_index, y_position) for line in nickname_lines])
            all_points.extend([(line, chunk_index, y_position) for line in points_lines])
            
            # Move to next chunk
            y_position = chunk_end - overlap_pixels
            chunk_index += 1
            
            # Safety check
            if chunk_index > 100:
                print("⚠️ Too many chunks, stopping to prevent infinite loop")
                break
        
        # Match nicknames with points
        matched_players = self.match_nicknames_with_points(all_nicknames, all_points)
        
        return matched_players

    def clean_nickname(self, raw_name: str) -> Optional[str]:
        """Clean and validate a nickname based on config settings"""
        cleaned = re.sub(r'[^\w\s\[\]{}()_-]', ' ', raw_name)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Look for clan tag patterns
        clan_tag_match = re.search(r'\[K?\d+\]', cleaned)
        if clan_tag_match:
            after_tag = cleaned[clan_tag_match.end():].strip()
            if after_tag:
                words = after_tag.split()
                if len(words) >= 1:
                    max_words = self.config["validation_settings"]["max_nickname_words"]
                    return ' '.join(words[:max_words])
        
        # Remove number artifacts
        cleaned = re.sub(r'^\d+\s*', '', cleaned)
        cleaned = re.sub(r'\s*\d+$', '', cleaned)
        
        min_length = self.config["validation_settings"]["min_nickname_length"]
        if len(cleaned) >= min_length and re.search(r'[a-zA-Z]', cleaned):
            words = cleaned.split()
            max_words = self.config["validation_settings"]["max_nickname_words"]
            return ' '.join(words[:max_words])
        
        return None

    def clean_points(self, raw_points: str) -> Optional[str]:
        """Clean and validate points value based on config settings"""
        points_match = re.search(r'(\d{1,3}(?:,\d{3})*)', raw_points)
        if points_match:
            points_str = points_match.group(1)
            try:
                points_num = int(points_str.replace(',', ''))
                min_pts = self.config["validation_settings"]["min_points"]
                max_pts = self.config["validation_settings"]["max_points"]
                if min_pts <= points_num <= max_pts:
                    return points_str
            except ValueError:
                pass
        return None

    def match_nicknames_with_points(self, nicknames: List[Tuple[str, int, int]], 
                                   points: List[Tuple[str, int, int]]) -> List[Tuple[str, str]]:
        """Match nicknames with their corresponding points based on position"""
        print("🔗 Matching nicknames with points...")
        
        # Clean data
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
        
        if self.config["processing_settings"]["debug_mode"]:
            print(f"\n📋 Found {len(clean_nicknames)} valid nicknames and {len(clean_points)} valid points")
            print("Nicknames:", [name for name, _, _ in clean_nicknames[:10]])
            print("Points:", [pts for pts, _, _ in clean_points[:10]])
        
        # Match by proximity
        matched_pairs = []
        used_points = set()
        chunk_height = (self.config["processing_settings"]["expected_player_height"] * 
                       self.config["processing_settings"]["players_per_chunk"])
        
        for name, name_chunk, name_y in clean_nicknames:
            best_match = None
            best_distance = float('inf')
            
            for i, (points_val, points_chunk, points_y) in enumerate(clean_points):
                if i in used_points:
                    continue
                
                chunk_distance = abs(name_chunk - points_chunk)
                y_distance = abs(name_y - points_y)
                total_distance = (chunk_distance * 1000) + y_distance
                
                if chunk_distance <= 1 and y_distance <= chunk_height:
                    if total_distance < best_distance:
                        best_distance = total_distance
                        best_match = (points_val, i)
            
            if best_match:
                points_val, points_idx = best_match
                matched_pairs.append((name, points_val))
                used_points.add(points_idx)
                
                if self.config["processing_settings"]["debug_mode"]:
                    print(f"✅ Matched: {name} -> {points_val}")
        
        return matched_pairs

    def save_results(self, data: List[Tuple[str, str]]) -> bool:
        """Save results to CSV file"""
        if not data:
            print("❌ No data to save")
            return False
        
        try:
            output_file = self.config["image_settings"]["output_csv"]
            df = pd.DataFrame(data, columns=["Nickname", "Points"])
            df.to_csv(output_file, index=False)
            print(f"✅ Successfully saved {len(data)} players to '{output_file}'")
            
            # Display results
            print("\n📊 Extracted Player Data:")
            print(df.to_string(index=False))
            
            return True
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return False

    def run(self) -> bool:
        """Main processing pipeline"""
        print("🎯 Configurable Large Clan Screenshot OCR Extractor")
        print("=" * 60)
        
        # Setup
        if not self.configure_tesseract():
            return False
        
        if not self.load_and_analyze_image():
            return False
        
        # Auto-adjust settings
        self.auto_adjust_settings()
        
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
                print("  • Config.json settings")
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
        # Try to get from config, fallback to default
        try:
            with open("config.json", 'r') as f:
                config = json.load(f)
            image_path = config["image_settings"]["input_image"]
        except:
            image_path = "points.jpg"
    
    extractor = ConfigurableClanOCR(image_path)
    success = extractor.run()
    
    if success:
        output_file = extractor.config["image_settings"]["output_csv"]
        print(f"\n✨ Process completed! Check '{output_file}' for results.")
    else:
        print("\n❌ Process failed. Check the error messages above.")
        print("💡 Try adjusting settings in config.json for better results.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())