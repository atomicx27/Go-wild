document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    setInterval(updateClock, 1000);
    loadWidgets();

    document.getElementById('command-form').addEventListener('submit', handleCommand);
});

function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString('en-US', { hour12: false });
}

let terminalOpen = true;
function toggleTerminal() {
    const terminal = document.getElementById('terminal-panel');
    if (terminalOpen) {
        terminal.style.transform = 'translateY(calc(100% - 24px))';
    } else {
        terminal.style.transform = 'translateY(0)';
    }
    terminalOpen = !terminalOpen;
}

function appendToTerminal(text, type = 'info') {
    const output = document.getElementById('terminal-output');
    const div = document.createElement('div');

    let colorClass = 'text-neon-blue';
    if (type === 'error') colorClass = 'text-neon-pink';
    if (type === 'success') colorClass = 'text-neon-green';
    if (type === 'system') colorClass = 'text-neon-purple';

    div.className = colorClass;
    div.textContent = `> ${text}`;

    output.appendChild(div);
    output.scrollTop = output.scrollHeight;
}

async function handleCommand(e) {
    e.preventDefault();
    const input = document.getElementById('command-input');
    const command = input.value.trim();
    if (!command) return;

    input.value = '';
    appendToTerminal(command, 'info');

    document.getElementById('status-indicator').textContent = 'SYS_THINKING...';
    document.getElementById('status-indicator').classList.add('text-neon-pink');

    try {
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        });

        const data = await response.json();

        if (data.status === 'success') {
            const agentResponse = data.response;

            if (agentResponse.type === 'error') {
                appendToTerminal(`ERR: ${agentResponse.message}`, 'error');
            } else {
                if (agentResponse.message) {
                    appendToTerminal(agentResponse.message, 'success');
                }

                if (agentResponse.type === 'widget_creation') {
                    appendToTerminal(`Widget [${agentResponse.name}] generated successfully.`, 'system');
                    loadWidgets(); // Reload widgets to show the new one
                }
            }
        } else {
            appendToTerminal(`ERR: Server responded with status ${data.status}`, 'error');
        }
    } catch (error) {
        appendToTerminal(`ERR: ${error.message}`, 'error');
    } finally {
        document.getElementById('status-indicator').textContent = 'SYS_ONLINE';
        document.getElementById('status-indicator').classList.remove('text-neon-pink');
    }
}

async function loadWidgets() {
    try {
        const response = await fetch('/api/widgets');
        const data = await response.json();

        if (data.status === 'success') {
            const desktop = document.getElementById('desktop');
            desktop.innerHTML = ''; // Clear current

            data.widgets.forEach(widget => {
                const container = document.createElement('div');
                container.className = 'widget-glass rounded-lg overflow-hidden flex flex-col h-64 transition-all duration-300';

                const header = document.createElement('div');
                header.className = 'h-8 bg-black/40 border-b border-neon-blue/20 flex items-center px-3 justify-between cursor-move';
                header.innerHTML = `
                    <span class="text-xs font-bold text-neon-blue uppercase">${widget.name}</span>
                    <button class="text-neon-pink hover:text-white transition-colors" onclick="this.closest('.widget-glass').remove()">×</button>
                `;

                const content = document.createElement('div');
                content.className = 'flex-1 p-4 overflow-y-auto relative';
                content.innerHTML = widget.html;

                // Execute any scripts that might have been generated in the HTML
                const scripts = content.getElementsByTagName('script');
                for (let i = 0; i < scripts.length; i++) {
                    const newScript = document.createElement('script');
                    newScript.text = scripts[i].text;
                    document.body.appendChild(newScript).parentNode.removeChild(newScript);
                }

                container.appendChild(header);
                container.appendChild(content);
                desktop.appendChild(container);
            });
        }
    } catch (error) {
        appendToTerminal(`Failed to load widgets: ${error.message}`, 'error');
    }
}