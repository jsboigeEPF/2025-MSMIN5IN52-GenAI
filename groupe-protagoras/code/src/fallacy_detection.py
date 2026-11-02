"""
Module d'analyse informelle pour la détection de sophismes dans un discours.
Utilise LangChain pour intégrer un LLM et identifier les erreurs de raisonnement courantes.
"""

from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser # Garder cet import
from pydantic import BaseModel, Field # Utiliser pydantic directement

class Fallacy(BaseModel):
    """Modèle pour un seul sophisme détecté."""
    type: str = Field(description="Le type de sophisme, par exemple 'attaque ad hominem' ou 'pente glissante'.")
    excerpt: str = Field(description="L'extrait exact du texte où le sophisme apparaît.")
    explanation: str = Field(description="Une brève explication de la raison pour laquelle cet extrait est un sophisme.")
class FallacyDetection(BaseModel):
    fallacies: List[Fallacy] = Field(description="Liste des sophismes détectés. Si aucun sophisme n'est trouvé, cette liste doit être vide.")
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
    prompt_template = """Tu es un expert en logique et en rhétorique. Analyse le discours suivant pour détecter les sophismes.

**Instructions importantes :**
1.  **Distingue les arguments valides des sophismes.** Un argument déductif valide (comme Modus Ponens ou Modus Tollens) n'est PAS un sophisme.
2.  **Identifie les sophismes formels** (erreurs de structure logique) et **informels** (erreurs de raisonnement).
3.  **Si l'énoncé est factuel ou ne contient pas d'argument, conclus qu'il n'y a aucun sophisme.**
4.  Si un sophisme est présent, tu DOIS fournir les trois informations suivantes pour chaque sophisme :
    - `type`: Le nom du sophisme.
    - `excerpt`: L'extrait de texte exact où le sophisme se produit.
    - `explanation`: Une explication claire et concise.

**Exemples de raisonnements VALIDES (NON-SOPHISTIQUÉS) :**
- **Modus Ponens :** "S'il pleut, alors le sol est mouillé. Il pleut. Donc, le sol est mouillé." -> Aucun sophisme.
- **Modus Tollens :** "Si le feu est rouge, je m'arrête. Je ne me suis pas arrêté. Donc, le feu n'était pas rouge." -> Aucun sophisme.

**Exemples de SOPHISMES :**
- **Affirmation du conséquent (Sophisme Formel) :** "Si j'étudie, je réussirai. J'ai réussi. Donc, j'ai étudié." -> Sophisme d'affirmation du conséquent.
- **Attaque personnelle (Sophisme Informel) :** "On ne peut pas faire confiance à son avis sur l'économie, il est toujours mal habillé." -> Sophisme d'attaque personnelle.

**Exemples d'affirmations FACTUELLES (NON-SOPHISTIQUÉES) :**
- **Discours :** "L’eau bout à 100°C au niveau de la mer."
  - **Analyse attendue :** Aucun sophisme détecté, c'est une affirmation factuelle.
- **Discours :** "Les chats sont des mammifères."
  - **Analyse attendue :** Aucun sophisme détecté, c'est un constat.

**Analyse du discours suivant :**

Discours : {texte}

**Ton analyse (au format JSON) :**
{format_instructions}
"""

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