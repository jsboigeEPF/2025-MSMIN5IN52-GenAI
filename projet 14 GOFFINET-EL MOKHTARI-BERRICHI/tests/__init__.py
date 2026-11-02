import sys
from pathlib import Path

# Ajoute le dossier racine du projet (qui contient "src/") dans le chemin Python
sys.path.append(str(Path(__file__).resolve().parent.parent))
