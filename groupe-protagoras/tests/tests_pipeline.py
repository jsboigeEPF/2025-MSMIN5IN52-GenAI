"""
Tests unitaires et fonctionnels pour le pipeline hybride d'analyse d'arguments.
Modules testés :
- preprocessing.py
- analyse_informelle.py
- analyse_formelle.py
- (à venir) analyse_globale.py
"""
import sys
import os
import pytest
# Ajoute le dossier src au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../code/src")))


from preprocessing import segmenter_discours, normaliser_en_logique_atomique
from analyse_informelle import detecter_sophismes
from analyse_formelle import verifier_coherence, verifier_inference

# ---------------------------------------------------------------------
# 1. Données de test
# ---------------------------------------------------------------------
arguments = {
    "valide": "Tous les hommes sont mortels. Socrate est un homme. Donc Socrate est mortel.",
    "fallacieux": "Si tu ne votes pas pour moi, le pays s'effondrera.",
    "incoherent": "Tous les chats sont des chiens. Aucun chien n'est un chat."
}

# ---------------------------------------------------------------------
# 2. Tests du module de prétraitement
# ---------------------------------------------------------------------
def test_segmentation_discours():
    segments = segmenter_discours(arguments["valide"])
    assert isinstance(segments, list)
    assert len(segments) >= 2
    assert any("Socrate" in s for s in segments)

def test_normalisation_logique():
    segments = segmenter_discours(arguments["valide"])
    propositions = normaliser_en_logique_atomique(segments)
    assert all(p.startswith("p") for p in propositions)
    assert len(propositions) == len(segments)

# ---------------------------------------------------------------------
# 3. Tests du module d’analyse informelle (LLM)
# ---------------------------------------------------------------------
@pytest.mark.parametrize("texte", [arguments["valide"], arguments["fallacieux"]])
def test_detection_sophismes(monkeypatch, texte):
    """Simule un appel au LLM avec un résultat fictif pour tester la structure."""
    def fake_call(prompt):
        if "effondrera" in texte:
            return {"fallacies": ["appel à la peur"], "details": "utilise la peur pour convaincre"}
        return {"fallacies": [], "details": "aucun sophisme détecté"}

    monkeypatch.setattr("analyse_informelle.detecter_sophismes", lambda t, llm=None: fake_call(t))
    result = detecter_sophismes(texte)
    assert "fallacies" in result
    assert isinstance(result["fallacies"], list)

# ---------------------------------------------------------------------
# 4. Tests du module d’analyse formelle (TweetyProject)
# ---------------------------------------------------------------------
def test_coherence_tweety():
    propositions = ["p1", "p2", "p3"]
    resultat = verifier_coherence(propositions)
    assert "coherent" in resultat
    assert isinstance(resultat["coherent"], bool)

def test_inference_valide():
    premisses = ["Tous les hommes sont mortels", "Socrate est un homme"]
    conclusion = "Socrate est mortel"
    resultat = verifier_inference(premisses, conclusion)
    assert "valid" in resultat
    assert isinstance(resultat["valid"], bool)

# ---------------------------------------------------------------------
# 5. Tests intégrés (pipeline complet)
# ---------------------------------------------------------------------
def test_integration_simple(monkeypatch):
    """Teste le passage complet : prétraitement → analyse informelle → formelle"""
    from analyse_globale import analyse_argument_complete

    # Simule un LLM qui retourne un sophisme pour le texte fallacieux
    def fake_llm_call(t):
        return {"fallacies": ["appel à la peur"], "details": "utilise la peur pour convaincre"}
    monkeypatch.setattr("analyse_informelle.detecter_sophismes", lambda t, llm=None: fake_llm_call(t))

    texte = arguments["fallacieux"]
    verdict = analyse_argument_complete(texte, llm_chain=None)
    
    assert "coherence_logique" in verdict
    assert "sophismes_detectes" in verdict
    assert "analyse_globale" in verdict
    assert isinstance(verdict["analyse_globale"], str)
