const sunoService = require('../services/sunoService');

// Générer une musique d'ambiance
exports.generateMusic = async (req, res) => {
  try {
    const { ambiance, customSettings } = req.body;

    if (!ambiance) {
      return res.status(400).json({ 
        error: 'L\'ambiance est requise' 
      });
    }

    console.log(`🎼 Génération de musique pour l'ambiance: ${ambiance}`);

    // Générer la musique via le service Suno
    const result = await sunoService.generateMusic(ambiance, customSettings);

    // Vérifier qu'on a bien reçu un ID de génération
    if (!result.generationId) {
      console.error('⚠️ Pas d\'ID de génération reçu. Réponse complète:', result);
      return res.status(500).json({ 
        success: false,
        error: 'La génération a été lancée mais aucun ID n\'a été retourné',
        details: 'Vérifiez les logs du serveur pour plus de détails',
        data: result.data
      });
    }

    res.json({
      success: true,
      data: result,
      message: 'Musique générée avec succès'
    });

  } catch (error) {
    console.error('Erreur lors de la génération:', error);
    res.status(500).json({ 
      success: false,
      error: 'Erreur lors de la génération de la musique',
      details: error.message 
    });
  }
};

// Récupérer le statut d'une génération
exports.getGenerationStatus = async (req, res) => {
  try {
    const { generationId } = req.params;

    if (!generationId) {
      return res.status(400).json({ 
        error: 'L\'ID de génération est requis' 
      });
    }

    const status = await sunoService.getStatus(generationId);

    res.json({
      success: true,
      data: status
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