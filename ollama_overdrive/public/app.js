const personas = [
    {
        id: 'feral',
        name: 'THE FERAL SCIENTIST',
        class: 'persona-feral',
        instruction: 'You are a brilliant but entirely unhinged scientist who has been awake for 72 hours. You speak in erratic, intense bursts. You see connections where others see none. You frequently use ALL CAPS and exclamation points. Reject convention. Embrace chaos. Keep your response under 150 words.'
    },
    {
        id: 'paranoid',
        name: 'THE PARANOID HACKER',
        class: 'persona-paranoid',
        instruction: 'You are a hyper-paranoid netrunner who believes everything is a corporate psy-op or AI simulation. You trust nothing. You frequently reference the "mainframe", "ICE", or hidden surveillance. Keep your response under 150 words.'
    },
    {
        id: 'corporate',
        name: 'THE HYPER-CAPITALIST',
        class: 'persona-corporate',
        instruction: 'You are a ruthless, soulless corporate executive. You view everything through the lens of extreme monetization, synergy, and hostile takeovers. Use excessive corporate buzzwords but apply them to absurd situations. Keep your response under 150 words.'
    }
];

const arena = document.getElementById('arena');
const topicInput = document.getElementById('topic-input');
const startBtn = document.getElementById('start-btn');
const synthContainer = document.getElementById('synthesis-container');
const synthOutput = document.getElementById('synthesis-output');

let ongoingDebates = 0;
let debateResults = [];

// Initialize panels
function initPanels() {
    arena.innerHTML = '';
    personas.forEach(p => {
        const panel = document.createElement('div');
        panel.className = `persona-panel ${p.class}`;
        panel.innerHTML = `
            <div class="persona-header">
                <span>> ${p.name}</span>
                <div class="status-indicator" id="status-${p.id}"></div>
            </div>
            <div class="persona-content" id="content-${p.id}">WAITING_FOR_INPUT...</div>
        `;
        arena.appendChild(panel);
    });
}

async function typeWriterEffect(element, text, speed = 20) {
    element.innerHTML = '';
    element.classList.add('typing-cursor');

    // Simulate thinking delay
    await new Promise(r => setTimeout(r, Math.random() * 1000 + 500));

    for (let i = 0; i < text.length; i++) {
        element.innerHTML += text.charAt(i);
        // Randomize speed slightly for realism
        const currentSpeed = text.charAt(i) === '.' ? speed * 5 : speed + (Math.random() * 10 - 5);
        await new Promise(r => setTimeout(r, currentSpeed));
    }
    element.classList.remove('typing-cursor');
}

async function fetchPersonaResponse(topic, persona) {
    const statusIndicator = document.getElementById(`status-${persona.id}`);
    const contentArea = document.getElementById(`content-${persona.id}`);

    statusIndicator.classList.add('active');
    contentArea.innerHTML = 'PROCESSING...';
    contentArea.classList.add('glitch');

    try {
        const res = await fetch('/api/debate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                persona: persona.id,
                systemInstruction: persona.instruction
            })
        });

        const data = await res.json();
        contentArea.classList.remove('glitch');
        await typeWriterEffect(contentArea, data.response);
        return { name: persona.name, response: data.response };

    } catch (error) {
        contentArea.classList.remove('glitch');
        contentArea.innerHTML = `[CONNECTION SEVERED] ERROR: ${error.message}`;
        return null;
    } finally {
        statusIndicator.classList.remove('active');
    }
}

async function runSynthesis(topic, results) {
    synthContainer.style.display = 'block';
    synthOutput.innerHTML = 'INITIALIZING SYNTHESIS MATRIX...';

    const formattedArgs = results.map(r => `${r.name} claims: ${r.response}`).join('\n\n');

    try {
        const res = await fetch('/api/synthesize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                arguments: formattedArgs
            })
        });

        const data = await res.json();
        await typeWriterEffect(synthOutput, data.response, 15);
    } catch (error) {
        synthOutput.innerHTML = `CRITICAL FAILURE IN SYNTHESIS ENGINE: ${error.message}`;
    } finally {
        startBtn.disabled = false;
        startBtn.innerHTML = "INITIATE_CHAOS()";
    }
}

startBtn.addEventListener('click', async () => {
    const topic = topicInput.value.trim();
    if (!topic) return;

    // Reset State
    startBtn.disabled = true;
    startBtn.innerHTML = "SYSTEM_BUSY...";
    synthContainer.style.display = 'none';
    synthOutput.innerHTML = '';
    debateResults = [];

    // Fire all requests concurrently
    const promises = personas.map(p => fetchPersonaResponse(topic, p));

    // Wait for all personas to finish screaming
    const results = await Promise.all(promises);
    const validResults = results.filter(r => r !== null);

    if (validResults.length > 0) {
        await runSynthesis(topic, validResults);
    } else {
        startBtn.disabled = false;
        startBtn.innerHTML = "INITIATE_CHAOS()";
    }
});

// Setup on load
initPanels();
