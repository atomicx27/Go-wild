const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const topicInput = document.getElementById('topicInput');
const transcript = document.getElementById('transcript');
const statusText = document.getElementById('status-text');
const recordingDot = document.getElementById('recording-dot');

let debateActive = false;
let currentTopic = "";
let history = [];
let turnCount = 0;
const MAX_TURNS = 6; // Moderator intro + 4 debate turns + Moderator outro

const agents = ["Moderator", "Alpha", "Omega"];
let voices = [];

// Initialize speech synthesis
function initVoices() {
    voices = window.speechSynthesis.getVoices();
}
window.speechSynthesis.onvoiceschanged = initVoices;

function getVoiceForAgent(agentName) {
    if (voices.length === 0) return null;

    // Attempt to assign distinct voices based on typical OS availability
    if (agentName === "Moderator") {
        return voices.find(v => v.name.includes("Google UK English Male") || v.name.includes("Daniel") || v.lang === 'en-GB') || voices[0];
    } else if (agentName === "Alpha") {
        // Chaotic/younger sounding
        return voices.find(v => v.name.includes("Google US English") || v.name.includes("Samantha") || v.name.includes("Zira")) || voices[0];
    } else if (agentName === "Omega") {
        // Robotic/deep sounding
        return voices.find(v => v.name.includes("Microsoft David") || v.name.includes("Alex") || v.name.includes("Fred")) || voices[0];
    }
    return voices[0];
}

function speak(text, agentName) {
    return new Promise((resolve) => {
        if (!window.speechSynthesis) {
            resolve();
            return;
        }

        const utterance = new SpeechSynthesisUtterance(text);
        const voice = getVoiceForAgent(agentName);
        if (voice) utterance.voice = voice;

        // Adjust pitch/rate for character
        if (agentName === "Alpha") {
            utterance.pitch = 1.2;
            utterance.rate = 1.1;
        } else if (agentName === "Omega") {
            utterance.pitch = 0.5;
            utterance.rate = 0.9;
        } else {
            utterance.pitch = 1.0;
            utterance.rate = 1.0;
        }

        utterance.onend = resolve;
        utterance.onerror = resolve; // Continue even if speech fails

        window.speechSynthesis.speak(utterance);
    });
}

function setActiveAgent(agentName, isThinking = false) {
    agents.forEach(a => {
        const card = document.getElementById(`card-${a}`);
        card.classList.remove('active', 'thinking');
        if (a === agentName) {
            card.classList.add('active');
            if (isThinking) {
                card.classList.add('thinking');
                statusText.innerText = `${agentName} IS PROCESSING...`;
            } else {
                statusText.innerText = `${agentName} IS SPEAKING`;
            }
        }
    });
}

function appendMessage(agentName, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message message-${agentName.toLowerCase()}`;

    const nameDiv = document.createElement('div');
    nameDiv.className = 'agent-name';
    nameDiv.innerText = agentName;

    const contentDiv = document.createElement('div');
    contentDiv.innerText = text;

    msgDiv.appendChild(nameDiv);
    msgDiv.appendChild(contentDiv);

    transcript.appendChild(msgDiv);
    transcript.scrollTop = transcript.scrollHeight;
}

async function executeTurn(agentName) {
    if (!debateActive) return;

    setActiveAgent(agentName, true);

    try {
        const response = await fetch('/api/debate/turn', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: currentTopic,
                history: history,
                agent: agentName
            })
        });

        if (!response.ok) throw new Error("API Error");

        const data = await response.json();
        const speechText = data.response;

        setActiveAgent(agentName, false);
        appendMessage(agentName, speechText);
        history.push({ agent: agentName, text: speechText });

        await speak(speechText, agentName);

    } catch (error) {
        console.error("Turn error:", error);
        const errorMsg = `[Connection error while connecting to neural network]`;
        setActiveAgent(agentName, false);
        appendMessage(agentName, errorMsg);
        await new Promise(r => setTimeout(r, 2000)); // Pause briefly on error
    }
}

async function debateLoop() {
    transcript.innerHTML = '';
    history = [];
    turnCount = 0;

    recordingDot.classList.remove('hidden');

    while (debateActive && turnCount < MAX_TURNS) {
        let currentAgent;
        if (turnCount === 0) {
            currentAgent = "Moderator";
        } else if (turnCount === MAX_TURNS - 1) {
            currentAgent = "Moderator"; // Conclusion
        } else {
            currentAgent = turnCount % 2 === 1 ? "Alpha" : "Omega";
        }

        await executeTurn(currentAgent);
        turnCount++;

        if (debateActive && turnCount < MAX_TURNS) {
            // Brief pause between speakers
            await new Promise(r => setTimeout(r, 1000));
        }
    }

    stopDebate();
}

function stopDebate() {
    debateActive = false;
    window.speechSynthesis.cancel();
    startBtn.classList.remove('hidden');
    stopBtn.classList.add('hidden');
    topicInput.disabled = false;
    recordingDot.classList.add('hidden');
    statusText.innerText = "IDLE";

    agents.forEach(a => {
        document.getElementById(`card-${a}`).classList.remove('active', 'thinking');
    });
}

startBtn.addEventListener('click', async () => {
    const topic = topicInput.value.trim();
    if (!topic) {
        alert("Please enter a debate topic.");
        return;
    }

    try {
        const response = await fetch('/api/debate/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: topic })
        });

        if (response.ok) {
            currentTopic = topic;
            debateActive = true;
            startBtn.classList.add('hidden');
            stopBtn.classList.remove('hidden');
            topicInput.disabled = true;

            // Start the loop asynchronously
            debateLoop();
        }
    } catch (e) {
        alert("Failed to connect to backend server.");
    }
});

stopBtn.addEventListener('click', stopDebate);

// Initialize voices if already loaded
if (speechSynthesis.getVoices().length > 0) {
    initVoices();
}
