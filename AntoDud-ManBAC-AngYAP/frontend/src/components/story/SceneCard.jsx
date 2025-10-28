/**
 * Composant SceneCard
 * Responsable de l'affichage d'une scène individuelle
 * Respecte le principe SRP - gère uniquement l'affichage d'une scène
 */

import { useState } from 'react';
import { ImageIcon, Maximize2 } from 'lucide-react';
import Card from '../ui/Card';
import { imageService } from '../../services/api';
import ReactMarkdown from 'react-markdown';

const SceneCard = ({ scene, isLatest = false }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [showFullImage, setShowFullImage] = useState(false);
  
  const imageUrl = scene.image_url ? imageService.getImageUrl(scene.image_url) : null;
  
  return (
    <div className={`animate-slide-up ${isLatest ? 'ring-2 ring-blue-400' : ''}`}>
      <Card variant="gradient" className="overflow-hidden">
        <div className="space-y-4">
          {/* Numéro de scène */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-blue-400 uppercase tracking-wide">
              Scène {scene.scene_number}
            </span>
            {isLatest && (
              <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full">
                Dernière
              </span>
            )}
          </div>
          
          {/* Image générée */}
          {imageUrl && !imageError && (
            <div className="relative group">
              <div className="relative overflow-hidden rounded-lg bg-slate-800/50 aspect-square">
                {!imageLoaded && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="flex flex-col items-center gap-2">
                      <ImageIcon className="w-8 h-8 text-white/20 animate-pulse" />
                      <p className="text-xs text-white/40">Chargement de l'image...</p>
                    </div>
                  </div>
                )}
                <img
                  src={imageUrl}
                  alt={`Scène ${scene.scene_number}`}
                  className={`w-full h-full object-cover transition-opacity duration-300 ${
                    imageLoaded ? 'opacity-100' : 'opacity-0'
                  }`}
                  onLoad={() => setImageLoaded(true)}
                  onError={() => {
                    setImageError(true);
                    console.error('Erreur chargement image:', imageUrl);
                  }}
                />
                {imageLoaded && (
                  <button
                    onClick={() => setShowFullImage(true)}
                    className="absolute top-2 right-2 p-2 bg-black/50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Maximize2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          )}
          
          {imageError && (
            <div className="bg-slate-800/50 aspect-square rounded-lg flex items-center justify-center">
              <div className="text-center">
                <ImageIcon className="w-8 h-8 text-white/20 mx-auto mb-2" />
                <p className="text-xs text-white/40">Image non disponible</p>
              </div>
            </div>
          )}
          
          {/* Texte narratif */}
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              className="text-white/90 leading-relaxed"
              components={{
                p: ({ children }) => <p className="mb-3">{children}</p>,
                strong: ({ children }) => <strong className="text-blue-300 font-semibold">{children}</strong>,
                em: ({ children }) => <em className="text-purple-300">{children}</em>,
              }}
            >
              {scene.narrative_text}
            </ReactMarkdown>
          </div>
          
          {/* Action utilisateur (si présente) */}
          {scene.user_action && (
            <div className="pt-3 border-t border-white/10">
              <p className="text-xs text-white/50 mb-1">Votre action :</p>
              <p className="text-sm text-green-300 italic">
                → {scene.user_action.action_text}
              </p>
            </div>
          )}
        </div>
      </Card>
      
      {/* Modal plein écran pour l'image */}
      {showFullImage && imageUrl && (
        <div
          className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setShowFullImage(false)}
        >
          <div className="relative max-w-4xl max-h-[90vh]">
            <img
              src={imageUrl}
              alt={`Scène ${scene.scene_number}`}
              className="max-w-full max-h-[90vh] object-contain rounded-lg"
            />
            <button
              onClick={() => setShowFullImage(false)}
              className="absolute top-4 right-4 p-2 bg-black/50 rounded-lg hover:bg-black/70 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SceneCard;
