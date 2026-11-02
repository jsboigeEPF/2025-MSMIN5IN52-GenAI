/**
 * Configuration pour tester le frontend sans backend
 * Mode démo avec données mockées
 */

export const DEMO_MODE = false; // Mettre à true pour tester sans backend

export const mockStoryResponse = {
  story_id: "demo-story-123",
  current_scene: {
    scene_id: "scene-1",
    scene_number: 1,
    story_id: "demo-story-123",
    narrative_text: "Vous vous réveillez dans une forêt enchantée. Les arbres autour de vous semblent vivants, leurs branches se balançant doucement comme pour vous saluer. Une brume mystérieuse enveloppe le sol, cachant partiellement un sentier qui s'enfonce dans les profondeurs de la forêt. Au loin, vous entendez le son d'une cascade et des chants d'oiseaux inconnus.",
    suggested_actions: [
      "Suivre le sentier dans la forêt",
      "Explorer les environs immédiats",
      "Appeler pour voir si quelqu'un répond",
      "Examiner les arbres de plus près"
    ],
    timestamp: new Date().toISOString(),
    image_url: null
  },
  suggested_actions: [
    "Suivre le sentier dans la forêt",
    "Explorer les environs immédiats",
    "Appeler pour voir si quelqu'un répond",
    "Examiner les arbres de plus près"
  ],
  story_state: "in_progress",
  scene_count: 1
};

export const mockContinueResponse = {
  story_id: "demo-story-123",
  current_scene: {
    scene_id: "scene-2",
    scene_number: 2,
    story_id: "demo-story-123",
    narrative_text: "Vous avancez prudemment sur le sentier. La forêt s'ouvre sur une clairière baignée de lumière dorée. Au centre, une fontaine de cristal scintille, entourée de fleurs luminescentes. Un petit personnage ailé, pas plus grand qu'une main, volette autour de la fontaine. Il vous remarque et s'approche avec curiosité.",
    user_action: {
      action_text: "Suivre le sentier dans la forêt",
      timestamp: new Date().toISOString(),
      scene_number: 2
    },
    suggested_actions: [
      "Saluer le personnage ailé",
      "S'approcher de la fontaine",
      "Observer sans bouger",
      "Demander où vous êtes"
    ],
    timestamp: new Date().toISOString(),
    image_url: null
  },
  suggested_actions: [
    "Saluer le personnage ailé",
    "S'approcher de la fontaine",
    "Observer sans bouger",
    "Demander où vous êtes"
  ],
  story_state: "in_progress",
  scene_count: 2
};

// Simuler un délai réseau
export const mockDelay = (ms = 2000) => new Promise(resolve => setTimeout(resolve, ms));
