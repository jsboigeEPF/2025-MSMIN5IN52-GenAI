"""
Point d'entrée principal pour l'Agent de Recrutement Augmenté.
"""

from src.parsers.cv_parser import load_all_cvs
from src.models.ranking_model import rank_candidates
from src.utils.report_generator import generate_csv_report, generate_html_report
from src.parsers.entity_extractor import extract_entities_from_cv

def main():
    # Chemins
    cv_folder = "data/cv_samples"
    job_desc_path = "data/job_descriptions/description_poste.txt"
    csv_output = "docs/ranking_report.csv"
    html_output = "docs/ranking_report.html"
    
    # Lire la description du poste
    try:
        with open(job_desc_path, 'r', encoding='utf-8') as f:
            job_description = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de la description du poste : {e}")
        return
    
    # Charger et parser les CVs
    cvs = load_all_cvs(cv_folder)
    if not cvs:
        print("Aucun CV chargé. Vérifiez le dossier data/cv_samples.")
        return
        
    # Afficher les entités extraites pour vérification
    for cv in cvs:
        print(f"\nEntités extraites pour {cv['filename']}:")
        entities = cv.get('entities', {})
        for entity_type, entity_data in entities.items():
            print(f"  {entity_type}: {entity_data}")
    
    # Classer les candidats
    ranked = rank_candidates(cvs, job_description)
    
    # Générer les rapports
    generate_csv_report(ranked, csv_output)
    generate_html_report(ranked, html_output)

if __name__ == "__main__":
    main()