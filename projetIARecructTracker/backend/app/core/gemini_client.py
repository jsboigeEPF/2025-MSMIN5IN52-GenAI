"""
Client pour l'API Gemini (Google AI) - Fallback si Mistral échoue
"""
import os
import httpx
from typing import Dict, Any, Optional, List
from loguru import logger
from app.core.config import settings


class GeminiClient:
    """Client pour interagir avec l'API Gemini de Google"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = os.getenv("GEMINI_MODEL", "gemini-pro")
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
        
        if self.api_key:
            logger.info("Gemini AI client initialized successfully")
        else:
            logger.warning("GEMINI_API_KEY not found in environment variables")
    
    def is_available(self) -> bool:
        """Vérifier si le client Gemini est disponible"""
        return self.api_key is not None
    
    async def classify_text(
        self,
        text: str,
        categories: List[str],
        context: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Classifier un texte avec Gemini AI
        
        Args:
            text: Texte à classifier
            categories: Liste des catégories possibles
            context: Contexte/instructions pour la classification
            
        Returns:
            Dict avec category, confidence, reasoning
        """
        if not self.is_available():
            logger.warning("Gemini API key not configured")
            return None
        
        try:
            # Construire le prompt pour Gemini
            prompt = self._build_classification_prompt(text, categories, context)
            
            # Appel API Gemini
            url = f"{self.base_url}/models/{self.model}:generateContent"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    params={"key": self.api_key}
                )
                
                if response.status_code != 200:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                    return None
                
                result = response.json()
                
                # Extraire la réponse
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_classification_response(content, categories)
                
                logger.error("No valid response from Gemini API")
                return None
                
        except httpx.TimeoutException:
            logger.error("Gemini API timeout")
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini AI for classification: {str(e)}")
            return None
    
    def _build_classification_prompt(
        self,
        text: str,
        categories: List[str],
        context: str
    ) -> str:
        """Construire le prompt de classification pour Gemini"""
        
        prompt = f"""{context}

TEXTE À CLASSIFIER:
{text}

CATÉGORIES POSSIBLES: {', '.join(categories)}

INSTRUCTIONS:
Analyse ce texte et retourne UNIQUEMENT un JSON valide avec ce format exact:
{{
    "category": "LA_CATEGORIE_CHOISIE",
    "confidence": 0.XX,
    "reasoning": "Explication courte de ton choix"
}}

Réponds UNIQUEMENT avec le JSON, sans texte avant ou après.
"""
        return prompt
    
    def _parse_classification_response(
        self,
        response: str,
        categories: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Parser la réponse de Gemini pour extraire la classification"""
        try:
            import json
            import re
            
            # Extraire le JSON de la réponse (au cas où il y a du texte autour)
            json_match = re.search(r'\{[^}]*"category"[^}]*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Valider que la catégorie existe
                if result.get("category") in categories:
                    return {
                        "category": result.get("category"),
                        "confidence": float(result.get("confidence", 0.5)),
                        "reasoning": result.get("reasoning", "Classification by Gemini AI")
                    }
            
            logger.warning(f"Could not parse Gemini response: {response[:200]}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return None
    
    async def extract_entities(
        self,
        text: str,
        schema: Dict[str, Any],
        context: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Extraire des entités structurées d'un texte avec Gemini
        
        Args:
            text: Texte à analyser
            schema: Schéma des entités à extraire
            context: Contexte/instructions pour l'extraction
            
        Returns:
            Dict avec les entités extraites
        """
        if not self.is_available():
            return None
        
        try:
            prompt = f"""{context}

TEXTE À ANALYSER:
{text}

SCHÉMA D'EXTRACTION:
{schema}

INSTRUCTIONS:
Extrais les informations du texte selon le schéma fourni.
Retourne UNIQUEMENT un JSON valide avec les champs demandés.
Si une information n'est pas présente, mets null.

Réponds UNIQUEMENT avec le JSON, sans texte avant ou après.
"""
            
            url = f"{self.base_url}/models/{self.model}:generateContent"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens,
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    params={"key": self.api_key}
                )
                
                if response.status_code != 200:
                    logger.error(f"Gemini API error: {response.status_code}")
                    return None
                
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_json_response(content)
                
                return None
                
        except Exception as e:
            logger.error(f"Error calling Gemini AI for extraction: {str(e)}")
            return None
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parser une réponse JSON de Gemini"""
        try:
            import json
            import re
            
            # Extraire le JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
            return None


# Instance globale
gemini_client = GeminiClient()
