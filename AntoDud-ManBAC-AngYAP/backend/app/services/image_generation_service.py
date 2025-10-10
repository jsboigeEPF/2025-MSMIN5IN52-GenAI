"""
Service de génération d'images pour les histoires interactives

Ce service gère la génération d'images illustrant les scènes narratives
en utilisant des modèles de diffusion (Stable Diffusion). Il est responsable de :
- Chargement et gestion du modèle de génération d'images
- Construction de prompts visuels à partir du contexte narratif
- Génération d'images cohérentes avec le style et le genre
- Optimisation et sauvegarde des images générées
- Gestion des erreurs et modes dégradés

Architecture :
- Singleton pattern pour éviter de recharger le modèle
- Cache des images générées pour éviter la regénération
- Support de différents backends (local, API externe)
"""

import asyncio
import time
import os
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime
from PIL import Image
import io
import base64

try:
    import torch
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    print("Warning: diffusers not available. Using mock image generation.")

from app.models.schemas import Story, Scene, StoryGenre
from app.config import settings


class ImageGenerationService:
    """
    Service de génération d'images pour les scènes narratives
    
    Ce service encapsule toute la logique de génération d'images :
    - Gestion du modèle Stable Diffusion
    - Construction de prompts visuels contextuels
    - Génération et optimisation d'images
    - Cache et sauvegarde des résultats
    """
    
    _instance = None
    _pipeline = None
    _model_loaded = False
    
    def __new__(cls):
        """
        Implémentation du pattern Singleton
        Évite de recharger le modèle coûteux à chaque instanciation
        """
        if cls._instance is None:
            cls._instance = super(ImageGenerationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialise le service de génération d'images
        Ne charge le modèle que si ce n'est pas déjà fait (Singleton)
        """
        if not hasattr(self, '_initialized'):
            self._initialized = True
            
            # Détection automatique du device
            self.device = self._detect_device(settings.IMAGE_MODEL_DEVICE)
            self.model_name = settings.IMAGE_MODEL_NAME
            self.images_path = settings.IMAGES_PATH
            
            print(f"🎨 Service d'images configuré - Device: {self.device}, Modèle: {self.model_name}")
            
            # Assurer que le répertoire d'images existe
            os.makedirs(self.images_path, exist_ok=True)
            
            # Paramètres de génération par défaut
            self.generation_params = {
                "width": 512,
                "height": 512,
                "num_inference_steps": 20,  # Balance qualité/vitesse
                "guidance_scale": 7.5,
                "num_images_per_prompt": 1,
                "generator": None  # Sera défini avec une seed
            }
            
            # Cache des images générées (évite regénération)
            self._image_cache = {}
            self._cache_max_size = 50
            
            # Templates de style par genre
            self._genre_styles = self._initialize_genre_styles()
            
            # Prompts négatifs par défaut
            self.negative_prompts = {
                "default": "blurry, low quality, distorted, deformed, text, watermark, signature, username, logo",
                "realistic": "cartoon, anime, painting, drawing, illustration, comic",
                "artistic": "photograph, photorealistic, realistic"
            }
    
    def _detect_device(self, device_setting: str) -> str:
        """
        Détecte automatiquement le meilleur device disponible
        
        Args:
            device_setting: Configuration du device ('auto', 'cuda', 'cpu')
            
        Returns:
            str: Device à utiliser ('cuda' ou 'cpu')
        """
        if device_setting.lower() == "auto":
            if DIFFUSERS_AVAILABLE and torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                print(f"🎮 CUDA détecté pour les images! GPU disponibles: {gpu_count}, Nom: {gpu_name}")
                return "cuda"
            else:
                print("💻 CUDA non disponible pour les images, utilisation du CPU")
                return "cpu"
        else:
            return device_setting.lower()
    
    async def initialize_model(self) -> bool:
        """
        Charge le modèle de génération d'images de manière asynchrone
        
        Returns:
            bool: True si le modèle est chargé avec succès
        """
        if self._model_loaded:
            return True
        
        if not DIFFUSERS_AVAILABLE:
            print("Diffusers non disponible. Mode simulation activé.")
            self._model_loaded = True
            return True
        
        try:
            print(f"Chargement du modèle d'images {self.model_name}...")
            start_time = time.time()
            
            # Chargement du pipeline Stable Diffusion avec paramètres plus compatibles
            pipeline_kwargs = {
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "safety_checker": None,
                "requires_safety_checker": False,
                "use_safetensors": True
            }
            
            self._pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_name,
                **pipeline_kwargs
            )
            
            # Optimisation du scheduler pour vitesse
            try:
                self._pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                    self._pipeline.scheduler.config
                )
            except Exception as scheduler_error:
                print(f"Avertissement: Impossible de configurer le scheduler optimisé: {scheduler_error}")
                # Continuer avec le scheduler par défaut
            
            # Déplacement sur le device approprié
            self._pipeline = self._pipeline.to(self.device)
            
            # Optimisations mémoire si CUDA (avec gestion d'erreur)
            if self.device == "cuda":
                try:
                    if hasattr(self._pipeline, 'enable_memory_efficient_attention'):
                        self._pipeline.enable_memory_efficient_attention()
                    if hasattr(self._pipeline, 'enable_xformers_memory_efficient_attention'):
                        self._pipeline.enable_xformers_memory_efficient_attention()
                except Exception as optimization_error:
                    print(f"Avertissement: Optimisations mémoire non disponibles: {optimization_error}")
            
            load_time = time.time() - start_time
            print(f"Modèle d'images chargé avec succès en {load_time:.2f}s")
            
            self._model_loaded = True
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement du modèle d'images: {str(e)}")
            print("Basculement vers le mode simulation d'images...")
            self._model_loaded = True  # Mode dégradé
            return False
    
    async def generate_scene_image(self, story: Story, scene: Scene, style_override: Optional[str] = None) -> Optional[str]:
        """
        Génère une image pour une scène donnée
        
        Args:
            story: Histoire associée
            scene: Scène à illustrer
            style_override: Style visuel optionnel pour surcharger le genre
            
        Returns:
            Optional[str]: URL/path de l'image générée ou None si erreur
        """
        try:
            # Construction du prompt visuel
            image_prompt = self._build_image_prompt(story, scene, style_override)
            
            # Vérification du cache
            cache_key = self._get_cache_key(image_prompt)
            if cache_key in self._image_cache:
                print(f"Image trouvée en cache pour la scène {scene.scene_number}")
                return self._image_cache[cache_key]
            
            # Génération de l'image
            image_path = await self._generate_image(image_prompt, story.story_id, scene.scene_number)
            
            if image_path:
                # Mise à jour du cache
                self._image_cache[cache_key] = image_path
                
                # Limitation de la taille du cache
                if len(self._image_cache) > self._cache_max_size:
                    oldest_key = next(iter(self._image_cache))
                    del self._image_cache[oldest_key]
                
                # Mise à jour de la scène
                scene.image_url = image_path
                scene.image_prompt = image_prompt
                
                return image_path
            
            return None
            
        except Exception as e:
            print(f"Erreur génération image pour scène {scene.scene_number}: {str(e)}")
            return None
    
    def _build_image_prompt(self, story: Story, scene: Scene, style_override: Optional[str] = None) -> str:
        """
        Construit un prompt visuel à partir du contexte narratif
        
        Args:
            story: Histoire pour le contexte
            scene: Scène à illustrer
            style_override: Style personnalisé optionnel
            
        Returns:
            str: Prompt visuel optimisé
        """
        # Style de base selon le genre ou override
        if style_override:
            style = style_override
        else:
            style = self._genre_styles[story.genre]["base_style"]
        
        # Extraction des éléments visuels du texte narratif
        visual_elements = self._extract_visual_elements(scene.narrative_text)
        
        # Construction du prompt principal
        main_prompt = f"{visual_elements}, {style}"
        
        # Ajout d'éléments de genre spécifiques
        genre_elements = self._genre_styles[story.genre]["elements"]
        full_prompt = f"{main_prompt}, {genre_elements}"
        
        # Ajout des qualificatifs de qualité
        quality_terms = "highly detailed, professional artwork, cinematic lighting, masterpiece"
        final_prompt = f"{full_prompt}, {quality_terms}"
        
        return final_prompt
    
    def _extract_visual_elements(self, narrative_text: str) -> str:
        """
        Extrait les éléments visuels descriptifs du texte narratif
        
        Args:
            narrative_text: Texte de la scène
            
        Returns:
            str: Éléments visuels extraits
        """
        # Simplification pour l'instant - extraction basique
        # TODO: Implémenter NLP pour extraction sophistiquée
        
        # Mots-clés visuels communs à rechercher
        visual_keywords = {
            'forest': 'mystical forest',
            'castle': 'ancient castle',
            'space': 'cosmic space scene',
            'city': 'urban cityscape',
            'mountain': 'majestic mountains',
            'ocean': 'vast ocean',
            'house': 'mysterious house',
            'room': 'atmospheric interior room',
            'character': 'dramatic character portrait',
            'creature': 'fantastical creature',
            'magic': 'magical effects',
            'technology': 'futuristic technology',
            'darkness': 'dark atmospheric scene',
            'light': 'dramatic lighting'
        }
        
        # Recherche de mots-clés dans le texte
        found_elements = []
        text_lower = narrative_text.lower()
        
        for keyword, visual in visual_keywords.items():
            if keyword in text_lower:
                found_elements.append(visual)
        
        # Si aucun élément trouvé, utiliser un prompt générique
        if not found_elements:
            found_elements = ["atmospheric scene", "detailed environment"]
        
        return ", ".join(found_elements[:3])  # Limiter à 3 éléments principaux
    
    async def _generate_image(self, prompt: str, story_id: str, scene_number: int) -> Optional[str]:
        """
        Génère une image à partir d'un prompt
        
        Args:
            prompt: Prompt visuel
            story_id: ID de l'histoire
            scene_number: Numéro de la scène
            
        Returns:
            Optional[str]: Chemin vers l'image générée
        """
        if not self._model_loaded:
            await self.initialize_model()
        
        if not DIFFUSERS_AVAILABLE or self._pipeline is None:
            return self._create_placeholder_image(story_id, scene_number)
        
        try:
            # Génération avec seed pour reproductibilité
            generator = torch.Generator(device=self.device)
            generator.manual_seed(hash(f"{story_id}_{scene_number}") % 2**32)
            
            # Prompt négatif pour améliorer la qualité
            negative_prompt = self.negative_prompts["default"]
            
            print(f"Génération d'image pour scène {scene_number}...")
            start_time = time.time()
            
            # Génération de l'image avec gestion d'erreur améliorée
            try:
                if self.device == "cuda":
                    with torch.autocast("cuda"):
                        result = self._pipeline(
                            prompt=prompt,
                            negative_prompt=negative_prompt,
                            width=self.generation_params["width"],
                            height=self.generation_params["height"],
                            num_inference_steps=self.generation_params["num_inference_steps"],
                            guidance_scale=self.generation_params["guidance_scale"],
                            generator=generator
                        )
                else:
                    # Pour CPU, pas d'autocast
                    result = self._pipeline(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        width=self.generation_params["width"],
                        height=self.generation_params["height"],
                        num_inference_steps=self.generation_params["num_inference_steps"],
                        guidance_scale=self.generation_params["guidance_scale"],
                        generator=generator
                    )
            except Exception as gen_error:
                print(f"Erreur lors de la génération avec paramètres complets: {gen_error}")
                # Essai avec paramètres simplifiés
                result = self._pipeline(
                    prompt=prompt,
                    width=512,
                    height=512,
                    num_inference_steps=10  # Plus rapide pour test
                )
            
            generation_time = time.time() - start_time
            print(f"Image générée en {generation_time:.2f}s")
            
            # Sauvegarde de l'image
            image = result.images[0]
            image_path = self._save_image(image, story_id, scene_number)
            
            return image_path
            
        except Exception as e:
            print(f"Erreur lors de la génération d'image: {str(e)}")
            return self._create_placeholder_image(story_id, scene_number)
    
    def _save_image(self, image: Image.Image, story_id: str, scene_number: int) -> str:
        """
        Sauvegarde une image générée
        
        Args:
            image: Image PIL à sauvegarder
            story_id: ID de l'histoire
            scene_number: Numéro de la scène
            
        Returns:
            str: Chemin vers l'image sauvegardée
        """
        # Création du répertoire spécifique à l'histoire
        story_images_dir = os.path.join(self.images_path, story_id)
        os.makedirs(story_images_dir, exist_ok=True)
        
        # Nom de fichier avec timestamp pour unicité
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scene_{scene_number:03d}_{timestamp}.png"
        image_path = os.path.join(story_images_dir, filename)
        
        # Sauvegarde avec optimisation
        image.save(image_path, "PNG", optimize=True, quality=85)
        
        return image_path
    
    def _create_placeholder_image(self, story_id: str, scene_number: int) -> str:
        """
        Crée une image placeholder en mode dégradé
        
        Args:
            story_id: ID de l'histoire
            scene_number: Numéro de la scène
            
        Returns:
            str: Chemin vers l'image placeholder
        """
        try:
            # Création d'une image simple avec PIL
            from PIL import Image, ImageDraw, ImageFont
            
            image = Image.new('RGB', (512, 512), color=(70, 70, 100))
            draw = ImageDraw.Draw(image)
            
            # Texte placeholder
            text = f"Scene {scene_number}\n[Image Generation\nUnavailable]"
            
            # Tentative d'utiliser une police par défaut
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Centrage du texte
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (512 - text_width) // 2
            y = (512 - text_height) // 2
            
            draw.text((x, y), text, fill=(200, 200, 200), font=font, align='center')
            
            # Sauvegarde
            return self._save_image(image, story_id, scene_number)
            
        except Exception as e:
            print(f"Erreur création placeholder: {str(e)}")
            return f"placeholder_scene_{scene_number}.png"
    
    def _get_cache_key(self, prompt: str) -> str:
        """
        Génère une clé de cache pour un prompt
        
        Args:
            prompt: Prompt à hasher
            
        Returns:
            str: Clé de cache unique
        """
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _initialize_genre_styles(self) -> Dict[StoryGenre, Dict[str, str]]:
        """
        Initialise les styles visuels par genre
        
        Returns:
            Dict: Styles structurés par genre
        """
        return {
            StoryGenre.FANTASY: {
                "base_style": "fantasy art, magical realism, ethereal atmosphere",
                "elements": "enchanted forest, mystical creatures, magical effects, medieval architecture, glowing lights, fantasy landscape"
            },
            StoryGenre.SCIENCE_FICTION: {
                "base_style": "sci-fi art, futuristic, cyberpunk aesthetic, digital art",
                "elements": "spaceships, alien worlds, futuristic technology, neon lights, holographic displays, space stations"
            },
            StoryGenre.HORROR: {
                "base_style": "dark horror art, gothic atmosphere, ominous lighting",
                "elements": "haunted house, creepy shadows, fog, dark corridors, mysterious figures, eerie atmosphere"
            },
            StoryGenre.MYSTERY: {
                "base_style": "noir mystery art, detective aesthetic, moody lighting",
                "elements": "urban setting, rain, shadows, investigation scene, dramatic lighting, film noir style"
            },
            StoryGenre.ADVENTURE: {
                "base_style": "adventure art, dynamic composition, epic landscape",
                "elements": "mountain peaks, treasure maps, ancient ruins, jungle exploration, heroic poses, dramatic skies"
            },
            StoryGenre.ROMANCE: {
                "base_style": "romantic art, soft lighting, warm colors, emotional atmosphere",
                "elements": "elegant settings, soft focus, golden hour lighting, intimate scenes, beautiful landscapes, dreamy atmosphere"
            }
        }
    
    def get_model_status(self) -> Dict[str, any]:
        """
        Retourne l'état actuel du modèle d'images
        
        Returns:
            Dict: Informations sur l'état du modèle
        """
        return {
            "model_loaded": self._model_loaded,
            "model_name": self.model_name,
            "device": self.device,
            "diffusers_available": DIFFUSERS_AVAILABLE,
            "cache_size": len(self._image_cache),
            "images_path": self.images_path
        }
    
    def clear_cache(self):
        """Nettoie le cache d'images"""
        self._image_cache.clear()
        print("Cache d'images nettoyé")
    
    async def generate_custom_image(self, prompt: str, style: str = "default") -> Optional[str]:
        """
        Génère une image personnalisée avec prompt libre
        
        Args:
            prompt: Prompt libre pour la génération
            style: Style à appliquer
            
        Returns:
            Optional[str]: Chemin vers l'image générée
        """
        custom_prompt = f"{prompt}, {self._genre_styles[StoryGenre.FANTASY]['base_style']}"
        return await self._generate_image(custom_prompt, "custom", 0)