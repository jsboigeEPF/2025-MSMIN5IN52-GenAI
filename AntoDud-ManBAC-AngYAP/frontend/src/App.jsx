/**
 * Composant principal de l'application
 * Gère le routing entre la création et l'affichage de l'histoire
 */

import { useState } from 'react';
import StoryCreation from './components/story/StoryCreation';
import StoryDisplay from './components/story/StoryDisplay';
import Loading from './components/ui/Loading';
import useStoryStore from './store/storyStore';

function App() {
  const [view, setView] = useState('creation'); // 'creation' | 'story'
  const { storyId, isCreating, resetStory } = useStoryStore();
  
  const handleStoryCreated = () => {
    setView('story');
  };
  
  const handleReset = () => {
    resetStory();
    setView('creation');
  };
  
  return (
    <div className="min-h-screen py-8">
      {/* Loading global pendant la création */}
      {isCreating && (
        <Loading 
          fullScreen 
          size="xl" 
          text="Création de votre histoire en cours..." 
        />
      )}
      
      {/* Vue de création ou d'affichage */}
      {view === 'creation' && !storyId && (
        <StoryCreation onStoryCreated={handleStoryCreated} />
      )}
      
      {view === 'story' && storyId && (
        <StoryDisplay onReset={handleReset} />
      )}
    </div>
  );
}

export default App;
