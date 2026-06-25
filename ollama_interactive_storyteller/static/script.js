let storyContext = "";

document.getElementById('start-btn').addEventListener('click', startStory);
document.getElementById('submit-custom').addEventListener('click', submitCustomAction);
document.getElementById('custom-action').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        submitCustomAction();
    }
});

async function startStory() {
    const genreInput = document.getElementById('genre-input').value;
    const genre = genreInput ? genreInput : "Cyberpunk";

    document.getElementById('setup-container').classList.add('hidden');
    document.getElementById('story-container').classList.remove('hidden');

    showLoading();
    try {
        const response = await fetch('/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ genre: genre })
        });

        const data = await response.json();
        handleStoryResponse(data.text);
    } catch (error) {
        console.error("Error starting story:", error);
        appendLog("SYSTEM ERROR: UNABLE TO CONNECT TO AI CORE.", "error");
    } finally {
        hideLoading();
    }
}

async function submitAction(action) {
    showLoading();
    try {
        const response = await fetch('/continue', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action: action, context: storyContext })
        });

        const data = await response.json();
        handleStoryResponse(data.text);
    } catch (error) {
        console.error("Error continuing story:", error);
        appendLog("SYSTEM ERROR: UNABLE TO CONNECT TO AI CORE.", "error");
    } finally {
        hideLoading();
    }
}

function submitCustomAction() {
    const inputField = document.getElementById('custom-action');
    const action = inputField.value.trim();
    if (action) {
        appendLog(`> USER ACTION: ${action}`, "user");
        inputField.value = "";
        submitAction(action);
    }
}

function handleStoryResponse(text) {
    // Parse the response to separate story and choices
    // Expected format:
    // [Story]
    // Choices:
    // 1. [Choice 1]
    // 2. [Choice 2]
    // 3. [Choice 3]

    let storyPart = text;
    let choicesText = "";

    const choicesSplit = text.split(/Choices?:/i);
    if (choicesSplit.length > 1) {
        storyPart = choicesSplit[0].trim();
        choicesText = choicesSplit[1].trim();
    }

    // Append to context for future requests
    storyContext += "\n" + storyPart;

    // Keep context from getting too large (very rough heuristic)
    if (storyContext.length > 4000) {
        storyContext = storyContext.substring(storyContext.length - 4000);
    }

    appendLog(storyPart, "story");
    renderChoices(choicesText);
}

function appendLog(text, type) {
    const logDiv = document.getElementById('story-log');
    const entryDiv = document.createElement('div');
    entryDiv.className = 'mb-4';

    if (type === 'user') {
        entryDiv.classList.add('text-green-300', 'font-bold');
        entryDiv.textContent = text;
    } else if (type === 'error') {
        entryDiv.classList.add('text-red-500', 'font-bold');
        entryDiv.textContent = text;
    } else {
        // Convert markdown to HTML for story text
        entryDiv.innerHTML = marked.parse(text);
    }

    logDiv.appendChild(entryDiv);
    logDiv.scrollTop = logDiv.scrollHeight;
}

function renderChoices(choicesText) {
    const container = document.getElementById('choices-container');
    container.innerHTML = ""; // Clear old choices

    if (!choicesText) return;

    // Parse lines like "1. Do something"
    const choiceLines = choicesText.split('\n').filter(line => line.trim().match(/^\d+\./));

    choiceLines.forEach(line => {
        const match = line.match(/^\d+\.\s*(.+)/);
        if (match) {
            const actionText = match[1].trim();
            const btn = document.createElement('button');
            btn.className = "choice-btn w-full bg-green-900 border border-green-500 hover:bg-green-700 text-green-300 py-2 px-4 rounded shadow-sm shadow-green-500/50";
            btn.textContent = line;
            btn.onclick = () => {
                appendLog(`> ${line}`, "user");
                submitAction(actionText);
            };
            container.appendChild(btn);
        }
    });
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('choices-container').innerHTML = ""; // hide choices while loading
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}
