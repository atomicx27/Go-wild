const API_BASE = '/api';

// --- Polling & State ---
let pollInterval;

async function fetchTickets() {
    try {
        const res = await fetch(`${API_BASE}/tickets`);
        const tickets = await res.json();
        renderKanban(tickets);
    } catch (e) {
        console.error("Failed to fetch tickets", e);
    }
}

function startPolling() {
    fetchTickets();
    pollInterval = setInterval(fetchTickets, 5000);
}

// --- Render ---
function renderKanban(tickets) {
    const columns = {
        'TODO': document.getElementById('list-TODO'),
        'IN PROGRESS': document.getElementById('list-IN PROGRESS'),
        'REVIEW': document.getElementById('list-REVIEW'),
        'DONE': document.getElementById('list-DONE')
    };

    const counts = {
        'TODO': 0, 'IN PROGRESS': 0, 'REVIEW': 0, 'DONE': 0
    };

    // Clear existing
    for (const col in columns) {
        columns[col].innerHTML = '';
    }

    tickets.forEach(ticket => {
        if (columns[ticket.status]) {
            const card = document.createElement('div');
            card.className = 'ticket-card bg-gray-800 border border-gray-700 p-4 rounded shadow-md relative';
            card.draggable = true;
            card.dataset.id = ticket.id;
            card.dataset.status = ticket.status;

            // AI indicator
            const aiBadge = ticket.ai_processed
                ? `<span class="absolute top-2 right-2 w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_5px_#22d3ee]" title="AI Analyzed"></span>`
                : `<span class="absolute top-2 right-2 w-2 h-2 rounded-full bg-yellow-500 animate-pulse" title="Awaiting AI"></span>`;

            card.innerHTML = `
                ${aiBadge}
                <h3 class="font-bold text-gray-200 mb-1 pr-4 truncate" title="${ticket.title}">${ticket.title}</h3>
                <p class="text-xs text-gray-500 line-clamp-2">${ticket.description}</p>
                <div class="mt-3 flex justify-between items-center">
                    <span class="text-[10px] text-gray-500 uppercase">${new Date(ticket.created_at).toLocaleDateString()}</span>
                    <button onclick="openTicketDetail('${ticket.id}')" class="text-xs text-cyan-400 hover:text-cyan-300">View &rarr;</button>
                </div>
            `;

            // Drag events
            card.addEventListener('dragstart', handleDragStart);
            card.addEventListener('dragend', handleDragEnd);

            columns[ticket.status].appendChild(card);
            counts[ticket.status]++;
        }
    });

    // Update counts
    for (const status in counts) {
        document.getElementById(`count-${status}`).innerText = counts[status];
    }
}

// --- Drag and Drop ---
let draggedTicket = null;

function handleDragStart(e) {
    draggedTicket = this;
    setTimeout(() => this.classList.add('dragging'), 0);
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedTicket = null;
    document.querySelectorAll('.kanban-column').forEach(col => col.classList.remove('drag-over'));
}

document.querySelectorAll('.kanban-column').forEach(col => {
    col.addEventListener('dragover', e => {
        e.preventDefault();
        col.classList.add('drag-over');
    });

    col.addEventListener('dragleave', () => {
        col.classList.remove('drag-over');
    });

    col.addEventListener('drop', async e => {
        e.preventDefault();
        col.classList.remove('drag-over');
        if (draggedTicket) {
            const newStatus = col.dataset.status;
            const ticketId = draggedTicket.dataset.id;

            // Optimistic UI update
            col.querySelector('.ticket-list').appendChild(draggedTicket);

            try {
                await fetch(`${API_BASE}/tickets/${ticketId}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                fetchTickets(); // Refresh counts and true state
            } catch (err) {
                console.error("Failed to update status", err);
                fetchTickets(); // Revert on failure
            }
        }
    });
});

// --- Modals ---
function openNewTicketModal() {
    document.getElementById('newTicketModal').classList.remove('hidden');
    document.getElementById('ticketTitle').focus();
}

function closeNewTicketModal() {
    document.getElementById('newTicketModal').classList.add('hidden');
    document.getElementById('newTicketForm').reset();
}

document.getElementById('newTicketForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('ticketTitle').value;
    const description = document.getElementById('ticketDescription').value;

    try {
        await fetch(`${API_BASE}/tickets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, status: 'TODO' })
        });
        closeNewTicketModal();
        fetchTickets();
    } catch (err) {
        alert("Failed to create ticket");
    }
});

// --- Ticket Detail & Comments ---
let detailPollInterval;

async function openTicketDetail(ticketId) {
    document.getElementById('ticketDetailModal').classList.remove('hidden');
    document.getElementById('currentTicketId').value = ticketId;

    await loadTicketDetail(ticketId);

    // Poll for comments while modal is open
    detailPollInterval = setInterval(() => loadComments(ticketId), 3000);
}

function closeTicketDetailModal() {
    document.getElementById('ticketDetailModal').classList.add('hidden');
    clearInterval(detailPollInterval);
}

async function loadTicketDetail(ticketId) {
    try {
        // Find ticket in current DOM state to avoid extra fetch if possible,
        // but better to fetch fresh to ensure we have description.
        // Since we don't have a GET /ticket/{id} endpoint, we can filter from get_tickets
        const res = await fetch(`${API_BASE}/tickets`);
        const tickets = await res.json();
        const ticket = tickets.find(t => t.id === ticketId);

        if (ticket) {
            document.getElementById('detailTitle').innerText = ticket.title;
            document.getElementById('detailStatus').innerText = ticket.status;
            document.getElementById('detailDescription').innerText = ticket.description || "No description provided.";

            const aiStatus = document.getElementById('aiStatusBadge');
            if (ticket.ai_processed) {
                aiStatus.innerText = "AI Analyzed";
                aiStatus.className = "text-xs px-2 py-1 rounded-full bg-cyan-900 text-cyan-200 border border-cyan-700";
            } else {
                aiStatus.innerText = "Awaiting AI...";
                aiStatus.className = "text-xs px-2 py-1 rounded-full bg-yellow-900 text-yellow-200 border border-yellow-700 animate-pulse";
            }
        }

        await loadComments(ticketId);
    } catch (e) {
        console.error(e);
    }
}

async function loadComments(ticketId) {
    try {
        const res = await fetch(`${API_BASE}/tickets/${ticketId}/comments`);
        const comments = await res.json();

        const list = document.getElementById('commentsList');
        // Simple check to prevent re-rendering if count is same (imperfect but works for demo)
        if (list.childElementCount === comments.length) return;

        list.innerHTML = '';

        comments.forEach(c => {
            const isAI = c.author === 'Neural PM';
            const htmlContent = marked.parse(c.content);

            const el = document.createElement('div');
            el.className = `comment-card p-3 rounded-md bg-gray-800 border border-gray-700 ${isAI ? 'ai-comment' : ''}`;

            el.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <span class="font-semibold text-sm ${isAI ? 'text-cyan-400 flex items-center gap-1' : 'text-gray-300'}">
                        ${isAI ? '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>' : ''}
                        ${c.author}
                    </span>
                    <span class="text-[10px] text-gray-500">${new Date(c.created_at).toLocaleString()}</span>
                </div>
                <div class="prose prose-invert prose-sm max-w-none text-gray-300">
                    ${htmlContent}
                </div>
            `;
            list.appendChild(el);
        });

        // Auto scroll to bottom
        list.scrollTop = list.scrollHeight;

    } catch (e) {
        console.error(e);
    }
}

document.getElementById('commentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ticketId = document.getElementById('currentTicketId').value;
    const content = document.getElementById('newCommentContent').value;

    try {
        await fetch(`${API_BASE}/tickets/${ticketId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author: 'Human User', content })
        });
        document.getElementById('newCommentContent').value = '';
        loadComments(ticketId);
    } catch (err) {
        alert("Failed to post comment");
    }
});

// Initialize
startPolling();
