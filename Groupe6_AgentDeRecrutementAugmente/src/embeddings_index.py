# src/embeddings_index.py
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss  # FAISS pour recherche vectorielle
import os

MODEL_NAME = "all-MiniLM-L6-v2"
CACHE_FOLDER = os.path.join(os.path.dirname(__file__), 'models_cache')  # dossier local pour le cache
os.makedirs(CACHE_FOLDER, exist_ok=True)

# Classe pour gérer l'index FAISS et le matching
class SimpleFaissIndex:
    def __init__(self, model_name=MODEL_NAME):
        # Charger le modèle de sentence embeddings sur CPU avec cache local
        self.model = SentenceTransformer(model_name, device='cpu', cache_folder=CACHE_FOLDER)
        self.dim = self.model.get_sentence_embedding_dimension()
        # Index FAISS pour recherche de similarité cosinus
        self.index = faiss.IndexFlatIP(self.dim)
        self.texts = []

    def add(self, texts):
        """
        Ajouter une liste de textes à l'index
        """
        # Convertir les textes en embeddings
        embs = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        # FAISS attend un array float32
        embs = np.array(embs, dtype='float32')
        self.index.add(embs)  # type: ignore
        self.texts.extend(texts)

    def search(self, query, top_k=3):
        """
        Chercher les top_k textes les plus proches de la requête
        """
        # Encoder la requête
        q = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        q = np.array(q, dtype='float32')
        # Rechercher dans l'index
        D, I = self.index.search(q, top_k)  # type: ignore
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            results.append({"text": self.texts[idx], "score": float(score)})
        return results

# Création d'une instance globale pour que app.py puisse l'utiliser directement
faiss_index = SimpleFaissIndex()
