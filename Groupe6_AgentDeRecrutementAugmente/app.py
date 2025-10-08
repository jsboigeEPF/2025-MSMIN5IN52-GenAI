"""
Recruitment Agent Application

Flask application for matching CVs with job descriptions using FAISS vector search.
"""

import os
import logging
from typing import Optional, Dict, Any
from flask import Flask, request, render_template, Response, jsonify, make_response
from src.data_processor import process_job_and_cv
from src.embeddings_index import faiss_index

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
class Config:
    """Application configuration class"""
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Ensure upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
app.config.from_object(Config)

# Initialize FAISS index with example data
def initialize_index() -> None:
    """Initialize the FAISS index with example data"""
    try:
        faiss_index.add([
            "CV de John Doe, développeur Python avec 3 ans d'expérience",
            "Fiche de poste: développeur Python senior avec expérience Django",
            "CV de Jane Smith, data scientist spécialisée en NLP"
        ])
        logger.info("FAISS index initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize FAISS index: {e}")
        raise

# Route definitions
def configure_routes(app: Flask) -> None:
    """Configure Flask routes"""
    
    @app.route('/')
    def home() -> str:
        """Render the home page"""
        return render_template('index.html')

    @app.route('/match', methods=['POST'])
    def match_candidates() -> Response:
        """Match candidates with job description"""
        try:
            # Validate request
            if 'job_description' not in request.files or 'cv' not in request.files:
                return make_response(jsonify(error="Missing required files"), 400)

            job_file = request.files['job_description']
            cv_file = request.files['cv']

            # Validate filenames
            if not job_file.filename or not cv_file.filename:
                return make_response(jsonify(error="Files must have filenames"), 400)

            # Validate file extensions
            if not allowed_file(job_file.filename) or not allowed_file(cv_file.filename):
                return make_response(jsonify(error="File type not allowed"), 400)

            # Save files
            job_path = save_file(job_file, app.config['UPLOAD_FOLDER'])
            cv_path = save_file(cv_file, app.config['UPLOAD_FOLDER'])

            # Process files
            results_text = process_job_and_cv(job_path, cv_path)
            logger.info("Files processed successfully")

            # Search FAISS index
            search_results = faiss_index.search(results_text, top_k=3)
            logger.info(f"Found {len(search_results)} matching candidates")

            return make_response(render_template('results.html', results=search_results))

        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return make_response(jsonify(error="Internal server error"), 500)

def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_file(file: Any, upload_folder: str) -> str:
    """Save uploaded file to specified folder"""
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    logger.debug(f"Saved file to {file_path}")
    return file_path

# Application factory pattern
def create_app() -> Flask:
    """Create and configure the Flask application"""
    initialize_index()
    configure_routes(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
