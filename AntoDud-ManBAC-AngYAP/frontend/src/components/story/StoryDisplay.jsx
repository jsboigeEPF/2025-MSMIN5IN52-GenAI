/**
 * Composant StoryDisplay
 * Responsable de l'affichage de l'histoire en cours
 * Respecte le principe SRP - gère uniquement l'affichage et la navigation dans l'histoire
 */

import { useEffect, useRef } from 'react';
import { RotateCcw, BookOpen } from 'lucide-react';
import Button from '../ui/Button';
import SceneCard from './SceneCard';
import ActionInput from './ActionInput';
import Loading from '../ui/Loading';
import useStoryStore from '../../store/storyStore';

const StoryDisplay = ({ onReset }) => {
  const { allScenes, currentScene, continueStory, isContinuing, error, clearError } = useStoryStore();
  const scenesEndRef = useRef(null);
  
  // Auto-scroll vers la dernière scène
  useEffect(() => {
    if (scenesEndRef.current) {
      scenesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [allScenes.length]);
  
  const handleAction = async (action) => {
    clearError();
    try {
      await continueStory(action);
    } catch (err) {
      console.error('Erreur continuation:', err);
    }
  };
  
  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-8">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-gradient-to-b from-slate-900 to-transparent py-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <BookOpen className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Votre Histoire</h2>
              <p className="text-sm text-white/60">
                {allScenes.length} scène{allScenes.length > 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <Button
            variant="secondary"
            onClick={onReset}
            disabled={isContinuing}
          >
            <RotateCcw className="w-4 h-4" />
            Nouvelle histoire
          </Button>
        </div>
      </div>
      
      {/* Messages d'erreur */}
      {error && (
        <div className="mb-6 animate-slide-up">
          <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4">
            <p className="text-red-400">{error}</p>
            <button
              onClick={clearError}
              className="mt-2 text-sm text-red-300 hover:text-red-200 underline"
            >
              Fermer
            </button>
          </div>
        </div>
      )}
      
      {/* Liste des scènes */}
      <div className="space-y-6 mb-6">
        {allScenes.map((scene, index) => (
          <SceneCard
            key={scene.scene_id || index}
            scene={scene}
            isLatest={index === allScenes.length - 1}
          />
        ))}
        <div ref={scenesEndRef} />
      </div>
      
      {/* Loading pendant génération */}
      {isContinuing && (
        <div className="mb-6">
          <Loading size="md" text="Génération de la suite en cours..." />
        </div>
      )}
      
      {/* Input d'action */}
      {currentScene && !isContinuing && (
        <ActionInput
          suggestedActions={currentScene.suggested_actions || []}
          onSubmitAction={handleAction}
          isLoading={isContinuing}
        />
      )}
    </div>
  );
};

export default StoryDisplay;
