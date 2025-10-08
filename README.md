# Musical Loop Generation Application

This application generates musical loops based on ambiance types using external AI music generation APIs. It provides a web interface for users to select ambiance types and generate corresponding instrumental loops.

## 1. Prerequisites and Dependencies

Before setting up the application, ensure you have the following prerequisites installed:

### System Requirements
- Python 3.8 or higher
- Node.js (for frontend development, optional)
- Git (for cloning the repository)

### Python Dependencies
The application requires the following Python packages:
- Flask (web framework)
- aiohttp (asynchronous HTTP client)
- python-dotenv (environment variable management)
- pytest (testing framework)

Install the required Python packages using pip:
```bash
pip install flask aiohttp python-dotenv pytest
```

### External API Services
The application integrates with three external music generation APIs:
- Suno AI
- Udio
- Stable Audio

You'll need to obtain API keys from these services to use the full functionality.

## 2. Environment Setup

### Clone the Repository
```bash
git clone https://github.com/your-username/musical-loop-generator.git
cd musical-loop-generator
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
Copy the example configuration file and update it with your API keys:

```bash
cp config/app_config.json config/app_config.json
```

Edit the `config/app_config.json` file to add your API keys:

```json
{
  "api_keys": {
    "suno": "your_suno_api_key_here",
    "udio": "your_udio_api_key_here",
    "stable_audio": "your_stable_audio_api_key_here"
  },
  "api_endpoints": {
    "suno": "https://api.suno.ai/v1/music",
    "udio": "https://api.udio.com/v1/generate",
    "stable_audio": "https://api.stableaudio.com/v1/sound"
  }
}
```

## 3. API Key Configuration

To configure API keys for the external services:

1. **Suno API**:
   - Visit [Suno AI](https://www.suno.ai/) and create an account
   - Navigate to your account settings to generate an API key
   - Add the key to the `api_keys.suno` field in `config/app_config.json`

2. **Udio API**:
   - Visit [Udio](https://www.udio.com/) and create an account
   - Access the developer portal to generate an API key
   - Add the key to the `api_keys.udio` field in `config/app_config.json`

3. **Stable Audio**:
   - Visit [Stable Audio](https://stableaudio.com/) and create an account
   - Navigate to the API section to generate an API key
   - Add the key to the `api_keys.stable_audio` field in `config/app_config.json`

**Security Note**: Never commit your API keys to version control. The `config/app_config.json` file is included in `.gitignore` by default.

## 4. Launching the Application

The application consists of a Flask backend server and a frontend interface. Both need to be running.

### Start the Flask Server
```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

### Start the Frontend Server
In a separate terminal, navigate to the project root and start the frontend server:
```bash
python -m http.server 8000
```

Alternatively, you can open `src/ui/index.html` directly in your browser.

### Access the Application
Open your web browser and navigate to:
- Frontend: `http://localhost:8000/src/ui/index.html`
- API Endpoint: `http://localhost:5000`

## 5. Using the Application Interface

Once the application is running, you can use the web interface to generate musical loops:

1. **Select Ambiance Type**:
   - Use the dropdown menu to select from available ambiance types
   - Current options include: Mysterious Forest, Cyberpunk in the Rain, Medieval Castle, and Sports Fans Chanting

2. **Adjust Parameters**:
   - **Tempo**: Use the slider to adjust the beats per minute (BPM)
   - **Volume**: Control the overall volume of the generated loop

3. **Generate and Play**:
   - Click the play button to generate and play the musical loop
   - The first generation may take several seconds as it calls external APIs
   - Subsequent generations with the same parameters will be faster due to caching

4. **Download**:
   - Click the "Download Loop" button to save the generated audio as a WAV file
   - The filename will include the ambiance type and tempo

5. **Request New Ambiance**:
   - Click the "Request New Ambiance" button to submit a request for a new ambiance type
   - Fill out the form with the desired ambiance name and description
   - This feature allows users to suggest new ambiance types for future implementation

## 6. Adding New Ambiance Types

To add a new ambiance type to the application:

### Step 1: Create an Ambiance Configuration File
Create a new JSON file in the `assets/ambiance_configs/` directory with a descriptive name (use snake_case):

```bash
touch assets/ambiance_configs/new_ambiance.json
```

### Step 2: Define the Ambiance Configuration
Edit the JSON file with the following structure:

```json
{
  "tempo": 72,
  "instruments": [
    {
      "name": "instrument_name",
      "volume": -6,
      "effects": ["reverb", "delay"],
      "pattern": "random_interval"
    }
  ],
  "effects_chain": ["reverb", "low_pass_filter"],
  "description": "A description of the ambiance and mood"
}
```

Key configuration options:
- `tempo`: BPM for the generated music
- `instruments`: Array of instruments to include
  - `name`: Instrument identifier
  - `volume`: Volume level in dB
  - `effects`: Array of audio effects to apply
  - `pattern`: Generation pattern (e.g., "random_interval", "steady_beat")
- `effects_chain`: Order of effects to apply to the final mix

### Step 3: Add Instrument Samples (Optional)
For custom instruments, add WAV files to `assets/audio_samples/` with the naming convention:
```
[ambiance]_[instrument]_[variation].wav
```

For example: `forest_birds_01.wav`

### Step 4: Verify the New Ambiance
Restart the application server and check that your new ambiance appears in the dropdown menu.

## 7. Running Unit Tests

The application includes a comprehensive test suite to ensure functionality and prevent regressions.

### Run All Tests
```bash
python -m pytest tests/
```

### Run Specific Test Files
```bash
# Test ambiance manager
python -m pytest tests/test_ambiance_manager.py

# Test audio generation
python -m pytest tests/test_audio_generation.py

# Test application core
python -m pytest tests/test_application.py
```

### Run Tests with Coverage
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

This will generate a coverage report in the `htmlcov/` directory.

### Test Structure
The test suite is organized as follows:
- `tests/test_ambiance_manager.py`: Tests for ambiance configuration loading and validation
- `tests/test_audio_generation.py`: Tests for audio generation service and API integration
- `tests/test_application.py`: Tests for the main application controller

Each test file contains unit tests that verify the functionality of the corresponding module, including edge cases and error handling.

## Troubleshooting

### Common Issues
1. **API Keys Not Working**:
   - Verify that your API keys are correctly entered in `config/app_config.json`
   - Check that the API services are operational
   - Ensure you have sufficient credits/quotas with the service providers

2. **CORS Errors**:
   - Make sure the frontend and backend are running on the correct ports
   - The Flask server (port 5000) serves as the API endpoint for the frontend

3. **Audio Generation Failures**:
   - Check the application logs for error messages
   - Verify internet connectivity
   - Try a different ambiance type or parameters

4. **Missing Ambiance Types**:
   - Ensure configuration files are in the correct directory (`assets/ambiance_configs/`)
   - Verify JSON files are valid and contain required fields

For additional support, please contact the development team or consult the project documentation.
# Projet de Fin de Cours - IA Générative 2025

Bienvenue sur le dépôt officiel pour la soumission du projet de fin de cours sur l'IA Générative.

## Instructions de Soumission

1.  **Forkez ce dépôt :** Chaque groupe doit créer un "fork" de ce dépôt pour y travailler.
2.  **Créez un dossier pour votre groupe :** À la racine de votre fork, créez un dossier unique pour votre groupe (ex: `groupe-alpha`, `projet-rag-chatbot`, etc.).
3.  **Placez vos livrables :** Tous vos livrables (code, `README.md` de votre projet, slides, etc.) doivent être placés à l'intérieur de ce dossier.
4.  **Soumettez via une Pull Request :** Une fois votre projet terminé, créez une Pull Request depuis votre fork vers le dépôt principal. La PR doit être soumise au plus tard **l'avant-veille de la présentation finale**.

## Sujets Proposé

Voici quelques pistes de sujets. Vous êtes encouragés à proposer les vôtres.

### Catégorie : Agents et Systèmes Intelligents

1.  **Agent RAG pour la documentation du cours**
    *   Description : Créer un chatbot capable de répondre aux questions des étudiants sur le contenu du cours en se basant sur les supports fournis.
    *   Technologies clés : RAG, Base de données vectorielle, LangChain/Semantic Kernel.
    *   Difficulté : ⭐⭐ (Intermédiaire)

2.  **Agent autonome pour la planification de voyage**
    *   Description : Créer un agent capable de planifier un itinéraire de voyage en utilisant des outils (recherche web, API) via du "Function Calling".
    *   Technologies clés : IA Agentique, Function Calling, API externes.
    *   Difficulté : ⭐⭐⭐⭐ (Très avancé)

3.  **Tuteur de code adaptatif**
    *   Description : Développer un agent qui aide les étudiants à apprendre un concept de programmation en posant des questions et en expliquant les erreurs.
    *   Technologies clés : Prompt engineering avancé (rôle, CoT), analyse de code.
    *   Difficulté : ⭐⭐⭐ (Avancé)

4.  **Agent d'Analyse d'Arguments Hybride**
    *   Description : Un système qui analyse un débat en utilisant un LLM pour l'analyse informelle (sophismes) et une bibliothèque d'IA symbolique (TweetyProject) pour valider la structure logique.
    *   Technologies clés : IA Hybride, TweetyProject, LangChain/Semantic Kernel.
    *   Difficulté : ⭐⭐⭐⭐ (Très avancé)

5.  **Simulateur de Scénario Ludique Multi-Agents**
    *   Description : Concevoir une simulation textuelle (escape game, mini-jeu de rôle) où plusieurs agents IA dotés de personnalités distinctes doivent interagir pour atteindre un objectif.
    *   Technologies clés : Semantic Kernel (AgentGroupChat), stratégies de conversation.
    *   Difficulté : ⭐⭐⭐ (Avancé)

### Catégorie : Applications Métier

6.  **Agent de Recrutement Augmenté**
    *   Description : Développez un outil qui compare un lot de CVs à une fiche de poste et produit un classement justifié des candidats.
    *   Technologies clés : RAG, extraction d'entités, Pandas.
    *   Difficulté : ⭐⭐⭐ (Avancé)

7.  **Veille Concurrentielle Automatisée**
    *   Description : Créez un agent qui scrape les sites de concurrents et synthétise les informations clés dans un rapport de veille hebdomadaire.
    *   Technologies clés : Scraping web, analyse et synthèse de texte.
    *   Difficulté : ⭐⭐⭐ (Avancé)

8.  **Assistant de Réponse à Appel d'Offres**
    *   Description : Concevez un système qui génère une première ébauche de réponse technique à un appel d'offres en se basant sur le cahier des charges et une base de connaissances interne.
    *   Technologies clés : RAG, génération de texte long format.
    *   Difficulté : ⭐⭐⭐⭐ (Très avancé)

### Catégorie : Génération Multimédia et Créative

9.  **Générateur d'histoires multimodales**
    *   Description : Développer une application qui génère une histoire courte et illustre chaque paragraphe avec une image générée.
    *   Technologies clés : API OpenAI (GPT-4o, DALL-E 3) ou modèles locaux.
    *   Difficulté : ⭐⭐⭐ (Avancé)

10. **Compositeur de Bandes Sonores d'Ambiance**
    *   Description : Créez une application qui génère des boucles musicales instrumentales pour des ambiances spécifiques (ex: "forêt mystérieuse", "cyberpunk sous la pluie").
    *   Technologies clés : API de génération musicale (Suno, Udio, Stable Audio).
    *   Difficulté : ⭐⭐⭐ (Avancé)

11. **Générateur de Storyboards Vidéo**
    *   Description : Développez un outil qui prend un court scénario et le transforme en une séquence de clips vidéo courts (storyboard animé).
    *   Technologies clés : LLM pour la scénarisation, API de génération vidéo (Luma Dream Machine).
    *   Difficulté : ⭐⭐⭐⭐ (Très avancé)

12. **Créateur d'Assets 3D pour le Prototypage**
    *   Description : Concevez une application qui génère rapidement des modèles 3D simples à partir d'images ou de textes pour une utilisation dans un moteur de jeu.
    *   Technologies clés : Modèles Image-to-3D (TripoSR) ou Text-to-3D (Luma Genie).
    *   Difficulté : ⭐⭐⭐ (Avancé)

### Catégorie : Outils de Développement et d'Analyse

13. **Auditeur de biais dans les LLMs**
    *   Description : Concevoir un outil qui évalue les biais d'un modèle de langage en lui soumettant des prompts standardisés et en analysant les réponses.
    *   Technologies clés : Prompt engineering, analyse de texte, visualisation de données.
    *   Difficulté : ⭐⭐ (Intermédiaire)

14. **Générateur de Contenu Structuré (CV, Facture, Rapport)**
    *   Description : Développez un workflow multi-agents qui prend des informations en langage naturel et génère un document structuré au format PDF.
    *   Technologies clés : Semantic Kernel, ReportLab (pour PDF), gestion de workflow.
    *   Difficulté : ⭐⭐⭐ (Avancé)

---
Pour toutes les autres informations (planning, critères d'évaluation détaillés), veuillez vous référer au document de modalités fourni dans le dossier du cours.

Bon projet à tous !
