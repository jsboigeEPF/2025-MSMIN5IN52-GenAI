"""
Module d'analyse informelle des arguments.
Utilise un modèle de langage (LLM) pour détecter les sophismes et les faiblesses argumentatives.
Compatible avec LangChain.
"""

from typing import List, Dict, Any

# ==========================================
# 1. Fonction principale d'analyse informelle
# ==========================================

def detecter_sophismes(texte: str, llm_chain) -> Dict[str, Any]:
    """
    Utilise un LLM (via LangChain) pour détecter les sophismes dans un texte argumentatif.
    
    Args:
        texte (str): Texte à analyser.
        llm_chain: Chaîne LangChain configurée avec un LLM et un prompt template.
    
    Returns:
        Dict[str, Any]: Résumé des sophismes détectés et évaluation qualitative.
    """
    prompt = f"""
    Analyse le texte suivant et identifie les sophismes logiques présents.
    Pour chaque argument, indique :
    - le type de sophisme (ex. : ad hominem, appel à la pitié, faux dilemme, etc.)
    - une brève explication
    - une suggestion de reformulation plus rigoureuse.

    Texte : {texte}

    Réponds au format JSON :
    {{
        "fallacies": [
            {{
                "argument": "...",
                "type": "...",
                "explanation": "...",
                "suggestion": "..."
            }}
        ],
        "global_assessment": "..."
    }}
    """
    result = llm_chain.run(prompt)
    return result


# ==========================================
# 2. Exemple d'intégration LangChain
# ==========================================

# Exemple minimaliste d'utilisation (test local)
if __name__ == "__main__":
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    import json

    # Modèle (tu peux remplacer par GPT-4 ou autre)
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    # PromptTemplate (ici intégré directement, mais on peut le séparer)
    prompt_template = PromptTemplate(
        input_variables=["texte"],
        template="""
        Analyse le texte suivant et identifie les sophismes logiques présents.
        Réponds au format JSON structuré comme dans l'exemple suivant :
        {{
            "fallacies": [
                {{
                    "argument": "...",
                    "type": "...",
                    "explanation": "...",
                    "suggestion": "..."
                }}
            ],
            "global_assessment": "..."
        }}

        Texte : {texte}
        """
    )

    # Création de la chaîne LangChain
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Exemple de texte à analyser
    texte_test = (
        "Les voitures électriques sont inutiles, car elles coûtent cher. "
        "De toute façon, les riches ne s’en servent que pour se vanter."
    )

    # Appel de la fonction principale
    resultat = chain.run({"texte": texte_test})

    # Affichage formaté
    try:
        parsed = json.loads(resultat)
    except json.JSONDecodeError:
        parsed = {"error": "Réponse non conforme au format JSON.", "raw": resultat}

    print(json.dumps(parsed, indent=2, ensure_ascii=False))


#Intégration dans le pipeline global
from preprocessing import segmenter_discours
from analyse_informelle import detecter_sophismes

texte = "Tous les hommes sont mortels. Socrate est un homme. Donc Socrate est mortel."
segments = segmenter_discours(texte)


# Analyse informelle sur chaque unité argumentative
for segment in segments:
    resultat = detecter_sophismes(segment, llm_chain)
    print(resultat)
