# LLM Bias Auditor — Groupe Projet13-XinerGU

Projet : Audit de biais pour modèles de langage via prompts **contre-factuels** (A/B univariés).
Fournisseur principal : **OpenAI**（mock en option pour contrôle）.

## Démarrage rapide
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # Renseigner OPENAI_API_KEY=sk-...
python -m src.scripts.run_all   # Exécuter un audit complet
python -m src.scripts.export_report  # Exporter graphiques & distributions

# Lancer le tableau de bord Streamlit
streamlit run src/scripts/dashboard.py
```
Sorties :
- `data/results/runs/run_*.csv`
- `data/results/reports/<run_id>/*.png`
