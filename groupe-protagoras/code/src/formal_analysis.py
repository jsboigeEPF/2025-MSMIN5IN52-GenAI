"""
Module d'analyse formelle utilisant TweetyProject via JPype1.
Valide la structure logique des arguments transformés en formules formelles.
"""

from typing import List, Dict, Any
import jpype
import jpype.imports
from jpype.types import *

# S'assurer que la JVM est démarrée par un point d'entrée (ex: java_config.py)
if not jpype.isJVMStarted():
    # Cette condition est une sécurité. L'initialisation doit se faire en amont.
    print("AVERTISSEMENT: formal_analysis.py est importé avant que la JVM ne soit démarrée.")
else:
    # Tenter d'importer les classes critiques. Si cela échoue, c'est que la config est mauvaise.
    try:
        PlParser = jpype.JClass("org.tweetyproject.logics.pl.parser.PlParser")
        SatReasoner = jpype.JClass("org.tweetyproject.logics.pl.reasoner.SatReasoner")
        PlBeliefSet = jpype.JClass("org.tweetyproject.logics.pl.syntax.PlBeliefSet")        
    except Exception as e:
        # Si l'import échoue ici, on lève une erreur claire.
        raise ImportError(f"Impossible d'importer les classes TweetyProject. La configuration de la JVM est peut-être incorrecte. Erreur: {e}")

def normaliser_syntaxe_tweety(formule: str) -> str:
    """
    Convertit une formule logique vers une syntaxe compatible avec une version spécifique de Tweety.
    Cette version semble préférer '=>' et des opérateurs de style C/Java.
    """
    formule = formule.strip()

    # Remplacements basés sur les tests et les conventions courantes des parseurs Java
    formule = formule.replace("->", "=>")   # Implication
    formule = formule.replace("&", "&&")    # Conjonction (ET logique)
    formule = formule.replace("|", "||")    # Disjonction (OU logique)
    formule = formule.replace("~", "!")     # Négation
    formule = formule.replace("¬", "!")     # Négation (alternative)

    # Nettoyage des doubles espaces qui pourraient résulter des remplacements
    formule = " ".join(formule.split())

    return formule


def analyser_validite_formelle(formules: List[str]) -> Dict[str, Any]:
    """
    Analyse la validité logique d'un ensemble de formules en utilisant TweetyProject.
    
    Args:
        formules (List[str]): Liste de formules logiques en format TweetyProject
        
    Returns:
        Dict[str, Any]: Résultat contenant la validité, les incohérences et les implications
    """
    if not jpype.isJVMStarted():
        raise RuntimeError("La JVM n'est pas démarrée. L'analyse formelle ne peut pas continuer.")

    # Créer un raisonneur classique
    reasoner = SatReasoner()
    
    # Créer une nouvelle instance du parser à chaque appel pour éviter les problèmes d'état
    parser = PlParser()
    propositional_kb = PlBeliefSet()

    # Séparer les prémisses de la conclusion (par convention, la dernière formule)
    if len(formules) > 1:
        premisses_str = formules[:-1]
        conclusion_str = formules[-1]
    else:
        # S'il n'y a qu'une seule formule, il n'y a pas d'inférence à vérifier.
        # On vérifie juste la cohérence de cette unique formule.
        premisses_str = formules
        conclusion_str = None

    try:
        # 1. Construire la base de connaissances avec les prémisses
        for formule_str in premisses_str:
            # Normaliser la syntaxe avant de la passer au parser
            formule_norm = normaliser_syntaxe_tweety(formule_str)
            parsed_formula = parser.parseFormula(formule_norm)
            propositional_kb.add(parsed_formula)

        # 2. Vérifier si les prémisses impliquent la conclusion
        if conclusion_str:
            conclusion_norm = normaliser_syntaxe_tweety(conclusion_str)
            conclusion_formula = parser.parseFormula(conclusion_norm)
            # query() renvoie True si la base de connaissances implique la conclusion
            is_valid_inference = reasoner.query(propositional_kb, conclusion_formula)
        else:
            # S'il n'y a pas de conclusion, un argument n'est pas "valide" au sens de l'inférence.
            is_valid_inference = False

    except Exception as e:
        print(f"Erreur majeure lors de l'analyse formelle: {e}")
        is_valid_inference = False

    return {
        "is_valid": is_valid_inference,
        "inconsistencies": [], # Cette partie pourrait être améliorée pour vérifier la cohérence des prémisses
        "logical_implications": []
    }

# Exemple d'utilisation
if __name__ == "__main__":
    # Pour un test autonome, il faut explicitement initialiser la config Java
    try:
        from java_config import initialize_tweety
        jvm_ready = initialize_tweety()
    except ImportError:
        print("Erreur: Impossible d'importer 'java_config'. Assurez-vous que le chemin est correct.")
        jvm_ready = False

    formules = [
        "A -> B",
        "A"
        # La conclusion "B" serait implicite pour une inférence valide
    ]
    
    if jvm_ready:
        resultat = analyser_validite_formelle(formules)
        print("Résultat de l'analyse formelle:", resultat)
    else:
        print("Impossible de lancer l'analyse formelle car la JVM n'a pas pu être initialisée.")