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

class ArgumentFormulas(BaseModel):
    """Modèle pour la structure logique d'un argument."""
    premises: List[str] = Field(description="Liste des prémisses sous forme de formules logiques.")
    conclusion: str = Field(description="La conclusion sous forme de formule logique.")

def traduire_argument_en_logique(texte: str, llm_client) -> Dict[str, Any]:
    """
    Utilise un LLM pour traduire un argument complet en un ensemble de prémisses et une conclusion logiques.
    """
    parser = JsonOutputParser(pydantic_object=ArgumentFormulas)

    prompt_template = """Tu es un expert en logique propositionnelle. Analyse l'argument suivant et traduis-le en une structure logique formelle.

**Instructions :**
1.  Identifie les prémisses et la conclusion de l'argument.
2.  Assigne des atomes simples (mots courts en minuscules, ex: 'pleut', 'sol_mouille') aux concepts.
3.  Construis les formules logiques pour les prémisses et la conclusion en utilisant les opérateurs compatibles Tweety : `=>` (implication), `&&` (ET), `||` (OU), `!` (NON).
4.  Retourne le résultat au format JSON demandé.

**Exemple 1 :**
- **Argument d'entrée :** "S'il pleut, alors le sol sera mouillé. Il pleut. Donc, le sol est mouillé."
- **Analyse attendue :** {{"premises": ["pleut => sol_mouille", "pleut"], "conclusion": "sol_mouille"}}

**Exemple 2 :**
- **Argument d'entrée :** "Tous les chats sont des mammifères. Tous les mammifères ont un cœur. Donc, tous les chats ont un cœur."
- **Analyse attendue :** {{"premises": ["chats => mammiferes", "mammiferes => coeur"], "conclusion": "chats => coeur"}}

**Argument à analyser :**
{texte}

{format_instructions}
"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["texte"], partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = prompt | llm_client | parser
    return chain.invoke({"texte": texte})

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

class LogicalForm(BaseModel):
    formulas: List[str] = Field(description="La liste des phrases traduites en formules logiques propositionnelles.")

def normaliser_avec_llm(phrases: List[str], llm_client) -> List[str]:
    """
    Utilise un LLM pour convertir une liste de phrases en formules logiques.
    """
    parser = JsonOutputParser(pydantic_object=LogicalForm)

    prompt_template = """Tu es un logicien. Traduis chaque phrase de la liste suivante en une formule de logique propositionnelle.
Utilise des atomes simples (ex: 'chats', 'mammiferes', 'coeur') et les opérateurs logiques compatibles avec Tweety ('=>' pour l'implication, '&&' pour ET, '||' pour OU, '!' pour NON).

**Instructions :**
1.  Identifie les concepts clés dans chaque phrase.
2.  Assigne un atome (un mot court en minuscules) à chaque concept.
3.  Construis une formule logique pour chaque phrase.
4.  Retourne la liste des formules dans le même ordre que les phrases d'entrée.

**Exemple :**
- **Phrases d'entrée :** ["Tous les chats sont des mammifères", "tous les mammifères ont un cœur"]
- **Analyse attendue :** ["chats => mammiferes", "mammiferes => coeur"]

**Phrases à traduire :**
{phrases_json}

{format_instructions}
"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["phrases_json"], partial_variables={"format_instructions": parser.get_format_instructions()})
    chain = prompt | llm_client | parser
    resultat = chain.invoke({"phrases_json": json.dumps(phrases)})
    return resultat.get("formulas", [])

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