document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const taskInput = document.getElementById('task-input');
    const sendBtn = document.getElementById('send-btn');
    const statusDot = document.querySelector('#connection-status div');
    const statusText = document.querySelector('#connection-status');
    const welcomeMessage = document.getElementById('welcome-message');
    const loadingIndicator = document.getElementById('loading-indicator');

    let ws = null;
    let currentMessageDiv = null;

    function connect() {
        // Use wss:// if hosted on https, otherwise ws://
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

        ws.onopen = () => {
            statusDot.className = 'w-3 h-3 rounded-full bg-emerald-500 active-pulse';
            statusText.innerHTML = '<div class="w-3 h-3 rounded-full bg-emerald-500 active-pulse"></div> Connected';
        };

        ws.onclose = () => {
            statusDot.className = 'w-3 h-3 rounded-full bg-red-500';
            statusText.innerHTML = '<div class="w-3 h-3 rounded-full bg-red-500"></div> Disconnected';
            setTimeout(connect, 3000); // Auto reconnect
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleMessage(data);
        };
    }

    function appendMessage(role, content, type = 'normal') {
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }

        const msgDiv = document.createElement('div');
        msgDiv.className = `flex flex-col max-w-full ${role === 'user' ? 'items-end' : 'items-start'}`;

        const innerDiv = document.createElement('div');

        let bgClass = '';
        let borderClass = '';
        let textClass = 'text-slate-200';
        let icon = '';

        if (role === 'user') {
            bgClass = 'bg-sky-900/50';
            borderClass = 'border border-sky-800';
            icon = '<i class="fas fa-user text-sky-400 mt-1"></i>';
        } else {
            bgClass = 'bg-slate-800/80';
            borderClass = 'border border-slate-700';
            icon = '<i class="fas fa-robot text-emerald-400 mt-1"></i>';

            if (type === 'think') {
                bgClass = 'bg-purple-900/30';
                borderClass = 'border border-purple-800/50';
                textClass = 'text-purple-200 italic';
                icon = '<i class="fas fa-brain text-purple-400 mt-1"></i>';
            } else if (type === 'execute') {
                bgClass = 'bg-amber-900/30';
                borderClass = 'border border-amber-800/50';
                textClass = 'text-amber-200 terminal-output';
                icon = '<i class="fas fa-terminal text-amber-400 mt-1"></i>';
            } else if (type === 'command_output') {
                bgClass = 'bg-slate-950';
                borderClass = 'border border-slate-800';
                textClass = 'text-slate-300 terminal-output text-sm';
                icon = '<i class="fas fa-chevron-right text-slate-500 mt-1"></i>';
            } else if (type === 'error') {
                bgClass = 'bg-red-900/30';
                borderClass = 'border border-red-800/50';
                textClass = 'text-red-200';
                icon = '<i class="fas fa-exclamation-triangle text-red-400 mt-1"></i>';
            } else if (type === 'status') {
                 bgClass = 'bg-transparent';
                 borderClass = '';
                 textClass = 'text-slate-500 text-xs uppercase tracking-widest';
                 icon = '';
            }
        }

        innerDiv.className = `p-4 rounded-lg flex gap-3 max-w-[85%] ${bgClass} ${borderClass}`;

        const contentHTML = content.replace(/\n/g, '<br>');

        innerDiv.innerHTML = `
            ${icon}
            <div class="${textClass} overflow-x-auto w-full">${contentHTML}</div>
        `;

        msgDiv.appendChild(innerDiv);
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        return innerDiv;
    }

    function handleMessage(data) {
        switch (data.type) {
            case 'status':
                appendMessage('system', data.content, 'status');
                break;
            case 'think':
                appendMessage('agent', data.content, 'think');
                break;
            case 'execute':
                appendMessage('agent', `Executing:\n${data.content}`, 'execute');
                break;
            case 'command_output':
                appendMessage('system', data.content, 'command_output');
                break;
            case 'answer':
                appendMessage('agent', data.content, 'normal');
                setLoading(false);
                break;
            case 'error':
                appendMessage('system', data.content, 'error');
                setLoading(false);
                break;
            case 'stream_start':
                // We could set up a container for streaming text
                break;
            case 'stream_chunk':
                // For simplicity, we just wait for the parsed blocks,
                // but we could animate the raw stream here if desired.
                break;
            case 'stream_end':
                break;
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.classList.remove('hidden');
            sendBtn.disabled = true;
            sendBtn.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            loadingIndicator.classList.add('hidden');
            sendBtn.disabled = false;
            sendBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    function sendTask() {
        const task = taskInput.value.trim();
        if (!task || !ws || ws.readyState !== WebSocket.OPEN) return;

        appendMessage('user', task);
        ws.send(JSON.stringify({ type: 'task', content: task }));
        taskInput.value = '';
        setLoading(true);
    }

    sendBtn.addEventListener('click', sendTask);
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendTask();
    });

    // Initialize connection
    connect();
});
