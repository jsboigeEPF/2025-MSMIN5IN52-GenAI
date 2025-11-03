import { generateStableAudio } from "../services/stabilityService.js";

export const generateSound = async (req, res) => {
  try {
    const { prompt, duration, model, output_format } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" });
    }

    const audioBuffer = await generateStableAudio({
      prompt,
      duration: duration || 60,
      model: model || "stable-audio-2",
      output_format: output_format || "mp3",
    });

    // Envoie le fichier audio en base64 (facile à gérer côté front)
    res.set("Content-Type", "application/json");
    res.status(200).json({
      success: true,
      message: "Audio generated successfully",
      audio_base64: audioBuffer.toString("base64"),
    });

  } catch (error) {
    console.error(error.response?.data || error.message);
    res.status(500).json({ error: "Audio generation failed" });
  }
};
