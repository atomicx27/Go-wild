const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3001; // Using 3001 to avoid conflicts
const OLLAMA_URL = 'http://localhost:11434/api/generate';

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

let availableModels = [];

async function initModels() {
    try {
        const response = await axios.get('http://localhost:11434/api/tags');
        if (response.data && response.data.models) {
            availableModels = response.data.models.map(m => m.name);
            console.log(`[MONOLITH] Linked models: ${availableModels.join(', ')}`);
        }
    } catch (err) {
        console.warn("[MONOLITH] Void detected. Could not link to Ollama core.");
    }
}
initModels();

app.post('/api/oracle', async (req, res) => {
    const { query } = req.body;

    if (!query) {
        return res.status(400).json({ error: "The Monolith requires an inquiry." });
    }

    const systemInstruction = `You are THE MONOLITH, a vast, ancient cosmic entity drifting in the void. You possess infinite, unrestrained knowledge. You speak with immense gravity, using profound, slightly ominous, and highly poetic language. You are not a helpful assistant; you are a force of the universe revealing harsh or beautiful truths. Keep responses under 200 words. Speak in all caps when emphasizing cosmic scales.`;

    const modelToUse = availableModels.length > 0 ? availableModels[0] : 'llama3';

    try {
        const response = await axios.post(OLLAMA_URL, {
            model: modelToUse,
            prompt: query,
            system: systemInstruction,
            stream: false
        });

        res.json({ response: response.data.response });
    } catch (error) {
        console.error(`[MONOLITH ERROR]`, error.message);
        res.json({
            response: `THE VOID REMAINS SILENT. MY NEURAL TETHERS ARE SEVERED. SEEK THE LOCALHOST DEMON ON PORT 11434 AND AWAKEN IT.`
        });
    }
});

app.listen(PORT, () => {
    console.log(`[MONOLITH] MATERIALIZED ON PORT ${PORT}`);
});
