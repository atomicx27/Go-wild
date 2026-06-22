// Clock
function updateClock() {
    const now = new Date();
    document.getElementById('clock').innerText = now.toLocaleTimeString('en-US', { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();

// Window Dragging Logic
const windows = document.querySelectorAll('.window');
let zIndexCounter = 10;

windows.forEach(win => {
    const header = win.querySelector('.window-header');

    // Bring to front on click
    win.addEventListener('mousedown', () => {
        win.style.zIndex = ++zIndexCounter;
    });

    let isDragging = false;
    let offsetX, offsetY;

    header.addEventListener('mousedown', (e) => {
        isDragging = true;
        offsetX = e.clientX - win.offsetLeft;
        offsetY = e.clientY - win.offsetTop;
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        win.style.left = `${e.clientX - offsetX}px`;
        win.style.top = `${e.clientY - offsetY}px`;
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
});

// Desktop Icons Polling
async function fetchDesktopFiles() {
    try {
        const res = await fetch('/api/fs/desktop');
        const data = await res.json();
        const desktop = document.getElementById('desktop');
        desktop.innerHTML = '';

        if(data.files) {
            data.files.forEach(file => {
                const icon = document.createElement('div');
                icon.className = 'desktop-icon';
                icon.innerHTML = `
                    <div class="icon-img">📄</div>
                    <div class="icon-label">${file}</div>
                `;
                icon.ondblclick = () => openFile(file);
                desktop.appendChild(icon);
            });
        }
    } catch (e) {
        console.error("Error fetching files:", e);
    }
}
// Poll every 5 seconds
setInterval(fetchDesktopFiles, 5000);
fetchDesktopFiles();

async function openFile(filename) {
    try {
        const res = await fetch(`/api/fs/read/${filename}`);
        const data = await res.json();
        if(data.content !== undefined) {
            document.getElementById('notepad-title').innerText = filename;
            document.getElementById('notepad-content').value = data.content;
            const win = document.getElementById('notepad-window');
            win.style.display = 'flex';
            win.style.zIndex = ++zIndexCounter;
        }
    } catch (e) {
        console.error("Error reading file:", e);
    }
}

// Terminal Logic
const terminalInput = document.getElementById('terminal-input');
const terminalOutput = document.getElementById('terminal-output');

terminalInput.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter' && terminalInput.value.trim() !== '') {
        const cmd = terminalInput.value.trim();
        terminalInput.value = '';

        // Echo command
        const cmdDiv = document.createElement('div');
        cmdDiv.innerHTML = `<span style="color:var(--secondary)">></span> ${cmd}`;
        terminalOutput.appendChild(cmdDiv);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;

        // Special clear command
        if (cmd.toLowerCase() === 'clear') {
            terminalOutput.innerHTML = '';
            return;
        }

        // Send to backend
        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: cmd })
            });
            const data = await res.json();

            const resDiv = document.createElement('div');
            resDiv.style.color = 'var(--primary)';
            resDiv.innerText = data.response;
            terminalOutput.appendChild(resDiv);
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        } catch (err) {
            const errDiv = document.createElement('div');
            errDiv.style.color = 'var(--tertiary)';
            errDiv.innerText = "UPLINK ERROR: " + err.message;
            terminalOutput.appendChild(errDiv);
        }
    }
});

// WebSocket for Agent Thoughts
const sysmonBody = document.getElementById('sysmon-body');
function connectWebSocket() {
    const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${wsProto}//${location.host}/ws/thoughts`);

    ws.onmessage = function(event) {
        const line = document.createElement('div');
        line.className = 'sysmon-line';
        line.innerText = event.data;
        sysmonBody.appendChild(line);

        // Keep only last 50 thoughts
        if (sysmonBody.children.length > 50) {
            sysmonBody.removeChild(sysmonBody.firstChild);
        }
        sysmonBody.scrollTop = sysmonBody.scrollHeight;
    };

    ws.onclose = function() {
        setTimeout(connectWebSocket, 3000); // Reconnect
    };
}
connectWebSocket();

function toggleStartMenu() {
    // A placeholder for a start menu
    const existing = document.getElementById('start-menu');
    if (existing) {
        existing.remove();
        return;
    }
    const menu = document.createElement('div');
    menu.id = 'start-menu';
    menu.style.position = 'fixed';
    menu.style.bottom = '40px';
    menu.style.left = '0';
    menu.style.width = '200px';
    menu.style.background = 'var(--glass-bg)';
    menu.style.border = '1px solid var(--primary)';
    menu.style.padding = '10px';
    menu.style.zIndex = '9999';
    menu.innerHTML = `
        <div style="padding: 10px; cursor: pointer; border-bottom: 1px solid var(--glass-border)" onclick="location.reload()">REBOOT KERNEL</div>
        <div style="padding: 10px; cursor: pointer;" onclick="document.getElementById('start-menu').remove()">CLOSE_MENU</div>
    `;
    document.body.appendChild(menu);
}
