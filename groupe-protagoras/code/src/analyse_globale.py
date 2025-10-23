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

# Modules du projet
try:
    from preprocessing import segmenter_discours, normaliser_en_logique_atomique, extraire_premisses_conclusions
except Exception as e:
    raise ImportError("Impossible d'importer 'preprocessing'. Vérifie que preprocessing.py est dans le PYTHONPATH.") from e

try:
    from analyse_informelle import detecter_sophismes
except Exception as e:
    raise ImportError("Impossible d'importer 'analyse_informelle'. Vérifie que analyse_informelle.py est dans le PYTHONPATH.") from e

try:
    from analyse_formelle import initialiser_tweety, verifier_inference, verifier_coherence
except Exception as e:
    raise ImportError("Impossible d'importer 'analyse_formelle'. Vérifie que analyse_formelle.py est dans le PYTHONPATH.") from e

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
    llm_client: Optional[Any] = None,
    tweety_jar: Optional[str] = None,
    simulate_llm: bool = False
) -> Dict[str, Any]:
    """
    Orchestrateur principal.
    - texte: texte à analyser
    - llm_chain: (optionnel) objet LangChain LLMChain ; utilisé par detecter_sophismes
    - llm_client: (optionnel) client générique avec méthode generate(prompt) ; utilisé par preproc
    - tweety_jar: chemin vers le JAR Tweety (si None, on suppose Tweety déjà initialisé ou non nécessaire pour tests)
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
        if llm_client:
            logger.info("Extraction des prémisses/conclusions via llm_client...")
            reponse = extraire_premisses_conclusions(texte, llm_client)
            extracted = safe_json_load(reponse) if isinstance(reponse, str) else reponse
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
                sophismes_result = detecter_sophismes(texte, llm_chain)
            else:
                # si detecter_sophismes dépend d'un llm_chain, on essaye de l'appeler avec None (il peut lever)
                try:
                    sophismes_result = detecter_sophismes(texte, None)
                except Exception as e:
                    logger.warning("Aucun LLM utilisable pour detecter_sophismes ; passage en simulation.")
                    sophismes_result = {"fallacies": []}
    except Exception as e:
        logger.exception("Erreur lors de la détection des sophismes.")
        sophismes_result = {"fallacies": []}

    report["sophisms_raw"] = sophismes_result
    report["sophisms"] = summarise_sophismes(sophismes_result)

    # 5) Initialiser Tweety (si nécessaire)
    if tweety_jar:
        try:
            initialiser_tweety(tweety_jar)
            logger.info("Tweety initialisé.")
        except Exception as e:
            logger.warning(f"Impossible d'initialiser TweetyProject avec {tweety_jar}: {e}")

    # 6) Analyse formelle : cohérence & validité
    # On prendra la dernière formule comme conclusion candidate si possible
    formal_results = {}
    try:
        if formules:
            # Si plusieurs formules, tenter inférence : dernières comme conclusion
            if len(formules) >= 2:
                premisses_for_inference = formules[:-1]
                conclusion_candidate = formules[-1]
                inf_res = verifier_inference(premisses_for_inference, conclusion_candidate)
                formal_results["inference"] = inf_res
            else:
                formal_results["inference"] = {"valid": False, "reason": "Pas assez de formules pour inférer."}

            # cohérence sur l'ensemble
            coh_res = verifier_coherence(formules)
            formal_results["coherence"] = coh_res
        else:
            formal_results["inference"] = {"valid": False, "reason": "Aucune formule fournie."}
            formal_results["coherence"] = {"coherent": False, "reason": "Aucune formule fournie."}
    except Exception as e:
        logger.exception("Erreur durant l'analyse formelle.")
        formal_results = {"error": str(e)}

    report["formal"] = formal_results

    # 7) Fusion des résultats (règles heuristiques simples)
    fusion = {}
    valid_inference = bool(formal_results.get("inference", {}).get("valid", False))
    coherent = bool(formal_results.get("coherence", {}).get("coherent", False))
    has_fallacies = len(report["sophisms"]) > 0

    if valid_inference and coherent and not has_fallacies:
        fusion["verdict"] = "Argument solide : logique valide et pas de sophismes détectés."
    elif valid_inference and coherent and has_fallacies:
        fusion["verdict"] = "Conclusion valide d'un point de vue logique, mais des sophismes informels ont été détectés (attention aux prémisses)."
    elif not valid_inference and coherent and has_fallacies:
        fusion["verdict"] = "Argument cohérent mais la conclusion ne suit pas logiquement; de plus, des sophismes ont été détectés."
    elif not coherent:
        fusion["verdict"] = "Incohérence détectée dans l'ensemble des propositions."
    else:
        fusion["verdict"] = "Résultat mitigé — merci d'examiner les détails."

    fusion["valid_inference"] = valid_inference
    fusion["coherent"] = coherent
    fusion["has_fallacies"] = has_fallacies
    fusion["num_fallacies"] = len(report["sophisms"])
    report["fusion"] = fusion

    return report

# -----------------------
# CLI / Entrypoint
# -----------------------
def parse_args():
    p = argparse.ArgumentParser(description="Pipeline d'analyse d'arguments hybride (LLM + Tweety).")
    p.add_argument("--input", "-i", help="Texte à analyser (entre guillemets).", default=None)
    p.add_argument("--input-file", "-I", help="Fichier texte (.txt) à analyser.", default=None)
    p.add_argument("--tweety-jar", "-j", help="Chemin vers le jar TweetyProject.", default=None)
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
        llm_chain=None,
        llm_client=None,
        tweety_jar=args.tweety_jar,
        simulate_llm=args.simulate_llm
    )

    # Affichage minimal
    print("=== VERDICT ===")
    print(report["fusion"]["verdict"])
    print()
    print("Détails (synthèse) :")
    print(f" - Cohérence logique : {report['formal'].get('coherence')}")
    print(f" - Validité de l'inférence : {report['formal'].get('inference')}")
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
