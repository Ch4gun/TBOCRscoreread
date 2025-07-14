import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pandas as pd
import re

# Path to Tesseract executable (update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Preprocess the image (grayscale, contrast, sharpen, resize)
def preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.resize((img.width * 2, img.height * 2))  # Upscale for better OCR
    img = img.convert("L")  # Grayscale
    img = img.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(3.0)  # Stronger contrast
    return img

# Extract names and points from OCR output
def extract_players_and_points(img):
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(img, config=custom_config)

    print("----- OCR OUTPUT -----")
    print(text)
    print("----------------------")

    lines = text.splitlines()
    results = []

    prev_name = None
    for line in lines:
        # Try to find a player name line like "[K178] Spider Friend"
        name_match = re.search(r'\[K\d+\]\s*(.+)', line)
        if name_match:
            raw_name = name_match.group(1)

            # Remove symbols and numbers
            cleaned_name = re.sub(r'[^A-Za-z\s]', '', raw_name).strip()

            # Keep max 2 words (avoid extras like "Yay", "(ay")
            words = cleaned_name.split()
            cleaned_name = ' '.join(words[:2])
            prev_name = cleaned_name
            continue

        # Try to find a points value like "215,600 points"
        points_match = re.search(r'(\d{1,3}(?:,\d{3})?)\s+points', line)
        if prev_name and points_match:
            points = points_match.group(1).strip()
            results.append((prev_name, points))
            prev_name = None

    return results

# Run it
if __name__ == "__main__":
    image_path = "points.jpg"  # Make sure your image is named this
    img = preprocess_image(image_path)
    data = extract_players_and_points(img)

    if data:
        df = pd.DataFrame(data, columns=["Name", "Points"])
        df.to_csv("clan_points.csv", index=False)
        print("✅ Done! Saved to 'clan_points.csv'")
        print(df)
    else:
        print("❌ No matches found. Check OCR output above to adjust regex if needed.")
