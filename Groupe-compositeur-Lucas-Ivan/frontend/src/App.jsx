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
  const [generationData, setGenerationData] = useState(null);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [allTracks, setAllTracks] = useState([]);
  const [customAmbianceData, setCustomAmbianceData] = useState(null); // Pour stocker les infos custom

  // Charger les ambiances au démarrage
  useEffect(() => {
    fetchAmbiances();
  }, []);

  // Récupérer les ambiances disponibles
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

  // Générer une musique
  const handleGenerate = async (ambianceId) => {
    setIsGenerating(true);
    setError(null);
    setAudioUrl(null);
    setAllTracks([]);
    setSelectedAmbiance(ambianceId);

    try {
      const response = await fetch(`${API_BASE_URL}/music/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ambiance: ambianceId,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setGenerationData(data.data);
        // Démarrer le polling pour vérifier le statut
        pollGenerationStatus(data.data.generationId);
      } else {
        setError(data.error || 'Erreur lors de la génération');
        setIsGenerating(false);
      }
    } catch (err) {
      console.error('Erreur:', err);
      setError('Erreur de connexion au serveur');
      setIsGenerating(false);
    }
  };

  // Vérifier le statut de la génération
  const pollGenerationStatus = async (generationId) => {
    const maxAttempts = 60; // 5 minutes max (60 * 5 secondes)
    let attempts = 0;

    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/music/status/${generationId}`);
        const data = await response.json();

        if (data.success) {
          console.log('📊 Statut reçu:', data.data);
          
          const statusData = data.data.data || data.data;
          const status = statusData.status;

          // Si la génération est terminée avec succès
          if (status === 'SUCCESS' || status === 'completed') {
            // Extraire l'URL audio de la structure Suno
            const sunoData = statusData.response?.sunoData;
            
            if (sunoData && sunoData.length > 0) {
              // Stocker toutes les pistes
              setAllTracks(sunoData);
              // Prendre la première piste audio générée par défaut
              const audioUrl = sunoData[0].audioUrl || sunoData[0].sourceAudioUrl;
              
              if (audioUrl) {
                console.log('🎵 URL audio trouvée:', audioUrl);
                setAudioUrl(audioUrl);
                setIsGenerating(false);
                return;
              }
            }
          } else if (status === 'FAILED' || status === 'failed' || status === 'error') {
            setError('La génération a échoué');
            setIsGenerating(false);
            return;
          }
          // Si status est autre chose (PROCESSING, PENDING, etc.), on continue à poller
        }

        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(checkStatus, 5000); // Vérifier toutes les 5 secondes
        } else {
          setError('Timeout: la génération prend trop de temps');
          setIsGenerating(false);
        }
      } catch (err) {
        console.error('Erreur lors de la vérification du statut:', err);
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(checkStatus, 5000);
        }
      }
    };

    checkStatus();
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎵 Compositeur d'Ambiances</h1>
          <p className="subtitle">Créez des boucles musicales immersives en quelques clics</p>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <AmbianceSelector
          ambiances={ambiances}
          selectedAmbiance={selectedAmbiance}
          onSelect={handleGenerate}
          isGenerating={isGenerating}
        />

        <CustomGenerator
          onGenerate={handleGenerate}
          isGenerating={isGenerating}
        />

        {isGenerating && (
          <GenerationStatus 
            ambiance={ambiances.find(a => a.id === selectedAmbiance)}
            isCustom={selectedAmbiance === 'custom'}
            customData={customAmbianceData}
          />
        )}

        {audioUrl && !isGenerating && (
          <MusicPlayer
            audioUrl={audioUrl}
            ambiance={customAmbianceData || ambiances.find(a => a.id === selectedAmbiance)}
            allTracks={allTracks}
            onTrackChange={(trackIndex) => {
              const newUrl = allTracks[trackIndex].audioUrl || allTracks[trackIndex].sourceAudioUrl;
              setAudioUrl(newUrl);
            }}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>Projet réalisé par Lucas & Ivan - 2025-MSMIN5IN52-GenAI</p>
      </footer>
    </div>
  );
}

export default App;