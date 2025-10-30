"""
Module d'analyse informelle pour la détection de sophismes dans un discours.
Utilise LangChain pour intégrer un LLM et identifier les erreurs de raisonnement courantes.
"""

from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser # Garder cet import
from pydantic import BaseModel, Field # Utiliser pydantic directement

class FallacyDetection(BaseModel):
    fallacies: List[Dict[str, str]] = Field(description="Liste des sophismes détectés")
    overall_assessment: str = Field(description="Évaluation globale de la qualité argumentative")

def detecter_sophismes(texte: str, llm_client) -> Dict[str, Any]:
    """
    Analyse un discours pour détecter les sophismes courants.
    
    Args:
        texte (str): Le discours à analyser
        llm_client: Client LLM compatible LangChain avec méthode d'invocation
    
    Returns:
        Dict[str, Any]: Résultat contenant les sophismes détectés et une évaluation globale
    """
    # Définir le parser pour garantir un JSON structuré
    parser = JsonOutputParser(pydantic_object=FallacyDetection)

    # Créer le template du prompt avec format d'instructions
    prompt_template = """Analyse le discours suivant pour détecter les sophismes (erreurs de raisonnement informel).
Identifie les types courants tels que : attaque ad hominem, pente glissante, faux dilemme, appel à la peur, généralisation hâtive, etc.

Pour chaque sophisme détecté, fournis :
- Le type de sophisme
- L'extrait de texte concerné
- Une brève explication

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