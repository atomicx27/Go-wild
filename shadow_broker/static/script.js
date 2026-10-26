async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('stat-total').innerText = data.total_bounties;
        document.getElementById('stat-open').innerText = data.open_bounties;
        document.getElementById('stat-completed').innerText = data.completed_bounties;
    } catch (e) {
        console.error("Failed to fetch stats", e);
    }
}

async function fetchBounties() {
    try {
        const res = await fetch('/api/bounties');
        const data = await res.json();

        const list = document.getElementById('bounty-list');
        list.innerHTML = '';

        data.forEach(bounty => {
            const card = document.createElement('div');
            card.className = 'bounty-card';
            card.setAttribute('data-status', bounty.status);

            const escapeHTML = str => str.replace(/[&<>'"]/g,
                tag => ({
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    "'": '&#39;',
                    '"': '&quot;'
                }[tag] || tag)
            );

            let codeSection = `<div class="code-old"><strong>ORIGINAL</strong><pre>${escapeHTML(bounty.original_code)}</pre></div>`;
            if (bounty.status === 'COMPLETED' && bounty.proposed_fix) {
                codeSection = `
                    <div class="diff-grid">
                        <div class="code-old"><strong>ORIGINAL</strong><pre>${escapeHTML(bounty.original_code)}</pre></div>
                        <div class="code-new"><strong>MERC FIX</strong><pre>${escapeHTML(bounty.proposed_fix)}</pre></div>
                    </div>
                `;
            } else if (bounty.status === 'CLAIMED') {
                codeSection += `<div style="margin-top:10px; color:#ff003c;">Mercenary is analyzing...</div>`;
            }

            card.innerHTML = `
                <div class="bounty-header">
                    <div>
                        <strong>ID:</strong> #${bounty.id} |
                        <strong>FILE:</strong> ${escapeHTML(bounty.filepath)}
                    </div>
                    <div class="status-badge ${bounty.status}">${bounty.status}</div>
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>[${bounty.comment_type}]</strong> ${escapeHTML(bounty.description)}
                </div>
                ${codeSection}
            `;
            list.appendChild(card);
        });

    } catch (e) {
        console.error("Failed to fetch bounties", e);
    }
}

function updateDashboard() {
    fetchStats();
    fetchBounties();
}

// Initial load
updateDashboard();

// Poll every 5 seconds
setInterval(updateDashboard, 5000);