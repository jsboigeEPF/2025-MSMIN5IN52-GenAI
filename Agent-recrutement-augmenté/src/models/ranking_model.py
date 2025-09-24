"""
Squelette pour le modèle de classement utilisant LangChain ou Semantic Kernel.
"""

from typing import List, Dict

def compute_match_score(cv_text: str, job_description: str) -> float:
    """
    Calcule un score de correspondance entre un CV et une description de poste.
    À implémenter avec LangChain ou Semantic Kernel.
    
    Args:
        cv_text (str): Texte extrait du CV.
        job_description (str): Description du poste.
    
    Returns:
        float: Score de correspondance (0 à 1).
    """
    # Placeholder pour intégration future avec LLM
    return 0.0

def rank_candidates(cvs: List[Dict[str, str]], job_description: str) -> List[Dict[str, str]]:
    """
    Classe les candidats selon leur score de correspondance.
    
    Args:
        cvs (List[Dict[str, str]]): Liste des CVs parsés.
        job_description (str): Description du poste.
    
    Returns:
        List[Dict[str, str]]: Liste des candidats classés avec scores et justifications.
    """
    ranked = []
    for cv in cvs:
        score = compute_match_score(cv["text"], job_description)
        ranked.append({
            "filename": cv["filename"],
            "score": score,
            "justification": f"Correspondance estimée à {score:.2%}"
        })
    # Trier par score décroissant
    return sorted(ranked, key=lambda x: x["score"], reverse=True)