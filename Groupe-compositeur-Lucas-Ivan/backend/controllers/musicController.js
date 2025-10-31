const axios = require('axios');

const PYTHON_API_URL = 'http://localhost:5001/api';

// Mapper les ambiances (optionnel, pour enrichir les descriptions)
const AMBIANCE_DESCRIPTIONS = {
  'foret-mysterieuse': 'Ambient forest sounds with mysterious piano and ethereal pads',
  'cyberpunk-pluie': 'Cyberpunk synthwave with rain sounds and electronic beats',
  'plage-coucher-soleil': 'Relaxing tropical beach music with soft guitar and ocean waves',
  'meditation-zen': 'Peaceful zen meditation music with bells and nature sounds',
  'cafe-jazz': 'Smooth jazz music perfect for a cozy café atmosphere',
  'montagne-majestueuse': 'Epic orchestral music with majestic mountain atmosphere',
  'desert-nocturne': 'Atmospheric ethnic music with desert night ambiance',
  'ville-futuriste': 'Futuristic electronic cinematic music with urban atmosphere'
};

// Générer une musique d'ambiance
exports.generateMusic = async (req, res) => {
  try {
    const { ambiance, customSettings } = req.body;

    if (!ambiance) {
      return res.status(400).json({ 
        success: false,
        error: 'L\'ambiance est requise' 
      });
    }

    console.log(`🎼 Génération locale pour l'ambiance: ${ambiance}`);

    // Préparer la description
    const description = customSettings?.description || AMBIANCE_DESCRIPTIONS[ambiance] || ambiance;

    // Appeler l'API Python locale
    const response = await axios.post(`${PYTHON_API_URL}/generate`, {
      ambiance,
      customDescription: description
    }, {
      timeout: 300000 // Timeout de 5 minutes
    });

    const result = response.data;

    if (!result.success) {
      return res.status(500).json({
        success: false,
        error: result.error || 'Erreur lors de la génération'
      });
    }

    // Retourner immédiatement l'URL de l'audio (génération synchrone)
    res.json({
      success: true,
      data: {
        generationId: result.data.generation_id,
        status: 'complete',
        audioUrl: `http://localhost:5001/api/audio/${result.data.generation_id}`
      },
      message: 'Musique générée avec succès'
    });

  } catch (error) {
    console.error('Erreur lors de la génération:', error.message);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la génération de la musique',
      details: error.message 
    });
  }
};

// Récupérer le statut d'une génération (pour la compatibilité)
exports.getGenerationStatus = async (req, res) => {
  try {
    const { generationId } = req.params;

    if (!generationId) {
      return res.status(400).json({ 
        success: false,
        error: 'L\'ID de génération est requis' 
      });
    }

    // Avec MusicGen local, la génération est synchrone
    // On retourne toujours "complete"
    res.json({
      success: true,
      data: {
        status: 'complete',
        generationId: generationId,
        audioUrl: `http://localhost:5001/api/audio/${generationId}`
      }
    });

  } catch (error) {
    console.error('Erreur lors de la récupération du statut:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la récupération du statut',
      details: error.message 
    });
  }
};

// Récupérer les ambiances disponibles
exports.getAmbiances = (req, res) => {
  const ambiances = [
    { id: 'foret-mysterieuse', name: 'Forêt Mystérieuse', style: 'Ambient, Nature' },
    { id: 'cyberpunk-pluie', name: 'Cyberpunk sous la Pluie', style: 'Electronic, Synthwave' },
    { id: 'plage-coucher-soleil', name: 'Plage au Coucher du Soleil', style: 'Chill, Tropical' },
    { id: 'meditation-zen', name: 'Méditation Zen', style: 'Ambient, Peaceful' },
    { id: 'cafe-jazz', name: 'Café Jazz', style: 'Jazz, Relaxing' },
    { id: 'montagne-majestueuse', name: 'Montagne Majestueuse', style: 'Orchestral, Epic' },
    { id: 'desert-nocturne', name: 'Désert Nocturne', style: 'Ethnic, Atmospheric' },
    { id: 'ville-futuriste', name: 'Ville Futuriste', style: 'Electronic, Cinematic' }
  ];

  res.json({
    success: true,
    data: ambiances
  });
};