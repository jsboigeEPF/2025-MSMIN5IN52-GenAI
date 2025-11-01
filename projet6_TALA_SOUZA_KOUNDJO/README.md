# 🤖 Agent IA de Recrutement – Projet RAG & LLM

<p align="center">
  <img src="assets/interface.png" alt="Interface de l'assistant RAG" width="700">
</p>


## 📚 Contexte académique

Projet réalisé dans le cadre du module  
**GénAI – Intelligence Artificielle Générative**  
**EPF Paris-Cachan — Promotion 2025**

---

## 👥 Équipe – Groupe 6

| Membres |
|--------|
| Lamyae TALA |
| Marilson SOUZA |
| Brenda KOUNDJO |

---

## 🎯 Objectif

Développer un **assistant intelligent de recrutement** capable de :

- Lire une fiche de poste 💼  
- Extraire les compétences clés 🧠  
- Comparer automatiquement plusieurs CV 📄  
- Identifier les meilleurs profils ✅  
- Expliquer ses choix 🔍

Ce projet implémente une approche **RAG (Retrieval-Augmented Generation)** combinée à un **LLM** pour booster la présélection des candidats.

---

## ✨ Fonctionnalités

| Fonction | Description |
|--------|------------|
📎 Upload CSV | Liste de CV à analyser  
🔍 Recherche sémantique | Embeddings + FAISS  
🧠 RAG + RAG-Fusion | Génération de sous-requêtes  
💬 Chat IA | Interaction avec le recruteur  
📊 Classement | + Justification détaillée  

---

## 🏗️ Architecture du système

### Pipeline RAG

```mermaid
flowchart TD
A[CSV CVs] --> B[Embeddings HF]
B --> C[FAISS Index]
D[Fiche de poste] --> E[LLM - sous requêtes]
E --> F[Recherche + Fusion]
C --> F
F --> G[LLM Réponse + Justification]
```

---

## 🛠️ Stack Technique

| Composant | Technologie |
|---|---|
LLM | OpenAI GPT  
Embeddings | HuggingFace  
RAG Framework | LangChain  
Vector Store | FAISS  
Interface | Streamlit  
Données | CSV + Pandas  

---

## 📦 Installation

```bash
git clone <URL_DU_REPO>
cd projet6_TALA_SOUZA_KOUNDJO

python -m venv venv
venv\Scripts\activate   # Windows
# ou
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

---

## 🚀 Lancer l'application

```bash
streamlit run app.py
```

---

## 📂 Format CSV attendu

| ID | Resume |
|---|---|
| 101 | "Ingénieur Data, 3 ans d’expérience…" |
| 102 | "Développeur IA, NLP, Python…" |

> ⚠️ Le fichier doit obligatoirement contenir les colonnes **ID** et **Resume**

---

## ✅ Résultats attendus

- 🔝 Sélection des CV les plus pertinents  
- 📊 Classement des candidats  
- 🧾 Justification argumentée  
- 💬 Interface d’échange pour ajustement du besoin  

---

