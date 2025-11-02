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

        kernel = sk.Kernel()

        kernel.add_service(
            OpenAIChatCompletion(
                service_id="openai-chat",
                ai_model_id="gpt-4o-mini",
                api_key=api_key,
            )
        )

        # === Prompt template dynamique selon doc_type ===
        if doc_type.lower() == "cv":
            full_prompt = f"""
Tu es un assistant structuré. Transforme le texte suivant en JSON VALIDE correspondant au modèle suivant :

{{
  "personal_info": {{
    "name": "Nom complet",
    "birth_date": "Date de naissance au format AAAA-MM-JJ ou null",
    "email": "Email",
    "phone": "Téléphone",
    "address": "Adresse complète",
    "city": "Ville",
    "country": "Pays",
    "linkedin": "URL LinkedIn ou null",
    "portfolio": "URL du portfolio ou null",
    "photo": "Nom du fichier photo si présent"
  }},
  "summary": "Courte présentation du profil professionnel si présente",
  "work_experience": [
    {{
      "title": "Titre du poste",
      "company": "Nom de l’entreprise",
      "location": "Ville/Pays",
      "start_date": "Mois Année",
      "end_date": "Mois Année ou 'Présent'",
      "description": "Résumé des missions principales"
    }}
  ],
  "education": [
    {{
      "institution": "Nom de l’école",
      "degree": "Diplôme obtenu",
      "start_year": "Année de début",
      "end_year": "Année de fin",
      "location": "Ville/Pays"
    }}
  ],
  "projects": [
    {{
      "name": "Nom du projet personnel ou académique",
      "year": "Année du projet",
      "description": "Brève description du projet",
      "technologies": ["Tech1", "Tech2", "Tech3"]
    }}
  ],
  "skills": {{
    "frontend": ["HTML", "CSS", "JavaScript", "React", "etc."],
    "backend": ["Node.js", "Express", "Django", "etc."],
    "databases": ["MySQL", "MongoDB", "etc."],
    "devops": ["Docker", "GitHub Actions", "AWS", "etc."],
    "tools": ["Git", "Figma", "Postman", "Jira", "etc."]
  }},
  "languages": [
    {{
      "language": "Nom de la langue",
      "level": "Niveau (A1–C2 ou équivalent)"
    }}
  ],
  "certifications": [
    {{
      "name": "Nom de la certification",
      "organization": "Organisme émetteur",
      "year": "Année d’obtention"
    }}
  ],
  "interests": ["Centre d’intérêt 1", "Centre d’intérêt 2", "Centre d’intérêt 3"]
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
  "title": "Titre du rapport (ex: Rapport de stage – Digital D3A)",
  "subtitle": "Sous-titre décrivant le contexte ou le sujet (ex: Développement d’un site vitrine pour la plateforme Digital D3A)",
  "author": {{
    "name": "Nom complet de l’auteur (ex: Thomas Dupont)",
    "organization": "Nom de l’établissement ou entreprise (ex: Université Grenoble Alpes ou Digital D3A)"
  }},
  "date": "Date de fin ou de rédaction (AAAA-MM-JJ)",
  "summary": "Résumé synthétique du rapport",
  "content": [
    {{
      "section_title": "Titre de la section (ex: Contexte du stage)",
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
Tu es un assistant structuré. Analyse attentivement le texte suivant et transforme-le en JSON VALIDE correspondant au modèle ci-dessous.

Le JSON doit **contenir toutes les informations présentes** : numéro de facture, dates, entreprises, TVA, articles, montants HT/TTC, coordonnées bancaires, pénalités, etc.

Modèle attendu :
{{
  "invoice_number": "Numéro de la facture (ex: WS-2025-112)",
  "issue_date": "Date d’émission (AAAA-MM-JJ)",
  "due_date": "Date limite de paiement (AAAA-MM-JJ)",
  "seller": {{
    "name": "Nom complet de l’entreprise émettrice",
    "address": "Adresse complète du vendeur",
    "siret": "Numéro SIRET si présent",
    "vat_number": "Numéro de TVA intracommunautaire si présent",
    "email": "Adresse email de contact",
    "phone": "Numéro de téléphone",
    "bank": {{
      "bank_name": "Nom de la banque",
      "account_holder": "Titulaire du compte",
      "iban": "IBAN complet",
      "bic": "BIC"
    }}
  }},
  "client": {{
    "name": "Nom de l’entreprise cliente",
    "contact_person": "Nom du contact principal",
    "email": "Email du contact principal",
    "address": "Adresse complète du client",
    "siret": "Numéro SIRET si présent",
    "vat_number": "Numéro de TVA intracommunautaire si présent"
  }},
  "items": [
    {{
      "description": "Description de la prestation ou du produit",
      "quantity": 1,
      "unit_price_ht": 0.0,
      "total_ht": 0.0
    }}
  ],
  "subtotal_ht": 0.0,
  "tax_rate": 0.0,
  "tax_amount": 0.0,
  "total_ttc": 0.0,
  "currency": "EUR",
  "payment_terms": "Conditions de paiement (ex: virement sous 30 jours)",
  "late_penalties": {{
    "rate": "Taux de pénalité (ex: 10% par mois de retard)",
    "fixed_fee": "Montant forfaitaire (ex: 40 euros)",
    "legal_reference": "Référence légale (ex: article L441-10 du Code de commerce)"
  }},
  "notes": "Informations complémentaires ou remarques de la facture"
}}

Texte à transformer :
---
{prompt}
---

⚠️ Règles importantes :
- N’invente rien : extrais uniquement les données réellement présentes.
- Utilise des formats numériques pour les montants (ex: 1940.0, 388.0, 2328.0).
- Convertis les dates en format ISO (AAAA-MM-JJ).
- Réponds uniquement avec du JSON valide, sans texte avant ni après.
"""


        else:
            raise ValueError(f"Type de document non reconnu : {doc_type}")

        result = await kernel.invoke_prompt(full_prompt, service_id="openai-chat")

        text = str(result).strip()
        try:
            structured = json.loads(text)
        except json.JSONDecodeError:
            structured = json.loads(text[text.find("{"): text.rfind("}") + 1])

        # ✅ fallback automatique
        if "personal" in structured and "personal_info" not in structured:
            structured["personal_info"] = structured.pop("personal")

        return structured

    except Exception as e:
        raise ValueError(f"Erreur dans le Semantic Agent : {str(e)}")
