// global_ui.js

(function() {
    const style = document.createElement('style');
    style.textContent = `
        .modern-interactive {
            transition: all 0.3s ease !important;
        }

        .modern-hover-glow {
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5), inset 0 0 10px rgba(0, 255, 255, 0.3) !important;
            transform: translateY(-2px) !important;
            border-color: rgba(0, 255, 255, 0.8) !important;
        }

        .modern-entry-animation {
            animation: modernFadeIn 0.5s ease-out forwards;
        }

        @keyframes modernFadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
                filter: blur(4px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
                filter: blur(0);
            }
        }

        #modern-cursor-glow {
            position: fixed;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(138, 43, 226, 0.15) 0%, rgba(0, 255, 255, 0.05) 40%, rgba(0,0,0,0) 70%);
            border-radius: 50%;
            pointer-events: none;
            z-index: 99999;
            transform: translate(-50%, -50%);
            transition: width 0.2s, height 0.2s;
        }

        .modern-glass {
            background: rgba(20, 20, 30, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    `;
    document.head.appendChild(style);

    const cursorGlow = document.createElement('div');
    cursorGlow.id = 'modern-cursor-glow';
    document.body.appendChild(cursorGlow);

    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        cursorGlow.style.left = mouseX + 'px';
        cursorGlow.style.top = mouseY + 'px';
    });

    document.addEventListener('mousedown', () => {
        cursorGlow.style.width = '300px';
        cursorGlow.style.height = '300px';
    });
    document.addEventListener('mouseup', () => {
        cursorGlow.style.width = '400px';
        cursorGlow.style.height = '400px';
    });

    document.addEventListener('mouseover', (e) => {
        const target = e.target.closest('button, a, input, select, textarea, .card, [class*="btn"], [class*="card"], [class*="item"]');
        if (target && target !== document.body && target !== document.documentElement) {
            target.classList.add('modern-interactive');
            target.classList.add('modern-hover-glow');
        }
    });

    document.addEventListener('mouseout', (e) => {
        const target = e.target.closest('button, a, input, select, textarea, .card, [class*="btn"], [class*="card"], [class*="item"]');
        if (target) {
            target.classList.remove('modern-hover-glow');
        }
    });

    function applyStyles(node) {
        if (node.nodeType === Node.ELEMENT_NODE) {
            if (['SCRIPT', 'STYLE', 'LINK', 'META'].includes(node.tagName) || node.id === 'modern-cursor-glow') return;

            if (['DIV', 'LI', 'ARTICLE', 'SECTION', 'P', 'SPAN'].includes(node.tagName)) {
                node.classList.add('modern-entry-animation');

                if (node.classList && (
                    (node.className.includes && (node.className.includes('card') || node.className.includes('modal') || node.className.includes('popup') || node.className.includes('dialog')))
                )) {
                    node.classList.add('modern-glass');
                }
            }
        }
    }

    // Apply to existing elements
    document.querySelectorAll('div, li, article, section, p, span').forEach(applyStyles);

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(applyStyles);
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();
