import axios from "axios";
import FormData from "form-data";

export const generateStableAudio = async ({ prompt, duration, model, output_format }) => {
  const formData = new FormData();
  formData.append("prompt", prompt);
  formData.append("duration", duration);
  formData.append("model", model);
  formData.append("output_format", output_format);

  const response = await axios.post(
    "https://api.stability.ai/v2beta/stable-audio/generate/",
    formData,
    {
      headers: {
        Authorization: `Bearer ${process.env.STABILITY_API_KEY}`,
        Accept: "application/json",
        ...formData.getHeaders(),
      },
      responseType: "json",
    }
  );

  // Le son est encodé en base64 dans response.data.audio
  const base64Audio = response.data.audio;
  return Buffer.from(base64Audio, "base64");
};
