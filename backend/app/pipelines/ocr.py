import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import fitz  # PyMuPDF — for PDF OCR
import os

# ✅ Configure tesseract path if needed (uncomment if not in PATH)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess_image_for_ocr(image_path: str) -> Image.Image:
    """
    Preprocess the image to improve OCR accuracy:
    - Converts to grayscale
    - Removes noise and smooths edges
    - Increases contrast
    """
    try:
        img = Image.open(image_path).convert("L")  # grayscale
        img = img.filter(ImageFilter.MedianFilter())
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)
        return img
    except Exception as e:
        print(f"⚠️ OCR preprocessing failed for {image_path}: {e}")
        return Image.open(image_path)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from all pages of a PDF using OCR (image-based PDFs included).
    """
    text = ""
    try:
        pdf_doc = fitz.open(pdf_path)
        for page_number in range(len(pdf_doc)):
            page = pdf_doc.load_page(page_number)
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img)
            text += f"\n\n--- Page {page_number + 1} ---\n{page_text.strip()}"
        pdf_doc.close()
    except Exception as e:
        print(f"⚠️ PDF OCR failed for {pdf_path}: {e}")
    return text.strip()


def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from an image or PDF file using Tesseract OCR.
    Handles both JPG/PNG screenshots and scanned PDFs.
    """
    try:
        ext = os.path.splitext(image_path)[1].lower()

        # 🧾 PDF OCR
        if ext == ".pdf":
            return extract_text_from_pdf(image_path)

        # 🖼️ Image OCR with preprocessing
        img = preprocess_image_for_ocr(image_path)
        text = pytesseract.image_to_string(img)

        # 🧠 Optional fallback with OpenCV (for poor-quality images)
        if not text.strip():
            cv_img = cv2.imread(image_path)
            if cv_img is not None:
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                text = pytesseract.image_to_string(gray)

        return text.strip()

    except Exception as e:
        print(f"⚠️ OCR Error ({image_path}): {e}")
        return ""


# ✅ Quick local test
if __name__ == "__main__":
    test_file = "app/data/uploads/sample_scam.png"
    if os.path.exists(test_file):
        print("🔍 OCR Output:\n")
        print(extract_text_from_image(test_file))
    else:
        print("⚠️ Sample file not found.")
