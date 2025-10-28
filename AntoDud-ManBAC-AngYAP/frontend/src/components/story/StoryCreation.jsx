/**
 * Composant StoryCreation
 * Responsable de l'interface de création d'une nouvelle histoire
 * Respecte le principe SRP - gère uniquement la sélection du genre et le prompt initial
 */

import { useState } from 'react';
import { Sparkles, Wand2, Skull, Search, Compass, Heart } from 'lucide-react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Textarea from '../ui/Textarea';
import useStoryStore from '../../store/storyStore';

const GENRES = [
  {
    id: 'fantasy',
    name: 'Fantasy',
    icon: Wand2,
    description: 'Magie, créatures fantastiques et aventures épiques',
    color: 'from-purple-500 to-pink-500',
  },
  {
    id: 'sci-fi',
    name: 'Science-Fiction',
    icon: Sparkles,
    description: 'Technologies futuristes et voyages spatiaux',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    id: 'horror',
    name: 'Horreur',
    icon: Skull,
    description: 'Suspense et atmosphère terrifiante',
    color: 'from-red-500 to-orange-500',
  },
  {
    id: 'mystery',
    name: 'Mystère',
    icon: Search,
    description: 'Enquêtes et indices à découvrir',
    color: 'from-indigo-500 to-purple-500',
  },
  {
    id: 'adventure',
    name: 'Aventure',
    icon: Compass,
    description: 'Quêtes passionnantes et découvertes',
    color: 'from-green-500 to-emerald-500',
  },
  {
    id: 'romance',
    name: 'Romance',
    icon: Heart,
    description: 'Histoires d\'amour et émotions',
    color: 'from-pink-500 to-rose-500',
  },
];

const StoryCreation = ({ onStoryCreated }) => {
  const [selectedGenre, setSelectedGenre] = useState(null);
  const [initialPrompt, setInitialPrompt] = useState('');
  const [showPromptInput, setShowPromptInput] = useState(false);
  
  const { createStory, isCreating, error } = useStoryStore();
  
  const handleGenreSelect = (genre) => {
    setSelectedGenre(genre);
    setShowPromptInput(true);
  };
  
  const handleMouseMove = (e) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    // Position de la souris pour le spotlight
    card.style.setProperty('--mouse-x', `${x}%`);
    card.style.setProperty('--mouse-y', `${y}%`);
    
    // Calcul de l'inclinaison pour l'effet 3D
    // Centre = (50, 50), on calcule le décalage
    const rotateX = ((y - 50) / 50) * -10; // -10 à +10 degrés
    const rotateY = ((x - 50) / 50) * 10;  // -10 à +10 degrés
    
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
  };
  
  const handleMouseLeave = (e) => {
    const card = e.currentTarget;
    // Transition uniquement pour le retour
    card.style.transition = 'transform 0.3s ease';
    card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';
    // Retirer la transition après l'animation de retour
    setTimeout(() => {
      card.style.transition = 'none';
    }, 300);
  };
  
  const handleCreateStory = async () => {
    if (!selectedGenre) return;
    
    try {
      await createStory(selectedGenre.id, initialPrompt);
      if (onStoryCreated) {
        onStoryCreated();
      }
    } catch (err) {
      console.error('Erreur création:', err);
    }
  };
  
  const handleBack = () => {
    setShowPromptInput(false);
    setSelectedGenre(null);
    setInitialPrompt('');
  };
  
  return (
    <div className="w-full max-w-6xl mx-auto px-4 animate-fade-in">
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Générateur d'Histoires Interactives
        </h1>
        <p className="text-xl text-white/70">
          Créez votre propre aventure avec l'intelligence artificielle
        </p>
      </div>
      
      {!showPromptInput ? (
        <div>
          <h2 className="text-2xl font-semibold text-center mb-6 text-white/90">
            Choisissez votre genre d'histoire
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {GENRES.map((genre) => {
              const Icon = genre.icon;
              return (
                <div
                  key={genre.id}
                  className="genre-card cursor-pointer group"
                  onClick={() => handleGenreSelect(genre)}
                  onMouseMove={handleMouseMove}
                  onMouseLeave={handleMouseLeave}
                  style={{ transformStyle: 'preserve-3d', transition: 'none' }}
                >
                  <Card
                    variant="gradient"
                    className="genre-card-content h-full"
                  >
                    <div className="flex flex-col items-center text-center p-6 h-full">
                      <div className={`p-4 rounded-full bg-gradient-to-r ${genre.color} mb-4 group-hover:scale-110 transition-transform`}>
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-xl font-bold mb-2">{genre.name}</h3>
                      <p className="text-sm text-white/60 flex-grow">{genre.description}</p>
                    </div>
                  </Card>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <Card variant="gradient" className="max-w-2xl mx-auto animate-slide-up">
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-full bg-gradient-to-r ${selectedGenre.color}`}>
                {<selectedGenre.icon className="w-6 h-6 text-white" />}
              </div>
              <div>
                <h2 className="text-2xl font-bold">{selectedGenre.name}</h2>
                <p className="text-white/60">{selectedGenre.description}</p>
              </div>
            </div>
            
            <div>
              <Textarea
                label="Contexte initial (optionnel)"
                placeholder="Décrivez le monde, le personnage ou la situation de départ... Laissez vide pour laisser l'IA décider !"
                value={initialPrompt}
                onChange={(e) => setInitialPrompt(e.target.value)}
                rows={6}
              />
              <p className="text-xs text-white/40 mt-2">
                💡 Astuce : Plus vous donnez de détails, plus l'histoire sera personnalisée !
              </p>
            </div>
            
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}
            
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={handleBack}
                disabled={isCreating}
                className="flex-1"
              >
                Retour
              </Button>
              <Button
                variant="primary"
                onClick={handleCreateStory}
                isLoading={isCreating}
                disabled={isCreating}
                className="flex-1"
              >
                {isCreating ? 'Création en cours...' : 'Commencer l\'aventure'}
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default StoryCreation;
