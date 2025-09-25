"""
Application Streamlit pour l'Agent de Recrutement Augmenté.
"""

import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
from src.parsers.cv_parser import load_all_cvs
from src.models.ranking_model import rank_candidates, load_config
from src.utils.report_generator import generate_csv_report, generate_html_report

def main():
    st.set_page_config(page_title="Agent de Recrutement Augmenté", layout="wide")
    st.title("📊 Agent de Recrutement Augmenté")
    st.markdown("Comparez des CVs à une description de poste et obtenez un classement intelligent.")

    # Section 1: Téléchargement des CVs
    st.header("1. Téléchargez les CVs")
    uploaded_files = st.file_uploader("Téléchargez les CVs (PDF/DOCX)", accept_multiple_files=True, type=["pdf", "docx"])
    
    cv_folder = "data/cv_samples"
    if not os.path.exists(cv_folder):
        os.makedirs(cv_folder)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(cv_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"{len(uploaded_files)} CV(s) téléchargé(s) avec succès !")

    # Section 2: Description du poste
    st.header("2. Description du poste")
    job_description = st.text_area("Entrez la description du poste", height=200)
    job_desc_path = "data/job_descriptions/description_poste.txt"
    
    if job_description:
        if not os.path.exists("data/job_descriptions"):
            os.makedirs("data/job_descriptions")
        with open(job_desc_path, "w", encoding="utf-8") as f:
            f.write(job_description)
        st.success("Description du poste enregistrée !")

    # Section 3: Lancer l'analyse
    st.header("3. Lancer l'analyse")
    # Section de configuration
    st.header("🔧 Configuration")
    config = load_config()
    
    col1, col2 = st.columns(2)
    with col1:
        model_name = st.selectbox(
            "Modèle LLM",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"].index(config["model"]["name"]) if config["model"]["name"] in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"] else 0
        )
        
        temperature = st.slider(
            "Température",
            0.0, 1.0,
            float(config["model"]["temperature"]),
            0.1,
            help="Contrôle la créativité du modèle. Plus la valeur est élevée, plus les réponses sont créatives."
        )
    
    with col2:
        st.markdown("Poids des critères de scoring:")
        weights = {}
        weights["skills"] = st.slider("Compétences", 0.0, 1.0, float(config["scoring"]["weights"]["skills"]), 0.05)
        weights["experience"] = st.slider("Expérience", 0.0, 1.0, float(config["scoring"]["weights"]["experience"]), 0.05)
        weights["education"] = st.slider("Éducation", 0.0, 1.0, float(config["scoring"]["weights"]["education"]), 0.05)
        weights["certifications"] = st.slider("Certifications", 0.0, 1.0, float(config["scoring"]["weights"]["certifications"]), 0.05)
        
        # Normaliser les poids pour qu'ils totalisent 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
    
    # Mettre à jour la configuration
    config["model"]["name"] = model_name
    config["model"]["temperature"] = temperature
    config["scoring"]["weights"] = weights
    
    # Sauvegarder la configuration
    if not os.path.exists("config"):
        os.makedirs("config")
    with open("config/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    if st.button("🎯 Lancer le classement"):
        if not os.listdir(cv_folder):
            st.error("Veuillez d'abord télécharger au moins un CV.")
        elif not job_description:
            st.error("Veuillez entrer une description de poste.")
        else:
            with st.spinner("Analyse en cours..."):
                # Charger les CVs
                cvs = load_all_cvs(cv_folder)
                if not cvs:
                    st.error("Aucun CV valide chargé. Vérifiez les formats.")
                else:
                    # Classer les candidats
                    ranked = rank_candidates(cvs, job_description)
                    
                    # Générer les rapports
                    csv_output = "docs/ranking_report.csv"
                    html_output = "docs/ranking_report.html"
                    generate_csv_report(ranked, csv_output)
                    generate_html_report(ranked, html_output)
                    
                    # Afficher les résultats
                    st.success("Analyse terminée !")
                    st.subheader("Résultats du classement")
                    # Afficher les résultats avec des visualisations
                    st.subheader("Analyse des compétences")
                    
                    # Créer un graphique des compétences
                    import pandas as pd
                    import plotly.express as px
                    
                    # Extraire les compétences pour le graphique
                    skills_data = []
                    for candidate in ranked:
                        if 'entities' in candidate and 'skills' in candidate['entities']:
                            for skill in candidate['entities']['skills']:
                                skills_data.append({
                                    'Candidat': candidate['filename'],
                                    'Compétence': skill,
                                    'Score': candidate['score']
                                })
                    
                    if skills_data:
                        df_skills = pd.DataFrame(skills_data)
                        fig = px.bar(df_skills, x='Candidat', y='Compétence', color='Score',
                                   title="Compétences par candidat",
                                   color_continuous_scale='viridis')
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Afficher le classement
                    st.subheader("Classement des candidats")
                    df_ranked = pd.DataFrame(ranked)
                    df_ranked_display = df_ranked[['filename', 'score']].copy()
                    df_ranked_display.columns = ['Candidat', 'Score']
                    df_ranked_display['Score'] = df_ranked_display['Score'].apply(lambda x: f"{x:.2%}")
                    
                    st.dataframe(df_ranked_display, use_container_width=True)
                    
                    # Afficher les justifications
                    st.subheader("Justifications détaillées")
                    for i, candidate in enumerate(ranked):
                        with st.expander(f"📄 {candidate['filename']} (Score: {candidate['score']:.2%})"):
                            st.markdown(candidate['justification'])
                            
                            # Afficher les compétences manquantes
                            if 'missing_skills' in candidate and candidate['missing_skills']:
                                st.markdown("**Compétences manquantes:**")
                                st.write(", ".join(candidate['missing_skills']))
                            
                            # Afficher les questions d'entretien
                            if 'interview_questions' in candidate and candidate['interview_questions']:
                                st.markdown("**Questions d'entretien suggérées:**")
                                for question in candidate['interview_questions']:
                                    st.write(f"• {question}")
                    
                    # Téléchargement des rapports
                    st.subheader("Télécharger les rapports")
                    col1, col2 = st.columns(2)
                    with col1:
                        with open(csv_output, "rb") as f:
                            st.download_button("📥 Télécharger CSV", f, file_name="ranking_report.csv", mime="text/csv")
                    with col2:
                        with open(html_output, "rb") as f:
                            st.download_button("📥 Télécharger HTML", f, file_name="ranking_report.html", mime="text/html")

    # Section 4: Informations
    st.header("4. Informations")
    st.info("""
    - Les CVs sont stockés temporairement dans `data/cv_samples/`
    - La description du poste est sauvegardée dans `data/job_descriptions/`
    - Les rapports sont générés dans `docs/`
    - Le scoring sémantique sera implémenté dans les prochaines étapes
    """)

if __name__ == "__main__":
    main()