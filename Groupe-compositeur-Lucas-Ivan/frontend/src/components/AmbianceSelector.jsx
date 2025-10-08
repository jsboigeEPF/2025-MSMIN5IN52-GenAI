import React from 'react';
import './AmbianceSelector.css';

const ambianceIcons = {
  'foret-mysterieuse': '🌲',
  'cyberpunk-pluie': '🌃',
  'plage-coucher-soleil': '🏖️',
  'meditation-zen': '🧘',
  'cafe-jazz': '☕',
  'montagne-majestueuse': '🏔️',
  'desert-nocturne': '🌵',
  'ville-futuriste': '🏙️'
};

function AmbianceSelector({ ambiances, selectedAmbiance, onSelect, isGenerating }) {
  return (
    <section className="ambiance-selector">
      <h2>Choisissez votre ambiance</h2>
      <div className="ambiances-grid">
        {ambiances.map((ambiance) => (
          <button
            key={ambiance.id}
            className={`ambiance-card ${selectedAmbiance === ambiance.id ? 'selected' : ''}`}
            onClick={() => onSelect(ambiance.id)}
            disabled={isGenerating}
          >
            <div className="ambiance-icon">
              {ambianceIcons[ambiance.id] || '🎵'}
            </div>
            <h3>{ambiance.name}</h3>
            <p className="ambiance-style">{ambiance.style}</p>
            {selectedAmbiance === ambiance.id && isGenerating && (
              <div className="generating-badge">Génération...</div>
            )}
          </button>
        ))}
      </div>
    </section>
  );
}

export default AmbianceSelector;