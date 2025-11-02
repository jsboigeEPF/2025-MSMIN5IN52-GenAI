import sys, os
sys.dont_write_bytecode = True

import time
from dotenv import load_dotenv

import pandas as pd
import streamlit as st
import openai
from streamlit_modal import Modal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy
from langchain_community.embeddings import HuggingFaceEmbeddings

from llm_agent import ChatBot
from ingest_data import ingest
from retriever import SelfQueryRetriever
import chatbot_verbosity as chatbot_verbosity

# ==============================================
# ✅ CONFIG PAGE
# ==============================================
load_dotenv()
st.set_page_config(page_title="Assistant IA de Sélection de CV", page_icon="🤖", layout="wide")

DATA_PATH = os.getenv("DATA_PATH")
FAISS_PATH = os.getenv("FAISS_PATH")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# ==============================================
# 🎨 ✅ CUSTOM THEME (Violet Pastel)
# ==============================================
custom_css = """
<style>
/* App Background */
body, .stApp {
    background-color: #FFFFFF !important;
    color: #2E2E2E !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #F7ECFF !important;
    border-right: 2px solid #8A2BE2 !important;
}

/* Buttons */
button {
    background-color: #8A2BE2 !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
}

/* Inputs */
textarea, input, .stTextInput>div>div>input {
    background-color: #FFFFFF !important;
    border: 1px solid #8A2BE2 !important;
    border-radius: 10px !important;
}

/* Chat message bubbles */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 12px !important;
}

/* Titles */
h1, h2, h3 {
    color: #8A2BE2 !important;
    font-weight: bold !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================
# ✅ INTRO MESSAGE
# ==============================================
welcome_message = """
#### Introduction 🚀

Ce projet est un prototype étudiant basé sur une approche RAG (Retrieval-Augmented Generation) pour assister les recruteurs dans l’analyse et la présélection de CV.

Il permet d’identifier automatiquement les candidats les plus pertinents en fonction d'une fiche de poste grâce à :
- une recherche sémantique pour trouver les CV les plus proches de l’offre,
- un modèle de langage (LLM) pour analyser les profils et générer des recommandations.

#### Comment utiliser 🛠️

1️⃣ Entrez votre clé API OpenAI 🔑  
2️⃣ Tapez une description de poste 💬  
3️⃣ Téléchargez un fichier CSV de CV 📄  

Vous pouvez maintenant échanger avec l'assistant et demander des recommandations de candidats !
"""

st.title("Assistant IA de Sélection de CV 🤖📄")

# ==============================================
# ✅ SESSION STATE INIT
# ==============================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [AIMessage(content=welcome_message)]

if "df" not in st.session_state:
    st.session_state.df = pd.read_csv(DATA_PATH)

if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})

if "rag_pipeline" not in st.session_state:
    vectordb = FAISS.load_local(FAISS_PATH, st.session_state.embedding_model, distance_strategy=DistanceStrategy.COSINE, allow_dangerous_deserialization=True)
    st.session_state.rag_pipeline = SelfQueryRetriever(vectordb, st.session_state.df)

if "resume_list" not in st.session_state:
    st.session_state.resume_list = []

# ==============================================
# ✅ UPLOAD FILE
# ==============================================
def upload_file():
    modal = Modal(key="Erreur fichier", title="Erreur fichier", max_width=500)
    if st.session_state.uploaded_file != None:
        try:  
            df_load = pd.read_csv(st.session_state.uploaded_file)
        except Exception as error:
            with modal.container():
                st.markdown("Erreur lors de la lecture du fichier. Vérifiez votre CSV.")
                st.error(error)
        else:
            if "Resume" not in df_load.columns or "ID" not in df_load.columns:
                with modal.container():
                    st.error("Votre fichier doit contenir les colonnes : \"Resume\" et \"ID\".")
            else:
                with st.toast('Indexation des CV… merci de patienter ⏳'):
                    st.session_state.df = df_load
                    vectordb = ingest(st.session_state.df, "Resume", st.session_state.embedding_model)
                    st.session_state.rag_pipeline = SelfQueryRetriever(vectordb, st.session_state.df)
    else:
        st.session_state.df = pd.read_csv(DATA_PATH)
        vectordb = FAISS.load_local(FAISS_PATH, st.session_state.embedding_model, distance_strategy=DistanceStrategy.COSINE, allow_dangerous_deserialization=True)
        st.session_state.rag_pipeline = SelfQueryRetriever(vectordb, st.session_state.df)

# ==============================================
# ✅ API KEY CHECK
# ==============================================
def check_openai_api_key(api_key: str):
    openai.api_key = api_key
    try:
        _ = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Bonjour"}],
            max_tokens=3
        )
        return True
    except openai.AuthenticationError:
        return False

# ==============================================
# ✅ CLEAR CHAT
# ==============================================
def clear_message():
    st.session_state.resume_list = []
    st.session_state.chat_history = [AIMessage(content=welcome_message)]

# ==============================================
# ✅ SIDEBAR UI
# ==============================================
with st.sidebar:
    st.markdown("### Paramètres ⚙️")
    st.text_input("Clé API OpenAI", type="password", key="api_key")
    st.selectbox("Mode RAG", ["Générique RAG", "RAG Fusion"], key="rag_selection")
    st.text_input("Modèle GPT", "gpt-4o-mini", key="gpt_selection")
    st.file_uploader("Importer des CV (CSV)", type=["csv"], key="uploaded_file", on_change=upload_file)
    st.button("Réinitialiser la conversation", on_click=clear_message)

# ==============================================
# ✅ CHAT HISTORY DISPLAY
# ==============================================
for message in st.session_state.chat_history:
    role = "AI" if isinstance(message, AIMessage) else "Humain"
    with st.chat_message(role):
        st.write(message.content)

# ==============================================
# ✅ API KEY VALIDATION
# ==============================================
if not st.session_state.api_key:
    st.info("Veuillez entrer votre clé API OpenAI pour continuer.")
    st.stop()

if not check_openai_api_key(st.session_state.api_key):
    st.error("❌ Clé API invalide. Veuillez entrer une clé valide.")
    st.stop()

# ==============================================
# ✅ RUN CHATBOT
# ==============================================
retriever = st.session_state.rag_pipeline
llm = ChatBot(api_key=st.session_state.api_key, model=st.session_state.gpt_selection)

user_query = st.chat_input("Écrivez votre message ici...")

if user_query:
    with st.chat_message("Humain"):
        st.markdown(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("AI"):
        start = time.time()
        with st.spinner("Analyse en cours…"):
            document_list = retriever.retrieve_docs(user_query, llm, st.session_state.rag_selection)
            query_type = retriever.meta_data["query_type"]
            st.session_state.resume_list = document_list
            stream_message = llm.generate_message_stream(user_query, document_list, [], query_type)

        response = st.write_stream(stream_message)
        end = time.time()

        retriever_message = chatbot_verbosity
        retriever_message.render(document_list, retriever.meta_data, end-start)

        st.session_state.chat_history.append(AIMessage(content=response))
        st.session_state.chat_history.append((retriever_message, document_list, retriever.meta_data, end-start))
