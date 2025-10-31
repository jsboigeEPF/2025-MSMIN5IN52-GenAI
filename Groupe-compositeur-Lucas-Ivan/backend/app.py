from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from services.musicgenService import MusicGenService
from services.ImageGeneratorService import ImageGeneratorService

app = Flask(__name__)
CORS(app)

# Initialiser les services
music_service = MusicGenService()
image_service = ImageGeneratorService()

# Mapping des ambiances vers des descriptions
AMBIANCE_DESCRIPTIONS = {
    'foret-mysterieuse': "Ambient forest sounds with mysterious piano and ethereal pads",
    'cyberpunk-pluie': "Cyberpunk synthwave with rain sounds and electronic beats",
    'plage-coucher-soleil': "Relaxing tropical beach music with soft guitar and ocean waves",
    'meditation-zen': "Peaceful zen meditation music with bells and nature sounds",
    'cafe-jazz': "Smooth jazz music perfect for a cozy café atmosphere",
    'montagne-majestueuse': "Epic orchestral music with majestic mountain atmosphere",
    'desert-nocturne': "Atmospheric ethnic music with desert night ambiance",
    'ville-futuriste': "Futuristic electronic cinematic music with urban atmosphere"
}

# Mapping pour les images (descriptions plus visuelles)
AMBIANCE_IMAGE_PROMPTS = {
    'foret-mysterieuse': "mysterious enchanted forest, misty atmosphere, ethereal light, magical trees, fantasy landscape",
    'cyberpunk-pluie': "cyberpunk city at night, neon lights, rain, futuristic buildings, dark atmosphere",
    'plage-coucher-soleil': "tropical beach sunset, palm trees, golden hour, peaceful ocean, warm colors",
    'meditation-zen': "zen garden, peaceful atmosphere, bamboo, stones, minimalist, tranquil water",
    'cafe-jazz': "cozy vintage jazz café, warm lighting, instruments, intimate atmosphere",
    'montagne-majestueuse': "majestic mountain landscape, epic scenery, dramatic clouds, snow peaks",
    'desert-nocturne': "desert night sky, stars, sand dunes, mystical atmosphere, moonlight",
    'ville-futuriste': "futuristic cityscape, sci-fi architecture, flying vehicles, neon glow"
}

@app.route('/api/generate', methods=['POST'])
def generate_music():
    data = request.json
    ambiance = data.get('ambiance')
    custom_description = data.get('customDescription')
    
    # Utiliser la description personnalisée ou celle prédéfinie
    music_description = custom_description or AMBIANCE_DESCRIPTIONS.get(ambiance, ambiance)
    image_description = custom_description or AMBIANCE_IMAGE_PROMPTS.get(ambiance, ambiance)
    
    try:
        # Générer la musique
        music_result = music_service.generate_music(music_description)
        generation_id = music_result["generation_id"]
        
        # Générer l'image en parallèle
        image_result = image_service.generate_image(image_description, generation_id)
        
        return jsonify({
            "success": True,
            "data": {
                "generation_id": generation_id,
                "audio_path": music_result["audio_path"],
                "image_path": image_result.get("image_path"),
                "image_generated": image_result["success"],
                "status": "complete"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/audio/<generation_id>', methods=['GET'])
def get_audio(generation_id):
    try:
        audio_path = f"generated_music/music_{generation_id}.wav"
        return send_file(audio_path, mimetype='audio/wav')
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/image/<generation_id>', methods=['GET'])
def get_image(generation_id):
    try:
        image_path = f"generated_images/image_{generation_id}.jpg"
        return send_file(image_path, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)