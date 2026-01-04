import easyocr
import gc # <--- Memory management
import os

def extract_text_from_image(image_path):
    """
    Extracts text from an image using EasyOCR.
    Optimized for low-RAM environments.
    """
    if not os.path.exists(image_path):
        return ""

    reader = None
    text = ""

    try:
        print("⏳ Loading OCR Engine...")
        
        # Initialize EasyOCR reader for English
        # gpu=False is CRITICAL for Render free tier (no GPU available)
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        print("🔍 Scanning Image...")
        result = reader.readtext(image_path, detail=0) # detail=0 returns just the text list
        
        # Join extracted lines into a single string
        text = " ".join(result)
        print("✅ OCR Extraction Complete")

    except Exception as e:
        print(f"⚠️ OCR Failed: {e}")
        return ""

    finally:
        # --- AGGRESSIVE CLEANUP ---
        if reader:
            del reader
        
        gc.collect() # Force RAM release
        print("✅ OCR Engine Unloaded")

    return text