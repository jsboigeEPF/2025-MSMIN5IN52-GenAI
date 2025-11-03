import os, shutil
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, Response, stream_with_context
import pandas as pd
from dotenv import load_dotenv
import asyncio
import sqlite3
import json

from matching.parse import is_allowed, read_any, normalize_text
from matching.job_generator import JobGenerator

# Load environment variables
load_dotenv()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = "change-me"

# Global chatbot instance
chatbot_instance = None

def safe_filename(name:str)->str:
    return name.replace(" ", "_")

# Remove global job_generator - we'll instantiate it per request with user's API key

@app.route("/", methods=["GET"])
def index():
    return render_template("landing.html")

@app.route("/processor", methods=["GET"])
def processor():
    return render_template("index.html")

@app.route("/generate", methods=["GET"])
def generate_page():
    return render_template("generate.html")

def run_async(coro):
    """Helper to run async code in sync Flask route"""
    return asyncio.run(coro)

@app.route("/generate_description", methods=["POST"])
def generate_description():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Get API key from request
        api_key = data.get("api_key", "").strip()
        if not api_key:
            return jsonify({"error": "OpenAI API key is required"}), 400
        
        basic_desc = data.get("basic_desc", "").strip()
        verbosity = data.get("verbosity", "long")
        if not basic_desc:
            return jsonify({"error": "Description cannot be empty"}), 400
        
        # Create job generator with user's API key
        job_generator = JobGenerator(api_key=api_key)
        
        # Validate input
        is_valid, error = job_generator.validate_input(basic_desc)
        if not is_valid:
            return jsonify({"error": error}), 400
        # Map verbosity to max_tokens
        verbosity_map = {"short": 250, "medium": 400, "long": 700}
        max_tokens = verbosity_map.get(verbosity, 700)
        description = run_async(job_generator.generate_description(basic_desc, max_tokens=max_tokens))
        if description.startswith("Error:"):
            return jsonify({"error": description}), 500
        return jsonify({"description": description})
    except Exception as e:
        app.logger.error(f"Error in generate_description: {str(e)}")
        return jsonify({"error": f"Failed to generate description: {str(e)}"}), 500

# --- Simple SQLite DB for fiches de poste ---
import sqlite3
DB_PATH = os.path.join(os.path.dirname(__file__), 'fiches.db')
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS fiches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
init_db()

@app.route('/add_fiche', methods=['POST'])
def add_fiche():
    data = request.json
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    if not title or not description:
        return jsonify({'success': False, 'error': 'Titre ou description manquant'}), 400
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO fiches (title, description) VALUES (?, ?)", (title, description))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/fiches', methods=['GET'])
def fiches():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT id, title, description, created_at FROM fiches ORDER BY created_at DESC").fetchall()
        fiches = [dict(row) for row in rows]
    return render_template('fiches.html', fiches=fiches)

@app.route('/edit_fiche/<int:fiche_id>', methods=['POST'])
def edit_fiche(fiche_id):
    data = request.json
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    if not title or not description:
        return jsonify({'success': False, 'error': 'Titre ou description manquant'}), 400
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE fiches SET title = ?, description = ? WHERE id = ?", (title, description, fiche_id))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete_fiche/<int:fiche_id>', methods=['POST'])
def delete_fiche(fiche_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM fiches WHERE id = ?", (fiche_id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/process_cvs", methods=["POST"])
def process_cvs():
    """Process uploaded CVs and generate standardized CSV"""
    from matching.cv_processor import create_cv_entry
    
    cv_files = request.files.getlist("cv_files")
    
    if not cv_files or not any(f.filename for f in cv_files):
        flash("Merci de fournir au moins un CV (formats acceptés: PDF, DOCX, TXT).")
        return redirect(url_for("index"))
    
    # Get API key from form data
    api_key = request.form.get("api_key", "").strip()
    if not api_key:
        flash("La clé API OpenAI est requise.")
        return redirect(url_for("index"))
    
    # Generate timestamp for CSV
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"resumes_{stamp}.csv"
    csv_path = os.path.join(OUTPUT_DIR, csv_filename)
    
    # Process each CV file
    entries = []
    for idx, f in enumerate(cv_files, start=1):
        if not f or not f.filename:
            continue
        if not is_allowed(f.filename):
            continue
        
        # Save file temporarily
        file_path = os.path.join(UPLOAD_DIR, safe_filename(f.filename))
        f.save(file_path)
        
        # Extract text and normalize
        text = normalize_text(read_any(file_path))
        if not text:
            continue
            
        # Create standardized entry with API key
        try:
            entry = create_cv_entry(text, idx, api_key)
            entries.append(entry)
        except Exception as e:
            print(f"Error processing {f.filename}: {e}")
            continue
    
    if not entries:
        flash("Aucun CV valide n'a pu être traité. Vérifiez les formats de fichiers.")
        return redirect(url_for("index"))
    
    # Create DataFrame and save CSV with UTF-8 BOM for Excel compatibility
    df = pd.DataFrame(entries)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    # Prepare preview (first 5 entries)
    preview = df.head(5).to_dict(orient="records")
    
    return render_template("results.html",
                           total_cvs=len(entries),
                           csv_filename=csv_filename,
                           preview=preview)

@app.route("/download/<path:filename>")
def download(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.isfile(path):
        return send_file(path, as_attachment=True)
    return "Not found", 404

# ==============================================
# CHATBOT ROUTES
# ==============================================

@app.route("/chatbot", methods=["GET"])
def chatbot_page():
    """Render chatbot interface"""
    return render_template("chatbot.html")

@app.route("/chatbot/upload", methods=["POST"])
def chatbot_upload():
    """Upload and index CSV of CVs"""
    global chatbot_instance
    
    if "csv_file" not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files["csv_file"]
    if not file or not file.filename:
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({"success": False, "error": "File must be CSV"}), 400
    
    # Get API key from form data
    api_key = request.form.get("api_key", "").strip()
    if not api_key:
        return jsonify({
            "success": False,
            "error": "OpenAI API key is required"
        }), 400
    
    try:
        # Save file temporarily
        temp_path = os.path.join(UPLOAD_DIR, "temp_cvs.csv")
        file.save(temp_path)
        
        # Read and validate CSV
        df = pd.read_csv(temp_path)
        if "Resume" not in df.columns or "ID" not in df.columns:
            return jsonify({
                "success": False,
                "error": "CSV must contain 'ID' and 'Resume' columns"
            }), 400
        
        # Initialize chatbot with user's API key
        from matching.cv_chatbot import CVChatbot
        chatbot_instance = CVChatbot(api_key=api_key)
        cv_count = chatbot_instance.load_cvs(df=df)
        
        return jsonify({
            "success": True,
            "cv_count": cv_count,
            "message": f"{cv_count} CVs indexed successfully"
        })
        
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/chatbot/chat", methods=["GET"])
def chatbot_chat():
    """Stream chatbot response using Server-Sent Events"""
    global chatbot_instance
    
    if chatbot_instance is None:
        return jsonify({"error": "Please upload CVs first"}), 400
    
    user_message = request.args.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    def generate():
        try:
            # Get fiches de poste context
            fiches_context = ""
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    rows = conn.execute("SELECT title, description FROM fiches").fetchall()
                    if rows:
                        fiches_list = [f"Titre: {title}\n{desc}" for title, desc in rows]
                        fiches_context = "\n\n---\n\n".join(fiches_list)
            except Exception as e:
                print(f"[WARNING] Could not load fiches: {e}")
            
            # Stream response
            stream = chatbot_instance.generate_response_stream(user_message, fiches_context)
            
            for chunk in stream:
                content = chunk.content
                if content:
                    yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
            
            # Signal completion
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            print(f"[ERROR] Chat failed: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

if __name__ == "__main__":
    print(">>> starting Flask")
    app.run(host="0.0.0.0", port=5000, debug=True)
