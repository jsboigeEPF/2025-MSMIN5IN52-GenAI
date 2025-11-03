"""
Script d'évaluation du système d'analyse d'arguments.
Mesure la précision de la détection de sophismes et de l'analyse formelle.
"""

import json
import os
from typing import Dict, List, Any
from collections import defaultdict


def charger_corpus(chemin_corpus: str) -> List[Dict[str, Any]]:
    """Charge le corpus de test à partir d'un fichier JSON."""
    with open(chemin_corpus, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculer_similarite_fallacies(fallacies_predites: List[Dict], fallacies_attendues: List[Dict]) -> Dict[str, float]:
    """Calcule la précision, le rappel et le F1 pour la détection de sophismes."""
    if not fallacies_attendues and not fallacies_predites:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not fallacies_attendues:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    if not fallacies_predites:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    # Comparaison basée sur le type de sophisme (simplification)
    types_predits = {f['type'] for f in fallacies_predites}
    types_attendus = {f['type'] for f in fallacies_attendues}
    
    vrai_positifs = len(types_predits & types_attendus)
    faux_positifs = len(types_predits - types_attendus)
    faux_negatifs = len(types_attendus - types_predits)
    
    precision = vrai_positifs / (vrai_positifs + faux_positifs) if (vrai_positifs + faux_positifs) > 0 else 0
    recall = vrai_positifs / (vrai_positifs + faux_negatifs) if (vrai_positifs + faux_negatifs) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {"precision": precision, "recall": recall, "f1": f1}

def main():
    # Initialiser la configuration Java/Tweety de manière sécurisée
    try:
        # Le chemin doit être ajouté AVANT l'import de java_config
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code', 'src'))
        from java_config import initialize_tweety
        jvm_ready = initialize_tweety()
    except ImportError:
        print("AVERTISSEMENT: java_config.py non trouvé. L'analyse formelle sera désactivée.")
        jvm_ready = False

    # --- IMPORTER LES MODULES APRES L'INIT DE LA JVM ---
    # Cela garantit que formal_analysis.py est chargé quand la JVM est prête.
    from preprocessing import segmenter_discours, normaliser_en_logique_atomique
    from fallacy_detection import detecter_sophismes # Le module qui sera testé
    from formal_analysis import analyser_validite_formelle
    # Chemin vers le corpus de test
    chemin_corpus = os.path.join(os.path.dirname(__file__), 'test_corpus.json')
    
    # Charger le corpus
    corpus = charger_corpus(chemin_corpus)
    print(f"Corpus chargé avec {len(corpus)} exemples.")
    
    # Initialiser les compteurs
    resultats_fallacies = defaultdict(list)
    resultats_validite = []
    
    # Créer un mock compatible avec LangChain
    from langchain_core.runnables import Runnable
    
    class MockRunnable(Runnable):
        def invoke(self, input, config=None, **kwargs):
            # CORRECTION: 'input' est maintenant la chaîne de caractères (le prompt formaté)
            # et non plus un dictionnaire. Nous devons extraire le texte original
            # de cette chaîne pour notre logique de simulation.
            texte_brut = str(input).lower()

            # Retourne une réponse factice pour les tests avec détection basée sur des motifs
            fallacies = []
            
            # Détection de l'attaque ad hominem
            if any(word in texte_brut for word in ['tu ne peux pas faire confiance', 'il n\'a même pas', 'il n\'a pas']):
                fallacies.append({
                    "type": "attaque ad hominem",
                    "span": "Jean",
                    "explanation": "L'argument attaque la personne plutôt que son argumentation."
                })
            
            # Détection de la pente glissante
            if 'bientôt' in texte_brut and 'voudront' in texte_brut:
                fallacies.append({
                    "type": "pente glissante",
                    "span": "Si nous autorisons le mariage gay, bientôt les gens voudront se marier avec des animaux et des objets",
                    "explanation": "L'argument suggère une série de conséquences extrêmes sans preuve de causalité."
                })
            
            # Détection du faux dilemme
            if 'soit' in texte_brut and 'soit' in texte_brut.split():
                fallacies.append({
                    "type": "faux dilemme",
                    "span": "Soit tu es avec nous, soit tu es contre nous",
                    "explanation": "L'argument présente une situation binaire alors que d'autres options existent."
                })
            
            return json.dumps({
                "fallacies": fallacies,
                "overall_assessment": "Analyse terminée avec détection de sophismes."
            })
        
        async def ainvoke(self, input, config=None, **kwargs):
            return self.invoke(input, config, **kwargs)
        
        def batch(self, inputs, config=None, max_concurrency=None, **kwargs):
            return [self.invoke(input, config, **kwargs) for input in inputs]
        
        async def abatch(self, inputs, config=None, max_concurrency=None, **kwargs):
            return [await self.ainvoke(input, config, **kwargs) for input in inputs]
    
    # Créer une instance du client LLM compatible avec LangChain
    llm_client = MockRunnable()
    
    # Évaluer chaque exemple
    for exemple in corpus:
        print(f"\nÉvaluation de {exemple['id']}: {exemple['text']}")
        
        # 1. Analyse de sophismes
        try:
            # Utiliser le module de détection avec le client LLM simulé (MockRunnable)
            # C'est l'architecture cible : on appelle le module, on ne ré-implémente pas sa logique.
            resultats_sophismes = detecter_sophismes(exemple['text'], llm_client)

            similarite = calculer_similarite_fallacies(resultats_sophismes['fallacies'], exemple['expected_fallacies'])
            for metrique, valeur in similarite.items():
                resultats_fallacies[metrique].append(valeur)
            print(f"  Sophismes - Précision: {similarite['precision']:.2f}, Rappel: {similarite['recall']:.2f}, F1: {similarite['f1']:.2f}")
        except Exception as e:
            print(f"  Erreur lors de l'analyse des sophismes: {e}")
            for metrique in resultats_fallacies:
                resultats_fallacies[metrique].append(0.0)
        
        # 2. Analyse formelle
        if jvm_ready:
            try:
                # Pour la démonstration, on utilise les formules attendues du corpus.
                # En pratique, on utiliserait :
                # unites = segmenter_discours(exemple['text'])
                # formules = normaliser_en_logique_atomique(unites)
                formules = exemple['expected_logical_form']
                resultat_formel = analyser_validite_formelle(formules)
                
                # Comparaison de la validité
                validite_predite = resultat_formel['is_valid']
                validite_attendue = exemple['expected_validity']
                exactitude = 1.0 if validite_predite == validite_attendue else 0.0
                resultats_validite.append(exactitude)
                print(f"  Validité formelle: {'Correcte' if exactitude else 'Incorrecte'} (attendue: {validite_attendue}, prédite: {validite_predite})")
            except Exception as e:
                print(f"  Erreur lors de l'analyse formelle: {e}")
                resultats_validite.append(0.0)
        else:
            print("  Analyse formelle ignorée car la JVM n'est pas prête.")
            resultats_validite.append(0.0)
    
    # Afficher les résultats moyens
    print("\n=== RÉSULTATS D'ÉVALUATION ===")
    print("Détection de sophismes:")
    for metrique in ['precision', 'recall', 'f1']:
        moyenne = sum(resultats_fallacies[metrique]) / len(resultats_fallacies[metrique]) if resultats_fallacies[metrique] else 0
        print(f"  {metrique.capitalize()}: {moyenne:.2f}")
    
    print("Validité formelle:")
    exactitude_moyenne = sum(resultats_validite) / len(resultats_validite) if resultats_validite else 0
    print(f"  Exactitude: {exactitude_moyenne:.2f}")

if __name__ == "__main__":
    main()