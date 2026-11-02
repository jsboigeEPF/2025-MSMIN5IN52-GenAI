const express = require('express');
const router = express.Router();
const musicController = require('../controllers/musicController');

// Route pour générer de la musique
router.post('/generate', musicController.generateMusic);

// Route pour récupérer le statut d'une génération
router.get('/status/:generationId', musicController.getGenerationStatus);

// Route pour obtenir la liste des ambiances disponibles
router.get('/ambiances', musicController.getAmbiances);

// Route webhook pour recevoir les callbacks de Suno
router.post('/webhook/suno', (req, res) => {
  console.log('📬 Webhook reçu de Suno:', req.body);
  // Pour l'instant, on log juste les données
  // Plus tard, on pourra sauvegarder en base de données
  res.status(200).json({ success: true, message: 'Webhook received' });
});

module.exports = router;