// cyberpunk_ui.js
document.addEventListener('DOMContentLoaded', () => {
    // Inject global styles
    const style = document.createElement('style');
    style.innerHTML = `
        /* Global Cyberpunk Enhancements */
        :root {
            --neon-blue: #00f3ff;
            --neon-purple: #bc13fe;
            --neon-pink: #ff00ff;
            --cyber-bg: rgba(10, 10, 15, 0.85);
            --glass-border: rgba(0, 243, 255, 0.3);
        }

        /* Hover Glow for buttons */
        .cyber-hover {
            transition: all 0.3s ease-in-out !important;
        }

        .cyber-hover:hover {
            box-shadow: 0 0 15px var(--neon-blue), inset 0 0 10px var(--neon-blue) !important;
            text-shadow: 0 0 5px #fff, 0 0 10px var(--neon-blue) !important;
            transform: translateY(-2px) scale(1.02) !important;
            border-color: var(--neon-blue) !important;
            z-index: 10;
        }

        /* Click Ripple / Pulse */
        @keyframes cyber-pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 243, 255, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(0, 243, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 243, 255, 0); }
        }

        .cyber-pulse-anim {
            animation: cyber-pulse 0.5s ease-out;
        }

        /* Glassmorphism for containers/cards */
        .cyber-glass {
            background: var(--cyber-bg) !important;
            color: #ffffff !important; /* Ensure text legibility against dark background */
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        }

        /* Prevent text color from overriding nested elements unexpectedly if they need specific colors */
        .cyber-glass p, .cyber-glass span, .cyber-glass h1, .cyber-glass h2, .cyber-glass h3, .cyber-glass h4, .cyber-glass h5, .cyber-glass h6, .cyber-glass label, .cyber-glass th, .cyber-glass td {
             text-shadow: 0 0 2px rgba(255, 255, 255, 0.2);
        }

        /* Input focus effects */
        .cyber-input {
            transition: border-color 0.3s, box-shadow 0.3s !important;
        }

        .cyber-input:focus {
            outline: none !important;
            border-color: var(--neon-purple) !important;
            box-shadow: 0 0 10px var(--neon-purple) !important;
        }
    `;
    document.head.appendChild(style);

    // Event Delegation
    document.body.addEventListener('mouseover', (e) => {
        const target = e.target;
        if (target.tagName === 'BUTTON' || target.classList.contains('btn') || target.tagName === 'A') {
            target.classList.add('cyber-hover');
        }
    });

    document.body.addEventListener('mousedown', (e) => {
        const target = e.target;
        if (target.tagName === 'BUTTON' || target.classList.contains('btn') || target.tagName === 'A') {
            target.classList.add('cyber-pulse-anim');
            setTimeout(() => {
                target.classList.remove('cyber-pulse-anim');
            }, 500);
        }
    });

    document.body.addEventListener('focusin', (e) => {
        const target = e.target;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
            target.classList.add('cyber-input');
        }
    });

    // Apply glassmorphism to common container elements dynamically
    const applyGlass = () => {
        const containers = document.querySelectorAll('.card, .container, .panel, .board, .kanban-column, .modal, .box, #side-panel, .terminal-box');
        containers.forEach(el => {
            if(!el.classList.contains('cyber-glass')) {
                el.classList.add('cyber-glass');
            }
        });
    };

    applyGlass();

    // Use MutationObserver instead of setInterval to watch for dynamic elements
    const observer = new MutationObserver((mutations) => {
        let shouldApply = false;
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length > 0) {
                shouldApply = true;
            }
        });
        if (shouldApply) {
            applyGlass();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
