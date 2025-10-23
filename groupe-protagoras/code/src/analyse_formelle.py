"""
Module d'analyse formelle des arguments.
Utilise la bibliothèque symbolique TweetyProject pour vérifier la cohérence et la validité logique
des propositions normalisées issues du prétraitement.
"""

from typing import List, Dict, Any
import jpype
import jpype.imports
from jpype.types import *

import os

jar_path =  jar_path = "C:/Users/julie/Documents/5A/GenAI Projet 4/2025-MSMIN5IN52-GenAI/groupe-protagoras/code/src/tweetyproject-full-with-dependencies-1.29.jar"
if not os.path.exists(jar_path):
    raise FileNotFoundError(f"Fichier TweetyProject introuvable : {jar_path}")

# Démarrage de la JVM avec le bon classpath
if not jpype.isJVMStarted():
    jpype.startJVM(classpath=[jar_path])
    print("✅ JVM initialisée avec TweetyProject.")
else:
    print("ℹ️ JVM déjà active.")

# Test d'import
try:
    from net.sf.tweety.logics.prop import PropParser, Proposition, PlBeliefSet
    print("✅ Import Java réussi.")
except Exception as e:
    print("❌ Erreur d'import Tweety:", e)
# Vérification

# ==========================================
# 1. Gestion de l'environnement TweetyProject
# ==========================================

def initialiser_tweety(jar_path: str):
    """
    Initialise la JVM et charge le JAR de TweetyProject.
    Args:
        jar_path (str): chemin vers le fichier TweetyProject .jar
    """
    if not jpype.isJVMStarted():
        if not os.path.exists(jar_path):
            raise FileNotFoundError(f"Fichier TweetyProject introuvable : {jar_path}")
        jpype.startJVM(classpath=[jar_path])
        print("✅ JVM initialisée et TweetyProject chargé.")


# ==========================================
# 2. Vérification de la cohérence logique
# ==========================================

def verifier_coherence(propositions: List[str]) -> Dict[str, Any]:
    """
    Vérifie si l'ensemble des propositions est logiquement cohérent.
    Utilise la logique propositionnelle de TweetyProject.
    
    Args:
        propositions (List[str]): liste de formules logiques (ex. ["A -> B", "A", "¬B"])
    
    Returns:
        Dict[str, Any]: résultat contenant la cohérence et les détails éventuels
    """
    from net.sf.tweety.logics.prop import PropParser, Proposition, PlBeliefSet
    from net.sf.tweety.logics.pl.sat import SatReasoner

    parser = PropParser()
    base = PlBeliefSet()

    for prop in propositions:
        try:
            formule = parser.parseFormula(prop)
            base.add(formule)
        except Exception as e:
            print(f"⚠️ Erreur de parsing sur {prop} : {e}")

    reasoner = SatReasoner()
    coherent = reasoner.isConsistent(base)

    return {
        "coherent": bool(coherent),
        "nombre_formules": len(base),
        "formules": [str(f) for f in base]
    }


# ==========================================
# 3. Vérification de la validité d'une inférence
# ==========================================

def verifier_inference(premisses: List[str], conclusion: str) -> Dict[str, Any]:
    """
    Vérifie si la conclusion découle logiquement des prémisses.
    
    Args:
        premisses (List[str]): liste de formules logiques
        conclusion (str): formule logique représentant la conclusion
    
    Returns:
        Dict[str, Any]: résultat avec verdict et explication
    """
    from net.sf.tweety.logics.prop import PropParser, Proposition, PlBeliefSet
    from net.sf.tweety.logics.pl.sat import SatReasoner

    parser = PropParser()
    base = PlBeliefSet()
    reasoner = SatReasoner()

    for p in premisses:
        try:
            base.add(parser.parseFormula(p))
        except Exception as e:
            print(f"⚠️ Erreur dans la prémisse '{p}': {e}")

    try:
        conclusion_formula = parser.parseFormula(conclusion)
    except Exception as e:
        return {"valid": False, "error": f"Erreur dans la conclusion : {e}"}

    valid = reasoner.entails(base, conclusion_formula)

    return {
        "valid": bool(valid),
        "premisses": premisses,
        "conclusion": conclusion,
        "explication": "La conclusion découle logiquement des prémisses."
        if valid else "La conclusion ne découle pas logiquement des prémisses."
    }


# ==========================================
# 4. Exemple d’utilisation
# ==========================================

if __name__ == "__main__":
    # 🧠 Exemple : syllogisme classique
    jar_path = "C:/Users/julie/Documents/5A/GenAI Projet 4/2025-MSMIN5IN52-GenAI/groupe-protagoras/code/src/tweetyproject-full-with-dependencies-1.29.jar"  # 🔧 À adapter à ton environnement

    try:
        initialiser_tweety(jar_path)
    except Exception as e:
        print(f"Erreur d'initialisation TweetyProject : {e}")
        exit(1)

    premisses = ["Human -> Mortal", "Human(Socrate)"]
    conclusion = "Mortal(Socrate)"

    resultat_inference = verifier_inference(premisses, conclusion)
    print("Résultat de l'inférence :", resultat_inference)

    resultat_coherence = verifier_coherence(premisses + [conclusion])
    print("Résultat de la cohérence :", resultat_coherence)
