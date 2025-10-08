"""
Application Streamlit pour l'Agent de Recrutement Augmenté.
"""
import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import List, Dict, Any

# Configuration de la page
st.set_page_config(
    page_title="Agent de Recrutement Augmenté",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importation des modules après configuration
try:
    from src.parsers.cv_parser import load_all_cvs
    from src.models.ranking_model import HybridRankingModel
    from src.utils.report_generator import generate_csv_report, generate_html_report
    from src.utils.logger import logger
except ImportError as e:
    st.error(f"Erreur d'importation: {e}")
    st.stop()

def main():
    st.title("📊 Agent de Recrutement Augmenté")
    st.markdown("""
    Comparez des CVs à une description de poste et obtenez un classement intelligent 
    avec analyse détaillée et recommandations.
    """)
    
    # Initialisation du logger
    try:
        logger.info("Application démarrée", module="app", function="main")
    except:
        pass  # Le logger peut ne pas être disponible
    
    # Créer les répertoires nécessaires
    os.makedirs("data/cv_samples", exist_ok=True)
    os.makedirs("data/job_descriptions", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # État de l'application
    if 'ranking_done' not in st.session_state:
        st.session_state.ranking_done = False
        st.session_state.ranked_candidates = []
    
    # Colonne latérale pour la navigation
    with st.sidebar:
        st.header("🧭 Navigation")
        page = st.radio("Aller à", ["🏠 Accueil", "📤 Téléchargement", "⚙️ Configuration", "📊 Résultats", "ℹ️ Informations"])
        
        st.divider()
        st.markdown("### 📊 Statistiques")
        try:
            cv_count = len([f for f in os.listdir("data/cv_samples") if f.lower().endswith(('.pdf', '.docx'))])
            st.metric("CVs disponibles", cv_count)
        except:
            st.metric("CVs disponibles", 0)
        
        if st.session_state.ranking_done:
            st.metric("Candidats classés", len(st.session_state.ranked_candidates))
    
    # Page principale selon la navigation
    if page == "🏠 Accueil":
        show_home_page()
    elif page == "📤 Téléchargement":
        show_upload_page()
    elif page == "⚙️ Configuration":
        show_config_page()
    elif page == "📊 Résultats":
        show_results_page()
    elif page == "ℹ️ Informations":
        show_info_page()

def show_home_page():
    """Affiche la page d'accueil."""
    st.header("Bienvenue !")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Fonctionnalités
        - 📄 Analyse de CVs (PDF/DOCX)
        - 🔍 Extraction d'entités structurées
        - ⚖️ Classement hybride (TF-IDF + LLM + mots-clés)
        - 📊 Visualisation interactive
        - 📥 Export des rapports
        """)
    
    with col2:
        st.markdown("""
        ### 🚀 Comment ça marche ?
        1. Téléchargez les CVs
        2. Entrez la description du poste
        3. Configurez les paramètres
        4. Lancez l'analyse
        5. Consultez les résultats
        """)
    
    # Dernière analyse
    if st.session_state.ranking_done and st.session_state.ranked_candidates:
        st.divider()
        st.subheader("📊 Dernière analyse")
        latest_ranking = st.session_state.ranked_candidates
        top_candidate = latest_ranking[0] if latest_ranking else None
        
        if top_candidate:
            st.markdown(f"**Meilleur candidat :** {top_candidate['filename']}")
            st.markdown(f"**Score :** {top_candidate['score']:.2%}")
            st.markdown(f"**Date :** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

def show_upload_page():
    """Affiche la page de téléchargement."""
    st.header("📤 Téléchargement des CVs")
    
    # Téléchargement des CVs
    uploaded_files = st.file_uploader(
        "Téléchargez les CVs (PDF/DOCX)", 
        accept_multiple_files=True, 
        type=["pdf", "docx"],
        help="Formats supportés : PDF et DOCX"
    )
    
    if uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            file_path = os.path.join("data/cv_samples", uploaded_file.name)
            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                status_text.text(f"Téléchargement de {uploaded_file.name}...")
            except Exception as e:
                st.error(f"Erreur lors du téléchargement de {uploaded_file.name}: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        st.success(f"✅ {len(uploaded_files)} CV(s) téléchargé(s) avec succès !")
        
        # Réinitialiser l'état
        st.session_state.ranking_done = False
        
        # Journalisation
        try:
            logger.info(
                f"{len(uploaded_files)} CVs téléchargés", 
                module="app", 
                function="show_upload_page",
                data={"file_count": len(uploaded_files)}
            )
        except:
            pass

def show_config_page():
    """Affiche la page de configuration."""
    st.header("⚙️ Configuration")
    
    # Chargement de la configuration
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("settings", "config/settings.py")
        settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings)
        config = settings.config
    except Exception as e:
        st.warning(f"Impossible de charger la configuration: {e}")
        from config.settings import Config
        config = Config()
    
    # Configuration du modèle
    st.subheader("🤖 Modèle d'IA")
    col1, col2 = st.columns(2)
    
    with col1:
        llm_model = st.selectbox(
            "Modèle LLM",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-2", "claude-instant"],
            index=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-2", "claude-instant"].index(config.model.llm_model) 
            if config.model.llm_model in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-2", "claude-instant"] 
            else 0
        )
        
        temperature = st.slider(
            "Température",
            0.0, 1.0,
            float(config.model.temperature),
            0.1,
            help="Contrôle la créativité du modèle. Plus la valeur est élevée, plus les réponses sont créatives."
        )
    
    with col2:
        max_tokens = st.number_input(
            "Tokens maximaux",
            min_value=100,
            max_value=4000,
            value=int(config.model.max_tokens),
            help="Nombre maximum de tokens dans la réponse"
        )
    
    # Configuration du classement
    st.subheader("📊 Classement des candidats")
    st.markdown("Poids des différents critères de scoring:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tfidf_weight = st.slider("TF-IDF", 0.0, 1.0, float(config.ranking.tfidf_weight), 0.05)
    
    with col2:
        llm_weight = st.slider("LLM", 0.0, 1.0, float(config.ranking.llm_weight), 0.05)
    
    with col3:
        keyword_weight = st.slider("Mots-clés", 0.0, 1.0, float(config.ranking.keyword_weight), 0.05)
    
    # Normalisation des poids
    total_weight = tfidf_weight + llm_weight + keyword_weight
    if abs(total_weight - 1.0) > 0.01:  # Tolérance pour les erreurs d'arrondi
        st.warning("⚠️ La somme des poids doit être égale à 1.0. Normalisation automatique.")
        if total_weight > 0:
            tfidf_weight /= total_weight
            llm_weight /= total_weight
            keyword_weight /= total_weight
    
    # Description du poste
    st.subheader("📝 Description du poste")
    job_description = st.text_area(
        "Entrez la description du poste", 
        height=200,
        help="Décrivez le poste à pourvoir, les compétences requises, etc."
    )
    
    job_desc_path = "data/job_descriptions/description_poste.txt"
    
    if job_description:
        try:
            with open(job_desc_path, "w", encoding="utf-8") as f:
                f.write(job_description)
            st.success("✅ Description du poste enregistrée !")
        except Exception as e:
            st.error(f"Erreur lors de l'enregistrement: {e}")
    
    # Bouton de lancement
    if st.button("🎯 Lancer l'analyse", type="primary"):
        if not os.listdir("data/cv_samples"):
            st.error("❌ Veuillez d'abord télécharger au moins un CV.")
        elif not job_description:
            st.error("❌ Veuillez entrer une description de poste.")
        else:
            with st.spinner("🔍 Analyse en cours..."):
                try:
                    # Charger les CVs
                    cvs = load_all_cvs("data/cv_samples")
                    if not cvs:
                        st.error("❌ Aucun CV valide chargé. Vérifiez les formats.")
                        return
                    
                    # Initialiser le modèle de ranking
                    ranking_model = HybridRankingModel()
                    
                    # Classer les candidats
                    ranked = ranking_model.rank_candidates(cvs, job_description)
                    
                    # Sauvegarder les résultats
                    st.session_state.ranked_candidates = ranked
                    st.session_state.ranking_done = True
                    
                    # Générer les rapports
                    csv_output = "output/ranking_report.csv"
                    html_output = "output/ranking_report.html"
                    generate_csv_report(ranked, csv_output)
                    generate_html_report(ranked, html_output)
                    
                    st.success("✅ Analyse terminée avec succès !")
                    
                    # Journalisation
                    try:
                        logger.info(
                            "Analyse terminée", 
                            module="app", 
                            function="show_config_page",
                            data={
                                "candidate_count": len(ranked),
                                "job_description_length": len(job_description)
                            }
                        )
                    except:
                        pass
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {e}")
                    try:
                        logger.error(
                            "Erreur lors de l'analyse", 
                            module="app", 
                            function="show_config_page",
                            error=e
                        )
                    except:
                        pass

def show_results_page():
    """Affiche la page des résultats."""
    if not st.session_state.ranking_done:
        st.info("⚠️ Aucune analyse n'a été effectuée. Allez dans 'Configuration' pour lancer une analyse.")
        return
    
    st.header("📊 Résultats du classement")
    
    ranked = st.session_state.ranked_candidates
    
    # Métriques globales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre de candidats", len(ranked))
    with col2:
        avg_score = sum(c['score'] for c in ranked) / len(ranked) if ranked else 0
        st.metric("Score moyen", f"{avg_score:.2%}")
    with col3:
        top_score = max(c['score'] for c in ranked) if ranked else 0
        st.metric("Meilleur score", f"{top_score:.2%}")
    
    # Graphique des scores
    st.subheader("Distribution des scores")
    scores_df = pd.DataFrame([
        {'Candidat': c['filename'], 'Score': c['score'], 'Confiance': c['confidence']}
        for c in ranked
    ])
    
    fig = px.bar(
        scores_df, 
        x='Candidat', 
        y='Score',
        color='Confiance',
        title="Scores des candidats",
        color_continuous_scale='viridis',
        labels={'Score': 'Score de correspondance', 'Confiance': 'Confiance'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des résultats
    st.subheader("Classement détaillé")
    results_df = pd.DataFrame([
        {
            'Candidat': c['filename'],
            'Score': f"{c['score']:.2%}",
            'Confiance': f"{c['confidence']:.2%}",
            'Temps de traitement': f"{c['processing_time']:.2f}s"
        }
        for c in ranked
    ])
    
    st.dataframe(
        results_df, 
        use_container_width=True,
        hide_index=True
    )
    
    # Détails par candidat
    st.subheader("Analyse détaillée")
    
    for i, candidate in enumerate(ranked):
        with st.expander(f"📄 {candidate['filename']} (Score: {candidate['score']:.2%})"):
            # Justification
            st.markdown("### 🔍 Analyse")
            st.markdown(candidate['reasoning'])
            
            # Détail des scores
            if 'detailed_scores' in candidate:
                st.markdown("### 📊 Détail des scores")
                detailed_scores = candidate['detailed_scores']
                score_cols = st.columns(3)
                
                with score_cols[0]:
                    st.metric("TF-IDF", f"{detailed_scores.get('tfidf', 0):.2%}")
                with score_cols[1]:
                    st.metric("Mots-clés", f"{detailed_scores.get('keyword', 0):.2%}")
                with score_cols[2]:
                    st.metric("LLM", f"{detailed_scores.get('llm', 0):.2%}")
            
            # Compétences manquantes
            if candidate['missing_skills']:
                st.markdown("### ⚠️ Compétences manquantes")
                st.write(", ".join(candidate['missing_skills']))
            
            # Questions d'entretien
            if candidate['interview_questions']:
                st.markdown("### ❓ Questions d'entretien suggérées")
                for question in candidate['interview_questions']:
                    st.write(f"• {question}")
            
            # Entités extraites
            if 'entities' in candidate and candidate['entities']:
                with st.expander("📋 Entités extraites"):
                    entities = candidate['entities']
                    for entity_type, entity_list in entities.items():
                        if entity_list:
                            st.markdown(f"**{entity_type.title()}**")
                            if isinstance(entity_list, list):
                                if isinstance(entity_list[0], dict):
                                    st.dataframe(pd.DataFrame(entity_list), hide_index=True)
                                else:
                                    st.write(", ".join(entity_list))
                            st.divider()

def show_info_page():
    """Affiche la page d'informations."""
    st.header("ℹ️ Informations")
    
    st.info("""
    ### 📁 Organisation des fichiers
    - **data/cv_samples/** : CVs téléchargés
    - **data/job_descriptions/** : Descriptions de poste
    - **output/** : Rapports générés
    - **logs/** : Fichiers de journalisation
    - **config/settings.py** : Configuration de l'application
    """)
    
    st.info("""
    ### 🛠️ Technologies utilisées
    - **Streamlit** : Interface utilisateur
    - **spaCy** : Extraction d'entités NLP
    - **scikit-learn** : Analyse TF-IDF
    - **OpenAI** : Évaluation LLM
    - **Plotly** : Visualisations interactives
    """)
    
    st.info("""
    ### 📚 Documentation
    Consultez le fichier README.md pour plus d'informations sur l'installation 
    et l'utilisation de l'application.
    """)
    
    # Informations système
    st.subheader("⚙️ Informations système")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Version")
        st.write("Agent Recrutement Augmenté v1.0.0")
    
    with col2:
        st.markdown("### Date")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()