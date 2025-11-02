# 🧳 Agent Autonome de Planification de Voyage  

## 🚀 Description du projet  
Ce projet met en place un **agent IA autonome** capable de planifier un **itinéraire de voyage complet** en utilisant :  

- 🌐 **Recherche web en temps réel** pour obtenir les meilleures informations (vols, hôtels, attractions, météo).  
- ⚙️ **Function Calling** pour connecter l’agent à des **API externes** (Google Maps, Skyscanner, OpenWeather, Booking, etc.).  
- 🤖 **Raisonnement autonome** : l’agent choisit lui-même quelles fonctions appeler, dans quel ordre, et combine les résultats pour créer un plan cohérent.  

---

## 🛠️ Technologies Clés  
- **IA Agentique** : un agent autonome qui réfléchit, planifie et agit.  
- **Function Calling** : permet à l’IA d’appeler des fonctions définies pour interagir avec le monde réel.  
- **Langage** : Python / Node.js (selon implémentation choisie).  
- **Orchestration** : utilisation d’un framework agentique (LangChain, OpenAI Agents, etc.).  

---

## 📂 Fonctionnalités  
✅ Trouver et comparer des vols ✈️  
✅ Réserver ou suggérer des hôtels 🏨  
✅ Vérifier la météo et ajuster l’itinéraire 🌦️  
✅ Proposer des activités locales 🗺️  
✅ Générer un itinéraire optimisé (jour par jour) 📅  
✅ Adapter les choix selon le **budget** et le **style de voyage** (détente, aventure, culture).  

---

## ⚙️ Comment ça marche ?  

### 1. Entrée utilisateur  
Tu indiques :  
- La **destination** (ex: Tokyo 🇯🇵)  
- Les **dates de voyage**  
- Ton **budget** et préférences  

### 2. Raisonnement de l’agent  
L’agent :  
1. Analyse la demande  
2. Décide quelles fonctions appeler (ex: `searchFlights`, `getHotels`, `getWeather`, `findAttractions`)  
3. Combine les résultats  
4. Produit un **plan de voyage complet**  

### 3. Sortie  
Un **itinéraire détaillé**, par exemple :  

Jour 1 : Arrivée à Tokyo - installation à l’hôtel Shinjuku
Jour 2 : Visite du quartier d’Asakusa + Tokyo Skytree
Jour 3 : Excursion au Mont Fuji (météo favorable)
Jour 4 : Shopping à Shibuya et Harajuku
Jour 5 : Retour

---

Planifie un voyage à Lisbonne pour 5 jours avec un budget moyen.

📖 Exemple de scénario

👉 Entrée :

"Je veux aller à Barcelone du 5 au 10 août, budget 1200€, je préfère la culture et la gastronomie."

👉 Sortie (extrait généré) :

Vol recommandé : Paris → Barcelone (Air France, 120€ A/R)

Hôtel 3★ dans le quartier de l’Eixample (450€ total)

Jour 1 : arrivée + tapas tour 🍷
Jour 2 : Sagrada Familia + Parc Güell
Jour 3 : Marché de la Boqueria + musée Picasso
Jour 4 : Excursion à Montserrat
Jour 5 : plage + retour

Architecture
User Request
      ⬇️
Agent (LLM + Reasoning)
      ⬇️
Recherche Web
      ⬇️
Aggregation & Planning
      ⬇️
Travel Itinerary

## 🚀 Installation Guide

Follow these steps to set up and run the AI Trip Planner application.

### Prerequisites

*   **Python 3.8+**: For the backend.
*   **Node.js (LTS recommended)**: For the frontend.
*   **npm** (comes with Node.js) or **Yarn**.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>/groupe-BESTFOREVER
```

### 2. Backend Setup

Navigate to the `backend` directory:

```bash
cd backend
```

#### Create a Python Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables (`.env`)

Create a `.env` file in the `groupe-BESTFOREVER/backend/` directory (if it doesn't exist) and add your API keys:

```
OPENAI_KEY=your_openai_api_key_here
GEMINI_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

*   **OpenAI API Key:** Obtain from [OpenAI Platform](https://platform.openai.com/).
*   **Google Gemini API Key:** Obtain from [Google AI Studio](https://aistudio.google.com/app/apikey).
*   **Tavily API Key:** Obtain from [Tavily](https://tavily.com/).

#### Run the Backend Server

```bash
uvicorn main:app --reload
```

The backend API will be running at `http://127.0.0.1:8000`. You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup

Open a **new terminal** and navigate to the `frontend` directory:

```bash
cd ../frontend
```

#### Install Node.js Dependencies

```bash
npm install
# or yarn install
```

#### Run the Frontend Development Server

```bash
npm run dev
# or yarn dev
```

The frontend application will be running at `http://localhost:5173` (or another port if 5173 is in use).

### 4. Usage

Open your browser to the frontend URL (e.g., `http://localhost:5173`). You can now interact with the AI Trip Planner, select your preferred AI model, and choose your language.

---