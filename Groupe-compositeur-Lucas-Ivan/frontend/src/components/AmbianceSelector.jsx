import React from 'react';
import './AmbianceSelector.css';

function AmbianceSelector({ ambiances, selectedAmbiance, onSelect, isGenerating }) {
  return (
    <div className="ambiance-selector">
      <div className="section-header">
        <h2>Ambiances Prédéfinies</h2>
        <span className="badge">{ambiances.length} disponibles</span>
      </div>
      
      <div className="ambiances-grid">
        {ambiances.map((ambiance) => (
          <button
            key={ambiance.id}
            className={`ambiance-card ${selectedAmbiance === ambiance.id ? 'selected' : ''} ${isGenerating ? 'disabled' : ''}`}
            onClick={() => !isGenerating && onSelect(ambiance.id)}
            disabled={isGenerating}
          >
            <div className="ambiance-content">
              <h3 className="ambiance-name">{ambiance.name}</h3>
              <p className="ambiance-style">{ambiance.style}</p>
            </div>
            {selectedAmbiance === ambiance.id && isGenerating && (
              <div className="generating-indicator">
                <div className="spinner"></div>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

export default AmbianceSelector;