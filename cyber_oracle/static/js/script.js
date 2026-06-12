document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('bounty-form');
    const queryInput = document.getElementById('query-input');
    const submitBtn = document.getElementById('submit-btn');
    const terminal = document.getElementById('terminal');
    const logOutput = document.getElementById('log-output');
    const statusIndicator = document.getElementById('status-indicator');
    const dossierContainer = document.getElementById('dossier-container');
    const dossierContent = document.getElementById('dossier-content');

    let currentEventSource = null;

    function appendLog(message, isError = false) {
        const timestamp = new Date().toISOString().split('T')[1].slice(0, -1);
        const logEntry = document.createElement('div');
        logEntry.className = `font-mono text-sm ${isError ? 'text-red-500' : 'text-green-400'}`;
        logEntry.innerHTML = `<span class="text-gray-500">[${timestamp}]</span> > ${message}`;
        logOutput.appendChild(logEntry);
        logOutput.scrollTop = logOutput.scrollHeight;
    }

    function resetUI() {
        logOutput.innerHTML = '';
        dossierContainer.classList.add('hidden');
        terminal.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
        statusIndicator.textContent = '[ CONNECTING ]';
        statusIndicator.className = 'text-yellow-400 animate-pulse';

        if (currentEventSource) {
            currentEventSource.close();
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;

        resetUI();
        appendLog(`Uplinking query: "${query}"`);

        try {
            // Initiate Bounty
            const response = await fetch('/api/bounty', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            if (!response.ok) throw new Error('Failed to initiate bounty.');

            const data = await response.json();
            const jobId = data.job_id;

            appendLog(`Bounty accepted. Tracking ID: ${jobId}`);

            // Connect to datastream
            currentEventSource = new EventSource(`/api/stream/${jobId}`);

            currentEventSource.onmessage = (event) => {
                const payload = JSON.parse(event.data);

                if (payload.status === 'ping') return; // Keep-alive

                if (payload.message) {
                    appendLog(payload.message, payload.status === 'error');
                }

                if (payload.status === 'error') {
                    statusIndicator.textContent = '[ ERR_SYS_FAULT ]';
                    statusIndicator.className = 'text-red-500 animate-pulse';
                    currentEventSource.close();
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                }

                if (payload.status === 'complete') {
                    statusIndicator.textContent = '[ CONNECTION_CLOSED ]';
                    statusIndicator.className = 'text-green-500';
                    currentEventSource.close();

                    // Render Markdown
                    if (payload.dossier) {
                        dossierContent.innerHTML = marked.parse(payload.dossier);
                        dossierContainer.classList.remove('hidden');

                        // Scroll to dossier
                        setTimeout(() => {
                            dossierContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }, 500);
                    }

                    submitBtn.disabled = false;
                    submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                }
            };

            currentEventSource.onerror = () => {
                appendLog('Datastream connection lost.', true);
                currentEventSource.close();
                submitBtn.disabled = false;
                submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            };

        } catch (error) {
            appendLog(error.message, true);
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });
});
