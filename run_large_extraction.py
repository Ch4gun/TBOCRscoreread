#!/usr/bin/env python3
"""
Simple runner for Large Clan Screenshot OCR Extractor
Provides easy command-line interface for processing large screenshots
"""

import sys
import os
import argparse
from extract_clan_points_configurable import ConfigurableClanOCR

def check_dependencies():
    """Check if required packages are available"""
    missing_packages = []
    
    try:
        import pytesseract
    except ImportError:
        missing_packages.append("pytesseract")
    
    try:
        import cv2
    except ImportError:
        missing_packages.append("opencv-python")
    
    try:
        import PIL
    except ImportError:
        missing_packages.append("Pillow")
    
    try:
        import pandas
    except ImportError:
        missing_packages.append("pandas")
    
    try:
        import numpy
    except ImportError:
        missing_packages.append("numpy")
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"  • {pkg}")
        print("\n💡 Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def print_banner():
    """Print application banner"""
    print("🎯 Large Clan Screenshot OCR Extractor")
    print("=" * 50)
    print("Designed for handling very large screenshots")
    print("(e.g., 623px × 11302px for 80-100 players)")
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description="Extract player nicknames and points from large clan screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_large_extraction.py                    # Use default image (points.jpg)
  python run_large_extraction.py my_clan.png        # Process specific image
  python run_large_extraction.py --quick my_clan.png # Quick mode (less debug output)
  python run_large_extraction.py --help             # Show this help

Supported image formats: PNG, JPG, JPEG, BMP, TIFF

For best results:
• Ensure nicknames are on the left side of the image
• Ensure points are on the right side of the image  
• Use high-quality screenshots (avoid scaling down)
• Clan tags should be in format [K123] or similar
        """
    )
    
    parser.add_argument(
        "image", 
        nargs="?", 
        default="points.jpg",
        help="Path to the clan screenshot image (default: points.jpg)"
    )
    
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Quick mode: disable debug output and intermediate images"
    )
    
    parser.add_argument(
        "--config", 
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    
    parser.add_argument(
        "--output", 
        help="Output CSV filename (overrides config setting)"
    )
    
    parser.add_argument(
        "--check-deps", 
        action="store_true",
        help="Check if all dependencies are installed"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check dependencies if requested
    if args.check_deps:
        print("\n🔍 Checking dependencies...")
        if check_dependencies():
            print("✅ All dependencies are installed!")
        return 0
    
    # Check dependencies before processing
    if not check_dependencies():
        return 1
    
    # Check if image file exists
    if not os.path.exists(args.image):
        print(f"❌ Image file '{args.image}' not found!")
        print("💡 Make sure the file path is correct and the file exists.")
        return 1
    
    # Get image info
    try:
        from PIL import Image
        with Image.open(args.image) as img:
            width, height = img.size
            print(f"\n📷 Image info:")
            print(f"   File: {args.image}")
            print(f"   Size: {width}x{height} pixels")
            print(f"   Format: {img.format}")
            
            # Estimate processing time
            if height > 10000:
                print("⏱️  Large image detected - processing may take 2-5 minutes")
            elif height > 5000:
                print("⏱️  Medium image - processing should take 1-2 minutes")
            else:
                print("⏱️  Small image - processing should be quick")
    except Exception as e:
        print(f"⚠️ Could not read image info: {e}")
    
    print(f"\n🚀 Starting extraction process...")
    
    try:
        # Create extractor instance
        extractor = ConfigurableClanOCR(args.image, args.config)
        
        # Apply quick mode settings
        if args.quick:
            extractor.config["processing_settings"]["debug_mode"] = False
            extractor.config["processing_settings"]["save_debug_images"] = False
            print("⚡ Quick mode enabled - reduced debug output")
        
        # Override output filename if specified
        if args.output:
            extractor.config["image_settings"]["output_csv"] = args.output
            print(f"📁 Output will be saved to: {args.output}")
        
        # Run extraction
        success = extractor.run()
        
        if success:
            output_file = extractor.config["image_settings"]["output_csv"]
            print(f"\n✨ SUCCESS! Results saved to: {output_file}")
            
            # Show file size and record count
            try:
                import pandas as pd
                df = pd.read_csv(output_file)
                print(f"📊 Extracted {len(df)} player records")
                
                if len(df) > 0:
                    print(f"📈 Points range: {df['Points'].min()} - {df['Points'].max()}")
            except:
                pass
            
            print("\n💡 Tips:")
            print("  • Check the CSV file for accuracy")
            print("  • If some nicknames are missing, try adjusting config.json")
            print("  • Debug images (if enabled) can help troubleshoot OCR issues")
            
        else:
            print("\n❌ FAILED! Check the error messages above.")
            print("\n🔧 Troubleshooting:")
            print("  • Ensure Tesseract OCR is installed")
            print("  • Check image quality and format")
            print("  • Verify nickname/points layout (left/right)")
            print("  • Try enabling debug mode to see OCR output")
            print("  • Adjust settings in config.json")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())