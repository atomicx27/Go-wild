const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';

app.use(cors());
app.use(express.json());

// Serve static frontend files
app.use(express.static(path.join(__dirname, 'public')));

// Proxy endpoint for Ollama chat
app.post('/api/chat', async (req, res) => {
    try {
        const { model, messages, stream } = req.body;

        if (!model || !messages) {
             return res.status(400).json({ error: 'Model and messages are required' });
        }

        const ollamaResponse = await axios.post(`${OLLAMA_URL}/api/chat`, {
            model,
            messages,
            stream: stream || false
        }, {
            responseType: stream ? 'stream' : 'json'
        });

        if (stream) {
            res.setHeader('Content-Type', 'text/event-stream');
            res.setHeader('Cache-Control', 'no-cache');
            res.setHeader('Connection', 'keep-alive');
            ollamaResponse.data.pipe(res);
        } else {
            res.json(ollamaResponse.data);
        }

    } catch (error) {
        console.error('Error communicating with Ollama:', error.message);

        let statusCode = 500;
        let errorMessage = 'Failed to communicate with local Ollama instance. Is it running?';

        if (error.response) {
            statusCode = error.response.status;
            errorMessage = error.response.data.error || errorMessage;
        } else if (error.code === 'ECONNREFUSED') {
             errorMessage = `Connection refused. Ensure Ollama is running at ${OLLAMA_URL}`;
        }

        res.status(statusCode).json({ error: errorMessage });
    }
});

// Proxy endpoint to list models
app.get('/api/tags', async (req, res) => {
    try {
         const response = await axios.get(`${OLLAMA_URL}/api/tags`);
         res.json(response.data);
    } catch(error) {
        console.error('Error fetching models:', error.message);
        res.status(500).json({ error: 'Failed to fetch models from Ollama.' });
    }
});

app.listen(PORT, () => {
    console.log(`Thought Weaver server running on http://localhost:${PORT}`);
    console.log(`Proxying requests to Ollama at: ${OLLAMA_URL}`);
});
