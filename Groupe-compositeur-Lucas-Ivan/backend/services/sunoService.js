const axios = require('axios');

const SUNO_API_URL = 'https://api.sunoapi.org/api/v1';
const SUNO_API_KEY = process.env.SUNO_API_KEY || 'c31d82d79a54f4d02f71fb9681e4df17';
const SUNO_CALLBACK_URL = process.env.SUNO_CALLBACK_URL || 'https://webhook.site/unique-id';

// Mapper les ambiances aux paramètres Suno
const ambianceToPrompt = {
  'foret-mysterieuse': {
    prompt: 'Mysterious forest ambience with soft nature sounds, gentle strings and ethereal pads creating a mystical atmosphere',
    style: 'Ambient, Cinematic',
    title: 'Mysterious Forest Ambience',
    negativeTags: 'Vocals, Drums, Heavy Bass'
  },
  'cyberpunk-pluie': {
    prompt: 'Dark cyberpunk atmosphere with rain sounds, synthetic textures, deep bass and futuristic soundscapes',
    style: 'Electronic, Synthwave',
    title: 'Cyberpunk Rain',
    negativeTags: 'Vocals, Acoustic, Bright'
  },
  'plage-coucher-soleil': {
    prompt: 'Relaxing beach sunset with soft waves, tropical guitars, warm pads and peaceful melodies',
    style: 'Chill, Tropical',
    title: 'Sunset Beach',
    negativeTags: 'Vocals, Heavy, Dark'
  },
  'meditation-zen': {
    prompt: 'Peaceful zen meditation music with calming tones, soft bells, gentle drones and tranquil atmosphere',
    style: 'Ambient, Peaceful',
    title: 'Zen Meditation',
    negativeTags: 'Vocals, Drums, Fast tempo'
  },
  'cafe-jazz': {
    prompt: 'Relaxing cafe jazz with smooth piano, soft brushes drums, walking bass and warm atmosphere',
    style: 'Jazz, Relaxing',
    title: 'Cafe Jazz Lounge',
    negativeTags: 'Vocals, Heavy, Aggressive'
  },
  'montagne-majestueuse': {
    prompt: 'Epic mountain landscape with orchestral strings, majestic horns, cinematic percussion and grandiose atmosphere',
    style: 'Orchestral, Epic',
    title: 'Majestic Mountains',
    negativeTags: 'Vocals, Electronic, Modern'
  },
  'desert-nocturne': {
    prompt: 'Nocturnal desert ambience with ethnic instruments, mystical drones, soft percussion and atmospheric textures',
    style: 'Ethnic, Atmospheric',
    title: 'Desert Night',
    negativeTags: 'Vocals, Heavy, Fast'
  },
  'ville-futuriste': {
    prompt: 'Futuristic city soundscape with electronic textures, cinematic pads, subtle rhythms and sci-fi atmosphere',
    style: 'Electronic, Cinematic',
    title: 'Futuristic City',
    negativeTags: 'Vocals, Acoustic, Organic'
  }
};

// Générer de la musique avec Suno
exports.generateMusic = async (ambiance, customSettings = {}) => {
  try {
    if (!SUNO_API_KEY) {
      throw new Error('Clé API Suno non configurée');
    }

    let ambianceParams;

    // Si c'est une ambiance custom, utiliser directement les paramètres fournis
    if (ambiance === 'custom' && customSettings.prompt) {
      ambianceParams = {
        prompt: customSettings.prompt,
        style: customSettings.style || 'Ambient',
        title: customSettings.title || 'Custom Ambience',
        negativeTags: customSettings.negativeTags || 'Vocals'
      };
    } else {
      // Sinon, récupérer les paramètres de l'ambiance prédéfinie
      ambianceParams = ambianceToPrompt[ambiance] || {
        prompt: customSettings.prompt || 'Calm and relaxing instrumental music',
        style: customSettings.style || 'Ambient',
        title: customSettings.title || 'Custom Ambience',
        negativeTags: customSettings.negativeTags || 'Vocals'
      };
    }

    // Construire le body de la requête
    const requestBody = {
      prompt: ambianceParams.prompt,
      style: ambianceParams.style,
      title: ambianceParams.title,
      customMode: true,
      instrumental: true,
      model: 'V3_5',
      negativeTags: ambianceParams.negativeTags,
      styleWeight: customSettings.styleWeight || 0.65,
      weirdnessConstraint: customSettings.weirdnessConstraint || 0.65,
      audioWeight: customSettings.audioWeight || 0.65,
      // callBackUrl obligatoire
      callBackUrl: customSettings.callBackUrl || SUNO_CALLBACK_URL
    };

    console.log('📤 Envoi de la requête à Suno API...');

    // Appeler l'API Suno
    const response = await axios.post(
      `${SUNO_API_URL}/generate`,
      requestBody,
      {
        headers: {
          'Authorization': `Bearer ${SUNO_API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000 // 30 secondes timeout
      }
    );

    console.log('✅ Réponse reçue de Suno API');
    console.log('📦 Données reçues:', JSON.stringify(response.data, null, 2));

    // Extraire le taskId de la réponse Suno
    const taskId = response.data.data?.taskId || 
                   response.data.taskId || 
                   response.data.id;

    if (!taskId) {
      console.error('⚠️ Aucun taskId trouvé dans la réponse');
      throw new Error('Aucun ID de tâche reçu de Suno API');
    }

    console.log('🎫 TaskId reçu:', taskId);

    return {
      generationId: taskId,
      taskId: taskId,
      status: 'processing',
      data: response.data,
      ambiance: ambiance,
      timestamp: new Date().toISOString()
    };

  } catch (error) {
    console.error('❌ Erreur API Suno:', error.response?.data || error.message);
    throw new Error(
      error.response?.data?.error || 
      error.message || 
      'Erreur lors de la génération musicale'
    );
  }
};

// Récupérer le statut d'une génération
exports.getStatus = async (taskId) => {
  try {
    if (!SUNO_API_KEY) {
      throw new Error('Clé API Suno non configurée');
    }

    console.log('🔍 Vérification du statut pour taskId:', taskId);

    const response = await axios.get(
      `${SUNO_API_URL}/generate/record-info?taskId=${taskId}`,
      {
        headers: {
          'Authorization': `Bearer ${SUNO_API_KEY}`
        },
        timeout: 10000
      }
    );

    console.log('✅ Statut récupéré:', JSON.stringify(response.data, null, 2));
    return response.data;

  } catch (error) {
    console.error('❌ Erreur lors de la récupération du statut:', error.response?.data || error.message);
    throw new Error(
      error.response?.data?.error || 
      error.message || 
      'Erreur lors de la récupération du statut'
    );
  }
};