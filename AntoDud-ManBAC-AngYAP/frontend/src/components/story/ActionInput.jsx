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
  const [showCustomInput, setShowCustomInput] = useState(false);
  
  const handleSuggestedAction = (action) => {
    onSubmitAction(action);
    setShowCustomInput(false);
    setCustomAction('');
  };
  
  const handleCustomAction = () => {
    if (customAction.trim()) {
      onSubmitAction(customAction);
      setCustomAction('');
      setShowCustomInput(false);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleCustomAction();
    }
  };
  
  return (
    <Card variant="gradient" className="sticky bottom-4">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          <h3 className="font-semibold text-white">Que faites-vous ?</h3>
        </div>
        
        {/* Actions suggérées */}
        {!showCustomInput && suggestedActions.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm text-white/60">Actions suggérées :</p>
            <div className="grid grid-cols-1 gap-2">
              {suggestedActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestedAction(action)}
                  disabled={isLoading}
                  className="text-left px-4 py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-blue-400/50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                  <span className="text-white/80 group-hover:text-white transition-colors">
                    {action}
                  </span>
                </button>
              ))}
            </div>
            
            <button
              onClick={() => setShowCustomInput(true)}
              disabled={isLoading}
              className="w-full text-center py-2 text-sm text-blue-400 hover:text-blue-300 transition-colors disabled:opacity-50"
            >
              ou écrivez votre propre action
            </button>
          </div>
        )}
        
        {/* Input personnalisé */}
        {showCustomInput && (
          <div className="space-y-3 animate-slide-up">
            <Textarea
              placeholder="Décrivez votre action..."
              value={customAction}
              onChange={(e) => setCustomAction(e.target.value)}
              onKeyPress={handleKeyPress}
              rows={3}
              disabled={isLoading}
            />
            
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() => {
                  setShowCustomInput(false);
                  setCustomAction('');
                }}
                disabled={isLoading}
                className="flex-1"
              >
                Annuler
              </Button>
              <Button
                variant="primary"
                onClick={handleCustomAction}
                disabled={!customAction.trim() || isLoading}
                isLoading={isLoading}
                className="flex-1"
              >
                <Send className="w-4 h-4" />
                Envoyer
              </Button>
            </div>
          </div>
        )}
        
        {/* Message pendant le chargement */}
        {isLoading && (
          <div className="text-center py-2">
            <p className="text-sm text-blue-400 animate-pulse">
              L'IA génère la suite de votre histoire...
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default ActionInput;
