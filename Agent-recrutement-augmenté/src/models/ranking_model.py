"""
Module pour le classement des candidats basé sur LangChain et OpenAI.
"""

from typing import List, Dict
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Configuration de l'API OpenAI
# Assurez-vous d'avoir défini la variable d'environnement OPENAI_API_KEY
# export OPENAI_API_KEY='votre_cle_api'

import json
import os
from typing import List, Dict, Optional

def load_config(config_path: str = "config/config.json") -> Dict:
    """
    Charge la configuration depuis un fichier JSON.
    
    Args:
        config_path (str): Chemin vers le fichier de configuration
        
    Returns:
        Dict: Configuration chargée
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        # Configuration par défaut
        return {
            "model": {
                "name": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 1000
            },
            "scoring": {
                "weights": {
                    "skills": 0.4,
                    "experience": 0.3,
                    "education": 0.2,
                    "certifications": 0.1
                },
                "confidence_threshold": 0.5
            }
        }

def compute_match_score(cv_text: str, job_description: str, cv_entities: Dict = None) -> Dict[str, float]:
    """
    Calcule un score de correspondance entre un CV et une description de poste
    en utilisant un modèle de langage (LLM) via LangChain.
    
    Args:
        cv_text (str): Texte extrait du CV.
        job_description (str): Description du poste.
    
    Returns:
        Dict[str, float]: Dictionnaire contenant le score (0-1) et la confiance.
    """
    try:
        # Charger la configuration
        config = load_config()
        
        # Initialiser le modèle LLM avec la configuration
        llm = ChatOpenAI(
            model=config["model"]["name"],
            temperature=config["model"]["temperature"],
            max_tokens=config["model"]["max_tokens"]
        )
        
        # Créer un prompt pour évaluer la correspondance
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Vous êtes un expert en recrutement.
            Votre tâche est d'évaluer la correspondance entre un CV et une description de poste.
            Analysez les compétences, l'expérience, l'éducation et les certifications du candidat
            par rapport aux exigences du poste.
            
            Donnez un score de correspondance entre 0 et 1, où:
            - 0 = aucune correspondance
            - 0.5 = correspondance partielle
            - 1 = correspondance parfaite
            
            Expliquez votre raisonnement en détail, en mentionnant:
            - Les compétences clés du poste présentes dans le CV
            - Les compétences clés du poste manquantes
            - L'expérience pertinente
            - L'éducation et les certifications pertinentes
            - Tout autre point fort ou faible
            
            Répondez UNIQUEMENT avec un objet JSON contenant:
            - score: le score de correspondance
            - confidence: votre niveau de confiance dans l'évaluation (0-1)
            - reasoning: votre raisonnement détaillé"""),
            ("human", """Description du poste:
            {job_description}
            
            CV du candidat:
            {cv_text}
            
            {entities_context}
            
            Répondez avec un objet JSON uniquement.""")
        ])
        
        # Créer la chaîne de traitement
        chain = prompt | llm | StrOutputParser()
        
        # Préparer le contexte des entités si disponibles
        entities_context = ""
        if cv_entities:
            entities_context = "\nInformations structurées extraites du CV:\n"
            for entity_type, entities in cv_entities.items():
                if entities:  # Ne pas inclure les listes vides
                    entities_context += f"- {entity_type}: {entities}\n"
        
        # Exécuter la chaîne
        response = chain.invoke({
            "job_description": job_description,
            "cv_text": cv_text,
            "entities_context": entities_context
        })
        
        # Parser la réponse JSON (simplifié - dans un cas réel, utiliser un vrai parser JSON)
        # Exemple de réponse attendue: {"score": 0.85, "confidence": 0.92}
        import json
        try:
            result = json.loads(response)
            return {
                "score": float(result.get("score", 0.0)),
                "confidence": float(result.get("confidence", 0.5)),
                "reasoning": result.get("reasoning", "")
            }
        except json.JSONDecodeError:
            # En cas d'erreur de parsing, retourner un score par défaut basé sur la similarité de texte
            score = _text_similarity_score(cv_text, job_description)
            return {"score": score, "confidence": 0.3, "reasoning": "Évaluation basée sur la similarité de texte des mots-clés."}
            
    except Exception as e:
        print(f"Erreur lors de l'évaluation avec LLM: {e}")
        # Fallback: scoring basé sur la similarité de texte
        score = _text_similarity_score(cv_text, job_description)
        return {"score": score, "confidence": 0.2, "reasoning": "Évaluation basée sur la similarité de texte des mots-clés en raison d'une erreur avec le modèle LLM."}

def _text_similarity_score(cv_text: str, job_description: str) -> float:
    """
    Score de similarité basé sur les mots-clés communs (fallback).
    """
    if not cv_text or not job_description:
        return 0.0
        
    # Convertir en minuscules et enlever la ponctuation basique
    cv_words = set(cv_text.lower().replace(',', '').replace('.', '').split())
    job_words = set(job_description.lower().replace(',', '').replace('.', '').split())
    
    # Trouver les mots communs
    common_words = cv_words.intersection(job_words)
    
    # Score basé sur la proportion de mots du poste présents dans le CV
    if len(job_words) == 0:
        return 0.0
        
    keyword_match_ratio = len(common_words) / len(job_words)
    
    # Bonus pour les mots-clés importants (à personnaliser selon le domaine)
    important_keywords = {'python', 'machine learning', 'expérience', 'compétences', 'diplôme'}
    important_matches = len(common_words.intersection(important_keywords))
    important_bonus = min(important_matches * 0.1, 0.3)
    
    return min(keyword_match_ratio * 0.7 + important_bonus, 1.0)

def rank_candidates(cvs: List[Dict[str, str]], job_description: str) -> List[Dict[str, str]]:
    """
    Classe les candidats selon leur score de correspondance.
    
    Args:
        cvs (List[Dict[str, str]]): Liste des CVs parsés.
        job_description (str): Description du poste.
    
    Returns:
        List[Dict[str, str]]: Liste des candidats classés avec scores et justifications.
    """
    ranked = []
    for cv in cvs:
        # Obtenir le score et la confiance
        cv_entities = cv.get("entities", {})
        result = compute_match_score(cv["text"], job_description, cv_entities)
        score = result["score"]
        confidence = result["confidence"]
        
        # Générer une justification détaillée
        justification = f"Score de correspondance : {score:.2%}\n"
        justification += f"Niveau de confiance de l'évaluation : {confidence:.2%}\n"
        
        if confidence < 0.5:
            justification += "⚠️ Évaluation basée sur une similarité de texte en raison d'une erreur avec le modèle LLM."
        else:
            justification += "✅ Évaluation effectuée par un modèle de langage avancé."
            
            # Ajouter une analyse plus détaillée
            justification += "\n\nAnalyse détaillée:"
            
            # Extraire les compétences manquantes
            missing_skills = _identify_missing_skills(cv_entities, job_description)
            if missing_skills:
                justification += f"\n- Compétences manquantes importantes : {', '.join(missing_skills[:3])}"
                if len(missing_skills) > 3:
                    justification += f" (et {len(missing_skills) - 3} autres)"
            
            # Suggestions de questions d'entretien
            interview_questions = _generate_interview_questions(cv_entities, job_description)
            if interview_questions:
                justification += f"\n- Questions d'entretien suggérées :"
                for question in interview_questions[:2]:
                    justification += f"\n  • {question}"
                if len(interview_questions) > 2:
                    justification += f"\n  • ... ({len(interview_questions) - 2} autres suggestions)"
            
        ranked.append({
            "filename": cv["filename"],
            "score": score,
            "justification": justification,
            "entities": cv_entities
        })
    
    # Trier par score décroissant
    return sorted(ranked, key=lambda x: x["score"], reverse=True)

def _identify_missing_skills(cv_entities: Dict, job_description: str) -> List[str]:
    """
    Identifie les compétences manquantes par rapport à la description de poste.
    
    Args:
        cv_entities (Dict): Entités extraites du CV
        job_description (str): Description du poste
        
    Returns:
        List[str]: Liste des compétences manquantes
    """
    # Dans une version complète, on utiliserait un LLM pour analyser les compétences requises
    # Pour l'instant, utilisation d'une approche simple basée sur des mots-clés
    required_skills = {'python', 'machine learning', 'deep learning', 'nlp', 'computer vision',
                      'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'}
    
    candidate_skills = set([skill.lower() for skill in cv_entities.get('skills', [])])
    
    missing = []
    for skill in required_skills:
        if skill not in candidate_skills and skill in job_description.lower():
            missing.append(skill.title())
    
    return missing

def _generate_interview_questions(cv_entities: Dict, job_description: str) -> List[str]:
    """
    Génère des questions d'entretien pertinentes basées sur le CV et la description de poste.
    
    Args:
        cv_entities (Dict): Entités extraites du CV
        job_description (str): Description du poste
        
    Returns:
        List[str]: Liste de questions d'entretien suggérées
    """
    questions = []
    
    # Questions basées sur l'expérience
    if 'experience' in cv_entities and len(cv_entities['experience']) > 0:
        questions.append("Pourriez-vous décrire votre expérience la plus pertinente par rapport aux exigences du poste ?")
        questions.append("Quel a été votre plus grand défi dans votre poste précédent et comment l'avez-vous surmonté ?")
    
    # Questions basées sur les compétences
    if 'skills' in cv_entities:
        technical_skills = [s for s in cv_entities['skills'] if s.lower() in ['python', 'machine learning', 'nlp']]
        if technical_skills:
            questions.append(f"Pourriez-vous décrire un projet où vous avez utilisé {technical_skills[0]} ?")
    
    # Questions basées sur l'éducation
    if 'education' in cv_entities and len(cv_entities['education']) > 0:
        questions.append("Comment votre formation vous a-t-elle préparé pour ce poste ?")
    
    return questions