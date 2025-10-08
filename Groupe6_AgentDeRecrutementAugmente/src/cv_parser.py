# src/cv_parser.py
import os
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

def read_txt(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def read_pdf_text(path):
    try:
        with pdfplumber.open(path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        text = "\n".join(pages).strip()
        if text:
            return text
    except Exception:
        pass
    # fallback OCR: convert first pages to images and OCR
    try:
        images = convert_from_path(path, dpi=200)
        ocr_texts = [pytesseract.image_to_string(img, lang='eng+fra') for img in images]
        return "\n".join(ocr_texts)
    except Exception:
        return ""

def read_file(path):
    path = str(path)
    ext = os.path.splitext(path)[1].lower()
    if ext in ['.txt', '.md']:
        return read_txt(path)
    if ext in ['.pdf']:
        return read_pdf_text(path)
    # other formats can be added (docx)
    return ""
