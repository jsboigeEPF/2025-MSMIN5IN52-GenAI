"""
Service de génération de texte narratif avec IA

Ce service gère la génération de contenu narratif interactif en utilisant
des modèles de langage (Transformers). Il est responsable de :
- Chargement et gestion du modèle de langage configuré
- Construction de prompts contextuels sophistiqués
- Génération de texte narratif cohérent et engageant
- Maintien de la cohérence narrative sur plusieurs scènes
- Adaptation du style selon le genre d'histoire

Architecture :
- Singleton pattern pour éviter de recharger le modèle
- Cache des prompts pour optimisation
- Gestion robuste des erreurs et fallbacks
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Using mock responses.")

from app.models.schemas import (
    Story, StoryMemory, Scene, UserAction, StoryGenre, Character, Location
)
from app.config import settings


class TextGenerationService:
    """
    Service de génération de texte narratif avec modèles de langage
    
    Ce service encapsule toute la logique de génération de contenu narratif :
    - Gestion du modèle de langage (chargement, optimisation)
    - Construction de prompts contextuels
    - Génération de texte avec paramètres adaptés
    - Extraction d'informations narratives (personnages, lieux)
    """
    
    _instance = None
    _model = None
    _tokenizer = None
    _pipeline = None
    _model_loaded = False
    
    def __new__(cls):
        """
        Implémentation du pattern Singleton
        Évite de recharger le modèle à chaque instanciation
        """
        if cls._instance is None:
            cls._instance = super(TextGenerationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialise le service de génération de texte
        Ne charge le modèle que si ce n'est pas déjà fait (Singleton)
        """
        if not hasattr(self, '_initialized'):
            self._initialized = True
            
            # Détection automatique du device
            self.device = self._detect_device(settings.TEXT_MODEL_DEVICE)
            self.model_name = settings.TEXT_MODEL_NAME
            self.max_context_length = settings.MAX_CONTEXT_LENGTH
            self.max_story_length = settings.MAX_STORY_LENGTH
            
            print(f"🔧 Service de texte configuré - Device: {self.device}, Modèle: {self.model_name}")
            
            # Paramètres de génération par défaut
            self.generation_params = {
                "max_new_tokens": 300,
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 50,
                "do_sample": True,
                "pad_token_id": None,  # Sera défini après chargement du tokenizer
                "eos_token_id": None,
                "repetition_penalty": 1.1
            }
            
            # Templates de prompts par genre
            self._genre_prompts = self._initialize_genre_prompts()
            
            # Cache des prompts récents (optimisation)
            self._prompt_cache = {}
            self._cache_max_size = 100
    
    def _detect_device(self, device_setting: str) -> str:
        """
        Détecte automatiquement le meilleur device disponible
        
        Args:
            device_setting: Configuration du device ('auto', 'cuda', 'cpu')
            
        Returns:
            str: Device à utiliser ('cuda' ou 'cpu')
        """
        if device_setting.lower() == "auto":
            if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                print(f"🎮 CUDA détecté! GPU disponibles: {gpu_count}, Nom: {gpu_name}")
                return "cuda"
            else:
                print("💻 CUDA non disponible, utilisation du CPU")
                return "cpu"
        else:
            return device_setting.lower()
    
    async def initialize_model(self) -> bool:
        """
        Charge le modèle de langage de manière asynchrone
        
        Returns:
            bool: True si le modèle est chargé avec succès
        """
        if self._model_loaded:
            return True
        
        if not TRANSFORMERS_AVAILABLE:
            print("Transformers non disponible. Mode simulation activé.")
            self._model_loaded = True
            return True
        
        try:
            print(f"Chargement du modèle {self.model_name}...")
            start_time = time.time()
            
            # Chargement du tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Configuration du padding token si nécessaire
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            
            # Chargement du modèle avec optimisations
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "low_cpu_mem_usage": True
            }
            
            # Ne pas utiliser device_map="auto" qui cause des problèmes
            if self.device == "cuda":
                model_kwargs["device_map"] = {"": 0}  # Utiliser GPU 0 explicitement
            
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Déplacer vers le device approprié si CPU
            if self.device == "cpu":
                self._model = self._model.to(self.device)
            
            # Création du pipeline de génération
            self._pipeline = pipeline(
                "text-generation",
                model=self._model,
                tokenizer=self._tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            # Mise à jour des paramètres de génération
            self.generation_params["pad_token_id"] = self._tokenizer.pad_token_id
            self.generation_params["eos_token_id"] = self._tokenizer.eos_token_id
            
            load_time = time.time() - start_time
            print(f"Modèle chargé avec succès en {load_time:.2f}s")
            
            self._model_loaded = True
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {str(e)}")
            print("Basculement vers le mode simulation...")
            self._model_loaded = True  # Mode dégradé
            return False
    
    async def generate_intro_scene(self, story: Story) -> Tuple[str, List[str]]:
        """
        Génère la scène d'introduction d'une histoire
        
        Args:
            story: Histoire pour laquelle générer l'introduction
            
        Returns:
            Tuple[str, List[str]]: (texte_narratif, actions_suggérées)
        """
        try:
            # Construction du prompt d'introduction
            prompt = self._build_intro_prompt(story)
            
            # Génération du texte
            narrative_text = await self._generate_text(prompt, story.genre)
            
            # Génération des actions suggérées
            suggested_actions = await self._generate_suggested_actions(
                narrative_text, story.genre, is_intro=True
            )
            
            return narrative_text, suggested_actions
            
        except Exception as e:
            print(f"Erreur génération intro: {str(e)}")
            return self._fallback_intro(story), self._fallback_actions(story.genre)
    
    async def generate_continuation(self, story: Story, user_action: UserAction) -> Tuple[str, List[str]]:
        """
        Génère la continuation d'une histoire basée sur l'action du joueur
        
        Args:
            story: Histoire en cours
            user_action: Action effectuée par le joueur
            
        Returns:
            Tuple[str, List[str]]: (texte_narratif, actions_suggérées)
        """
        try:
            # Construction du prompt de continuation
            prompt = self._build_continuation_prompt(story, user_action)
            
            # Génération du texte narratif
            narrative_text = await self._generate_text(prompt, story.genre)
            
            # Génération des actions suggérées
            suggested_actions = await self._generate_suggested_actions(
                narrative_text, story.genre, is_intro=False
            )
            
            return narrative_text, suggested_actions
            
        except Exception as e:
            print(f"Erreur génération continuation: {str(e)}")
            return self._fallback_continuation(user_action), self._fallback_actions(story.genre)
    
    async def _generate_text(self, prompt: str, genre: StoryGenre) -> str:
        """
        Génère du texte à partir d'un prompt
        
        Args:
            prompt: Prompt à utiliser pour la génération
            genre: Genre de l'histoire (pour adapter les paramètres)
            
        Returns:
            str: Texte généré et nettoyé
        """
        if not self._model_loaded:
            await self.initialize_model()
        
        if not TRANSFORMERS_AVAILABLE or self._pipeline is None:
            return self._simulate_generation(prompt, genre)
        
        try:
            # Adaptation des paramètres selon le genre
            params = self.generation_params.copy()
            params.update(self._get_genre_generation_params(genre))
            
            # Génération
            start_time = time.time()
            result = self._pipeline(
                prompt,
                max_new_tokens=params["max_new_tokens"],
                temperature=params["temperature"],
                top_p=params["top_p"],
                top_k=params["top_k"],
                do_sample=params["do_sample"],
                pad_token_id=params["pad_token_id"],
                eos_token_id=params["eos_token_id"],
                repetition_penalty=params["repetition_penalty"]
            )
            
            generation_time = time.time() - start_time
            print(f"Génération effectuée en {generation_time:.2f}s")
            
            # Extraction et nettoyage du texte généré
            generated_text = result[0]["generated_text"]
            clean_text = self._clean_generated_text(generated_text, prompt)
            
            return clean_text
            
        except Exception as e:
            print(f"Erreur lors de la génération: {str(e)}")
            return self._simulate_generation(prompt, genre)
    
    def _build_intro_prompt(self, story: Story) -> str:
        """
        Construit le prompt d'introduction pour une histoire
        
        Args:
            story: Histoire à initialiser
            
        Returns:
            str: Prompt d'introduction formaté
        """
        genre_template = self._genre_prompts[story.genre]
        
        prompt = f"""<|im_start|>system
{genre_template['system_prompt']}

Tu dois créer l'introduction d'une histoire interactive {story.genre.value}.
Règles importantes :
- Écris à la 2ème personne du singulier ("vous")
- Crée une scène immersive et engageante
- Termine par une situation nécessitant un choix du joueur
- Reste dans le genre {story.genre.value}
- Maximum 200 mots<|im_end|>

<|im_start|>user
Génère l'introduction d'une histoire {story.genre.value}."""
        
        if story.initial_prompt:
            prompt += f"\nContexte initial fourni par l'utilisateur : {story.initial_prompt}"
        
        prompt += "<|im_end|>\n\n<|im_start|>assistant\n"
        
        return prompt
    
    def _build_continuation_prompt(self, story: Story, user_action: UserAction) -> str:
        """
        Construit le prompt de continuation basé sur l'historique et l'action
        
        Args:
            story: Histoire en cours
            user_action: Dernière action du joueur
            
        Returns:
            str: Prompt de continuation formaté
        """
        genre_template = self._genre_prompts[story.genre]
        
        # Construction du contexte narratif
        context = self._build_story_context(story)
        
        prompt = f"""<|im_start|>system
{genre_template['system_prompt']}

Tu continues une histoire interactive {story.genre.value}.
Règles importantes :
- Écris à la 2ème personne du singulier ("vous")
- Prends en compte l'action du joueur
- Fais progresser l'histoire de manière logique
- Termine par une nouvelle situation nécessitant un choix
- Reste cohérent avec le contexte précédent
- Maximum 250 mots<|im_end|>

<|im_start|>user
Contexte de l'histoire :
{context}

Action du joueur : {user_action.action_text}

Continue l'histoire en tenant compte de cette action.<|im_end|>

<|im_start|>assistant
"""
        
        return prompt
    
    def _build_story_context(self, story: Story) -> str:
        """
        Construit un résumé contextuel de l'histoire pour les prompts
        
        Args:
            story: Histoire dont extraire le contexte
            
        Returns:
            str: Contexte formaté pour inclusion dans les prompts
        """
        context_parts = []
        
        # Résumé général
        if story.memory.current_summary:
            context_parts.append(f"Résumé : {story.memory.current_summary}")
        
        # Personnages importants
        if story.memory.characters:
            chars = ", ".join([f"{name} ({char.role})" 
                             for name, char in story.memory.characters.items()])
            context_parts.append(f"Personnages : {chars}")
        
        # Lieux visités
        if story.memory.locations:
            locs = ", ".join(story.memory.locations.keys())
            context_parts.append(f"Lieux : {locs}")
        
        # Dernières scènes (pour continuité immédiate)
        if story.scenes:
            recent_scenes = story.scenes[-2:] if len(story.scenes) > 1 else story.scenes[-1:]
            for scene in recent_scenes:
                context_parts.append(f"Scène {scene.scene_number} : {scene.narrative_text[:100]}...")
        
        return "\n".join(context_parts)
    
    async def _generate_suggested_actions(self, narrative_text: str, genre: StoryGenre, is_intro: bool = False) -> List[str]:
        """
        Génère des actions suggérées basées sur le contexte narratif
        
        Args:
            narrative_text: Texte narratif de la scène
            genre: Genre de l'histoire
            is_intro: Si c'est la scène d'introduction
            
        Returns:
            List[str]: Actions suggérées pour le joueur
        """
        # Pour l'instant, utilisation de templates pré-définis
        # TODO: Améliorer avec génération IA contextuelle
        
        if is_intro:
            return self._get_intro_actions(genre)
        else:
            return self._get_generic_actions(genre)
    
    def _get_intro_actions(self, genre: StoryGenre) -> List[str]:
        """Actions suggérées pour les scènes d'introduction par genre"""
        actions_by_genre = {
            StoryGenre.FANTASY: [
                "Explorer les environs magiques",
                "Chercher d'autres créatures intelligentes",
                "Examiner vos possessions",
                "Essayer de comprendre comment vous êtes arrivé ici"
            ],
            StoryGenre.SCIENCE_FICTION: [
                "Consulter les systèmes du vaisseau",
                "Analyser la planète par les scanners",
                "Chercher d'autres survivants",
                "Examiner votre équipement"
            ],
            StoryGenre.HORROR: [
                "Chercher une source de lumière",
                "Explorer prudemment la première pièce",
                "Écouter attentivement les bruits",
                "Chercher une sortie"
            ],
            StoryGenre.MYSTERY: [
                "Examiner les indices disponibles",
                "Interroger les témoins potentiels",
                "Explorer la scène de crime",
                "Consulter vos notes"
            ],
            StoryGenre.ADVENTURE: [
                "Étudier la carte et planifier votre route",
                "Vérifier votre équipement",
                "Chercher des compagnons de voyage",
                "Commencer immédiatement l'aventure"
            ],
            StoryGenre.ROMANCE: [
                "Engager la conversation",
                "Observer discrètement la situation",
                "Prendre le temps de réfléchir",
                "Agir selon votre instinct"
            ]
        }
        
        return actions_by_genre.get(genre, [
            "Explorer la situation",
            "Réfléchir aux options",
            "Agir prudemment",
            "Prendre une décision rapide"
        ])
    
    def _get_generic_actions(self, genre: StoryGenre) -> List[str]:
        """Actions suggérées génériques par genre"""
        return [
            "Continuer dans cette direction",
            "Changer d'approche",
            "Examiner les détails",
            "Demander de l'aide ou des informations"
        ]
    
    def _get_genre_generation_params(self, genre: StoryGenre) -> Dict:
        """
        Paramètres de génération adaptés par genre
        
        Args:
            genre: Genre de l'histoire
            
        Returns:
            Dict: Paramètres de génération spécifiques
        """
        genre_params = {
            StoryGenre.HORROR: {
                "temperature": 0.7,  # Plus déterministe pour suspense
                "top_p": 0.85
            },
            StoryGenre.MYSTERY: {
                "temperature": 0.6,  # Logique et cohérent
                "top_p": 0.8
            },
            StoryGenre.ROMANCE: {
                "temperature": 0.9,  # Plus créatif et émotionnel
                "top_p": 0.95
            }
        }
        
        return genre_params.get(genre, {})
    
    def _clean_generated_text(self, generated_text: str, original_prompt: str) -> str:
        """
        Nettoie le texte généré en retirant le prompt et les éléments indésirables
        
        Args:
            generated_text: Texte brut généré
            original_prompt: Prompt original à retirer
            
        Returns:
            str: Texte nettoyé
        """
        # Retirer le prompt original
        if original_prompt in generated_text:
            clean_text = generated_text.replace(original_prompt, "")
        else:
            clean_text = generated_text
        
        # Nettoyer les tokens spéciaux
        clean_text = clean_text.replace("<|im_start|>", "")
        clean_text = clean_text.replace("<|im_end|>", "")
        clean_text = clean_text.replace("<|assistant|>", "")
        
        # Nettoyer les espaces multiples et retours à la ligne
        clean_text = " ".join(clean_text.split())
        
        # Limiter la longueur si nécessaire
        if len(clean_text) > 500:
            clean_text = clean_text[:500] + "..."
        
        return clean_text.strip()
    
    def _initialize_genre_prompts(self) -> Dict[StoryGenre, Dict[str, str]]:
        """
        Initialise les templates de prompts par genre
        
        Returns:
            Dict: Templates structurés par genre
        """
        return {
            StoryGenre.FANTASY: {
                "system_prompt": "Tu es un maître conteur spécialisé dans la fantasy. Tu créés des histoires riches en magie, créatures fantastiques, quêtes épiques et mondes imaginaires. Ton style est immersif, descriptif et respecte les codes du genre fantasy."
            },
            StoryGenre.SCIENCE_FICTION: {
                "system_prompt": "Tu es un narrateur expert en science-fiction. Tu explores les technologies futuristes, l'espace, les voyages temporels, les intelligences artificielles et les concepts scientifiques avancés. Ton style est innovant et spéculatif."
            },
            StoryGenre.HORROR: {
                "system_prompt": "Tu es un maître de l'horreur. Tu créés des atmosphères oppressantes, du suspense psychologique, des créatures terrifiantes et des situations angoissantes. Ton style privilégie la tension et l'ambiance plutôt que la violence gratuite."
            },
            StoryGenre.MYSTERY: {
                "system_prompt": "Tu es un expert en récits policiers et mystères. Tu tisses des intrigues complexes, des enquêtes logiques, des indices subtils et des révélations surprenantes. Ton style est méthodique et respecte la logique déductive."
            },
            StoryGenre.ADVENTURE: {
                "system_prompt": "Tu es un guide d'aventures extraordinaires. Tu créés des quêtes passionnantes, des défis physiques, des découvertes fascinantes et des voyages épiques. Ton style est dynamique et plein d'action."
            },
            StoryGenre.ROMANCE: {
                "system_prompt": "Tu es un conteur de romances touchantes. Tu développes des relations émotionnelles profondes, des histoires d'amour complexes, des moments tendres et des conflits relationnels. Ton style est sensible et émotionnellement riche."
            }
        }
    
    # ===== MÉTHODES DE FALLBACK (MODE DÉGRADÉ) =====
    
    def _simulate_generation(self, prompt: str, genre: StoryGenre) -> str:
        """
        Simulation de génération quand le modèle n'est pas disponible
        
        Args:
            prompt: Prompt demandé
            genre: Genre de l'histoire
            
        Returns:
            str: Texte simulé
        """
        simulations = {
            StoryGenre.FANTASY: "La magie crépite dans l'air tandis que vous avancez dans cette terre mystérieuse. Des créatures étranges observent vos mouvements depuis les ombres de la forêt enchantée. Que décidez-vous de faire ?",
            StoryGenre.SCIENCE_FICTION: "Les systèmes du vaisseau clignotent d'alertes rouges. Par le hublot, cette planète inconnue semble receler des secrets que l'humanité n'a jamais découverts. Votre prochaine action pourrait changer le cours de l'histoire.",
            StoryGenre.HORROR: "Un frisson glacé parcourt votre échine. Les ombres semblent bouger d'elles-mêmes dans cette maison abandonnée. Chaque craquement du parquet vous met les nerfs à vif. Il faut prendre une décision rapidement.",
            StoryGenre.MYSTERY: "Les indices s'accumulent mais le puzzle reste incomplet. Cette affaire cache quelque chose de plus profond que prévu. Votre instinct de détective vous dit que vous êtes sur la bonne piste.",
            StoryGenre.ADVENTURE: "L'adrénaline monte tandis que vous faites face à ce nouveau défi. L'aventure que vous recherchiez se présente enfin à vous, mais elle sera plus périlleuse que prévu.",
            StoryGenre.ROMANCE: "Votre cœur s'accélère dans cette situation inattendue. Les émotions se mêlent et il devient difficile de distinguer ce que vous ressentez vraiment. Un choix s'impose à vous."
        }
        
        return simulations.get(genre, "L'histoire continue de se développer d'une manière inattendue...")
    
    def _fallback_intro(self, story: Story) -> str:
        """Texte d'introduction de fallback"""
        return f"Bienvenue dans cette aventure {story.genre.value} ! Votre histoire commence maintenant dans cet univers fascinant. Que souhaitez-vous faire ?"
    
    def _fallback_continuation(self, user_action: UserAction) -> str:
        """Texte de continuation de fallback"""
        return f"Vous décidez de {user_action.action_text.lower()}. Cette action a des conséquences intéressantes sur la suite de votre aventure..."
    
    def _fallback_actions(self, genre: StoryGenre) -> List[str]:
        """Actions de fallback par genre"""
        return [
            "Explorer les environs",
            "Chercher des informations",
            "Prendre une décision importante",
            "Continuer prudemment"
        ]
    
    def get_model_status(self) -> Dict[str, any]:
        """
        Retourne l'état actuel du modèle
        
        Returns:
            Dict: Informations sur l'état du modèle
        """
        return {
            "model_loaded": self._model_loaded,
            "model_name": self.model_name,
            "device": self.device,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "cache_size": len(self._prompt_cache)
        }