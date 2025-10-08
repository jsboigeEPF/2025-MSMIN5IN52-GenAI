import React, { useState } from 'react';
import './CustomGenerator.css';

function CustomGenerator({ onGenerate, isGenerating }) {
  const [isOpen, setIsOpen] = useState(false);
  const [customSettings, setCustomSettings] = useState({
    prompt: '',
    style: 'Ambient',
    title: '',
    negativeTags: '',
    styleWeight: 0.65,
    weirdnessConstraint: 0.65,
    audioWeight: 0.65
  });

  const musicStyles = [
    'Ambient', 'Classical', 'Electronic', 'Jazz', 'Rock', 'Pop',
    'Cinematic', 'Orchestral', 'Synthwave', 'Lo-fi', 'Chill',
    'Epic', 'Ethnic', 'Folk', 'Blues', 'R&B', 'Hip-Hop',
    'Metal', 'Indie', 'Tropical', 'House', 'Techno', 'Trance'
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!customSettings.prompt.trim()) {
      alert('Veuillez décrire l\'ambiance souhaitée');
      return;
    }

    onGenerate('custom', customSettings);
    setIsOpen(false);
  };

  const handleChange = (field, value) => {
    setCustomSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="custom-generator">
      <button 
        className="open-custom-button"
        onClick={() => setIsOpen(!isOpen)}
        disabled={isGenerating}
      >
        ✨ Créer une ambiance personnalisée
      </button>

      {isOpen && (
        <div className="custom-form-overlay" onClick={() => setIsOpen(false)}>
          <div className="custom-form-container" onClick={(e) => e.stopPropagation()}>
            <div className="custom-form-header">
              <h2>🎨 Personnaliser votre musique</h2>
              <button className="close-button" onClick={() => setIsOpen(false)}>✕</button>
            </div>

            <form onSubmit={handleSubmit} className="custom-form">
              {/* Description / Prompt */}
              <div className="form-group">
                <label htmlFor="prompt">
                  <strong>Description de l'ambiance</strong>
                  <span className="required">*</span>
                </label>
                <textarea
                  id="prompt"
                  rows="4"
                  placeholder="Ex: Une forêt enchantée au crépuscule avec des sons de nature apaisants et des mélodies mystérieuses..."
                  value={customSettings.prompt}
                  onChange={(e) => handleChange('prompt', e.target.value)}
                  required
                />
                <small>Décrivez l'ambiance, les instruments, l'émotion que vous souhaitez</small>
              </div>

              {/* Titre */}
              <div className="form-group">
                <label htmlFor="title">
                  <strong>Titre de la composition</strong>
                </label>
                <input
                  type="text"
                  id="title"
                  placeholder="Ex: Forêt Enchantée"
                  value={customSettings.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                />
              </div>

              {/* Style musical */}
              <div className="form-group">
                <label htmlFor="style">
                  <strong>Style musical</strong>
                </label>
                <select
                  id="style"
                  value={customSettings.style}
                  onChange={(e) => handleChange('style', e.target.value)}
                >
                  {musicStyles.map(style => (
                    <option key={style} value={style}>{style}</option>
                  ))}
                </select>
              </div>

              {/* Tags négatifs */}
              <div className="form-group">
                <label htmlFor="negativeTags">
                  <strong>Éléments à éviter</strong>
                </label>
                <input
                  type="text"
                  id="negativeTags"
                  placeholder="Ex: Vocals, Heavy Drums, Fast tempo"
                  value={customSettings.negativeTags}
                  onChange={(e) => handleChange('negativeTags', e.target.value)}
                />
                <small>Séparez par des virgules les éléments que vous ne voulez PAS</small>
              </div>

              {/* Paramètres avancés */}
              <div className="advanced-settings">
                <h3>⚙️ Paramètres avancés</h3>
                
                {/* Style Weight */}
                <div className="slider-group">
                  <label>
                    <strong>Fidélité au style</strong>
                    <span className="slider-value">{customSettings.styleWeight.toFixed(2)}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={customSettings.styleWeight}
                    onChange={(e) => handleChange('styleWeight', parseFloat(e.target.value))}
                  />
                  <div className="slider-labels">
                    <span>Plus libre</span>
                    <span>Plus fidèle</span>
                  </div>
                </div>

                {/* Weirdness Constraint */}
                <div className="slider-group">
                  <label>
                    <strong>Créativité</strong>
                    <span className="slider-value">{customSettings.weirdnessConstraint.toFixed(2)}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={customSettings.weirdnessConstraint}
                    onChange={(e) => handleChange('weirdnessConstraint', parseFloat(e.target.value))}
                  />
                  <div className="slider-labels">
                    <span>Conventionnel</span>
                    <span>Expérimental</span>
                  </div>
                </div>

                {/* Audio Weight */}
                <div className="slider-group">
                  <label>
                    <strong>Qualité audio</strong>
                    <span className="slider-value">{customSettings.audioWeight.toFixed(2)}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={customSettings.audioWeight}
                    onChange={(e) => handleChange('audioWeight', parseFloat(e.target.value))}
                  />
                  <div className="slider-labels">
                    <span>Standard</span>
                    <span>Haute qualité</span>
                  </div>
                </div>
              </div>

              {/* Boutons */}
              <div className="form-actions">
                <button 
                  type="button" 
                  className="cancel-button"
                  onClick={() => setIsOpen(false)}
                >
                  Annuler
                </button>
                <button 
                  type="submit" 
                  className="generate-button"
                  disabled={isGenerating}
                >
                  {isGenerating ? 'Génération...' : '🎵 Générer la musique'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default CustomGenerator;