document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('task-input');
    const executeBtn = document.getElementById('btn-execute');
    const clearBtn = document.getElementById('btn-clear');
    const terminalOutput = document.getElementById('terminal-output');
    const sysStatusDot = document.getElementById('sys-status-dot');
    const sysStatusText = document.getElementById('sys-status-text');
    const ollamaStatus = document.getElementById('ollama-status');

    let pollInterval = null;
    let isAgentRunning = false;

    // Fetch initial status
    checkStatus();
    setInterval(checkStatus, 5000); // Check every 5 seconds

    function checkStatus() {
        fetch('/api/status')
            .then(res => res.json())
            .then(data => {
                isAgentRunning = data.running;

                if (data.ollama_available) {
                    ollamaStatus.textContent = "ONLINE";
                    ollamaStatus.style.color = "var(--log-result)";
                } else {
                    ollamaStatus.textContent = "OFFLINE (MOCK MODE)";
                    ollamaStatus.style.color = "var(--log-error)";
                }

                if (isAgentRunning) {
                    sysStatusDot.className = 'dot working';
                    sysStatusText.textContent = 'SYSTEM ACTIVE // PROCESSING';
                    executeBtn.disabled = true;
                    if (!pollInterval) startPolling();
                } else {
                    sysStatusDot.className = 'dot active';
                    sysStatusText.textContent = 'SYSTEM IDLE // READY';
                    executeBtn.disabled = false;
                    if (pollInterval) {
                        clearInterval(pollInterval);
                        pollInterval = null;
                        fetchLogs(); // Final fetch
                    }
                }
            })
            .catch(err => {
                sysStatusDot.className = 'dot';
                sysStatusText.textContent = 'SYSTEM OFFLINE // NO CONNECTION';
                ollamaStatus.textContent = "UNKNOWN";
            });
    }

    function appendLog(log) {
        // Prevent duplicate entries in a simple way
        const existingLogs = Array.from(terminalOutput.children).map(el => el.textContent);
        if (existingLogs.includes(log.message)) return;

        const div = document.createElement('div');
        div.className = `log-entry ${log.type}`;

        let prefix = '';
        if (log.type === 'thought') prefix = '[THOUGHT] ';
        else if (log.type === 'action') prefix = '[ACTION] ';
        else if (log.type === 'result') prefix = '[RESULT] ';
        else if (log.type === 'error') prefix = '[ERROR] ';
        else if (log.type === 'final') prefix = '[FINAL OUTPUT] ';

        div.textContent = `${prefix}${log.message}`;
        terminalOutput.appendChild(div);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    function fetchLogs() {
        fetch('/api/logs')
            .then(res => res.json())
            .then(logs => {
                terminalOutput.innerHTML = ''; // In a real app, diff this. For now, clear and rewrite.
                logs.forEach(appendLog);
            })
            .catch(console.error);
    }

    function startPolling() {
        pollInterval = setInterval(fetchLogs, 1000);
    }

    executeBtn.addEventListener('click', () => {
        const task = taskInput.value.trim();
        if (!task) return;

        executeBtn.disabled = true;
        terminalOutput.innerHTML = '';
        appendLog({ type: 'system', message: 'Initializing task sequence...' });

        fetch('/api/task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: task })
        })
        .then(res => {
            if (!res.ok) throw new Error('Failed to start task');
            taskInput.value = '';
            checkStatus(); // Immediately check status to start polling
        })
        .catch(err => {
            appendLog({ type: 'error', message: err.message });
            executeBtn.disabled = false;
        });
    });

    clearBtn.addEventListener('click', () => {
        terminalOutput.innerHTML = '<div class="log-entry system">Logs cleared.</div>';
    });
});