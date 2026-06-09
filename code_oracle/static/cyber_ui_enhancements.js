// cyber_ui_enhancements.js
(function() {
    // Inject specific, non-conflicting CSS classes
    const styleEl = document.createElement('style');
    styleEl.id = 'cyber-ui-enhancements-styles';
    styleEl.textContent = `
        .cyber-cursor-follower {
            position: fixed;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0, 255, 255, 0.4) 0%, rgba(0, 255, 255, 0) 70%);
            pointer-events: none;
            transform: translate(-50%, -50%);
            z-index: 999999;
            transition: width 0.2s, height 0.2s, background 0.2s;
            mix-blend-mode: screen;
        }

        .cyber-cursor-follower.cyber-cursor-active {
            width: 50px;
            height: 50px;
            background: radial-gradient(circle, rgba(255, 0, 255, 0.6) 0%, rgba(255, 0, 255, 0) 70%);
        }

        .cyber-hover-glow {
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5) !important;
            transform: translateY(-2px) !important;
            transition: all 0.3s ease !important;
            z-index: 10;
        }

        .cyber-ripple {
            position: absolute;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 50%;
            transform: scale(0);
            animation: cyber-ripple-anim 0.6s linear;
            pointer-events: none;
        }

        @keyframes cyber-ripple-anim {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }

        @keyframes cyber-fade-in-up {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .cyber-animate-entrance {
            animation: cyber-fade-in-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
    `;
    document.head.appendChild(styleEl);

    // Create cursor follower
    const cursor = document.createElement('div');
    cursor.className = 'cyber-cursor-follower';
    document.body.appendChild(cursor);

    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });

    // Event Delegation for Hover Effects
    document.body.addEventListener('mouseover', (e) => {
        const target = e.target;
        if(target.nodeType !== Node.ELEMENT_NODE) return;
        const interactiveEl = target.closest('button, a, .task, .agent-card, .kanban-column, input, select');

        if (interactiveEl) {
            cursor.classList.add('cyber-cursor-active');
            interactiveEl.classList.add('cyber-hover-glow');
        }
    });

    document.body.addEventListener('mouseout', (e) => {
        const target = e.target;
        if(target.nodeType !== Node.ELEMENT_NODE) return;
        const interactiveEl = target.closest('button, a, .task, .agent-card, .kanban-column, input, select');

        if (interactiveEl) {
            cursor.classList.remove('cyber-cursor-active');
            interactiveEl.classList.remove('cyber-hover-glow');
        }
    });

    // Event Delegation for Ripple Effect on Buttons
    document.body.addEventListener('click', (e) => {
        const target = e.target;
        if(target.nodeType !== Node.ELEMENT_NODE) return;
        const btn = target.closest('button');
        if (btn) {
            const rect = btn.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            const ripple = document.createElement('span');
            ripple.className = 'cyber-ripple';
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            if (getComputedStyle(btn).position === 'static') {
                btn.style.position = 'relative';
            }
            btn.style.overflow = 'hidden'; // Ensure ripple is contained

            btn.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        }
    });

    // MutationObserver for Dynamic Elements (Entrance Animation)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const targetClasses = ['task', 'ticket', 'message', 'card', 'item', 'agent-card', 'kanban-column', 'chat-message', 'log-entry', 'column'];
                        let hasTargetClass = false;
                        if(node.classList) {
                            hasTargetClass = targetClasses.some(cls => node.classList.contains(cls));
                        }

                        if (hasTargetClass) {
                            node.classList.add('cyber-animate-entrance');
                        }
                    }
                });
            }
        });
    });

    // Start observing the body for injected content
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

})();
