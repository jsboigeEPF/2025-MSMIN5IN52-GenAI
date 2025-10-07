# Frontend - Interactive Story Generator

## Installation

### Prérequis
- Node.js 18.0 ou supérieur
- npm (gestionnaire de paquets Node.js)

### Installation des dépendances

1. Naviguez vers le dossier frontend :
```bash
cd frontend
```

2. Installez les dépendances :
```bash
npm install
```

## Configuration

1. Créez un fichier `.env.local` à la racine du dossier frontend :
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

2. Modifiez l'URL de l'API si votre backend est hébergé ailleurs.

## Lancement du serveur de développement

1. Lancez le serveur de développement :
```bash
npm run dev
```

L'application sera accessible sur `http://localhost:3000`

## Build de production

Pour créer une version de production :

1. Générez le build :
```bash
npm run build
```

2. Lancez la version de production :
```bash
npm start
```

## Scripts disponibles

- `npm run dev` : Lance le serveur de développement
- `npm run build` : Génère une version de production
- `npm start` : Lance la version de production
- `npm run lint` : Vérifie le code avec ESLint

## Technologies utilisées

- **Next.js 14** : Framework React pour les applications web
- **TypeScript** : Typage statique pour JavaScript
- **Tailwind CSS** : Framework CSS utilitaire
- **Radix UI** : Composants UI accessibles
- **Axios** : Client HTTP pour les appels API
- **Lucide React** : Icônes

## Structure du projet

```
frontend/
├── package.json         # Dépendances et scripts
├── next.config.js       # Configuration Next.js
├── tailwind.config.js   # Configuration Tailwind CSS
├── tsconfig.json        # Configuration TypeScript
├── .env.local          # Variables d'environnement locales
├── src/
│   ├── app/            # Pages et layouts (App Router)
│   ├── components/     # Composants réutilisables
│   ├── lib/           # Utilitaires et configuration
│   └── types/         # Types TypeScript
└── public/            # Fichiers statiques
```

## Développement

L'application utilise le nouveau App Router de Next.js 13+. Les pages sont définies dans le dossier `src/app/`.

Pour ajouter de nouvelles fonctionnalités :
1. Créez vos composants dans `src/components/`
2. Ajoutez vos types dans `src/types/`
3. Configurez vos appels API dans `src/lib/`