from flask import Flask, jsonify, request
from flask_cors import CORS
from Gmail_API import readMail
from Calendar_API import get_credentials, list_events, create_event
from login import get_credentials as auth_credentials
from googleapiclient.discovery import build
import datetime
import os
from chatbot import get_chatbot_response

app = Flask(__name__)
CORS(app)


@app.route('/api/emails')
def get_emails():
    try:
        emails = []
        # Capturer la sortie de readMail dans une structure de données
        # au lieu de l'imprimer
        creds = None
        results = readMail(10)  # Récupérer les 10 derniers emails
        return jsonify({"emails": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/calendar/events')
def get_calendar_events():
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)
        events = list_events(service)  # Utilise ta fonction
        return jsonify({"events": events})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/calendar/events', methods=['POST'])
def create_calendar_event():
    try:
        data = request.get_json()
        summary = data.get("summary")
        date = data.get("date")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        location = data.get("location", "")
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)
        event_id = create_event(service, summary, date,
                                start_time, end_time, location)
        return jsonify({"success": True, "event_id": event_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/auth/login', methods=['POST'])
def login():
    try:
        # Tentative d'authentification avec Google
        creds = auth_credentials()
        if creds and creds.valid:
            return jsonify({"success": True, "message": "Authentification réussie"})
        return jsonify({"success": False, "message": "Échec de l'authentification"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/auth/logout', methods=['POST'])
def logout():
    """
    Déconnecte l'utilisateur en supprimant le fichier token.json.
    Cette route est appelée par le bouton "Déconnexion" du front-end.
    """
    try:
        # Le chemin est relatif à l'endroit où le script est exécuté.
        # Si vous lancez `python API/api.py` depuis la racine, le chemin est correct.
        token_path = 'token.json'
        if os.path.exists(token_path):
            os.remove(token_path)
            return jsonify({'success': True, 'message': 'Déconnexion réussie, token supprimé.'})
        else:
            return jsonify({'success': True, 'message': 'Aucun token à supprimer, session déjà inexistante.'})
    except Exception as e:
        print(f"Erreur lors de la suppression de token.json: {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur lors de la déconnexion.'}), 500


@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        query = data.get("query")
        response = get_chatbot_response(query)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
