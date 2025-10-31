import React, { useState, useEffect } from 'react';
import AmbianceSelector from './components/AmbianceSelector';
import MusicPlayer from './components/MusicPlayer';
import GenerationStatus from './components/GenerationStatus';
import CustomGenerator from './components/CustomGenerator';
import './App.css';

const API_BASE_URL = 'http://localhost:3001/api';

function App() {
  const [ambiances, setAmbiances] = useState([]);
  const [selectedAmbiance, setSelectedAmbiance] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [generationTime, setGenerationTime] = useState(0);
  const [currentAmbiance, setCurrentAmbiance] = useState(null);

  useEffect(() => {
    fetchAmbiances();
  }, []);

  const fetchAmbiances = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/music/ambiances`);
      const data = await response.json();
      if (data.success) {
        setAmbiances(data.data);
      }
    } catch (err) {
      console.error('Erreur lors du chargement des ambiances:', err);
      setError('Impossible de charger les ambiances');
    }
  };

  const handleGenerate = async (ambianceId, customSettings = null) => {
    setIsGenerating(true);
    setError(null);
    setAudioUrl(null);
    setSelectedAmbiance(ambianceId);
    setGenerationTime(0);

    // Définir l'ambiance actuelle
    const ambiance = customSettings 
      ? { name: customSettings.name || 'Personnalisée', style: customSettings.style || 'Custom' }
      : ambiances.find(a => a.id === ambianceId);
    
    setCurrentAmbiance(ambiance);

    // Timer pour afficher le temps de génération
    const startTime = Date.now();
    const timer = setInterval(() => {
      setGenerationTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    try {
      const response = await fetch(`${API_BASE_URL}/music/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ambiance: ambianceId,
          customSettings: customSettings
        }),
      });

      const data = await response.json();
      clearInterval(timer);

      if (data.success) {
        setAudioUrl(data.data.audioUrl);
        setIsGenerating(false);
      } else {
        setError(data.error || 'Erreur lors de la génération');
        setIsGenerating(false);
      }
    } catch (err) {
      clearInterval(timer);
      console.error('Erreur:', err);
      setError('Erreur de connexion. Vérifiez que les serveurs sont lancés.');
      setIsGenerating(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🎵</span>
            <div className="logo-text">
              <h1>MusicGen Studio</h1>
              <p className="subtitle">Génération musicale locale par IA</p>
            </div>
          </div>
          <div className="status-badge">
            <span className="status-dot"></span>
            Modèle Local Actif
          </div>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{error}</span>
            <button className="error-close" onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <div className="content-grid">
          <div className="left-panel">
            <AmbianceSelector
              ambiances={ambiances}
              selectedAmbiance={selectedAmbiance}
              onSelect={handleGenerate}
              isGenerating={isGenerating}
            />

            <CustomGenerator
              onGenerate={(customSettings) => handleGenerate('custom', customSettings)}
              isGenerating={isGenerating}
            />
          </div>

          <div className="right-panel">
            {isGenerating && (
              <GenerationStatus 
                ambiance={currentAmbiance}
                generationTime={generationTime}
              />
            )}

            {audioUrl && !isGenerating && (
              <MusicPlayer
                audioUrl={audioUrl}
                ambiance={currentAmbiance}
              />
            )}

            {!isGenerating && !audioUrl && (
              <div className="placeholder">
                <div className="placeholder-icon">🎼</div>
                <h3>Prêt à créer</h3>
                <p>Sélectionnez une ambiance ou créez votre propre composition</p>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p>Projet Lucas & Ivan - EPF 2025</p>
          <p className="tech-stack">MusicGen (Meta) • Flask • React • Node.js</p>
        </div>
      </footer>
    </div>
  );
}

export default App;