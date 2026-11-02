import os, re
from io import StringIO
from typing import Tuple
from pdfminer.high_level import extract_text as pdf_extract_text

ALLOWED = {".pdf",".txt"}

def is_allowed(filename:str)->bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED

def read_any(path:str)->str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return pdf_extract_text(path) or ""
    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

def normalize_text(s:str)->str:
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()
