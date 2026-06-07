class WindowManager {
    constructor() {
        this.windows = [];
        this.zIndexCounter = 100;
        this.container = document.getElementById('windows-container');
        this.taskbarApps = document.getElementById('taskbar-apps');
    }

    createWindow(options) {
        const winId = 'win-' + Math.random().toString(36).substr(2, 9);
        const { title, width = 600, height = 400, theme = 'green' } = options;

        const borderClass = theme === 'purple' ? 'border-purple-500/50' : 'border-green-500/50';
        const textClass = theme === 'purple' ? 'text-purple-400' : 'text-green-400';
        const hoverClass = theme === 'purple' ? 'hover:bg-purple-900/50' : 'hover:bg-green-900/50';

        const winEl = document.createElement('div');
        winEl.id = winId;
        winEl.className = `os-window ${borderClass} w-[${width}px] h-[${height}px]`;
        winEl.style.width = width + 'px';
        winEl.style.height = height + 'px';

        // Random initial position slightly offset
        const top = Math.max(0, (window.innerHeight - height) / 2 + (Math.random() * 40 - 20));
        const left = Math.max(0, (window.innerWidth - width) / 2 + (Math.random() * 40 - 20));
        winEl.style.top = top + 'px';
        winEl.style.left = left + 'px';

        winEl.innerHTML = `
            <div class="window-header ${borderClass}">
                <div class="flex items-center gap-2">
                    <i class="fas fa-microchip ${textClass}"></i>
                    <span class="text-xs font-bold ${textClass}">${title}</span>
                </div>
                <div class="flex gap-2">
                    <button class="win-close-btn w-4 h-4 rounded-full bg-red-500/20 border border-red-500 hover:bg-red-500 transition-colors"></button>
                </div>
            </div>
            <div class="window-body"></div>
        `;

        this.container.appendChild(winEl);
        this.focusWindow(winEl);

        // Make draggable
        const header = winEl.querySelector('.window-header');
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = left;
        let yOffset = top;

        header.addEventListener('mousedown', (e) => {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
            isDragging = true;
            this.focusWindow(winEl);
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                xOffset = currentX;
                yOffset = currentY;

                // Boundaries
                if(yOffset < 0) yOffset = 0;
                if(yOffset > window.innerHeight - 40) yOffset = window.innerHeight - 40;

                winEl.style.left = currentX + 'px';
                winEl.style.top = currentY + 'px';
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        winEl.addEventListener('mousedown', () => this.focusWindow(winEl));

        // Close button
        winEl.querySelector('.win-close-btn').addEventListener('click', () => {
            this.closeWindow(winId);
        });

        // Add to taskbar
        const taskBtn = document.createElement('button');
        taskBtn.id = `task-${winId}`;
        taskBtn.className = `px-3 h-8 border ${borderClass} rounded text-xs truncate max-w-[120px] ${hoverClass} transition-colors flex items-center gap-2`;
        taskBtn.innerHTML = `<i class="fas fa-microchip ${textClass}"></i>${title}`;
        taskBtn.onclick = () => this.focusWindow(winEl);
        this.taskbarApps.appendChild(taskBtn);

        this.windows.push({ id: winId, el: winEl });

        return {
            id: winId,
            body: winEl.querySelector('.window-body')
        };
    }

    focusWindow(winEl) {
        this.zIndexCounter++;
        winEl.style.zIndex = this.zIndexCounter;

        document.querySelectorAll('.os-window').forEach(w => w.classList.remove('focused', 'border-green-400', 'border-purple-400'));

        const isPurple = winEl.classList.contains('border-purple-500/50');
        winEl.classList.add('focused', isPurple ? 'border-purple-400' : 'border-green-400');
    }

    closeWindow(winId) {
        const winIndex = this.windows.findIndex(w => w.id === winId);
        if (winIndex > -1) {
            this.windows[winIndex].el.remove();
            this.windows.splice(winIndex, 1);
            document.getElementById(`task-${winId}`)?.remove();
        }
    }
}

// OS Clock
setInterval(() => {
    const now = new Date();
    document.getElementById('clock').innerText = now.toLocaleTimeString('en-US', { hour12: false });
}, 1000);

const wm = new WindowManager();

const appManager = {
    openTerminal: () => {
        const win = wm.createWindow({ title: 'Terminal', width: 600, height: 400, theme: 'green' });

        let messages = [
            { role: 'system', content: 'You are an AI assistant integrated into a cyberpunk desktop operating system terminal.' }
        ];

        win.body.innerHTML = `
            <div class="flex flex-col h-full font-mono text-sm">
                <div class="flex-1 overflow-auto p-4 space-y-4 terminal-output">
                    <div class="text-green-500">Welcome to Cyber Deck OS Terminal. Connect via Ollama...</div>
                </div>
                <div class="p-2 border-t border-green-500/50 flex gap-2 bg-black">
                    <span class="text-green-500 mt-1">></span>
                    <input type="text" class="terminal-input flex-1 bg-transparent border-none outline-none text-green-400 placeholder-green-800" placeholder="Type a command...">
                </div>
            </div>
        `;

        const output = win.body.querySelector('.terminal-output');
        const input = win.body.querySelector('.terminal-input');

        input.focus();
        win.body.parentElement.addEventListener('mousedown', () => input.focus());

        const appendMessage = (role, content, stream = false) => {
            const el = document.createElement('div');
            el.className = role === 'user' ? 'text-white' : 'text-green-400';

            if (role === 'user') {
                el.innerHTML = `<span class="text-green-500">></span> ${content}`;
            } else {
                el.innerHTML = `<span class="text-green-500 typing-cursor"></span><span class="content">${content}</span>`;
            }

            output.appendChild(el);
            output.scrollTop = output.scrollHeight;
            return el;
        };

        input.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                const userText = input.value.trim();
                input.value = '';

                messages.push({ role: 'user', content: userText });
                appendMessage('user', userText);

                const responseEl = appendMessage('assistant', '');
                const contentSpan = responseEl.querySelector('.content');

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ messages })
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let fullResponse = '';

                    while (true) {
                        const { value, done } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\n');

                        for (const line of lines) {
                            if (line.trim()) {
                                try {
                                    const data = JSON.parse(line);
                                    if (data.message && data.message.content) {
                                        fullResponse += data.message.content;
                                        contentSpan.textContent = fullResponse;
                                        output.scrollTop = output.scrollHeight;
                                    }
                                } catch (e) {}
                            }
                        }
                    }

                    responseEl.querySelector('.typing-cursor').remove();
                    messages.push({ role: 'assistant', content: fullResponse });

                } catch (err) {
                    contentSpan.textContent = "Error: Connection failed.";
                    responseEl.querySelector('.typing-cursor').remove();
                }
            }
        });
    },

    openForge: () => {
        const win = wm.createWindow({ title: 'App Forge', width: 500, height: 300, theme: 'purple' });

        win.body.innerHTML = `
            <div class="flex flex-col h-full p-4 gap-4">
                <div class="text-purple-400 text-sm">
                    Describe the app you want to generate. Forge will construct a single-file HTML app and launch it.
                </div>
                <textarea class="forge-input flex-1 bg-black/50 border border-purple-500/50 rounded p-2 text-purple-300 resize-none outline-none focus:border-purple-400" placeholder="e.g., A neon styled to-do list app..."></textarea>
                <div class="flex justify-between items-center">
                    <div class="forge-status text-xs text-purple-500">Ready.</div>
                    <button class="forge-btn px-4 py-2 bg-purple-900/50 hover:bg-purple-700/50 border border-purple-500 text-purple-300 rounded font-bold transition-colors">
                        <i class="fas fa-hammer mr-2"></i>FORGE
                    </button>
                </div>
            </div>
        `;

        const input = win.body.querySelector('.forge-input');
        const btn = win.body.querySelector('.forge-btn');
        const status = win.body.querySelector('.forge-status');

        btn.addEventListener('click', async () => {
            const prompt = input.value.trim();
            if (!prompt) return;

            btn.disabled = true;
            btn.classList.add('opacity-50', 'cursor-not-allowed');
            status.innerHTML = `<span class="glitch-loader inline-block">Forging...</span>`;

            try {
                const response = await fetch('/api/forge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullHtml = '';

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.trim()) {
                            try {
                                const data = JSON.parse(line);
                                if (data.message && data.message.content) {
                                    fullHtml += data.message.content;
                                    status.textContent = `Receiving: ${fullHtml.length} bytes...`;
                                }
                            } catch (e) {}
                        }
                    }
                }

                // Clean up possible markdown code blocks
                fullHtml = fullHtml.replace(/^\s*```html/im, '').replace(/```\s*$/im, '').trim();

                status.textContent = "Forge Complete. Launching app.";

                // Launch the generated app
                const appWin = wm.createWindow({ title: 'Generated App', width: 800, height: 600, theme: 'green' });
                appWin.body.innerHTML = `<iframe class="w-full h-full border-none bg-white" srcdoc="${fullHtml.replace(/"/g, '&quot;')}"></iframe>`;

                input.value = '';

            } catch (err) {
                status.textContent = "Error: Forge failed.";
            } finally {
                btn.disabled = false;
                btn.classList.remove('opacity-50', 'cursor-not-allowed');
                setTimeout(() => { if(status.textContent !== "Error: Forge failed.") status.textContent = "Ready."; }, 3000);
            }
        });
    }
};
