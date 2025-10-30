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
import pathlib
from datetime import datetime, UTC
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv()

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

    timestamp = datetime.now(UTC).isoformat()
    report: Dict[str, Any] = {
        "meta": {"generated_at": timestamp, "input_length": len(texte), "original_text": texte},
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
        unites_to_normalize.extend(extracted.get("conclusions", [])) # Ajout de la conclusion pour l'analyse d'inférence
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

def generer_rapport_texte(report: Dict[str, Any]) -> str:
    """Génère un rapport textuel lisible (Markdown) à partir du rapport JSON."""
    lines = []
    input_file_name = report.get("meta", {}).get("source_file", "N/A")
    
    # Titre et métadonnées
    lines.append("# Rapport d'Analyse d'Argument")
    lines.append(f"**Généré le :** {report.get('meta', {}).get('generated_at', 'N/A')}")
    lines.append("\n---\n")

    # Verdict Final
    if "analyses" in report: # Mode multi-arguments
        lines.append(f"## Synthèse pour le fichier : {input_file_name}")
        total_args = len(report["analyses"])
        total_fallacies = sum(len(arg.get("sophisms", [])) for arg in report["analyses"])
        lines.append(f"- **Arguments analysés :** {total_args}")
        lines.append(f"- **Total des sophismes détectés :** {total_fallacies}")
        lines.append("\n---\n")
        for i, single_report in enumerate(report["analyses"], 1):
            lines.extend(_formater_analyse_unique(single_report, i))
    else: # Mode argument unique
        lines.extend(_formater_analyse_unique(report))

    return "\n".join(lines)

def _formater_analyse_unique(report: Dict[str, Any], index: int = 0) -> List[str]:
    """Helper pour formater une seule analyse d'argument."""
    lines = []
    original_text = report.get("meta", {}).get("original_text", "")
    header = f"### {index}. Analyse de l'argument : \"{original_text}\"" if index > 0 else "## Analyse de l'argument"
    lines.append(header)
    
    # Verdict
    verdict = report.get("fusion", {}).get("final_verdict", "Analyse incomplète.")
    lines.append(f"> **Verdict :** {verdict}")
    
    # Analyse Informelle (Sophismes)
    sophismes = report.get("sophisms", [])
    if not sophismes:
        lines.append("✅ Aucun sophisme n'a été détecté dans le discours.")
    else:
        lines.append(f"\n**Sophisme(s) détecté(s) :**")
        for i, sophisme in enumerate(sophismes, 1):
            lines.append(f"- **Type :** `{sophisme.get('type', 'Non spécifié')}`")
            lines.append(f"   - **Extrait concerné :** \"_{sophisme.get('excerpt', 'N/A')}_\"")
            lines.append(f"   - **Explication :** {sophisme.get('explanation', 'N/A')}")

    # Analyse Formelle
    formal = report.get("formal", {})
    if formal.get('is_valid'):
        lines.append("\n- **Validité formelle :** ✅ Valide (La conclusion découle logiquement des prémisses).")
    else:
        lines.append("\n- **Validité formelle :** ❌ Invalide (La conclusion ne peut pas être prouvée à partir des prémisses).")
    lines.append("\n---\n")
    return lines

# -----------------------
# CLI / Entrypoint
# -----------------------

def main():
    # Définir les chemins des dossiers d'entrée et de sortie
    project_root = pathlib.Path(__file__).parent.parent.parent
    input_dir = project_root / "input_texts"
    output_dir = project_root / "output_reports"

    # Créer le dossier de sortie s'il n'existe pas
    output_dir.mkdir(exist_ok=True)

    # Vérifier si le dossier d'entrée existe
    if not input_dir.is_dir():
        logger.error(f"Le dossier d'entrée '{input_dir}' est introuvable. Veuillez le créer et y ajouter des fichiers .txt.")
        input_dir.mkdir(exist_ok=True) # On le crée pour la première fois
        logger.info(f"Dossier '{input_dir}' créé. Ajoutez-y des fichiers .txt à analyser.")
        return

    # Trouver tous les fichiers .txt dans le dossier d'entrée
    text_files = list(input_dir.glob("*.txt"))

    if not text_files:
        logger.warning(f"Aucun fichier .txt trouvé dans '{input_dir}'. Rien à analyser.")
        return

    logger.info(f"Found {len(text_files)} argument(s) to analyze in '{input_dir}'.")

    # Instancier le client LLM d'OpenAI
    llm_client = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    for text_file in text_files:
        logger.info(f"\n--- Analyzing file: {text_file.name} ---")
        all_analyses = []
        with open(text_file, "r", encoding="utf-8") as f:
            # Chaque ligne non vide est traitée comme un argument séparé
            arguments = [line.strip() for line in f if line.strip()]

        if not arguments:
            logger.warning(f"Le fichier '{text_file.name}' est vide. Passage au suivant.")
            continue
        
        for i, argument_text in enumerate(arguments, 1):
            logger.info(f"  -> Processing argument {i}/{len(arguments)}: \"{argument_text[:70]}...\"")
            single_report = run_pipeline(
                texte=argument_text,
                llm_chain=llm_client,
                simulate_llm=False
            )
            all_analyses.append(single_report)

        # Créer un rapport global pour le fichier
        final_report = {
            "meta": {"source_file": text_file.name, "generated_at": datetime.now(UTC).isoformat()},
            "analyses": all_analyses
        }
        
        # Sauvegarder le rapport JSON
        report_filename = output_dir / f"{text_file.stem}_report.json"
        with open(report_filename, "w", encoding="utf-8") as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        # Générer et sauvegarder le rapport textuel (Markdown)
        rapport_texte = generer_rapport_texte(final_report)
        rapport_texte_filename = output_dir / f"{text_file.stem}_report.md"
        with open(rapport_texte_filename, "w", encoding="utf-8") as f:
            f.write(rapport_texte)

        logger.info(f"✅ Analysis complete for '{text_file.name}'.")
        logger.info(f"   - JSON report saved to '{report_filename}'")
        logger.info(f"   - Text report saved to '{rapport_texte_filename}'")

if __name__ == "__main__":
    main()
