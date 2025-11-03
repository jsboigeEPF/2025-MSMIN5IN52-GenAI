# Comment lancer le front-end

## Méthode 1 : Utiliser Python (le plus simple)

1. Ouvrez un terminal dans le dossier Front-end
2. Lancez la commande selon votre version de Python :

Pour Python 3 :

```bash
python -m http.server 8000
```

Pour Python 2 :

```bash
python -m SimpleHTTPServer 8000
```

3. Ouvrez votre navigateur et allez à l'adresse : http://localhost:8000

## Méthode 2 : Utiliser VS Code avec Live Server

1. Installez l'extension "Live Server" dans VS Code
2. Clic droit sur le fichier index.html
3. Sélectionnez "Open with Live Server"
4. Le site s'ouvrira automatiquement dans votre navigateur par défaut

## Note importante

Le site est une application statique qui fonctionne entièrement dans le navigateur. Vous n'avez pas besoin d'installer de dépendances ou de framework particulier.
