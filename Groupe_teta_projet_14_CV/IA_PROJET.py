# app_recruteur_augmente.py
# -------------------------------------------------------------
# Application Streamlit 100% en français : comparaison CV ↔ offre
# -------------------------------------------------------------
# Lancer :
#   1) pip install -r requirements.txt
#   2) Créer un fichier .env avec OPENAI_API_KEY=sk-...
#   3) streamlit run app_recruteur_augmente.py
#
# Fonctionnalités :
# - Importer plusieurs CV (PDF/DOCX/TXT) + une offre (coller du texte ou fichier)
# - Interface claire (onglets), zone Paramètres améliorée et persistante
# - Scoring LLM avec sortie JSON structurée (score global + sous-scores)
# - Curseurs de pondération, choix FR/EN, température
# - Tableau de classement + fiches candidates
# - Export CSV / JSONL / Rapport Markdown
# - Bouton “Tester la clé OpenAI” dans Paramètres
# -------------------------------------------------------------

import os
import io
import json
import time
import tempfile
import datetime as dt
from typing import Dict, Any, List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# --- Lecture fichiers ---
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    import docx2txt
except Exception:
    docx2txt = None

# --- Client OpenAI (SDK v1) ---
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# ================== CONFIG UI ==================
st.set_page_config(
    page_title="Agent de Recrutement Augmenté",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS léger
st.markdown(
    """
    <style>
      .gradient-bg {
        background: linear-gradient(135deg, #0ea5e9 0%, #9333ea 100%);
        padding: 18px 22px; border-radius: 18px; color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
      }
      .score-badge { font-weight:700; font-size:20px; padding:6px 10px; border-radius:12px; background:#eef2ff; display:inline-block; }
      .ok { background:#dcfce7; }
      .warn { background:#fef9c3; }
      .bad { background:#fee2e2; }
      .footer-note { color:#64748b; font-size:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="gradient-bg">
      <h1 style="margin:0">Agent de Recrutement Augmenté</h1>
      <p style="margin:4px 0 0 0">Compare automatiquement des CV à une offre et produit un classement justifié.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ================== ENV & ÉTAT ==================
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY", "")

# Valeurs par défaut des paramètres (persistants via session_state)
if "params" not in st.session_state:
    st.session_state.params = {
        "modele": "gpt-4o-mini",
        "temperature": 0.2,
        "langue": "Français",
        "w_comp": 35,
        "w_exp": 35,
        "w_edu": 15,
        "w_culture": 15,
    }

# ================== OUTILS ==================
def lire_fichier(upload) -> str:
    """Convertit le fichier importé en texte brut (PDF/DOCX/TXT)."""
    if upload is None:
        return ""
    nom = upload.name.lower()
    data = upload.read()

    if nom.endswith(".txt"):
        for enc in ("utf-8", "latin-1"):
            try:
                return data.decode(enc, errors="ignore")
            except Exception:
                continue
        return data.decode("utf-8", errors="ignore")

    if nom.endswith(".pdf"):
        if PdfReader is None:
            return "[Erreur] PyPDF2 n'est pas installé."
        try:
            reader = PdfReader(io.BytesIO(data))
            txt = []
            for p in reader.pages:
                txt.append(p.extract_text() or "")
            return "\n".join(txt).strip()
        except Exception as e:
            return f"[Erreur PDF] {e}"

    if nom.endswith(".docx"):
        if docx2txt is None:
            return "[Erreur] docx2txt n'est pas installé."
        try:
            # docx2txt attend un chemin : on passe par un fichier temp.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            contenu = docx2txt.process(tmp_path) or ""
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            return contenu.strip()
        except Exception as e:
            return f"[Erreur DOCX] {e}"

    return "[Erreur] Format non supporté (PDF, DOCX ou TXT)."

def normaliser_poids(p: Dict[str, int]) -> Dict[str, float]:
    total = sum(p.values())
    if total <= 0:
        return {k: 0.0 for k in p}
    return {k: (v / total) * 100.0 for k, v in p.items()}

def classe_couleur(score: int) -> str:
    if score >= 75: return "ok"
    if score >= 55: return "warn"
    return "bad"

def appeler_llm(texte_offre: str, texte_cv: str, poids: Dict[str, float],
                modele: str, temperature: float, langue: str) -> Dict[str, Any]:
    if OpenAI is None:
        raise RuntimeError("Le package 'openai' n'est pas installé (pip install openai).")
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY introuvable. Ajoute-le dans .env.")

    client = OpenAI(api_key=API_KEY)

    # Instructions FR/EN — retour JSON strict
    fr = f"""
Tu es un recruteur IA. Compare ce CV avec l'offre. Utilise ces pondérations (somme=100) :
- skills={poids['skills']:.1f}%
- experience={poids['experience']:.1f}%
- education={poids['education']:.1f}%
- culture={poids['culture']:.1f}%

Renvoie UNIQUEMENT du JSON valide selon ce schéma :
{{
  "overall": int,
  "breakdown": {{
    "skills": int,
    "experience": int,
    "education": int,
    "culture": int,
    "keywords_coverage": int
  }},
  "highlights": ["..."],
  "gaps": ["..."],
  "short_summary": "2-3 lignes en français",
  "verdict": "go" | "maybe" | "no"
}}

Rappels :
- Évalue compétences/outils, pertinence de l'expérience, formation, soft skills.
- "keywords_coverage" = % des mots clés essentiels de l'offre retrouvés dans le CV.
- Sois factuel pour "highlights" et "gaps".
"""
    en = f"""
You are an AI recruiter. Compare this resume with the job post. Use weights (sum=100):
- skills={poids['skills']:.1f}%
- experience={poids['experience']:.1f}%
- education={poids['education']:.1f}%
- culture={poids['culture']:.1f}%

Return ONLY strict JSON with this schema:
{{
  "overall": int,
  "breakdown": {{
    "skills": int,
    "experience": int,
    "education": int,
    "culture": int,
    "keywords_coverage": int
  }},
  "highlights": ["..."],
  "gaps": ["..."],
  "short_summary": "2-3 lines in English",
  "verdict": "go" | "maybe" | "no"
}}
"""
    system = fr if langue == "Français" else en
    messages = [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"=== OFFRE ===\n{texte_offre}\n\n=== CV ===\n{texte_cv}\n\nRéponds en JSON uniquement, sans texte autour."}
    ]

    reponse = client.chat.completions.create(
        model=modele,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    brut = reponse.choices[0].message.content
    try:
        return json.loads(brut)
    except Exception:
        # secours : tentative d'extraction du bloc JSON
        i, j = brut.find("{"), brut.rfind("}")
        return json.loads(brut[i:j+1])

# ================== PARAMÈTRES (SIDEBAR) ==================
with st.sidebar:
    st.subheader("Paramètres")

    if API_KEY:
        st.caption("🔑 Clé OpenAI trouvée dans .env")
    else:
        st.caption("❌ Clé absente (.env)")

    with st.form("form_params", clear_on_submit=False):
        modele = st.selectbox(
            "Modèle OpenAI",
            ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
            index=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"].index(st.session_state.params["modele"])
        )
        temperature = st.slider("Créativité (température)", 0.0, 1.2, st.session_state.params["temperature"], 0.05)
        langue = st.radio("Langue d'analyse", ["Français", "English"],
                          index=0 if st.session_state.params["langue"] == "Français" else 1)

        st.divider()
        st.caption("Pondération des critères (sera normalisée à 100)")
        w_comp = st.slider("Compétences techniques", 0, 100, st.session_state.params["w_comp"], 5)
        w_exp = st.slider("Expérience", 0, 100, st.session_state.params["w_exp"], 5)
        w_edu = st.slider("Formation", 0, 100, st.session_state.params["w_edu"], 5)
        w_culture = st.slider("Culture & Soft skills", 0, 100, st.session_state.params["w_culture"], 5)

        submitted = st.form_submit_button("Appliquer les paramètres", use_container_width=True)

    # Persistance explicite
    if submitted:
        st.session_state.params.update({
            "modele": modele,
            "temperature": temperature,
            "langue": langue,
            "w_comp": w_comp,
            "w_exp": w_exp,
            "w_edu": w_edu,
            "w_culture": w_culture,
        })
        st.success("Paramètres appliqués.")

    # Petit test de la clé (optionnel, non bloquant)
    if st.button("Tester la clé OpenAI", use_container_width=True):
        try:
            if OpenAI is None:
                raise RuntimeError("Le package 'openai' n'est pas installé.")
            if not API_KEY:
                raise RuntimeError("OPENAI_API_KEY manquant.")
            client = OpenAI(api_key=API_KEY)
            _ = client.chat.completions.create(
                model=st.session_state.params["modele"],
                messages=[{"role": "system", "content": "Réponds en JSON uniquement."},
                          {"role": "user", "content": "Donne {\"ok\": true}"}],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            st.success("Connexion OK ✅")
        except Exception as e:
            st.error(f"Échec de la connexion : {e}")

    total_w = (
        st.session_state.params["w_comp"]
        + st.session_state.params["w_exp"]
        + st.session_state.params["w_edu"]
        + st.session_state.params["w_culture"]
    )
    if total_w == 0:
        st.warning("Les poids ne peuvent pas tous être à 0.")
    else:
        st.caption(f"Somme actuelle des poids : **{total_w}** (normalisée automatiquement)")

# ================== ONGLET CONTENU ==================
onglet_import, onglet_resultats, onglet_apropos = st.tabs(["Importer", "Résultats", "À propos"])

with onglet_import:
    st.markdown("### 1) Offre d’emploi")
    col_offre, col_fichier = st.columns([2, 1], gap="large")
    with col_offre:
        offre_txt = st.text_area(
            "Collez la fiche de poste",
            height=220,
            placeholder="Description, missions, compétences requises, mots-clés…",
        )
    with col_fichier:
        fichier_offre = st.file_uploader("…ou charger un fichier (PDF/DOCX/TXT)",
                                         type=["pdf", "docx", "txt"], accept_multiple_files=False, key="offre_file")
        if fichier_offre is not None:
            lu = lire_fichier(fichier_offre)
            if lu and not offre_txt:
                offre_txt = lu
                st.success("Offre importée depuis le fichier.")
            elif lu:
                st.info("Contenu du fichier chargé. Cochez pour remplacer le texte saisi manuellement.")
                if st.checkbox("Remplacer par le contenu du fichier"):
                    offre_txt = lu

    st.markdown("### 2) CV des candidats")
    fichiers_cv = st.file_uploader("Charger 1..N CV (PDF/DOCX/TXT)",
                                   type=["pdf", "docx", "txt"], accept_multiple_files=True, key="cv_files")
    cvs_parses: List[Dict[str, str]] = []
    if fichiers_cv:
        for f in fichiers_cv:
            cvs_parses.append({"filename": f.name, "text": lire_fichier(f)})
        st.success(f"{len(cvs_parses)} CV importé(s).")

    st.markdown("### 3) Lancer la comparaison")
    lancer = st.button("Lancer l’analyse", type="primary", use_container_width=True)

    if lancer:
        if not offre_txt or len(offre_txt.strip()) < 30:
            st.error("Ajoutez une offre d’emploi (≥ 30 caractères).")
        elif not cvs_parses:
            st.error("Chargez au moins un CV.")
        elif (st.session_state.params["w_comp"] + st.session_state.params["w_exp"]
              + st.session_state.params["w_edu"] + st.session_state.params["w_culture"]) == 0:
            st.error("Ajustez les pondérations (non nulles).")
        else:
            poids_norm = normaliser_poids({
                "skills": st.session_state.params["w_comp"],
                "experience": st.session_state.params["w_exp"],
                "education": st.session_state.params["w_edu"],
                "culture": st.session_state.params["w_culture"],
            })

            lignes = []
            cartes = []
            barre = st.progress(0.0, text="Analyse des CV…")

            for i, item in enumerate(cvs_parses, start=1):
                try:
                    data = appeler_llm(
                        texte_offre=offre_txt,
                        texte_cv=item["text"],
                        poids=poids_norm,
                        modele=st.session_state.params["modele"],
                        temperature=st.session_state.params["temperature"],
                        langue=st.session_state.params["langue"],
                    )
                    br = data.get("breakdown", {})
                    lignes.append({
                        
                        "cv": item["filename"],
                        "overall": int(data.get("overall", 0)),
                        "skills": int(br.get("skills", 0)),
                        "experience": int(br.get("experience", 0)),
                        "education": int(br.get("education", 0)),
                        "culture": int(br.get("culture", 0)),
                        "keywords_coverage": int(br.get("keywords_coverage", 0)),
                        "verdict": data.get("verdict", ""),
                        "short_summary": data.get("short_summary", ""),
                        "highlights": " • ".join(data.get("highlights", [])),
                        "gaps": " • ".join(data.get("gaps", [])),

                        
                    })
                    
                    cartes.append((item["filename"], data))
                except Exception as e:
                    lignes.append({
                        "cv": item["filename"], "overall": 0, "skills": 0, "experience": 0, "education": 0,
                        "culture": 0, "keywords_coverage": 0, "verdict": "error",
                        "short_summary": f"Erreur: {e}", "highlights": "", "gaps": ""
                    })
                barre.progress(i / len(cvs_parses), text=f"Analyse {i}/{len(cvs_parses)}")
                time.sleep(0.05)

            st.session_state["results_df"] = pd.DataFrame(lignes)
            st.session_state["cards"] = cartes
            st.session_state["job_text"] = offre_txt

            st.success("Analyse terminée. Ouvrez l’onglet **Résultats**.")

with onglet_resultats:
    st.subheader("Classement des candidats")
    df = st.session_state.get("results_df")
    cartes = st.session_state.get("cards") or []

    # Rappel des paramètres actifs
    p = st.session_state.params
    st.caption(
        f"Modèle **{p['modele']}**, Température **{p['temperature']}**, Langue **{p['langue']}** — "
        f"Pondérations (normalisées) Comp:{p['w_comp']} / Exp:{p['w_exp']} / Form:{p['w_edu']} / Culture:{p['w_culture']}"
    )

    if df is None or df.empty:
        st.info("Pas encore de résultats. Allez dans l’onglet *Importer* pour lancer une analyse.")
    else:
        df_sorted = df.sort_values("overall", ascending=False).reset_index(drop=True)
        st.dataframe(
            df_sorted.style.format({
                "overall": "{:d}", "skills": "{:d}", "experience": "{:d}",
                "education": "{:d}", "culture": "{:d}", "keywords_coverage": "{:d}"
            })
        )

        # Exports
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "Exporter CSV",
                df_sorted.to_csv(index=False).encode("utf-8"),
                file_name="resultats.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c2:
            jsonl = "\n".join(df_sorted.apply(lambda r: json.dumps(r.to_dict(), ensure_ascii=False), axis=1).tolist())
            st.download_button(
                "Exporter JSONL",
                jsonl.encode("utf-8"),
                file_name="resultats.jsonl",
                mime="application/json",
                use_container_width=True,
            )
        with c3:
            maintenant = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
            md = [f"# Rapport de matching — {maintenant}\n"]
            if st.session_state.get("job_text"):
                md.append("## Offre d’emploi\n")
                md.append("```\n" + st.session_state["job_text"].strip()[:8000] + "\n```\n")
            md.append("## Classement\n")
            for i, (fname, _) in enumerate(cartes, start=1):
                ligne = df_sorted[df_sorted["cv"] == fname].iloc[0]
                md.append(f"### {i}. {fname} — Score {ligne['overall']}\n")
                md.append(f"- Verdict : **{ligne['verdict']}**")
                md.append(f"- Résumé : {ligne['short_summary']}")
                md.append(f"- Points forts : {ligne['highlights']}")
                md.append(f"- Lacunes : {ligne['gaps']}\n")
            st.download_button(
                "Exporter Rapport (Markdown)",
                "\n".join(md).encode("utf-8"),
                file_name="rapport_matching.md",
                mime="text/markdown",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown("### Fiches candidates")
        cols = st.columns(3)
        for idx, (fname, data) in enumerate(cartes):
            with cols[idx % 3]:
                br = data.get("breakdown", {})
                score = int(data.get("overall", 0))
                st.markdown(f"**{fname}**")
                st.markdown(
                    f"<span class='score-badge {classe_couleur(score)}'>Score {score}</span>",
                    unsafe_allow_html=True
                )
                st.caption(f"Verdict : {data.get('verdict', '')}")
                couv = int(br.get("keywords_coverage", 0))
                st.progress(couv / 100.0, text=f"Couverture mots-clés : {couv}%")
                with st.expander("Détails du scoring"):
                    st.write(br)
                with st.expander("Points forts"):
                    st.write(data.get("highlights", []))
                with st.expander("Lacunes / Risques"):
                    st.write(data.get("gaps", []))
                st.write(f"_{data.get('short_summary', '')}_")

with onglet_apropos:
    st.markdown(
        """
**Comment ça marche ?**  
- Le LLM lit l’offre et le CV puis renvoie un JSON (score global + détails).  
- Ajustez les poids à gauche pour modifier la grille d’évaluation.  
- Export possible en CSV / JSONL / Markdown.

**Conseils**  
- Détaillez correctement l’offre (missions, stack, soft skills).  
- En cas d’extraction PDF médiocre, préférez DOCX/TXT.  
- Combinez l’outil avec des entretiens pour la décision finale.

_Bâti avec Streamlit + OpenAI._
"""
    )
    st.markdown("<p class='footer-note'>© 2025 – Recruteur Augmenté</p>", unsafe_allow_html=True)