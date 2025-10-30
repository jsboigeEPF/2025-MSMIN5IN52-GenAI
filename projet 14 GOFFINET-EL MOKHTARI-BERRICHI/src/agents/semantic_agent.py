import json
import os
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

load_dotenv()

async def process_prompt_to_json(prompt: str, doc_type: str) -> dict:
    """
    Utilise Semantic Kernel + OpenAI pour transformer un texte libre
    en données structurées JSON selon le type de document (cv, invoice, report).
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Clé API OpenAI manquante. Vérifie ton fichier .env")

        # === Initialisation du kernel ===
        kernel = sk.Kernel()

        # Ajout du service OpenAI
        kernel.add_service(
            OpenAIChatCompletion(
                service_id="openai-chat",
                ai_model_id="gpt-4o-mini",  # tu peux tester "gpt-4-turbo" si tu veux plus de cohérence
                api_key=api_key,
            )
        )

        # === Prompt template dynamique selon doc_type ===
        if doc_type.lower() == "cv":
            full_prompt = f"""
Tu es un assistant structuré. Transforme le texte suivant en JSON VALIDE correspondant au modèle suivant :

{{
  "personal": {{
    "name": "Nom complet",
    "email": "Email",
    "phone": "Téléphone",
    "location": "Localisation"
  }},
  "experience": [
    {{
      "title": "Titre du poste",
      "company": "Nom de l’entreprise",
      "date": "Période",
      "description": "Résumé des missions"
    }}
  ],
  "education": [
    {{
      "institution": "Nom de l’école",
      "degree": "Diplôme obtenu",
      "date": "Année"
    }}
  ],
  "skills": ["Compétence 1", "Compétence 2", "Compétence 3"]
}}

Texte à transformer :
---
{prompt}
---

⚠️ Réponds uniquement avec du JSON bien formaté (aucun texte avant ou après).
"""

        elif doc_type.lower() in ["report", "rapport"]:
            full_prompt = f"""
Tu es un assistant structuré. Transforme le texte suivant en JSON VALIDE correspondant au modèle suivant :

{{
  "title": "Titre du rapport",
  "author": {{
    "name": "Nom complet",
    "email": "Adresse email",
    "organization": "Organisation"
  }},
  "date": "AAAA-MM-JJ",
  "summary": "Résumé du rapport",
  "content": [
    {{
      "section_title": "Titre de la section",
      "section_content": "Contenu textuel de la section"
    }}
  ]
}}

Texte à transformer :
---
{prompt}
---

⚠️ Réponds uniquement avec du JSON bien formaté (aucun texte avant ou après).
"""

        elif doc_type.lower() in ["invoice", "facture"]:
            full_prompt = f"""
Tu es un assistant structuré. Transforme le texte suivant en JSON VALIDE correspondant au modèle suivant :

{{
  "invoice_id": "INV-0001",
  "date": "AAAA-MM-JJ",
  "seller": {{
    "name": "Nom de l’entreprise",
    "address": "Adresse du vendeur",
    "email": "Email du vendeur"
  }},
  "buyer": {{
    "name": "Nom du client",
    "address": "Adresse du client",
    "email": "Email du client"
  }},
  "items": [
    {{
      "description": "Nom du produit ou service",
      "quantity": 1,
      "unit_price": 100.0
    }}
  ],
  "tax_rate": 20,
  "notes": "Informations complémentaires"
}}

Texte à transformer :
---
{prompt}
---

⚠️ Réponds uniquement avec du JSON bien formaté (aucun texte avant ou après).
"""

        else:
            raise ValueError(f"Type de document non reconnu : {doc_type}")

        # === Appel direct du modèle ===
        result = await kernel.invoke_prompt(full_prompt, service_id="openai-chat")

        # === Nettoyage et conversion du résultat en JSON ===
        text = str(result).strip()
        try:
            structured = json.loads(text)
        except json.JSONDecodeError:
            structured = json.loads(text[text.find("{") : text.rfind("}") + 1])

        return structured

    except Exception as e:
        raise ValueError(f"Erreur dans le Semantic Agent : {str(e)}")
