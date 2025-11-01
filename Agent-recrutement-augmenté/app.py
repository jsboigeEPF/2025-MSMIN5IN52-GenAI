"""
Application Streamlit pour l'Agent de Recrutement Augmenté.
"""
import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict, Any

# Configuration de la page
st.set_page_config(
    page_title="Agent de Recrutement Augmenté",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Headers */
    h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
    }
    
    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #2c3e50;
    }
    
    /* Cards */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #1f77b4 0%, #2ecc71 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Success/Error/Info boxes */
    .stSuccess {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        border-radius: 8px;
    }
    
    .stInfo {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        border-radius: 8px;
    }
    
    .stWarning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        border-radius: 8px;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 1rem;
        background-color: #f8f9fa;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Importation des modules après configuration
try:
    from src.parsers.cv_parser import load_all_cvs
    from src.models.ranking_model import HybridRankingModel
    from src.utils.report_generator import generate_csv_report, generate_html_report
    from src.utils.comparison import CVComparisonEngine
    from src.utils.logger import logger
    from src.utils.advanced_features import (
        PerformanceMonitor, SmartScorer, ExperienceAnalyzer, RecommendationEngine
    )
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
        page = st.radio("Aller à", ["🏠 Accueil", "📤 Téléchargement", "⚙️ Configuration", "📊 Résultats", "🔍 Mode Comparaison", "ℹ️ Informations"])
        
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
    elif page == "🔍 Mode Comparaison":
        show_comparison_page()
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
            # Performance monitoring
            monitor = PerformanceMonitor()
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Load CVs
                status_text.text("📂 Chargement des CVs...")
                progress_bar.progress(10)
                monitor.start_timer("load_cvs")
                cvs = load_all_cvs("data/cv_samples")
                monitor.end_timer("load_cvs")
                
                if not cvs:
                    st.error("❌ Aucun CV valide chargé. Vérifiez les formats.")
                    return
                
                progress_bar.progress(25)
                
                # Step 2: Initialize model
                status_text.text("🤖 Initialisation du modèle...")
                monitor.start_timer("init_model")
                ranking_model = HybridRankingModel()
                monitor.end_timer("init_model")
                progress_bar.progress(35)
                
                # Step 3: Detect industry
                status_text.text("🔍 Détection de l'industrie...")
                industry = SmartScorer.detect_industry(job_description)
                st.info(f"🏢 Industrie détectée: **{industry.upper()}**")
                progress_bar.progress(45)
                
                # Step 4: Rank candidates
                status_text.text("⚖️ Classement des candidats...")
                monitor.start_timer("ranking")
                ranked = ranking_model.rank_candidates(cvs, job_description)
                monitor.end_timer("ranking")
                progress_bar.progress(70)
                
                # Step 5: Generate reports
                status_text.text("📄 Génération des rapports...")
                monitor.start_timer("reports")
                csv_output = "output/ranking_report.csv"
                html_output = "output/ranking_report.html"
                generate_csv_report(ranked, csv_output)
                generate_html_report(ranked, html_output)
                monitor.end_timer("reports")
                progress_bar.progress(90)
                
                # Save results
                st.session_state.ranked_candidates = ranked
                st.session_state.ranking_done = True
                st.session_state.industry = industry
                st.session_state.performance = monitor.get_report()
                
                progress_bar.progress(100)
                status_text.text("✅ Analyse terminée!")
                
                # Show performance metrics
                perf_report = monitor.get_report()
                st.success(f"✅ Analyse terminée en {perf_report['total_time']:.2f}s")
                
                with st.expander("⚡ Détails des performances"):
                    perf_df = pd.DataFrame([
                        {'Étape': k, 'Durée (s)': f"{v.get('duration', 0):.2f}"}
                        for k, v in perf_report['operations'].items()
                    ])
                    st.dataframe(perf_df, use_container_width=True)
                
                # Journalisation
                try:
                    logger.info(
                        "Analyse terminée", 
                        module="app", 
                        function="show_config_page",
                        data={
                            "candidate_count": len(ranked),
                            "job_description_length": len(job_description),
                            "industry": industry,
                            "total_time": perf_report['total_time']
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
        # Experience analysis
        experience_years = 0
        seniority = "N/A"
        if 'entities' in candidate and candidate['entities']:
            entities = candidate['entities']
            if 'experience' in entities:
                experience_years = ExperienceAnalyzer.calculate_years_of_experience(entities['experience'])
                seniority = ExperienceAnalyzer.assess_seniority(experience_years)
        
        # Recommendations
        cv_analysis = {
            'missing_skills': candidate.get('missing_skills', []),
            'experience_years': experience_years,
            'certifications': candidate.get('entities', {}).get('certifications', []),
            'score': candidate['score'],
            'skills': candidate.get('entities', {}).get('skills', []),
            'experience': candidate.get('entities', {}).get('experience', [])
        }
        
        recommendations = RecommendationEngine.generate_candidate_recommendations(
            cv_analysis, 
            st.session_state.get('job_description', '')
        )
        
        # Generate smart interview questions
        interview_qs = RecommendationEngine.generate_interviewer_questions(
            cv_analysis,
            st.session_state.get('job_description', '')
        )
        
        with st.expander(f"📄 {candidate['filename']} - {seniority} ({experience_years:.1f} ans) - Score: {candidate['score']:.2%}"):
            # Quick stats
            stats_cols = st.columns(4)
            with stats_cols[0]:
                st.metric("🏅 Rang", f"#{i+1}")
            with stats_cols[1]:
                st.metric("⭐ Score", f"{candidate['score']:.1%}")
            with stats_cols[2]:
                st.metric("💼 Expérience", f"{experience_years:.1f} ans")
            with stats_cols[3]:
                st.metric("🎯 Confiance", f"{candidate['confidence']:.0%}")
            
            # Justification
            st.markdown("### 🔍 Analyse LLM")
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
            
            # Recommendations for candidate
            if recommendations:
                st.markdown("### 💡 Recommandations pour le candidat")
                for rec in recommendations:
                    st.info(rec)
            
            # Compétences manquantes
            if candidate['missing_skills']:
                st.markdown("### ⚠️ Compétences manquantes")
                missing_cols = st.columns(3)
                for idx, skill in enumerate(candidate['missing_skills'][:9]):
                    with missing_cols[idx % 3]:
                        st.markdown(f"- **{skill}**")
            
            # Smart interview questions
            if interview_qs:
                st.markdown("### ❓ Questions d'entretien intelligentes")
                for q in interview_qs:
                    with st.container():
                        st.markdown(f"**{q['category']}**: {q['question']}")
                        st.caption(f"🎯 {q['focus']}")
            
            # Entités extraites
            if 'entities' in candidate and candidate['entities']:
                st.markdown("### 📋 Entités extraites")
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

def show_comparison_page():
    """Affiche la page de comparaison détaillée des candidats."""
    st.header("🔍 Mode Comparaison des Candidats")
    
    if not st.session_state.ranking_done:
        st.warning("⚠️ Veuillez d'abord effectuer une analyse dans la section 'Configuration'.")
        st.info("💡 Le mode comparaison permet de comparer côte-à-côte plusieurs CVs pour la même offre d'emploi.")
        return
    
    ranked = st.session_state.ranked_candidates
    
    if len(ranked) < 2:
        st.warning("⚠️ Au moins 2 candidats sont nécessaires pour la comparaison.")
        return
    
    st.markdown("""
    ### 📊 Comparaison Multi-Candidats
    Comparez en détail les candidats pour identifier les meilleurs matchs et prendre des décisions éclairées.
    """)
    
    # Job description from session or file
    try:
        job_desc_path = "data/job_descriptions/description_poste.txt"
        with open(job_desc_path, 'r', encoding='utf-8') as f:
            job_description = f.read()
    except:
        job_description = ""
    
    # Initialize comparison engine
    comparison_engine = CVComparisonEngine(job_description)
    comparison = comparison_engine.compare_candidates(ranked)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Vue Globale", 
        "🎯 Matrice de Comparaison", 
        "💡 Insights", 
        "🔧 Compétences",
        "📋 Recommandation"
    ])
    
    with tab1:
        st.subheader("🏆 Classement et Scores")
        
        # Visual ranking
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Score comparison bar chart
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            # Add traces for each scoring method
            fig.add_trace(go.Bar(
                name='TF-IDF',
                x=[c['filename'] for c in ranked[:10]],
                y=[c.get('detailed_scores', {}).get('tfidf', 0) for c in ranked[:10]],
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                name='Mots-clés',
                x=[c['filename'] for c in ranked[:10]],
                y=[c.get('detailed_scores', {}).get('keyword', 0) for c in ranked[:10]],
                marker_color='lightgreen'
            ))
            fig.add_trace(go.Bar(
                name='LLM',
                x=[c['filename'] for c in ranked[:10]],
                y=[c.get('detailed_scores', {}).get('llm', 0) for c in ranked[:10]],
                marker_color='lightcoral'
            ))
            
            fig.update_layout(
                title='Comparaison des Scores par Méthode (Top 10)',
                barmode='group',
                height=400,
                xaxis_title='Candidats',
                yaxis_title='Score',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("Candidats Analysés", len(ranked))
            st.metric("Score Moyen", f"{sum(c['score'] for c in ranked) / len(ranked):.1%}")
        
        with col3:
            excellent = len([c for c in ranked if c['score'] >= 0.8])
            good = len([c for c in ranked if 0.6 <= c['score'] < 0.8])
            st.metric("Excellents (≥80%)", excellent)
            st.metric("Bons (60-80%)", good)
        
        # Detailed ranking table
        st.subheader("📋 Classement Détaillé")
        
        ranking_df = pd.DataFrame([{
            'Rang': i+1,
            'Candidat': c['filename'],
            'Score Global': f"{c['score']:.1%}",
            'TF-IDF': f"{c.get('detailed_scores', {}).get('tfidf', 0):.1%}",
            'Keywords': f"{c.get('detailed_scores', {}).get('keyword', 0):.1%}",
            'LLM': f"{c.get('detailed_scores', {}).get('llm', 0):.1%}",
            'Confiance': f"{c['confidence']:.1%}",
            'Compétences': len(c.get('entities', {}).get('skills', [])),
            'Manquantes': len(c.get('missing_skills', []))
        } for i, c in enumerate(ranked)])
        
        st.dataframe(ranking_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("🎯 Matrice de Comparaison")
        
        st.markdown("""
        Comparez rapidement tous les candidats sur les dimensions clés.
        """)
        
        # Display comparison matrix
        st.dataframe(
            comparison.comparison_matrix.style.background_gradient(
                subset=['Score Global', 'Confiance', 'TF-IDF', 'Mots-clés', 'LLM'],
                cmap='RdYlGn'
            ),
            use_container_width=True,
            hide_index=True
        )
        
        # Heatmap visualization
        st.subheader("🔥 Carte de Chaleur des Performances")
        
        numeric_cols = ['Score Global', 'TF-IDF', 'Mots-clés', 'LLM', 'Confiance']
        heatmap_data = comparison.comparison_matrix[['Candidat'] + numeric_cols].set_index('Candidat')
        
        fig = px.imshow(
            heatmap_data.T,
            labels=dict(x="Candidats", y="Métriques", color="Score"),
            color_continuous_scale='RdYlGn',
            aspect="auto",
            text_auto='.2f'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Download matrix
        st.download_button(
            label="📥 Télécharger la Matrice (CSV)",
            data=comparison.comparison_matrix.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"matrice_comparaison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader("💡 Insights et Découvertes")
        
        # Display insights by type
        insight_types = {
            'strength': ('💪 Points Forts', 'green'),
            'unique': ('⭐ Compétences Uniques', 'blue'),
            'weakness': ('⚠️ Points Attention', 'orange'),
            'common': ('🔄 Éléments Communs', 'gray')
        }
        
        for insight_type, (label, color) in insight_types.items():
            type_insights = [i for i in comparison.insights if i.insight_type == insight_type]
            if type_insights:
                st.markdown(f"### {label}")
                for insight in type_insights:
                    importance_bar = "🔥" * int(insight.importance * 5)
                    st.markdown(f"""
                    <div style="background-color: rgba(0,0,0,0.05); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {color};">
                        <strong>{insight.candidate}</strong><br>
                        {insight.description}<br>
                        <small>Importance: {importance_bar} ({insight.importance:.0%})</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Statistical insights
        st.subheader("📈 Statistiques de Groupe")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_skills = comparison.comparison_matrix['Nb Compétences'].mean()
            st.metric("Compétences Moyennes", f"{avg_skills:.1f}")
            
        with col2:
            avg_exp = comparison.comparison_matrix['Nb Expériences'].mean()
            st.metric("Expériences Moyennes", f"{avg_exp:.1f}")
        
        with col3:
            avg_missing = comparison.comparison_matrix['Compétences Manquantes'].mean()
            st.metric("Gaps Moyens", f"{avg_missing:.1f}")
    
    with tab4:
        st.subheader("🔧 Analyse des Compétences")
        
        # Skill coverage
        st.markdown("### 📊 Couverture des Compétences")
        
        skill_data = []
        for skill, candidates in list(comparison.skill_comparison.items())[:20]:
            coverage = len(candidates) / len(ranked) * 100
            skill_data.append({
                'Compétence': skill,
                'Nb Candidats': len(candidates),
                'Couverture': f"{coverage:.0f}%",
                'Candidats': ', '.join(candidates[:3]) + ('...' if len(candidates) > 3 else '')
            })
        
        skill_df = pd.DataFrame(skill_data)
        
        # Bar chart of skill coverage
        fig = px.bar(
            skill_df.head(15),
            x='Compétence',
            y='Nb Candidats',
            title='Top 15 Compétences les Plus Fréquentes',
            labels={'Nb Candidats': 'Nombre de Candidats'},
            color='Nb Candidats',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed skill table
        st.dataframe(skill_df, use_container_width=True, hide_index=True)
        
        # Unique skills per candidate
        st.markdown("### ⭐ Compétences Distinctives par Candidat")
        
        for candidate in ranked[:5]:  # Top 5
            candidate_skills = set([s.lower() for s in candidate.get('entities', {}).get('skills', [])])
            other_skills = set()
            for other in ranked:
                if other['filename'] != candidate['filename']:
                    other_skills.update([s.lower() for s in other.get('entities', {}).get('skills', [])])
            
            unique = candidate_skills - other_skills
            if unique:
                st.markdown(f"**{candidate['filename']}:** {', '.join(list(unique)[:5])}")
    
    with tab5:
        st.subheader("📋 Recommandation Finale")
        
        # Display recommendation
        st.markdown(comparison.recommendation)
        
        # Export options
        st.subheader("💾 Export des Résultats")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Exporter Comparaison Excel", key="export_excel"):
                try:
                    output_path = f"output/comparaison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    comparison_engine.export_comparison(comparison, output_path)
                    st.success(f"✅ Comparaison exportée: {output_path}")
                    
                    # Provide download
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="📥 Télécharger Excel",
                            data=f.read(),
                            file_name=os.path.basename(output_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'export: {e}")
        
        with col2:
            # Download recommendation as text
            recommendation_text = comparison.recommendation
            st.download_button(
                label="📄 Télécharger Recommandation (TXT)",
                data=recommendation_text.encode('utf-8'),
                file_name=f"recommandation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        # Action buttons
        st.subheader("🎯 Actions Rapides")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Préparer Emails", key="prepare_emails"):
                st.info("Fonctionnalité à venir: Génération automatique d'emails de contact")
        
        with col2:
            if st.button("📅 Planifier Entretiens", key="schedule_interviews"):
                st.info("Fonctionnalité à venir: Intégration calendrier")
        
        with col3:
            if st.button("📊 Générer Rapport Complet", key="full_report"):
                st.info("Fonctionnalité à venir: Rapport PDF personnalisé")

if __name__ == "__main__":
    main()