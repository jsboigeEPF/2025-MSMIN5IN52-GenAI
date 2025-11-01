from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy.io.wavfile
import numpy as np
import os
import uuid

# Configuration
app = Flask(__name__)
CORS(app)

# Chemin vers le dossier frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

# Créer le dossier pour les fichiers générés (CHEMIN ABSOLU)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_audio')
OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)  # Convertir en chemin absolu
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Dossier de sortie audio: {OUTPUT_DIR}")

# Charger le modèle
print("Chargement du modèle AudioCraft...")
model_name = "facebook/musicgen-small"
processor = AutoProcessor.from_pretrained(model_name)
model = MusicgenForConditionalGeneration.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Modèle chargé sur {device}")

# Routes pour servir le frontend
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# API Routes
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'model': model_name,
        'device': device
    })

@app.route('/api/generate', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        duration = data.get('duration', 10)
        temperature = data.get('temperature', 1.0)
        
        if not prompt:
            return jsonify({'error': 'Le prompt est requis'}), 400
        
        print(f"Génération audio - Prompt: {prompt}, Durée: {duration}s")
        
        inputs = processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        ).to(device)
        
        max_new_tokens = int(duration * 50)
        
        with torch.no_grad():
            audio_values = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
            )
        
        audio_data = audio_values[0].cpu().numpy()
        audio_data = audio_data / np.max(np.abs(audio_data))
        audio_data = (audio_data * 32767).astype(np.int16)
        
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        sample_rate = model.config.audio_encoder.sampling_rate
        scipy.io.wavfile.write(filepath, sample_rate, audio_data.T)
        
        print(f"Audio généré : {filename}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/api/download/{filename}'
        })
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'Fichier non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)