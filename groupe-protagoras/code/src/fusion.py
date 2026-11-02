"""
Module de fusion des résultats des analyses informelle et formelle.
Corréle les sophismes détectés par le LLM avec la validité logique établie par TweetyProject.
"""

from typing import Dict, Any

def fusionner_analyses(analyse_informelle: Dict[str, Any], analyse_formelle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne les résultats des analyses informelle et formelle pour produire un verdict global.
    
    Args:
        analyse_informelle (Dict[str, Any]): Résultats de l'analyse des sophismes
        analyse_formelle (Dict[str, Any]): Résultats de l'analyse de validité logique
        
    Returns:
        Dict[str, Any]: Verdict global sur la qualité de l'argument
    """
    # Déterminer la validité globale
    # Un argument peut être logiquement valide mais basé sur des sophismes
    # ou logiquement invalide mais sans sophismes évidents
    if analyse_formelle["is_valid"] and len(analyse_informelle.get("fallacies", [])) == 0:
        overall_validity = True
        final_verdict = "L'argument est logiquement valide et ne contient pas de sophismes apparents. C'est un argument solide."
    elif not analyse_formelle["is_valid"] and len(analyse_informelle.get("fallacies", [])) > 0:
        overall_validity = False
        final_verdict = "L'argument est logiquement invalide et contient des sophismes. C'est un argument faible sur les deux plans."
    elif not analyse_formelle["is_valid"]:
        overall_validity = False
        final_verdict = "L'argument est logiquement invalide, bien qu'il ne contienne pas de sophismes évidents. La structure logique est défaillante."
    else:  # analyse_formelle["is_valid"] mais avec sophismes
        overall_validity = False
        final_verdict = "L'argument est logiquement valide mais repose sur des sophismes. La conclusion pourrait être correcte, mais le raisonnement est fallacieux."
    
    return {
        "overall_validity": overall_validity,
        "informal_fallacies": analyse_informelle.get("fallacies", []),
        "formal_validity": {
            "is_valid": analyse_formelle["is_valid"],
            "inconsistencies": analyse_formelle.get("inconsistencies", []),
            "logical_implications": analyse_formelle.get("logical_implications", [])
        },
        "final_verdict": final_verdict
    }

# Exemple d'utilisation
if __name__ == "__main__":
    analyse_informelle = {
        "fallacies": [
            {
                "type": "attaque ad hominem",
                "location": "Socrate est un philosophe, donc il ne peut pas avoir raison",
                "explanation": "Attaque contre la personne plutôt que contre l'argument"
            }
        ],
        "overall_assessment": "L'argument contient une attaque personnelle"
    }
    
    analyse_formelle = {
        "is_valid": True,
        "inconsistencies": [],
        "logical_implications": []
    }
    
    resultat = fusionner_analyses(analyse_informelle, analyse_formelle)
    print("Verdict global:", resultat)