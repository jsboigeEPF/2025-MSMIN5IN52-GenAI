import sys
sys.dont_write_bytecode = True

import streamlit as st
import numpy as np

def render(document_list: list, meta_data: dict, time_elapsed: float):
  retriever_message = st.expander(f"Mode détaillé / Explications")
  message_map = {
    "retrieve_applicant_jd": "**Une description de poste a été détectée**. Le système utilise automatiquement le mode RAG.",
    "retrieve_applicant_id": "**Des IDs candidats ont été fournis**. Le système utilise une récupération directe par ID.",
    "no_retrieve": "**Aucune recherche de CV nécessaire pour cette requête**. Le système s'appuie sur l’historique de conversation."
  }

  with retriever_message:
    st.markdown(f"Temps total écoulé : {np.round(time_elapsed, 3)} secondes")
    st.markdown(f"{message_map[meta_data['query_type']]}")

    if meta_data["query_type"] == "retrieve_applicant_jd":
      st.markdown(f"Utilisation du mode {meta_data['rag_mode']} pour la recherche.")
      st.markdown(f"Retour des 5 CV les plus similaires.")

      button_columns = st.columns([0.2, 0.2, 0.2, 0.2, 0.2], gap="small")
      for index, document in enumerate(document_list[:5]):
        with button_columns[index], st.popover(f"CV {index + 1}"):
          st.markdown(document)

      st.markdown(f"**Requête extraite** :\n`{meta_data['extracted_input']}`\n")
      st.markdown(f"**Sous-questions générées** :\n`{meta_data['subquestion_list']}`")
      st.markdown(f"**Scores de re-classement des documents** :\n`{meta_data['retrieved_docs_with_scores']}`")

    elif meta_data["query_type"] == "retrieve_applicant_id":
      st.markdown(f"Utilisation de l’ID candidat pour la récupération.")

      button_columns = st.columns([0.2, 0.2, 0.2, 0.2, 0.2], gap="small")
      for index, document in enumerate(document_list[:5]):
        with button_columns[index], st.popover(f"CV {index + 1}"):
          st.markdown(document)

      st.markdown(f"**Requête extraite** :\n`{meta_data['extracted_input']}`\n")

if __name__ == "__main__":
  render(sys.argv[1], sys.argv[2])
