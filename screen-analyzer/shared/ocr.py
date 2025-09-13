# ocr.py
import cv2
import pytesseract

def extract_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    config = '--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config=config)
    return text.strip()
