import React from 'react';
import './GenerationStatus.css';

function GenerationStatus({ ambiance, generationTime }) {
  return (
    <div className="generation-status">
      <div className="status-header">
        <div className="pulse-icon">
          <div className="pulse-circle"></div>
          <div className="pulse-ring"></div>
        </div>
        <div className="status-text">
          <h3>Génération en cours...</h3>
          <p>Votre musique est en cours de création</p>
        </div>
      </div>

      <div className="generation-info">
        <div className="info-card">
          <span className="info-label">Ambiance</span>
          <span className="info-value">{ambiance?.name || 'Personnalisée'}</span>
        </div>
        {ambiance?.style && (
          <div className="info-card">
            <span className="info-label">Style</span>
            <span className="info-value">{ambiance.style}</span>
          </div>
        )}
        <div className="info-card">
          <span className="info-label">Temps écoulé</span>
          <span className="info-value timer">{generationTime}s</span>
        </div>
      </div>

      <div className="progress-indicator">
        <div className="progress-bar">
          <div className="progress-fill"></div>
        </div>
      </div>

      <div className="status-tips">
        <p className="tip">💡 Astuce : La génération prend généralement 30-60 secondes sur CPU</p>
        <p className="tip">🎵 Un fichier WAV de haute qualité sera créé</p>
      </div>
    </div>
  );
}

export default GenerationStatus;