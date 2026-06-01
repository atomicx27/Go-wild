const canvasContainer = document.getElementById('canvas-container');
const nodesLayer = document.getElementById('nodes-layer');
const edgesLayer = document.getElementById('edges-layer');
const inputModal = document.getElementById('input-modal');
const thoughtInput = document.getElementById('thought-input');

let localNodes = {};
let localEdges = [];

// Node Dragging State
let isDragging = false;
let currentDraggedNode = null;
let dragOffsetX = 0;
let dragOffsetY = 0;

// Poll backend state
async function fetchState() {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();
        updateCanvas(data);
    } catch (error) {
        console.error("Error fetching state:", error);
    }
}

function updateCanvas(state) {
    const { nodes, edges } = state;

    // Update or create nodes
    for (const [id, nodeData] of Object.entries(nodes)) {
        let nodeEl = document.getElementById(`node-${id}`);
        if (!nodeEl) {
            nodeEl = document.createElement('div');
            nodeEl.id = `node-${id}`;
            nodeEl.className = 'node';
            nodeEl.textContent = nodeData.text;

            // Drag events
            nodeEl.addEventListener('mousedown', (e) => startDrag(e, id));

            nodesLayer.appendChild(nodeEl);
            localNodes[id] = nodeEl;
        }

        // Update class for status styling
        nodeEl.className = `node ${nodeData.status}`;

        // Only update position if we aren't currently dragging this node
        if (currentDraggedNode !== id) {
             nodeEl.style.left = `${nodeData.x}px`;
             nodeEl.style.top = `${nodeData.y}px`;
        }
    }

    // Draw edges
    edgesLayer.innerHTML = ''; // lazy clear
    edges.forEach(edge => {
        const sourceNode = nodes[edge.source];
        const targetNode = nodes[edge.target];

        if (sourceNode && targetNode) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');

            // simple curve
            const sx = sourceNode.x;
            const sy = sourceNode.y;
            const tx = targetNode.x;
            const ty = targetNode.y;

            const dx = tx - sx;
            const dy = ty - sy;
            const d = `M ${sx} ${sy} Q ${sx + dx/2} ${sy}, ${sx + dx/2} ${sy + dy/2} T ${tx} ${ty}`;

            line.setAttribute('d', d);
            line.setAttribute('class', 'edge-line');
            edgesLayer.appendChild(line);
        }
    });
}

// Interaction handling
canvasContainer.addEventListener('dblclick', (e) => {
    if (e.target !== canvasContainer && e.target.parentElement !== canvasContainer) return;

    const rect = canvasContainer.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    inputModal.style.left = `${x}px`;
    inputModal.style.top = `${y}px`;
    inputModal.classList.remove('hidden');
    thoughtInput.value = '';
    thoughtInput.focus();

    // Store coordinates for submission
    inputModal.dataset.x = x;
    inputModal.dataset.y = y;
});

thoughtInput.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter' && thoughtInput.value.trim() !== '') {
        const text = thoughtInput.value.trim();
        const x = parseFloat(inputModal.dataset.x);
        const y = parseFloat(inputModal.dataset.y);

        inputModal.classList.add('hidden');

        try {
            await fetch('/api/nodes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, x, y })
            });
            fetchState(); // immediate update
        } catch (error) {
            console.error("Error creating node:", error);
        }
    } else if (e.key === 'Escape') {
        inputModal.classList.add('hidden');
    }
});

// Dragging logic
function startDrag(e, id) {
    if (e.button !== 0) return; // Only left click
    isDragging = true;
    currentDraggedNode = id;

    const nodeEl = localNodes[id];
    const rect = nodeEl.getBoundingClientRect();
    const containerRect = canvasContainer.getBoundingClientRect();

    // Calculate offset from mouse to element center
    dragOffsetX = e.clientX - (rect.left + rect.width/2);
    dragOffsetY = e.clientY - (rect.top + rect.height/2);

    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', endDrag);
}

function onDrag(e) {
    if (!isDragging || !currentDraggedNode) return;

    const containerRect = canvasContainer.getBoundingClientRect();
    const x = e.clientX - containerRect.left - dragOffsetX;
    const y = e.clientY - containerRect.top - dragOffsetY;

    const nodeEl = localNodes[currentDraggedNode];
    nodeEl.style.left = `${x}px`;
    nodeEl.style.top = `${y}px`;

    // We could update edges in real-time here but let's rely on polling for simplicity
}

async function endDrag(e) {
    if (!isDragging) return;

    const containerRect = canvasContainer.getBoundingClientRect();
    const x = e.clientX - containerRect.left - dragOffsetX;
    const y = e.clientY - containerRect.top - dragOffsetY;

    const id = currentDraggedNode;

    isDragging = false;
    currentDraggedNode = null;
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', endDrag);

    // Persist new position
    try {
        await fetch('/api/nodes/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, x, y })
        });
    } catch (error) {
        console.error("Error updating node position:", error);
    }
}

// Hide modal if clicked outside
document.addEventListener('click', (e) => {
    if (!inputModal.classList.contains('hidden') && e.target !== thoughtInput && e.target !== canvasContainer) {
       // if we aren't double clicking
    }
});

// Start polling
setInterval(fetchState, 1000);
fetchState();