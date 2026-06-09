// Initialize global state
let currentState = {
    nodes: [
        { id: 1, label: "Core AI", color: "#00ffcc", shape: "hexagon" },
        { id: 2, label: "Memory", color: "#ff00ff", shape: "dot" },
        { id: 3, label: "Logic", color: "#00ffff", shape: "dot" }
    ],
    edges: [
        { from: 1, to: 2 },
        { from: 1, to: 3 }
    ]
};

// Setup vis.js Network
const container = document.getElementById('mynetwork');
let nodesData = new vis.DataSet(currentState.nodes);
let edgesData = new vis.DataSet(currentState.edges);
let networkData = { nodes: nodesData, edges: edgesData };

const options = {
    nodes: {
        font: { color: '#ffffff', face: 'monospace' },
        borderWidth: 2,
        shadow: { enabled: true, color: 'rgba(0, 255, 204, 0.5)', size: 10 }
    },
    edges: {
        width: 2,
        color: { color: '#00ffcc', highlight: '#ffffff' },
        smooth: { type: 'continuous' }
    },
    physics: {
        barnesHut: { gravitationalConstant: -2000, centralGravity: 0.3, springLength: 95 },
        stabilization: { iterations: 150 }
    },
    interaction: { hover: true, tooltipDelay: 200 }
};

let network = new vis.Network(container, networkData, options);

// Chat UI Elements
const chatForm = document.getElementById('chat-form');
const promptInput = document.getElementById('prompt-input');
const chatHistory = document.getElementById('chat-history');
const loadingIndicator = document.getElementById('loading-indicator');

// Helper to append messages
function appendMessage(sender, text) {
    const div = document.createElement('div');
    div.className = `message text-sm p-2 rounded border shadow-neon-sm animate-pulse mb-2`;

    if (sender === 'user') {
        div.classList.add('border-blue-500/50', 'bg-blue-900/20', 'text-blue-300');
        div.innerHTML = `<span class="opacity-50">&gt; User:</span> ${text}`;
    } else {
        div.classList.add('border-purple-500/50', 'bg-purple-900/20', 'text-purple-300');
        div.innerHTML = `<span class="opacity-50">&gt; System:</span> ${text}`;
    }

    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Remove pulse after animation plays
    setTimeout(() => div.classList.remove('animate-pulse'), 1000);
}

// Update the canvas with new state
function updateCanvas(newState) {
    currentState = newState;

    // Update nodes
    const nodesArray = newState.nodes || [];
    // Basic diffing: update existing, add new
    nodesArray.forEach(node => {
        if (!node.shape) node.shape = 'dot'; // default shape
        if (nodesData.get(node.id)) {
            nodesData.update(node);
        } else {
            nodesData.add(node);
        }
    });

    // Update edges
    const edgesArray = newState.edges || [];
    edgesData.clear();
    edgesData.add(edgesArray);

    network.stabilize();
}

// Handle Form Submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    appendMessage('user', prompt);
    promptInput.value = '';
    loadingIndicator.classList.remove('hidden');

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt, state: currentState })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();

        if (data.status === 'success') {
            updateCanvas(data.state);
            appendMessage('system', 'Neural network topology updated successfully.');
        } else {
            appendMessage('system', 'Error: Failed to process modification.');
        }
    } catch (error) {
        console.error('Error:', error);
        appendMessage('system', 'Connection error. The network may be offline.');
    } finally {
        loadingIndicator.classList.add('hidden');
    }
});
