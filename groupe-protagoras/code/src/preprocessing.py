"""
Module de prétraitement des données pour l'analyse d'arguments.
Responsable de la segmentation du discours, de l'extraction des unités argumentatives
et de la normalisation en propositions logiques atomiques.
"""

from typing import List, Dict, Any
import re
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser # Garder cet import
from pydantic import BaseModel, Field # Utiliser pydantic directement


def segmenter_discours(texte: str) -> List[str]:
    """
    Segmente un discours en unités argumentatives (phrases ou propositions).
    """
    # Séparation par points, points d'interrogation, points d'exclamation
    phrases = re.split(r'[.!?]+', texte)
    # Nettoyage et suppression des éléments vides
    return [phrase.strip() for phrase in phrases if phrase.strip()]

class ArgumentExtraction(BaseModel):
    premises: List[str] = Field(description="Les prémisses de l'argument")
    conclusions: List[str] = Field(description="Les conclusions de l'argument")
    relations: List[str] = Field(description="Les relations entre les éléments de l'argument")

def extraire_premisses_conclusions(texte: str, llm_client) -> Dict[str, Any]:
    """
    Utilise LangChain avec un LLM pour extraire les prémisses, conclusions et relations.
    Le client LLM doit être compatible avec l'interface LangChain.
    """
    # Définir le parser pour garantir un JSON structuré
    parser = JsonOutputParser(pydantic_object=ArgumentExtraction)

    # Créer le template du prompt avec format d'instructions
    prompt_template = """Analyse le discours suivant et extrait :
1. Les prémisses (affirmations servant de base à l'argument)
2. La ou les conclusions (affirmations déduites)
3. Les relations implicites entre elles

Discours : {texte}

{format_instructions}"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["texte"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # Créer la chaîne LLM
    chain = prompt | llm_client | parser
    
    # Exécuter la chaîne
    resultat = chain.invoke({"texte": texte})
    
    return resultat

def normaliser_en_logique_atomique(phrases: List[str]) -> List[str]:
    """
    Normalise une liste de phrases en propositions logiques atomiques (A, B, C...).
    Chaque phrase unique est mappée à une lettre majuscule.
    Exemple: ["p", "q", "p"] -> ["A", "B", "A"]
    """
    mapping = {}
    lettres = [chr(ord('A') + i) for i in range(26)]
    formules_resultat = []
    
    lettre_idx = 0
    for phrase in phrases:
        # Normaliser la phrase pour ignorer la casse et les espaces superflus
        phrase_normalisee = phrase.strip().lower()
        if phrase_normalisee not in mapping:
            mapping[phrase_normalisee] = lettres[lettre_idx] if lettre_idx < len(lettres) else f"P{len(mapping)}"
            lettre_idx += 1
        formules_resultat.append(mapping[phrase_normalisee])
        
    return formules_resultat

# Exemple d'utilisation
if __name__ == "__main__":
    texte = "Tous les hommes sont mortels. Socrate est un homme. Donc Socrate est mortel."
    
    # 1. Segmentation
    unites = segmenter_discours(texte)
    print("Unités segmentées:", unites)
    
    # 2. Extraction (simulée sans LLM réel)
    # extraits = extraire_premisses_conclusions(texte, llm_client)
    
    # 3. Normalisation
    propositions = normaliser_en_logique_atomique(unites[:-1])  # Exclure la conclusion
    print("Propositions logiques:", propositions)