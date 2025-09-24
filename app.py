from flask import Flask, request, jsonify
from src.core.application import Application
from src.ambiance.ambiance_manager import AmbianceManager
from src.audio.generation_service import AudioGenerationService
import asyncio
import logging
import os

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the application components
application = Application()
ambiance_manager = AmbianceManager()
audio_generator = AudioGenerationService()

@app.route('/api/generate-loop', methods=['POST'])
def generate_loop():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        ambiance = data.get('ambiance')
        tempo = data.get('tempo', 120)
        duration = data.get('duration', 30)
        
        if not ambiance:
            return jsonify({'error': 'No ambiance provided'}), 400
            
        # Get ambiance configuration
        ambiance_config = ambiance_manager.get_ambiance_config(ambiance)
        if not ambiance_config:
            return jsonify({'error': f'Ambiance "{ambiance}" not found'}), 404
            
        # Update tempo if provided
        ambiance_config['tempo'] = tempo
        
        # Generate audio loop using the audio generator
        # We need to run the async function in the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            audio_result = loop.run_until_complete(
                audio_generator.generate_audio(ambiance_description=ambiance_config)
            )
            
            # Convert bytes to base64 for JSON serialization
            import base64
            audio_data = base64.b64encode(audio_result.audio_data).decode('utf-8')
            
            return jsonify({
                'success': True,
                'audio_data': audio_data,
                'metadata': audio_result.metadata,
                'api_used': audio_result.api_used,
                'generation_time': audio_result.generation_time,
                'cache_hit': audio_result.cache_hit
            }), 200
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error generating loop: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ambiances', methods=['GET'])
def get_ambiances():
    try:
        # Get available ambiances from the ambiance manager
        ambiances = ambiance_manager.get_available_ambiances()
        
        return jsonify({
            'success': True,
            'ambiances': ambiances
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting ambiances: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/request-ambiance', methods=['POST'])
def request_ambiance():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        ambiance_name = data.get('ambiance_name')
        if not ambiance_name:
            return jsonify({'error': 'No ambiance name provided'}), 400
            
        # In a real implementation, this would save the request for processing
        # For now, we'll just return a success message
        logger.info(f'Ambiance request received: {ambiance_name}')
        
        return jsonify({
            'success': True,
            'message': f'Ambiance request for "{ambiance_name}" received successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing ambiance request: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)