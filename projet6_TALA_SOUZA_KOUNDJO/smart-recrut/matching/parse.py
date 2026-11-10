import os, re
from io import StringIO
from typing import Tuple
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

ALLOWED = {".pdf", ".txt", ".docx"}

def is_allowed(filename:str)->bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED

def read_any(path:str)->str:
    """Read text from PDF, DOCX or TXT files"""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            return pdf_extract_text(path) or ""
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        if ext == ".docx":
            doc = Document(path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return ""

def normalize_text(s:str)->str:
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()
