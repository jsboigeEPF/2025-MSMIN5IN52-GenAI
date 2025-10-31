import React, { useState } from 'react';
import './CustomGenerator.css';

function CustomGenerator({ onGenerate, isGenerating }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [customName, setCustomName] = useState('');
  const [customDescription, setCustomDescription] = useState('');
  const [customStyle, setCustomStyle] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (customDescription.trim()) {
      onGenerate({
        name: customName.trim() || 'Composition personnalisée',
        description: customDescription.trim(),
        style: customStyle.trim() || 'Custom'
      });
      // Réinitialiser après génération
      setCustomName('');
      setCustomDescription('');
      setCustomStyle('');
      setIsExpanded(false);
    }
  };

  return (
    <div className="custom-generator">
      <button 
        className="expand-button"
        onClick={() => setIsExpanded(!isExpanded)}
        disabled={isGenerating}
      >
        <span className="expand-icon">{isExpanded ? '−' : '+'}</span>
        <div className="expand-text">
          <h3>Création Personnalisée</h3>
          <p>Décrivez votre propre ambiance musicale</p>
        </div>
        <svg 
          className={`chevron ${isExpanded ? 'rotated' : ''}`}
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {isExpanded && (
        <form className="custom-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="customName">Nom de la composition (optionnel)</label>
            <input
              id="customName"
              type="text"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder="ex: Aube Tranquille"
              disabled={isGenerating}
            />
          </div>

          <div className="form-group">
            <label htmlFor="customDescription">Description de l'ambiance *</label>
            <textarea
              id="customDescription"
              value={customDescription}
              onChange={(e) => setCustomDescription(e.target.value)}
              placeholder="Décrivez l'ambiance que vous souhaitez créer... ex: Piano doux avec des sons de pluie légère et des nappes atmosphériques"
              rows="4"
              required
              disabled={isGenerating}
            />
            <span className="char-count">{customDescription.length}/500</span>
          </div>

          <div className="form-group">
            <label htmlFor="customStyle">Style musical (optionnel)</label>
            <input
              id="customStyle"
              type="text"
              value={customStyle}
              onChange={(e) => setCustomStyle(e.target.value)}
              placeholder="ex: Ambient, Lo-fi, Classical"
              disabled={isGenerating}
            />
          </div>

          <button 
            type="submit" 
            className="generate-button"
            disabled={isGenerating || !customDescription.trim()}
          >
            {isGenerating ? (
              <>
                <div className="button-spinner"></div>
                Génération en cours...
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 18V5l12-2v13" />
                  <circle cx="6" cy="18" r="3" />
                  <circle cx="18" cy="16" r="3" />
                </svg>
                Générer la musique
              </>
            )}
          </button>
        </form>
      )}
    </div>
  );
}

export default CustomGenerator;