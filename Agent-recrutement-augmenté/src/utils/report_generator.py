"""
Génère des rapports détaillés de classement des candidats avec visualisations et insights.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generate_csv_report(ranked_candidates: List[Dict[str, Any]], output_path: str):
    """
    Génère un rapport CSV détaillé à partir de la liste classée des candidats.
    
    Args:
        ranked_candidates: Liste des candidats classés avec métadonnées
        output_path: Chemin du fichier de sortie
    """
    try:
        # Préparer les données pour CSV
        csv_data = []
        for i, candidate in enumerate(ranked_candidates, 1):
            row = {
                'Rang': i,
                'Candidat': candidate.get('filename', 'N/A'),
                'Score Global': f"{candidate.get('score', 0):.2%}",
                'Confiance': f"{candidate.get('confidence', 0):.2%}",
                'Score TF-IDF': f"{candidate.get('detailed_scores', {}).get('tfidf', 0):.2%}",
                'Score Mots-clés': f"{candidate.get('detailed_scores', {}).get('keyword', 0):.2%}",
                'Score LLM': f"{candidate.get('detailed_scores', {}).get('llm', 0):.2%}",
                'Compétences Manquantes': ', '.join(candidate.get('missing_skills', [])),
                'Temps de Traitement (s)': f"{candidate.get('processing_time', 0):.2f}"
            }
            csv_data.append(row)
        
        df = pd.DataFrame(csv_data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Rapport CSV généré avec succès: {output_path}")
        print(f"✅ Rapport CSV généré : {output_path}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du CSV: {e}")
        print(f"❌ Erreur lors de la génération du CSV: {e}")

def generate_html_report(ranked_candidates: List[Dict[str, Any]], output_path: str):
    """
    Génère un rapport HTML interactif et visuellement attrayant.
    
    Args:
        ranked_candidates: Liste des candidats classés
        output_path: Chemin du fichier de sortie
    """
    try:
        # Statistiques globales
        avg_score = sum(c['score'] for c in ranked_candidates) / len(ranked_candidates) if ranked_candidates else 0
        avg_confidence = sum(c['confidence'] for c in ranked_candidates) / len(ranked_candidates) if ranked_candidates else 0
        total_processing_time = sum(c.get('processing_time', 0) for c in ranked_candidates)
        
        # Créer un graphique de distribution des scores
        scores_fig = go.Figure()
        scores_fig.add_trace(go.Bar(
            x=[c['filename'] for c in ranked_candidates],
            y=[c['score'] for c in ranked_candidates],
            marker=dict(
                color=[c['score'] for c in ranked_candidates],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Score")
            ),
            text=[f"{c['score']:.1%}" for c in ranked_candidates],
            textposition='outside',
            name='Score Global'
        ))
        scores_fig.update_layout(
            title='Distribution des Scores de Correspondance',
            xaxis_title='Candidats',
            yaxis_title='Score',
            yaxis=dict(range=[0, 1]),
            height=400,
            template='plotly_white'
        )
        scores_html = scores_fig.to_html(include_plotlyjs='cdn', div_id='scores-chart')
        
        # Créer un graphique radar pour le top candidat
        if ranked_candidates:
            top_candidate = ranked_candidates[0]
            radar_fig = go.Figure()
            
            categories = ['TF-IDF', 'Mots-clés', 'LLM']
            values = [
                top_candidate.get('detailed_scores', {}).get('tfidf', 0),
                top_candidate.get('detailed_scores', {}).get('keyword', 0),
                top_candidate.get('detailed_scores', {}).get('llm', 0)
            ]
            
            radar_fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=top_candidate['filename']
            ))
            
            radar_fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title=f'Profil du Meilleur Candidat: {top_candidate["filename"]}',
                height=400
            )
            radar_html = radar_fig.to_html(include_plotlyjs='cdn', div_id='radar-chart')
        else:
            radar_html = "<p>Aucun candidat à afficher</p>"
        
        # Créer le tableau des candidats
        table_rows = ""
        for i, candidate in enumerate(ranked_candidates, 1):
            # Couleur de la ligne selon le score
            score = candidate['score']
            if score >= 0.8:
                row_class = "excellent"
            elif score >= 0.6:
                row_class = "good"
            elif score >= 0.4:
                row_class = "average"
            else:
                row_class = "poor"
            
            # Construire les détails
            missing_skills = candidate.get('missing_skills', [])
            missing_skills_html = ', '.join(missing_skills[:5]) if missing_skills else 'Aucune'
            if len(missing_skills) > 5:
                missing_skills_html += f' (+{len(missing_skills) - 5} autres)'
            
            # Questions d'entretien
            interview_q = candidate.get('interview_questions', [])
            interview_html = '<ul>'
            for q in interview_q[:3]:
                interview_html += f'<li>{q}</li>'
            interview_html += '</ul>'
            
            table_rows += f"""
            <tr class="{row_class}">
                <td class="rank"><strong>#{i}</strong></td>
                <td><strong>{candidate['filename']}</strong></td>
                <td class="score">{candidate['score']:.1%}</td>
                <td>{candidate.get('confidence', 0):.1%}</td>
                <td>
                    <div class="score-breakdown">
                        <span>TF-IDF: {candidate.get('detailed_scores', {}).get('tfidf', 0):.1%}</span><br>
                        <span>Mots-clés: {candidate.get('detailed_scores', {}).get('keyword', 0):.1%}</span><br>
                        <span>LLM: {candidate.get('detailed_scores', {}).get('llm', 0):.1%}</span>
                    </div>
                </td>
                <td>{missing_skills_html}</td>
                <td class="reasoning">
                    <details>
                        <summary>Voir l'analyse</summary>
                        <div class="reasoning-content">{candidate.get('reasoning', 'N/A')}</div>
                    </details>
                </td>
            </tr>
            """
        
        # HTML complet avec CSS moderne
        html_content = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rapport de Classement des Candidats - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    color: #333;
                }}
                
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                
                .header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    font-weight: 700;
                }}
                
                .header p {{
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    padding: 30px 40px;
                    background: #f8f9fa;
                }}
                
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                
                .stat-card h3 {{
                    color: #667eea;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                    font-weight: 600;
                }}
                
                .stat-card .value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #333;
                }}
                
                .charts {{
                    padding: 40px;
                }}
                
                .chart-section {{
                    margin-bottom: 40px;
                }}
                
                .content {{
                    padding: 40px;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 0.95em;
                }}
                
                th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px;
                    text-align: left;
                    font-weight: 600;
                    text-transform: uppercase;
                    font-size: 0.85em;
                    letter-spacing: 0.5px;
                }}
                
                td {{
                    padding: 15px;
                    border-bottom: 1px solid #eee;
                }}
                
                tr:hover {{
                    background: #f8f9fa;
                }}
                
                tr.excellent {{
                    background: linear-gradient(90deg, rgba(76, 175, 80, 0.1) 0%, transparent 100%);
                }}
                
                tr.good {{
                    background: linear-gradient(90deg, rgba(33, 150, 243, 0.1) 0%, transparent 100%);
                }}
                
                tr.average {{
                    background: linear-gradient(90deg, rgba(255, 152, 0, 0.1) 0%, transparent 100%);
                }}
                
                tr.poor {{
                    background: linear-gradient(90deg, rgba(244, 67, 54, 0.1) 0%, transparent 100%);
                }}
                
                .rank {{
                    font-size: 1.2em;
                    color: #667eea;
                }}
                
                .score {{
                    font-weight: bold;
                    font-size: 1.1em;
                    color: #4CAF50;
                }}
                
                .score-breakdown {{
                    font-size: 0.85em;
                    color: #666;
                    line-height: 1.6;
                }}
                
                .reasoning {{
                    max-width: 400px;
                }}
                
                details {{
                    cursor: pointer;
                }}
                
                summary {{
                    color: #667eea;
                    font-weight: 600;
                    padding: 5px 10px;
                    border-radius: 5px;
                    background: #f0f0f0;
                }}
                
                summary:hover {{
                    background: #e0e0e0;
                }}
                
                .reasoning-content {{
                    margin-top: 10px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    white-space: pre-wrap;
                    font-size: 0.9em;
                    line-height: 1.6;
                }}
                
                .footer {{
                    background: #f8f9fa;
                    padding: 20px 40px;
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                    border-top: 1px solid #eee;
                }}
                
                @media print {{
                    body {{
                        background: white;
                    }}
                    .container {{
                        box-shadow: none;
                    }}
                    details {{
                        open: true;
                    }}
                    summary {{
                        display: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Rapport de Classement des Candidats</h1>
                    <p>Généré le {datetime.now().strftime('%d %B %Y à %H:%M')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>Candidats Analysés</h3>
                        <div class="value">{len(ranked_candidates)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Score Moyen</h3>
                        <div class="value">{avg_score:.1%}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Confiance Moyenne</h3>
                        <div class="value">{avg_confidence:.1%}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Temps Total</h3>
                        <div class="value">{total_processing_time:.1f}s</div>
                    </div>
                </div>
                
                <div class="charts">
                    <div class="chart-section">
                        {scores_html}
                    </div>
                    <div class="chart-section">
                        {radar_html}
                    </div>
                </div>
                
                <div class="content">
                    <h2 style="margin-bottom: 20px; color: #333;">🏆 Classement Détaillé</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Rang</th>
                                <th>Candidat</th>
                                <th>Score Global</th>
                                <th>Confiance</th>
                                <th>Détail Scores</th>
                                <th>Compétences Manquantes</th>
                                <th>Analyse</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="footer">
                    <p>Agent de Recrutement Augmenté - Powered by AI & Machine Learning</p>
                    <p>© {datetime.now().year} - Tous droits réservés</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Rapport HTML généré avec succès: {output_path}")
        print(f"✅ Rapport HTML généré : {output_path}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du HTML: {e}")
        print(f"❌ Erreur lors de la génération du HTML: {e}")