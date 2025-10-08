import React from 'react';
import './GenerationStatus.css';

function GenerationStatus({ ambiance, isCustom, customData }) {
  return (
    <div className="generation-status">
      <div className="status-card">
        <div className="loader"></div>
        <h3>Génération en cours...</h3>
        {isCustom && customData ? (
          <div>
            <p>Création de <strong>{customData.name}</strong></p>
            {customData.style && <p className="custom-style">Style: {customData.style}</p>}
          </div>
        ) : (
          <p>Création de votre ambiance <strong>{ambiance?.name}</strong></p>
        )}
        <p className="status-info">Cela peut prendre quelques instants ☕</p>
        <p className="status-tip">💡 Suno génère 2 variantes que vous pourrez choisir</p>
      </div>
    </div>
  );
}

export default GenerationStatus;