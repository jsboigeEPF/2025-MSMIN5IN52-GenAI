"""
Génère un rapport de classement des candidats.
"""

import pandas as pd
from typing import List, Dict

def generate_csv_report(ranked_candidates: List[Dict[str, str]], output_path: str):
    """
    Génère un rapport CSV à partir de la liste classée des candidats.
    
    Args:
        ranked_candidates (List[Dict[str, str]]): Liste des candidats classés.
        output_path (str): Chemin du fichier de sortie.
    """
    df = pd.DataFrame(ranked_candidates)
    df.to_csv(output_path, index=False)
    print(f"Rapport CSV généré : {output_path}")

def generate_html_report(ranked_candidates: List[Dict[str, str]], output_path: str):
    """
    Génère un rapport HTML à partir de la liste classée des candidats.
    
    Args:
        ranked_candidates (List[Dict[str, str]]): Liste des candidats classés.
        output_path (str): Chemin du fichier de sortie.
    """
    df = pd.DataFrame(ranked_candidates)
    html_content = df.to_html(index=False, table_id="ranked-candidates", border=0)
    full_html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rapport de Classement des Candidats</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Rapport de Classement des Candidats</h1>
        {html_content}
    </body>
    </html>
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Rapport HTML généré : {output_path}")