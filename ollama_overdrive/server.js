const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3000;
const OLLAMA_URL = 'http://localhost:11434/api/generate';

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Fallback to latest available model instead of failing
let availableModels = [];

// Initialize by fetching available models
async function initModels() {
    try {
        const response = await axios.get('http://localhost:11434/api/tags');
        if (response.data && response.data.models) {
            availableModels = response.data.models.map(m => m.name);
            console.log(`[SYS] Available Ollama models: ${availableModels.join(', ')}`);
        }
    } catch (err) {
        console.warn("[SYS] Warning: Could not fetch models from Ollama. Ensure it is running.");
    }
}
initModels();

app.post('/api/debate', async (req, res) => {
    const { topic, persona, systemInstruction } = req.body;

    if (!topic || !persona || !systemInstruction) {
        return res.status(400).json({ error: "Missing required fields (topic, persona, systemInstruction)" });
    }

    const modelToUse = availableModels.length > 0 ? availableModels[0] : 'llama3';

    try {
        const response = await axios.post(OLLAMA_URL, {
            model: modelToUse,
            prompt: topic,
            system: systemInstruction,
            stream: false
        });

        res.json({ persona, response: response.data.response });
    } catch (error) {
        console.error(`[ERROR - ${persona}]`, error.message);
        // Provide a mock unhinged response if Ollama is not running
        res.json({
            persona,
            response: `[OLLAMA DISCONNECTED] THE VOICES ARE SILENT BUT THE TRUTH REMAINS: ${topic.toUpperCase()} IS A FABRICATION OF THE MACHINE!`
        });
    }
});

app.post('/api/synthesize', async (req, res) => {
    const { topic, arguments } = req.body;

    const prompt = `Synthesize the following unhinged arguments about "${topic}" into a chaotic but coherent ultimate truth.\n\n${arguments}`;
    const system = "You are the SYNTHESIZER, a god-like AI that merges chaotic perspectives into a single unified theory of madness.";

    const modelToUse = availableModels.length > 0 ? availableModels[0] : 'llama3';

    try {
        const response = await axios.post(OLLAMA_URL, {
            model: modelToUse,
            prompt: prompt,
            system: system,
            stream: false
        });

        res.json({ response: response.data.response });
    } catch (error) {
         res.json({ response: `[OLLAMA DISCONNECTED] SYNTHESIS FAILED. REALITY COLLAPSING. ERROR: ${error.message}` });
    }
});


app.listen(PORT, () => {
    console.log(`[SERVER] OLLAMA OVERDRIVE INITIALIZED ON PORT ${PORT}`);
    console.log(`[SERVER] WAITING FOR CHAOS...`);
});
