"""
Module de transformation des énoncés en logique formelle.
Convertit les propositions normalisées en formules logiques utilisables par TweetyProject.
"""

from typing import List, Dict, Any
import re

def transformer_en_logique_formelle(propositions: List[str]) -> List[str]:
    """
    Transforme une liste de propositions normalisées en formules logiques formelles.
    
    Args:
        propositions (List[str]): Liste de propositions normalisées (ex: "Chat(x) → Mignon(x)")
    
    Returns:
        List[str]: Liste de formules logiques prêtes pour l'analyse avec TweetyProject
    """
    formules = []
    for prop in propositions:
        # Remplacements pour la logique formelle
        formule = prop
        # Remplacer l'implication → par =>
        formule = re.sub(r'→', '=>', formule)
        # Remplacer la négation ¬ par !
        formule = re.sub(r'¬', '!', formule)
        # Ajouter des espaces autour des opérateurs pour la clarté
        formule = re.sub(r'([=!])', r' \1 ', formule)
        formules.append(formule.strip())
    
    return formules

# Exemple d'utilisation
if __name__ == "__main__":
    propositions = [
        "Homme(x) => Mortel(x)",
        "Socrate => Homme",
        "Socrate => Mortel"
    ]
    
    formules = transformer_en_logique_formelle(propositions)
    print("Formules logiques:", formules)