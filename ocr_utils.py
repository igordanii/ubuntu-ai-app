# ocr_utils.py
import pytesseract
from PIL import Image
import os

def extract_text_from_image(image_path):
    """
    Extracts text from an image using Tesseract OCR.
    Returns the extracted text as a string, or None if an error occurs or no text is found.
    """
    try:
        # Basic check for common image extensions (optional, Pillow might handle it)
        if not os.path.splitext(image_path)[1].lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
            print(f"File '{image_path}' does not appear to be a supported image type for OCR.")
            return None

        img = Image.open(image_path)
        # You might need to specify language(s) for Tesseract, e.g., lang='eng+por'
        text = pytesseract.image_to_string(img)
        return text.strip() if text else None # Return None if text is empty string after stripping
    except pytesseract.TesseractNotFoundError:
        print("OCR Error: Tesseract is not installed or not in your PATH.")
        # Consider raising this or returning a specific error code/message
        return "Error: Tesseract not found."
    except Exception as e:
        print(f"OCR Error processing '{image_path}': {e}")
        return None