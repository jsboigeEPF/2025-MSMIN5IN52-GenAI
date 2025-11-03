# Backend - Interactive Story Generator

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation des dépendances

1. Clonez le repository et naviguez vers le dossier backend :
```bash
cd backend
```

2. Créez un environnement virtuel Python :
```bash
python -m venv venv
```

3. Activez l'environnement virtuel :
- Sur Windows :
```bash
venv\Scripts\activate
```
- Sur Linux/Mac :
```bash
source venv/bin/activate
```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration

1. Copiez le fichier de configuration d'exemple :
```bash
copy .env.example .env
```

2. Modifiez le fichier `.env` selon vos besoins :
- Configurez les modèles IA (Qwen, Stable Diffusion)
- Ajoutez vos clés API si nécessaire (OpenAI, Hugging Face)
- Modifiez les paramètres de serveur si nécessaire

## Lancement du serveur

1. Assurez-vous que l'environnement virtuel est activé

2. Lancez le serveur de développement :
```bash
python main.py
```

Le serveur sera accessible sur `http://localhost:8000`

## API Documentation

Une fois le serveur lancé, vous pouvez accéder à la documentation interactive de l'API :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## Structure du projet

```
backend/
├── main.py              # Point d'entrée de l'application
├── requirements.txt     # Dépendances Python
├── .env.example        # Fichier de configuration d'exemple
├── app/
│   ├── config.py       # Configuration de l'application
│   ├── models/         # Modèles de données
│   ├── routers/        # Routes API
│   └── services/       # Services métier
└── data/
    ├── stories/        # Stockage des histoires
    └── images/         # Stockage des images générées
```