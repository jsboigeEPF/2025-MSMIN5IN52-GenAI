/**
 * Composant ActionInput
 * Responsable de la saisie et de l'envoi des actions utilisateur
 * Respecte le principe SRP - gère uniquement l'input et la soumission des actions
 */

import { useState } from 'react';
import { Send, Lightbulb } from 'lucide-react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Textarea from '../ui/Textarea';

const ActionInput = ({ suggestedActions = [], onSubmitAction, isLoading = false }) => {
  const [customAction, setCustomAction] = useState('');
  
  const handleSuggestedAction = (action) => {
    onSubmitAction(action);
    setCustomAction('');
  };
  
  const handleCustomAction = () => {
    if (customAction.trim()) {
      onSubmitAction(customAction);
      setCustomAction('');
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleCustomAction();
    }
  };
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 pb-3 border-b border-white/10">
        <Lightbulb className="w-5 h-5 text-yellow-400" />
        <h3 className="font-semibold text-white">Que faites-vous ?</h3>
      </div>
      
      {/* Actions suggérées */}
      {suggestedActions.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-white/60">Actions suggérées :</p>
          <div className="space-y-2">
            {suggestedActions.map((action, index) => (
              <button
                key={index}
                onClick={() => handleSuggestedAction(action)}
                disabled={isLoading}
                className="w-full text-left px-4 py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-blue-400/50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                <span className="text-white/80 group-hover:text-white transition-colors text-sm">
                  {action}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Input personnalisé toujours visible */}
      <div className="space-y-3">
        <p className="text-sm text-white/60">Ou écrivez votre action :</p>
        <Textarea
          placeholder="Décrivez votre action personnalisée..."
          value={customAction}
          onChange={(e) => setCustomAction(e.target.value)}
          onKeyPress={handleKeyPress}
          rows={4}
          disabled={isLoading}
        />
        
        <Button
          variant="primary"
          onClick={handleCustomAction}
          disabled={!customAction.trim() || isLoading}
          isLoading={isLoading}
          className="w-full"
        >
          <Send className="w-4 h-4" />
          Envoyer
        </Button>
      </div>
      
      {/* Message pendant le chargement */}
      {isLoading && (
        <div className="text-center py-2">
          <p className="text-sm text-blue-400 animate-pulse">
            L'IA génère la suite...
          </p>
        </div>
      )}
    </div>
  );
};

export default ActionInput;
