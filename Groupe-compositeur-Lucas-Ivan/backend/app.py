from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from services.musicgenService import MusicGenService

app = Flask(__name__)
CORS(app)

# Initialiser le service (le modèle se charge au démarrage)
music_service = MusicGenService()

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

@app.route('/api/generate', methods=['POST'])
def generate_music():
    data = request.json
    ambiance = data.get('ambiance')
    custom_description = data.get('customDescription')
    
    # Utiliser la description personnalisée ou celle prédéfinie
    description = custom_description or AMBIANCE_DESCRIPTIONS.get(ambiance, ambiance)
    
    try:
        result = music_service.generate_music(description)
        return jsonify({
            "success": True,
            "data": result
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)