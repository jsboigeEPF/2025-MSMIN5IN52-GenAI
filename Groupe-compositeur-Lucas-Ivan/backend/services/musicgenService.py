from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy.io.wavfile
import torch
import os
import uuid

class MusicGenService:
    def __init__(self):
        print("🎵 Chargement du modèle MusicGen...")
        self.processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        self.model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        print(f"✅ Modèle chargé sur : {self.device}")
        
        # Dossier pour sauvegarder les fichiers audio
        self.output_dir = "generated_music"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_music(self, description, duration_tokens=1024):
        """Génère de la musique à partir d'une description"""
        generation_id = str(uuid.uuid4())
        
        # Préparer les inputs
        inputs = self.processor(
            text=[description],
            padding=True,
            return_tensors="pt",
        ).to(self.device)
        
        # Générer l'audio
        audio_values = self.model.generate(**inputs, max_new_tokens=duration_tokens)
        
        # Récupérer le taux d'échantillonnage
        sampling_rate = self.model.config.audio_encoder.sampling_rate
        
        # Sauvegarder le fichier audio
        output_filename = f"{self.output_dir}/music_{generation_id}.wav"
        scipy.io.wavfile.write(
            output_filename,
            rate=sampling_rate,
            data=audio_values[0, 0].cpu().numpy()
        )
        
        return {
            "generation_id": generation_id,
            "audio_path": output_filename,
            "status": "complete"
        }