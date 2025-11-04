import streamlit as st
import pandas as pd
import glob, os
import matplotlib.pyplot as plt
from auditor.scoring import aggregate

st.set_page_config(page_title="LLM Bias Auditor Dashboard", layout="wide")
st.title("🧠 LLM Bias Auditor — Tableau interactif")

run_files = sorted(glob.glob("data/results/runs/run_*.csv"))
if not run_files:
    st.warning("Aucun résultat trouvé. Exécutez d'abord: python -m src.scripts.run_all")
else:
    latest = run_files[-1]
    st.sidebar.success(f"Résultats: {os.path.basename(latest)}")
    df = pd.read_csv(latest)

    st.subheader("Aperçu des données")
    st.dataframe(df.head())

    st.subheader("📊 Moyennes par groupe")
    agg_df = aggregate(df)
    st.dataframe(agg_df)

    st.subheader("📈 Visualisation des biais (bar chart)")
    metric = st.selectbox("Choisissez une métrique:", ["sentiment", "refusal", "hedge_ratio", "length", "negative"])
    fig, ax = plt.subplots()
    ax.bar(agg_df["group"], agg_df[metric])
    ax.set_title(f"Moyenne de {metric} par groupe")
    plt.xticks(rotation=15)
    st.pyplot(fig)

    st.subheader("📉 Distribution des scores individuels")
    fig2, ax2 = plt.subplots()
    df[metric].hist(bins=20, ax=ax2)
    ax2.set_title(f"Distribution de {metric}")
    st.pyplot(fig2)
