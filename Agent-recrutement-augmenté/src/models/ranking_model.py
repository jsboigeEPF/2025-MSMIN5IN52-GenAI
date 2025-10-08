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
                    "skills": 0.45,
                    "experience": 0.35,
                    "education": 0.15,
                    "certifications": 0.05
                },
                "confidence_threshold": 0.5
            }
        }

def compute_match_score(cv_text: str, job_description: str, cv_entities: Dict = None) -> Dict[str, float]:
    """
    Calcule un score de correspondance entre un CV et une description de poste
    en utilisant une approche hybride LLM + algorithmique.
    
    Args:
        cv_text (str): Texte extrait du CV.
        job_description (str): Description du poste.
    
    Returns:
        Dict[str, float]: Dictionnaire contenant le score (0-1), la confiance et le raisonnement.
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
        
        # Parser la réponse JSON
        import json
        try:
            result = json.loads(response)
            llm_score = float(result.get("score", 0.0))
            llm_confidence = float(result.get("confidence", 0.5))
            reasoning = result.get("reasoning", "")
            
            # Calculer le score algorithmique
            algo_score = _text_similarity_score(cv_text, job_description)
            
            # Fusionner les scores avec pondération adaptative
            # Plus le LLM est confiant, plus on lui fait confiance
            if llm_confidence >= config["scoring"]["confidence_threshold"]:
                # Approche hybride: combiner LLM et algorithme
                final_score = (llm_score * 0.7) + (algo_score * 0.3)
                final_confidence = llm_confidence
            else:
                # Si faible confiance du LLM, privilégier l'approche algorithmique
                final_score = (llm_score * 0.3) + (algo_score * 0.7)
                final_confidence = algo_score * 0.8  # Confiance basée sur le score algorithmique
            
            return {
                "score": min(final_score, 1.0),
                "confidence": min(final_confidence, 1.0),
                "reasoning": reasoning + f"\n\n[Score hybride: LLM={llm_score:.3f} (confiance={llm_confidence:.3f}), Algorithme={algo_score:.3f}, Score final={final_score:.3f}]"
            }
            
        except json.JSONDecodeError:
            # En cas d'erreur de parsing, utiliser uniquement le scoring algorithmique
            score = _text_similarity_score(cv_text, job_description)
            return {"score": score, "confidence": 0.3, "reasoning": "Évaluation basée sur la similarité de texte des mots-clés."}
            
    except Exception as e:
        print(f"Erreur lors de l'évaluation avec LLM: {e}")
        # Fallback: scoring basé sur la similarité de texte
        score = _text_similarity_score(cv_text, job_description)
        return {"score": score, "confidence": 0.2, "reasoning": "Évaluation basée sur la similarité de texte des mots-clés en raison d'une erreur avec le modèle LLM."}

def _text_similarity_score(cv_text: str, job_description: str) -> float:
    """
    Score de similarité amélioré utilisant TF-IDF et correspondance sémantique.
    """
    if not cv_text or not job_description:
        return 0.0
    
    # Extraire les mots-clés de la description de poste
    job_keywords = _extract_keywords_from_job_description(job_description)
    
    # Prétraitement du texte
    def preprocess_text(text: str) -> set:
        # Convertir en minuscules et enlever la ponctuation basique
        words = text.lower().replace(',', '').replace('.', '').replace(';', '').replace(':', '').split()
        # Filtrer les mots vides (stop words) simples
        stop_words = {'le', 'la', 'les', 'de', 'du', 'des', 'et', 'en', 'un', 'une', 'dans', 'sur', 'par', 'pour', 'avec', 'sans', 'qui', 'que', 'quoi', 'où', 'quand', 'comment', 'pourquoi', 'ce', 'cette', 'ces', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs', 'il', 'elle', 'ils', 'elles', 'je', 'tu', 'nous', 'vous', 'on', 'me', 'te', 'se', 'nous', 'vous', 'leur', 'y', 'en', 'ci', 'ça', 'cela', 'ceci', 'celui', 'celle', 'ceux', 'celles', 'même', 'même', 'tout', 'toute', 'tous', 'toutes', 'autre', 'autres', 'quel', 'quelle', 'quels', 'quelles', 'quelque', 'quelques', 'aucun', 'aucune', 'aucuns', 'aucunes', 'plusieurs', 'chaque', 'chacun', 'chacune', 'tout', 'toute', 'tous', 'toutes', 'mien', 'mienne', 'miens', 'miennes', 'tien', 'tienne', 'tiens', 'tiennes', 'sien', 'sienne', 'siens', 'siennes', 'nôtre', 'nôtre', 'nôtres', 'nôtres', 'vôtre', 'vôtre', 'vôtres', 'vôtres', 'leur', 'leur', 'leurs', 'leurs'}
        return set(word for word in words if word not in stop_words and len(word) > 2)
    
    cv_processed = preprocess_text(cv_text)
    job_processed = preprocess_text(' '.join(job_keywords))
    
    # Calculer la similarité TF-IDF pondérée
    if len(job_processed) == 0:
        return 0.0
    
    # Trouver les mots communs
    common_words = cv_processed.intersection(job_processed)
    
    # Calculer le score TF-IDF (approche simplifiée)
    tfidf_score = 0.0
    total_weight = 0.0
    
    # Poids des mots basés sur leur importance dans le domaine
    keyword_weights = {
        'python': 1.5, 'java': 1.5, 'spring': 1.4, 'sap': 1.4, 'erp': 1.3,
        'machine learning': 1.5, 'devops': 1.3, 'agile': 1.2, 'scrum': 1.2,
        'aws': 1.4, 'docker': 1.3, 'kubernetes': 1.4, 'postgresql': 1.3,
        'react': 1.3, 'angular': 1.3, 'javascript': 1.2, 'c++': 1.2, 'c#': 1.2,
        'microservices': 1.3, 'api': 1.1, 'rest': 1.1, 'ci/cd': 1.2,
        'gitlab': 1.1, 'github': 1.1, 'linux': 1.1, 'git': 1.1
    }
    
    for word in common_words:
        # Trouver le mot exact ou une variante dans les mots-clés
        word_weight = 1.0
        for keyword, weight in keyword_weights.items():
            if keyword in word or word in keyword:
                word_weight = weight
                break
        tfidf_score += word_weight
        total_weight += word_weight
    
    # Normaliser par le nombre total de mots-clés pertinents dans la description
    max_possible_score = sum(keyword_weights.get(kw, 1.0) for kw in job_keywords)
    if max_possible_score > 0:
        normalized_tfidf = tfidf_score / max_possible_score
    else:
        normalized_tfidf = 0.0
    
    # Score de correspondance exacte des mots-clés
    exact_match_ratio = len(common_words) / len(job_processed) if job_processed else 0.0
    
    # Score de complétude (combien de mots-clés du poste sont couverts)
    coverage_ratio = len(common_words) / len(job_processed) if job_processed else 0.0
    
    # Score final combiné avec pondérations optimisées
    final_score = (
        normalized_tfidf * 0.5 +    # Score TF-IDF pondéré
        exact_match_ratio * 0.3 +   # Correspondance exacte
        coverage_ratio * 0.2        # Complétude
    )
    
    return min(final_score, 1.0)

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
    # Extraire les mots-clés de la description de poste
    job_keywords = _extract_keywords_from_job_description(job_description)
    
    # Obtenir les compétences du candidat
    candidate_skills = set([skill.lower() for skill in cv_entities.get('skills', [])])
    
    # Identifier les compétences manquantes
    missing = []
    for skill in job_keywords:
        # Vérifier si la compétence est requise dans la description et absente du CV
        if skill not in candidate_skills and skill in job_description.lower():
            # Formater correctement le nom de la compétence
            formatted_skill = skill.title()
            if formatted_skill not in missing:
                missing.append(formatted_skill)
    
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

def _extract_keywords_from_job_description(job_description: str) -> List[str]:
    """
    Extrait les mots-clés pertinents de la description de poste.
    
    Args:
        job_description (str): Description du poste
        
    Returns:
        List[str]: Liste des mots-clés extraits
    """
    # Convertir en minuscules
    text = job_description.lower()
    
    # Mots-clés techniques à extraire
    technical_keywords = [
        'python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'sql', 'nosql',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'git', 'machine learning',
        'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch', 'keras',
        'scikit-learn', 'pandas', 'numpy', 'react', 'angular', 'vue', 'node.js',
        'django', 'flask', 'spring', 'hadoop', 'spark', 'kafka', 'airflow', 'jenkins',
        'ansible', 'postgresql', 'mongodb', 'mysql', 'redis', 'elasticsearch',
        'sap', 'erp', 'devops', 'agile', 'scrum', 'microservices', 'api', 'rest',
        'graphql', 'ci/cd', 'gitlab', 'github', 'jenkins', 'terraform', 'ansible',
        'prometheus', 'grafana', 'kubernetes', 'docker', 'aws', 'azure', 'gcp'
    ]
    
    # Extraire les mots-clés présents dans la description
    found_keywords = []
    for keyword in technical_keywords:
        if keyword in text:
            found_keywords.append(keyword)
    
    # Retirer les doublons et trier
    return list(set(found_keywords))