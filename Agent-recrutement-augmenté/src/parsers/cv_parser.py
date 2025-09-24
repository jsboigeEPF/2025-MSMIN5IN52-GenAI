"""
Module pour parser les CVs au format PDF et DOCX.
"""

import os
from typing import Dict, List

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extrait le texte d'un fichier PDF.
    
    Args:
        file_path (str): Chemin vers le fichier PDF.
    
    Returns:
        str: Texte extrait du PDF.
    """
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Erreur lors de la lecture du PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """
    Extrait le texte d'un fichier DOCX.
    
    Args:
        file_path (str): Chemin vers le fichier DOCX.
    
    Returns:
        str: Texte extrait du DOCX.
    """
    try:
        from docx import Document
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Erreur lors de la lecture du DOCX {file_path}: {e}")
        return ""

def parse_cv(cv_path: str) -> Dict[str, str]:
    """
    Parse un CV et extrait le texte brut selon le format.
    
    Args:
        cv_path (str): Chemin vers le fichier CV.
    
    Returns:
        Dict[str, str]: Dictionnaire contenant le texte extrait.
    """
    _, ext = os.path.splitext(cv_path)
    text = ""
    if ext.lower() == ".pdf":
        text = extract_text_from_pdf(cv_path)
    elif ext.lower() == ".docx":
        text = extract_text_from_docx(cv_path)
    else:
        print(f"Format non supporté : {ext}")
    
    return {
        "filename": os.path.basename(cv_path),
        "text": text
    }

def load_all_cvs(cv_folder: str) -> List[Dict[str, str]]:
    """
    Charge et parse tous les CVs d'un dossier.
    
    Args:
        cv_folder (str): Chemin vers le dossier contenant les CVs.
    
    Returns:
        List[Dict[str, str]]: Liste des CVs parsés.
    """
    cvs = []
    if not os.path.exists(cv_folder):
        print(f"Le dossier {cv_folder} n'existe pas.")
        return cvs
    
    for file in os.listdir(cv_folder):
        file_path = os.path.join(cv_folder, file)
        if file.lower().endswith(('.pdf', '.docx')):
            cv_data = parse_cv(file_path)
            if cv_data["text"]:
                cvs.append(cv_data)
    return cvs