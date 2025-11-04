# 🤖 AI Recruit Tracker - Suivi Intelligent de Candidatures

> Un système de suivi des candidatures d'emploi propulsé par l'IA (Mistral AI + Gemini AI), automatisant le traitement, la classification et le matching des emails de recrutement.

![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)
![Angular](https://img.shields.io/badge/Angular-20.3-red?logo=angular)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Mistral AI](https://img.shields.io/badge/Mistral_AI-Primary-orange)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-Fallback-purple)

---

## ✨ Fonctionnalités principales

### 🧠 Intelligence Artificielle Avancée

#### **Classification Multi-Niveaux (4 étapes)**
1. **Filtre d'exclusion** : 60+ patterns pour éliminer newsletters, marketing, e-commerce
2. **Validation recrutement** : Vérification des indicateurs RH (CV, candidature, poste, etc.)
3. **Règles regex intelligentes** : Patterns contextuels avec priorité (OFFER > REJECTED > INTERVIEW > REQUEST > ACK)
4. **IA avec fallback** : Mistral AI (primary) → Gemini AI (fallback si quota dépassé)

#### **Types de Classification**
- 📬 **ACK** (Acknowledgment) : Accusés de réception simples
- ❌ **REJECTED** : Refus explicites (priorité haute pour éviter faux espoirs)
- 🎯 **INTERVIEW** : Convocations et suivis d'actions ("Suite à votre candidature", "invitation à entretien")
- 🎉 **OFFER** : Offres et félicitations ("félicitations - votre candidature avance")
- 📄 **REQUEST** : Demandes de documents complémentaires
- 🔍 **OTHER** : Emails non-recrutement (newsletters filtrées automatiquement)

#### **Extraction d'Entités**
- Détection automatique : entreprises, postes, contacts, dates
- Valeurs par défaut intelligentes si extraction partielle
- Enrichissement contextuel des données

#### **Matching Sémantique**
- Liaison automatique emails ↔ candidatures via embeddings
- Détection de doublons et regroupement intelligent
- Score de confiance pour chaque match

### 📊 Tableau de Bord Complet
- **Vue d'ensemble** : Statistiques temps réel (Total, En cours, Entretiens, Acceptées)
- **Timeline interactive** : Historique complet des interactions par candidature
- **Filtres avancés** : Par statut, entreprise, poste, date, source
- **Alertes intelligentes** : Rappels basés sur l'analyse IA
- **Métriques de performance** : Taux de réponse, délais moyens, success rate

### � Authentification & Sécurité
- **Bearer Token JWT** : Authentification sécurisée avec tokens en sessionStorage
- **Session persistante** : Pas de déconnexion au rechargement de la page
- **Gmail OAuth 2.0** : Connexion sécurisée à votre boîte mail
- **Permissions granulaires** : Accès utilisateur isolé (multi-tenant ready)

---

## 🎯 Objectif du Projet

**Problème** : Suivre des dizaines de candidatures via emails est chronophage et source d'erreurs
- Perte d'historique
- Oublis de relances
- Newsletters polluant les vrais emails de recrutement
- Classification manuelle fastidieuse

**Solution** : Une application qui :
- ✅ Ingère automatiquement les emails Gmail
- ✅ Filtre les newsletters et spam (60+ patterns d'exclusion)
- ✅ Classifie intelligemment avec IA à 2 niveaux (Mistral + Gemini fallback)
- ✅ Extrait les informations clés (entreprise, poste, dates)
- ✅ Crée et met à jour automatiquement les candidatures
- ✅ Fournit un dashboard clair pour suivre et corriger

---

## 🏗️ Architecture Technique

### Stack Complète
- **Backend** : FastAPI (Python 3.13+) avec PostgreSQL 16
- **Frontend** : Angular 20.3 avec Angular Material
- **IA** : Mistral AI (mistral-large-latest) + Gemini AI (fallback)
- **Base de données** : PostgreSQL avec migrations Alembic
- **Infrastructure** : Docker Compose pour déploiement complet
- **Email** : Gmail API OAuth 2.0 avec auto-refresh tokens

### Flux de Traitement NLP

```mermaid
graph TD
    A[Email reçu] --> B[Filtre exclusion<br/>60+ patterns]
    B -->|Newsletter/Marketing| Z[Classification: OTHER]
    B -->|Passe| C[Validation recrutement<br/>CV, candidature, poste?]
    C -->|Non| Z
    C -->|Oui| D[Classification par règles<br/>Patterns contextuels]
    D -->|Confiance >= 0.7| E[Résultat final]
    D -->|Confiance < 0.7| F[IA Mistral]
    F -->|Erreur 429| G[IA Gemini Fallback]
    F -->|Succès| E
    G --> E
    E --> H[Extraction entités]
    H --> I[Matching candidatures]
    I --> J[Actions automatiques<br/>Création/Mise à jour]
```

### Système de Priorité de Classification

```python
OFFER (5) > REJECTED (4) > INTERVIEW (3) > REQUEST (2) > ACK (1) > OTHER (0)
```

**Logique** : Les décisions finales (OFFER/REJECTED) priment sur les actions intermédiaires (INTERVIEW), qui priment sur les simples accusés (ACK).

---

## 🚀 Démarrage Rapide (5 minutes)

### Prérequis
```bash
docker --version        # >= 20.10
docker-compose --version # >= 2.0
python --version        # >= 3.11 (pour dev backend)
node --version          # >= 18 (pour dev frontend)
```

### Installation Express

1. **Cloner et naviguer**
   ```bash
   git clone <repository-url>
   cd projetIARecructTracker
   ```

2. **Configuration environnement**
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   **Éditer `backend/.env` avec vos clés API** :
   ```bash
   # API Keys IA (OBLIGATOIRE)
   MISTRAL_API_KEY=your_mistral_key_here
   GEMINI_API_KEY=your_gemini_key_here  # Fallback optionnel mais recommandé
   
   # Base de données
   DATABASE_URL=postgresql+psycopg://airtrack:airtrackpwd@localhost:5432/airtrackdb
   
   # JWT Secret (générer avec: openssl rand -hex 32)
   SECRET_KEY=your_secret_key_here
   
   # Gmail OAuth (optionnel pour auto-sync)
   GMAIL_CLIENT_ID=your_gmail_client_id
   GMAIL_CLIENT_SECRET=your_gmail_client_secret
   ```

3. **Démarrage avec Docker**
   ```bash
   docker-compose up -d
   ```

4. **Vérification installation**
   ```bash
   # Santé du backend
   curl http://localhost:8000/health
   
   # Accès frontend
   open http://localhost:4200
   ```

### Accès aux Services
- 🌐 **Application Web** : http://localhost:4200
- 📚 **API Documentation** : http://localhost:8000/docs
- 🔍 **Health Check** : http://localhost:8000/health
- 🗃️ **PostgreSQL** : localhost:5432 (airtrack/airtrackpwd)

---

## 🧪 Tests et Validation

### Test de Classification (100% success rate)

```bash
cd backend
python test_classification.py
```

**Scénarios testés** :
- ✅ Newsletters Uber/Zalando → OTHER
- ✅ Emails e-commerce Carrefour → OTHER  
- ✅ Notifications LinkedIn → OTHER
- ✅ Accusé réception vraie candidature → ACK
- ✅ Refus de candidature → REJECTED
- ✅ Convocation entretien → INTERVIEW
- ✅ Alertes Indeed (pas candidature) → OTHER

### Test de Patterns Spécifiques

```bash
python test_suite_candidature.py
```

**Validation** :
- ✅ "Suite à votre candidature" → INTERVIEW (pas ACK)
- ✅ "Donnons suite" → INTERVIEW
- ✅ "Revenons vers vous" → INTERVIEW
- ✅ Refus avec "ne donnerons pas suite" → REJECTED (pas INTERVIEW)

### Test Félicitations & Offres

```bash
python test_felicitations.py
```

**Validation** :
- ✅ "Félicitations - Votre candidature avance" → OFFER
- ✅ Patterns avec/sans contexte de refus

### Test Fallback IA

```bash
python test_ai_fallback.py
```

**Validation** :
- ✅ Mistral AI primary classification
- ✅ Gemini AI fallback si quota Mistral dépassé (429)
- ✅ Retry logic et timeout handling

---
   ```bash
   ---

## 📂 Structure du Projet

```
projetIARecructTracker/
├── backend/                      # API FastAPI
│   ├── app/
│   │   ├── api/v1/endpoints/    # Routes REST
│   │   ├── core/                # Config, auth, AI clients
│   │   │   ├── mistral_client.py   # Client Mistral AI
│   │   │   ├── gemini_client.py    # Client Gemini (fallback)
│   │   │   └── gmail_client.py     # Gmail OAuth
│   │   ├── models/              # SQLAlchemy models & schemas
│   │   ├── services/            # Business logic
│   │   ├── nlp/                 # Services NLP
│   │   │   ├── classification_service.py  # 4-level classification
│   │   │   ├── extraction_service.py      # Entity extraction
│   │   │   ├── matching_service.py        # Semantic matching
│   │   │   └── nlp_orchestrator.py        # Workflow orchestration
│   │   └── main.py              # FastAPI app
│   ├── alembic/                 # Migrations DB
│   ├── tests/                   # Tests unitaires
│   ├── test_*.py                # Scripts de test
│   └── requirements.txt
├── frontend/                    # Application Angular
│   ├── src/app/
│   │   ├── components/
│   │   │   ├── job-applications/      # Liste & détails candidatures
│   │   │   ├── emails/                # Gestion emails
│   │   │   ├── nlp/                   # Dashboard NLP
│   │   │   └── intelligent-excel-tracker/  # Vue Excel-like
│   │   ├── services/           # Services HTTP
│   │   ├── guards/             # Auth guards
│   │   └── interceptors/       # JWT interceptor
│   ├── angular.json
│   └── package.json
├── infra/                       # Infrastructure
│   ├── docker-compose.yml
│   └── env/
│       ├── db.env
│       ├── backend.env
│       └── frontend.env
└── README.md
```

---

## 🔧 Configuration Avancée

### Variables d'Environnement Backend

```bash
# backend/.env

# ═══ DATABASE ═══
DATABASE_URL=postgresql+psycopg://airtrack:airtrackpwd@localhost:5432/airtrackdb

# ═══ SECURITY ═══
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ═══ AI SERVICES ═══
# Mistral AI (Primary classifier)
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-large-latest

# Gemini AI (Fallback when Mistral quota exceeded)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# ═══ GMAIL OAUTH 2.0 ═══
GMAIL_CLIENT_ID=your_gmail_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/auth/gmail/callback

# ═══ CORS ═══
ALLOWED_ORIGINS=http://localhost:4200,http://localhost:80

# ═══ LOGGING ═══
LOG_LEVEL=INFO
```

### Obtenir les Clés API

#### Mistral AI
1. Visitez https://console.mistral.ai/
2. Créez un compte et naviguez vers "API Keys"
3. Générez une nouvelle clé et copiez-la dans `MISTRAL_API_KEY`

#### Gemini AI (Optionnel mais recommandé)
1. Visitez https://makersuite.google.com/app/apikey
2. Créez une clé API Google AI Studio
3. Copiez-la dans `GEMINI_API_KEY`

#### Gmail OAuth 2.0 (Pour auto-sync)
1. Allez sur https://console.cloud.google.com/
2. Créez un projet et activez Gmail API
3. Configurez l'écran de consentement OAuth
4. Créez des identifiants OAuth 2.0 (Application Web)
5. Ajoutez `http://localhost:8000/api/v1/auth/gmail/callback` dans les URIs de redirection

---

## 💡 Utilisation

### 1. Première Connexion
```
1. Ouvrez http://localhost:4200
2. Cliquez sur "Se connecter"
3. Créez un compte ou connectez-vous
4. Le token JWT est stocké en sessionStorage (persistant au refresh)
```

### 2. Synchroniser Gmail
```
1. Dashboard → "Connecter Gmail"
2. Autorisez l'accès à votre boîte mail
3. Cliquez sur "Actualiser" pour sync les emails
4. La classification NLP se lance automatiquement
```

### 3. Voir les Résultats
```
1. Onglet "Emails" : Voir tous les emails classifiés
   - Badge coloré par type (ACK, INTERVIEW, OFFER, etc.)
   - Confiance de classification affichée
   - Filtrer par type ou rechercher

2. Onglet "Candidatures" : Vue agrégée
   - Statistiques en haut (Total, En cours, Entretiens, Acceptées)
   - Filtres par statut
   - Détails candidature avec timeline complète

3. Onglet "NLP Dashboard" : Métriques IA
   - Taux de classification par type
   - Distribution des confidences
   - Stats d'extraction d'entités
```

### 4. Actions Manuelles
```
- Créer une candidature manuellement
- Lier un email à une candidature existante
- Corriger une classification IA (feedback loop)
- Ajouter des notes et rappels
- Changer le statut manuellement
```

---

## 🤖 Détails Techniques NLP

### Classification - 4 Niveaux de Filtrage

#### **Niveau 1 : Exclusion (60+ patterns)**
Filtre préventif pour éliminer les faux positifs :

```python
# Domaines exclus
- uber.com, zalando, carrefour, amazon, etc.
- linkedin, facebook, twitter, instagram
- newsletter, marketing, promo keywords

# Contextes exclus
- Commandes, livraisons, factures
- Notifications sociales
- Events, meetups, webinaires
```

#### **Niveau 2 : Validation Recrutement**
Vérifie la présence d'indicateurs RH :

```python
Required keywords:
- candidature, application, CV, resume
- job, poste, position, offre
- entretien, interview
- recruteur, HR, ressources humaines
```

#### **Niveau 3 : Règles Regex Intelligentes**

**Patterns ACK (Acknowledgment)**
```python
- "avons bien reçu", "reçu votre candidature"
- "prise en compte", "candidature enregistrée"  
- "merci pour votre candidature" (SANS action follow-up)
```

**Patterns REJECTED (Priorité HAUTE)**
```python
- "ne donnerons pas suite", "candidature non retenue"
- "autres candidats", "profil différent"
- "malheureusement.*ne", "nous regrettons"
```

**Patterns INTERVIEW**
```python
# Actions de suivi (distinguer de ACK)
- "suite à votre candidature" (avec negative lookahead pour refus)
- "donnons suite" (MAIS PAS "ne donnerons pas suite")
- "revenons vers vous"

# Invitations explicites
- "invitation.*entretien", "convocation"
- "souhaitons vous rencontrer"
- "disponibilité.*entretien"
```

**Patterns OFFER**
```python
- "félicitations.*candidature" (très fort signal)
- "félicitations.*avance" (votre candidature avance)
- "heureux de vous proposer"
- "offre.*contrat", "proposition d'embauche"
- "(candidature|profil).*avance"
```

**Système de Priorité**
```python
priority_order = [
    OFFER (5),      # Décision positive finale
    REJECTED (4),   # Décision négative finale - AVANT INTERVIEW
    INTERVIEW (3),  # Action concrète
    REQUEST (2),    # Demande documents
    ACK (1)         # Simple accusé réception
]
```

**Pourquoi REJECTED avant INTERVIEW ?**
> Un email peut contenir à la fois "suite à votre candidature" ET "ne donnerons pas suite". Sans priorité correcte, il serait classé INTERVIEW au lieu de REJECTED (faux espoir!).

#### **Niveau 4 : IA avec Fallback**

```python
# Mistral AI (Primary)
- Model: mistral-large-latest
- Prompt: 350+ lignes avec exemples et contexte
- Confiance: retourne score 0.0-1.0

# Gemini AI (Fallback)
- Activé si Mistral → 429 (quota exceeded)
- Model: gemini-1.5-flash  
- Parsing robuste des réponses JSON
```

### Conditions de Création Automatique

```python
Créer une candidature SI:
✅ Pas de match existant (not matches)
✅ Email non déjà lié (not email.application_id)
✅ Type recrutement (ACK, INTERVIEW, OFFER, REQUEST, REJECTED)
✅ Confiance >= 0.7  # IMPORTANT: >= pas >

Extraction accepte valeurs par défaut:
- company_name = "Entreprise non spécifiée"
- job_title = "Poste non spécifié"
```

### Gestion des Erreurs

```python
# UUID dans JSON
✅ Fix: Conversion UUID → str avant JSONB (ApplicationEvent.payload)

# Transaction rollback
✅ Fix: Gestion propre des exceptions avec db.rollback()

# Mistral quota
✅ Fix: Fallback automatique vers Gemini si 429
```

---

## 📊 Métriques et Performance

### Taux de Succès (Tests Internes)

| Test Suite | Scénarios | Succès | Taux |
|------------|-----------|--------|------|
| Classification générale | 8 | 8/8 | 100% |
| Patterns spécifiques (ACK vs INTERVIEW) | 5 | 5/5 | 100% |
| Félicitations & Offres | 1 | 1/1 | 100% |
| AI Fallback (Mistral → Gemini) | 1 | 1/1 | 100% |

### Patterns d'Exclusion

- **60+ patterns** de filtrage newsletter/marketing
- **~95% précision** sur filtrage non-recrutement
- **<5% faux négatifs** (vrais emails recrutement exclus)

### Performance IA

- **Mistral classification** : ~2-3s par email
- **Gemini fallback** : ~1-2s par email
- **Extraction entités** : ~1s par email
- **Matching sémantique** : ~0.5s pour 50 candidatures

---

## 🐛 Débogage et Logs

### Logs Backend (Loguru)

```bash
# Voir les logs en temps réel
docker-compose logs -f backend

# Logs de classification
grep "🔍 Auto-creation check" logs/backend.log

# Logs IA
grep "Mistral AI\|Gemini AI" logs/backend.log
```

### Logs NLP Détaillés

Quand `batch-process` est appelé, les logs affichent :
```
🔍 Auto-creation check - Email <id>:
  - Has matches: False (count: 0)
  - Classification: INTERVIEW (confidence: 0.95)
  - Is recruitment type: True
  - Already linked to app: None
  - Condition 1 (not matches): True
  - Condition 2 (not email.application_id): True
  - Condition 3 (is recruitment): True
  - Condition 4 (confidence >= 0.7): True
  - ALL CONDITIONS: True
✅ Creating auto-application: <company> - <job>
```

### Problèmes Courants

**❌ Candidatures non créées**
```bash
# Check: Confiance >= 0.7 ?
# Check: Email déjà lié (application_id) ?
# Check: Type recrutement valide ?
# Solution: Voir logs "ALL CONDITIONS"
```

**❌ Mistral 429 Error**
```bash
# Quota API dépassé
# ✅ Fallback Gemini s'active automatiquement
# Check logs: "Falling back to Gemini"
```

**❌ Classification incorrecte**
```bash
# Option 1: Ajuster patterns dans classification_service.py
# Option 2: Feedback loop (feature future)
# Option 3: Correction manuelle dans UI
```

---
   ```

4. **Accéder aux services**
   - 🌍 Frontend: http://localhost:4200
   - 🔧 Backend API: http://localhost:8000
   - 📚 Documentation API: http://localhost:8000/docs

**Problème :** suivre des dizaines de candidatures via emails est chronophage (perte d'historique, oublis de relance).it Tracker — README (Light)

Gestion intelligente des candidatures à partir des **emails** et d’actions manuelles.  
Stack : **FastAPI** (Python) · **PostgreSQL** · **Angular** · **Docker Compose**

---

## 1) But du projet

**Problème :** suivre des dizaines de candidatures via emails est chronophage (perte d’historique, oublis de relance).  
**Solution :** une appli qui **ingère** les emails, **extrait** les infos clés, **met à jour** le statut des candidatures et propose un **dashboard** clair pour suivre et corriger.

---

## 2) Périmètre (MVP)

- Connexion à une boîte mail (Gmail/IMAP) **ou** import manuel (`.eml/.mbox`).  
- Extraction : **entreprise**, **intitulé de poste**, **dates** et **contacts**.  
- Classification par règles simples : `APPLIED`, `ACKNOWLEDGED`, `SCREENING`, `INTERVIEW`, `OFFER`, `REJECTED`, `ON_HOLD`, `WITHDRAWN`.  
- **Dashboard Angular** : liste + filtre + détail avec timeline d’événements.  
- **Relances** basiques : calcul de `next_action_at` (ex. J+7 sans réponse).

> Objectif MVP : ingestion + règles FR/EN + CRUD candidatures + UI liste/détail.

---

## 3) Stack & modules

- **Backend :** FastAPI, SQLAlchemy, Alembic, scheduler (APScheduler).  
- **Base :** PostgreSQL.  
- **Frontend :** Angular (tableau, filtres, détail).  
- **Conteneurisation :** Docker Compose.
- (Optionnel) Classif. légère : scikit-learn (LogReg / LinearSVC) + TF‑IDF.

---

## 4) Architecture (vue simple)
az
Angular (UI) ⟶ FastAPI (API REST + jobs d’ingestion) ⟶ PostgreSQL (données)

Connecteurs mails : Gmail API / IMAP (pull périodique) ou import manuel.

---

## 5) Modèle de données (résumé)

```sql
-- applications
id (uuid, pk), company_name, job_title, status, next_action_at, created_at

-- emails
id (uuid, pk), application_id (fk), external_id, subject, sender, sent_at, snippet, classification

-- application_events
id (uuid, pk), application_id (fk), event_type, payload(jsonb), created_at
```

---

## 6) Endpoints principaux (extraits)

- `GET /api/v1/applications` (filtres: status, q, company)  
- `POST /api/v1/applications`  
- `GET /api/v1/applications/{id}` & `GET /api/v1/applications/{id}/events`  
- `GET /api/v1/emails?unlinked=true`  
- `POST /api/v1/emails/import` (upload .eml/.mbox)  
- `POST /api/v1/ingestion/run` (pull immédiat)

---

## 7) Démarrage rapide (Docker)

**Arbo minimale**
```
ai-recruit-tracker/
  backend/
  frontend/
  infra/
    docker-compose.yml
    env/
      db.env
      backend.env
      frontend.env
```

**infra/docker-compose.yml**
```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    env_file: ./env/db.env
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports: ["5432:5432"]

  backend:
    build: ../backend
    env_file: ./env/backend.env
    depends_on:
      - db
    ports: ["8000:8000"]
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ../frontend
    depends_on:
      - backend
    ports: ["4200:80"]

volumes:
  pgdata:
```

**infra/env/db.env**
```
POSTGRES_USER=airtrack
POSTGRES_PASSWORD=airtrackpwd
POSTGRES_DB=airtrackdb
```

**infra/env/backend.env**
```
DATABASE_URL=postgresql+psycopg://airtrack:airtrackpwd@db:5432/airtrackdb
ALLOWED_ORIGINS=http://localhost:4200
```

**infra/env/frontend.env**
```
API_BASE_URL=http://localhost:8000/api/v1
```

---

## 8) Roadmap courte

- **S1** : CRUD + schéma + liste/détail Angular.  
- **S2** : import `.eml` + règles FR/EN + timeline.  
- **S3** : connecteur IMAP/Gmail + scheduler + relances.

---

## 9) Licence

À définir selon le contexte.
