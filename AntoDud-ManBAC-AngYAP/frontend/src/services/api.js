/**
 * Service API pour communiquer avec le backend
 * Gère toutes les requêtes HTTP vers l'API FastAPI
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Configuration d'axios avec intercepteurs
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes pour la génération IA
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour logger les requêtes (développement)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Le serveur a répondu avec un code d'erreur
      console.error('[API] Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      // La requête a été envoyée mais pas de réponse
      console.error('[API] No response received:', error.request);
    } else {
      // Erreur lors de la configuration de la requête
      console.error('[API] Request setup error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Service pour les opérations sur les histoires
 */
export const storyService = {
  /**
   * Crée une nouvelle histoire
   * @param {Object} data - Données de création { genre, initial_prompt? }
   * @returns {Promise<Object>} Réponse avec story_id et première scène
   */
  async createStory(data) {
    try {
      const response = await apiClient.post('/stories/', data);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erreur lors de la création de l\'histoire');
    }
  },

  /**
   * Continue une histoire existante
   * @param {string} storyId - ID de l'histoire
   * @param {Object} data - Données { user_action }
   * @returns {Promise<Object>} Réponse avec la nouvelle scène
   */
  async continueStory(storyId, data) {
    try {
      const response = await apiClient.post(`/stories/${storyId}/continue`, data);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erreur lors de la continuation de l\'histoire');
    }
  },

  /**
   * Récupère une histoire complète
   * @param {string} storyId - ID de l'histoire
   * @returns {Promise<Object>} Histoire complète
   */
  async getStory(storyId) {
    try {
      const response = await apiClient.get(`/stories/${storyId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erreur lors de la récupération de l\'histoire');
    }
  },

  /**
   * Récupère les scènes d'une histoire
   * @param {string} storyId - ID de l'histoire
   * @returns {Promise<Array>} Liste des scènes
   */
  async getStoryScenes(storyId) {
    try {
      const response = await apiClient.get(`/stories/${storyId}/scenes`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erreur lors de la récupération des scènes');
    }
  },

  /**
   * Gère les erreurs API
   * @private
   */
  handleError(error, defaultMessage) {
    if (error.response) {
      const message = error.response.data?.detail || defaultMessage;
      return new Error(message);
    } else if (error.request) {
      return new Error('Le serveur ne répond pas. Vérifiez que le backend est démarré.');
    } else {
      return new Error(defaultMessage);
    }
  },
};

/**
 * Service pour les opérations sur les images
 */
export const imageService = {
  /**
   * Construit l'URL complète d'une image
   * @param {string} imagePath - Chemin relatif de l'image
   * @returns {string} URL complète
   */
  getImageUrl(imagePath) {
    if (!imagePath) return null;
    
    // Si c'est déjà une URL complète, la retourner
    if (imagePath.startsWith('http')) {
      return imagePath;
    }
    
    // Extraire story_id et filename du path
    // Format attendu: /path/to/images/{story_id}/{filename}
    const parts = imagePath.split('/');
    const filename = parts[parts.length - 1];
    const storyId = parts[parts.length - 2];
    
    return `${API_BASE_URL}/images/${storyId}/${filename}`;
  },

  /**
   * Vérifie le statut du service d'images
   * @returns {Promise<Object>} Statut du service
   */
  async getStatus() {
    try {
      const response = await apiClient.get('/images/status');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du statut des images:', error);
      return null;
    }
  },
};

/**
 * Service pour le health check
 */
export const healthService = {
  /**
   * Vérifie l'état de l'API
   * @returns {Promise<Object>} État de l'API
   */
  async checkHealth() {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Erreur lors du health check:', error);
      return { status: 'unhealthy' };
    }
  },
};

export default apiClient;
