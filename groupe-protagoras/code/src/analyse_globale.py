#!/usr/bin/env python3
"""
analyse_globale.py
Orchestre le pipeline d'analyse d'arguments :
- prétraitement (segmentation, extraction, normalisation)
- analyse informelle (détection de sophismes via LLM)
- analyse formelle (TweetyProject : cohérence / validité)
- fusion des résultats + export JSON

Usage (exemples):
  python analyse_globale.py --input "Tous les hommes sont mortels. Socrate est un homme. Donc Socrate est mortel."
  python analyse_globale.py --input-file ./exemples/corpus.txt --out report.json
"""
from typing import List, Dict, Any, Optional
import json
import logging
import argparse
import os
from datetime import datetime

# --- Configuration robuste de l'environnement ---
# Initialise la JVM pour Tweety de manière centralisée et sécurisée.
try:
    from java_config import initialize_tweety
    JVM_READY = initialize_tweety()
except ImportError:
    print("AVERTISSEMENT: java_config.py non trouvé. L'analyse formelle sera désactivée.")
    JVM_READY = False

# Modules du projet
from preprocessing import segmenter_discours, normaliser_en_logique_atomique, extraire_premisses_conclusions
from fallacy_detection import detecter_sophismes  # Utilisation du module correct
from formal_analysis import analyser_validite_formelle # Utilisation du module correct
from fusion import fusionner_analyses

# -----------------------
# Logging
# -----------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("analyse_globale")

# -----------------------
# Helpers
# -----------------------
def safe_json_load(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return s

def summarise_sophismes(sophismes_result: Any) -> List[Dict[str, Any]]:
    """
    Normalise la sortie du module LLM en liste d'objets:
    attente: { "fallacies": [...], "global_assessment": "..." } ou une string JSON.
    """
    if not sophismes_result:
        return []
    if isinstance(sophismes_result, str):
        # tenter de parser
        try:
            data = json.loads(sophismes_result)
        except Exception:
            return [{"raw": sophismes_result}]
    else:
        data = sophismes_result

    if isinstance(data, dict) and "fallacies" in data:
        return data["fallacies"] or []
    # autre format: renvoyer brut
    return [data]

# -----------------------
# Pipeline core
# -----------------------
def run_pipeline(
    texte: str,
    llm_chain: Optional[Any] = None,
    simulate_llm: bool = False
) -> Dict[str, Any]:
    """
    Orchestrateur principal.
    - texte: texte à analyser.
    - llm_chain: (optionnel) objet LangChain compatible (Runnable) ; utilisé pour les sophismes et l'extraction.
    - simulate_llm: si True, retourne résultats LLM simulés (utile sans clé API)
    """

    timestamp = datetime.utcnow().isoformat() + "Z"
    report: Dict[str, Any] = {
        "meta": {"generated_at": timestamp, "input_length": len(texte)},
        "segments": [],
        "sophisms": None,
        "formal": {},
        "fusion": {}
    }

    # 1) Segmentation
    segments = segmenter_discours(texte)
    logger.info(f"{len(segments)} segments extraits.")
    report["segments_raw"] = segments

    # 2) Extraction (-> prémisses / conclusions)
    extracted = None
    try:
        if llm_chain and not simulate_llm:
            logger.info("Extraction des prémisses/conclusions via LLM...")
            extracted = extraire_premisses_conclusions(texte, llm_chain)
        else:
            logger.info("Aucun llm_client fourni : extraction simulée (segments -> premises/conclusions simples).")
            # heuristique simple : tout sauf dernière phrase comme prémisse, dernière comme conclusion si contient 'Donc' ou 'donc'
            premises = segments[:-1] if len(segments) > 1 else segments
            conclusions = [segments[-1]] if len(segments) > 0 else []
            extracted = {"premises": premises, "conclusions": conclusions, "relations": []}
    except Exception as e:
        logger.warning(f"Extraction LLM a échoué : {e}")
        extracted = {"premises": [], "conclusions": [], "relations": []}

    report["extracted"] = extracted

    # 3) Normalisation en formules logiques
    unites_to_normalize = []
    # on essaye d'utiliser explicitement les prémisses + conclusions extraites si présentes
    if isinstance(extracted, dict) and extracted.get("premises"):
        unites_to_normalize.extend(extracted.get("premises", []))
    else:
        unites_to_normalize.extend(segments[:-1] if len(segments) > 1 else segments)

    # normaliser (préprocessing.normaliser_en_logique_atomique)
    try:
        formules = normaliser_en_logique_atomique(unites_to_normalize)
    except Exception as e:
        logger.warning(f"Erreur lors de la normalisation : {e}")
        formules = [u for u in unites_to_normalize]

    report["formules"] = formules

    # 4) Analyse informelle (détection de sophismes)
    sophismes_result = None
    try:
        if simulate_llm:
            logger.info("Mode simulation LLM activé.")
            # simulation basique : si présence de 'tu' ou attaque personnelle => ad hominem
            simulated = {"fallacies": []}
            lower = texte.lower()
            if "tou" in lower or "tu " in lower:
                simulated["fallacies"].append({"argument": "présence de 'tu'", "type": "ad hominem", "explanation": "attaque de la personne", "suggestion": "focaliser sur les faits"})
            if "si tu ne" in lower or "si tu n" in lower:
                simulated["fallacies"].append({"argument": "menace/peur", "type": "appel à la peur", "explanation": "conclusion basée sur peur", "suggestion": "apporter preuves statistiques"})
            sophismes_result = simulated
        else:
            logger.info("Appel au module detecter_sophismes (LLM)...")
            # detecter_sophismes attend llm_chain (selon ton module)
            if llm_chain is not None:
                sophismes_result = detecter_sophismes(texte, llm_chain) # Appel à la bonne fonction
            else:
                logger.warning("Aucun LLM fourni pour detecter_sophismes ; passage en simulation.")
                sophismes_result = {"fallacies": []}
    except Exception as e:
        logger.exception("Erreur lors de la détection des sophismes.")
        sophismes_result = {"fallacies": []}

    report["sophisms_raw"] = sophismes_result
    report["sophisms"] = summarise_sophismes(sophismes_result)

    # 5) Analyse formelle : cohérence & validité
    formal_results = {}
    if JVM_READY:
        try:
            if formules:
                formal_results = analyser_validite_formelle(formules) # Appel à la bonne fonction
            else:
                formal_results = {"is_valid": False, "reason": "Aucune formule fournie."}
        except Exception as e:
            logger.exception("Erreur durant l'analyse formelle.")
            formal_results = {"error": str(e), "is_valid": False}
    else:
        logger.warning("Analyse formelle ignorée car la JVM n'est pas prête.")
        formal_results = {"is_valid": False, "reason": "JVM non initialisée."}

    report["formal"] = formal_results

    # 6) Fusion des résultats
    report["fusion"] = fusionner_analyses(report["sophisms_raw"], report["formal"])

    return report

# -----------------------
# CLI / Entrypoint
# -----------------------
def parse_args():
    p = argparse.ArgumentParser(description="Pipeline d'analyse d'arguments hybride (LLM + Tweety).")
    p.add_argument("--input", "-i", help="Texte à analyser (entre guillemets).", default=None)
    p.add_argument("--input-file", "-I", help="Fichier texte (.txt) à analyser.", default=None)
    p.add_argument("--out", "-o", help="Fichier JSON de sortie (report).", default=None)
    p.add_argument("--simulate-llm", action="store_true", help="Simuler le module LLM (utile pour test sans API).")
    return p.parse_args()

def main():
    args = parse_args()

    if not args.input and not args.input_file:
        logger.error("Aucun texte d'entrée fourni. Utilise --input ou --input-file.")
        return

    if args.input_file:
        if not os.path.exists(args.input_file):
            logger.error(f"Fichier introuvable : {args.input_file}")
            return
        with open(args.input_file, "r", encoding="utf-8") as f:
            texte = f.read()
    else:
        texte = args.input

    # NOTE: ici on ne crée pas de llm_chain ni de llm_client.
    # Si tu veux exécuter avec LangChain, importe et passe ton llm_chain au run_pipeline.
    report = run_pipeline(
        texte=texte,
        llm_chain=None, # Remplacer par un vrai client LLM pour une utilisation complète
        simulate_llm=args.simulate_llm
    )

    # Affichage minimal
    print("=== VERDICT ===")
    print(report.get("fusion", {}).get("final_verdict", "Analyse incomplète."))
    print()
    print("Détails (synthèse) :")
    print(f" - Validité formelle : {report['formal'].get('is_valid')}")
    print(f" - Sophismes détectés (count) : {len(report['sophisms'])}")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"Rapport sauvegardé dans {args.out}")
    else:
        # print full report compact
        print("\nFull report JSON:")
        print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
