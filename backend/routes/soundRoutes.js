import express from "express";
import axios from "axios";
import dotenv from "dotenv";
import fs from "node:fs";
import FormData from "form-data";

dotenv.config();
const router = express.Router();

router.post("/generate", async (req, res) => {
    const payload = {
    prompt:
        "A song in the 3/4 time signature that features cheerful acoustic guitar, live recorded drums, and rhythmic claps, The mood is happy and up-lifting.",
    output_format: "mp3",
    duration: 20,
    model: "stable-audio-2.5",
    };

    const response = await axios.postForm(
    `https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio`,
    axios.toFormData(payload, new FormData()),
    {
        validateStatus: undefined,
        responseType: "arraybuffer",
        headers: {
        Authorization: `Bearer sk-MYAPIKEY`,
        Accept: "audio/*",
        },
    }
    );

    if (response.status === 200) {
    fs.writeFileSync("./output.mp3", Buffer.from(response.data));
    } else {
    throw new Error(`${response.status}: ${response.data.toString()}`);
    }
});

export default router;
