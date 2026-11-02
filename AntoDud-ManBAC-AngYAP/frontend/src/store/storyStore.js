/**
 * Store Zustand pour la gestion de l'état global de l'application
 * Gère l'histoire courante, les scènes, et les états de chargement
 */

import { create } from 'zustand';
import { storyService } from '../services/api';

const useStoryStore = create((set, get) => ({
  // État de l'histoire
  currentStory: null,
  currentScene: null,
  allScenes: [],
  storyId: null,
  
  // États de chargement
  isLoading: false,
  isCreating: false,
  isContinuing: false,
  
  // États d'erreur
  error: null,
  
  // États UI
  selectedGenre: null,
  initialPrompt: '',
  
  /**
   * Crée une nouvelle histoire
   */
  createStory: async (genre, initialPrompt = '') => {
    set({ isCreating: true, error: null });
    
    try {
      const response = await storyService.createStory({
        genre,
        initial_prompt: initialPrompt || undefined,
      });
      
      set({
        storyId: response.story_id,
        currentScene: response.current_scene,
        allScenes: [response.current_scene],
        selectedGenre: genre,
        initialPrompt,
        isCreating: false,
        error: null,
      });
      
      return response;
    } catch (error) {
      set({ 
        error: error.message || 'Erreur lors de la création de l\'histoire',
        isCreating: false,
      });
      throw error;
    }
  },
  
  /**
   * Continue l'histoire avec une action utilisateur
   */
  continueStory: async (userAction) => {
    const { storyId, allScenes } = get();
    
    if (!storyId) {
      const error = new Error('Aucune histoire active');
      set({ error: error.message });
      throw error;
    }
    
    set({ isContinuing: true, error: null });
    
    try {
      const response = await storyService.continueStory(storyId, {
        user_action: userAction,
      });
      
      set({
        currentScene: response.current_scene,
        allScenes: [...allScenes, response.current_scene],
        isContinuing: false,
        error: null,
      });
      
      return response;
    } catch (error) {
      set({ 
        error: error.message || 'Erreur lors de la continuation de l\'histoire',
        isContinuing: false,
      });
      throw error;
    }
  },
  
  /**
   * Charge une histoire existante
   */
  loadStory: async (storyId) => {
    set({ isLoading: true, error: null });
    
    try {
      const story = await storyService.getStory(storyId);
      
      set({
        currentStory: story,
        storyId: story.story_id,
        allScenes: story.scenes,
        currentScene: story.scenes[story.scenes.length - 1],
        selectedGenre: story.genre,
        isLoading: false,
        error: null,
      });
      
      return story;
    } catch (error) {
      set({ 
        error: error.message || 'Erreur lors du chargement de l\'histoire',
        isLoading: false,
      });
      throw error;
    }
  },
  
  /**
   * Réinitialise l'histoire courante
   */
  resetStory: () => {
    set({
      currentStory: null,
      currentScene: null,
      allScenes: [],
      storyId: null,
      selectedGenre: null,
      initialPrompt: '',
      error: null,
      isLoading: false,
      isCreating: false,
      isContinuing: false,
    });
  },
  
  /**
   * Définit le genre sélectionné
   */
  setSelectedGenre: (genre) => {
    set({ selectedGenre: genre });
  },
  
  /**
   * Définit le prompt initial
   */
  setInitialPrompt: (prompt) => {
    set({ initialPrompt: prompt });
  },
  
  /**
   * Efface l'erreur
   */
  clearError: () => {
    set({ error: null });
  },
}));

export default useStoryStore;
