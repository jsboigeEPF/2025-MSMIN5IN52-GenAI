"""
Module d'analyse formelle utilisant TweetyProject via JPype1.
Valide la structure logique des arguments transformés en formules formelles.
"""

from typing import List, Dict, Any
import jpype
import jpype.imports
from jpype.types import *

def initialiser_tweety():
    """
    Démarre la machine virtuelle Java et charge la bibliothèque TweetyProject.
    Doit être appelé avant toute utilisation de TweetyProject.
    """
    if not jpype.isJVMStarted():
        jar_path = "groupe-protagoras/code/src/org.tweetyproject.tweety-full-1.29-with-dependencies.jar"
        jpype.startJVM(classpath=[jar_path])

def analyser_validite_formelle(formules: List[str]) -> Dict[str, Any]:
    """
    Analyse la validité logique d'un ensemble de formules en utilisant TweetyProject.
    
    Args:
        formules (List[str]): Liste de formules logiques en format TweetyProject
        
    Returns:
        Dict[str, Any]: Résultat contenant la validité, les incohérences et les implications
    """
    # S'assurer que la JVM est démarrée
    initialiser_tweety()
    
    # Importer les classes TweetyProject après le démarrage de la JVM
    from org.tweetyproject.logics.pl.syntax import PropositionalFormula
    from org.tweetyproject.logics.pl.semantics import ClassicInterpretation
    from org.tweetyproject.logics.pl.reasoner import ClassicReasoner
    
    # Créer un raisonneur classique
    reasoner = ClassicReasoner()
    
    # Convertir les formules en objets TweetyProject
    propositional_kb = jpype.JClass("org.tweetyproject.logics.pl.syntax.PlBeliefSet")()
    
    for formule in formules:
        try:
            # Créer une formule propositionnelle
            pf = PropositionalFormula(formule)
            propositional_kb.add(pf)
        except Exception as e:
            print(f"Erreur lors de l'analyse de la formule '{formule}': {str(e)}")
            continue
    
    # Vérifier la cohérence
    is_consistent = reasoner.query(propositional_kb, PropositionalFormula("TRUE"))
    
    # Pour une analyse plus complète, on pourrait vérifier des implications spécifiques
    # ou détecter des contradictions, mais cela dépend du contexte spécifique
    
    return {
        "is_valid": is_consistent,
        "inconsistencies": [] if is_consistent else ["Contradiction détectée dans l'ensemble des prémisses"],
        "logical_implications": []
    }

# Exemple d'utilisation
if __name__ == "__main__":
    formules = [
        "A => B",
        "A",
        "B"
    ]
    
    resultat = analyser_validite_formelle(formules)
    print("Résultat de l'analyse formelle:", resultat)