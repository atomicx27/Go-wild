(function() {
    // Inject Cyberpunk/Neon styles
    const style = document.createElement('style');
    style.innerHTML = `
        /* Cyber UI Enhancements */
        .cyber-glass {
            background: rgba(10, 15, 20, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(0, 255, 255, 0.15) !important;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2) !important;
        }

        .cyber-glow-hover {
            transition: box-shadow 0.3s ease, border-color 0.3s ease, transform 0.3s ease !important;
        }

        .cyber-glow-hover:hover {
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5), inset 0 0 10px rgba(0, 255, 255, 0.3) !important;
            border-color: rgba(0, 255, 255, 0.8) !important;
            transform: translateY(-2px) !important;
            z-index: 10;
        }

        /* Ripple effect container - ensuring it doesn't clip children of the button itself by being an isolated container */
        .ripple-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
            border-radius: inherit;
        }

        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(0, 255, 255, 0.5);
            transform: scale(0);
            animation: cyber-ripple 0.6s ease-out;
            pointer-events: none;
        }

        @keyframes cyber-ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }

        /* Mouse Trail */
        .cyber-trail {
            position: fixed;
            width: 6px;
            height: 6px;
            background: rgba(0, 255, 255, 0.8);
            border-radius: 50%;
            pointer-events: none;
            z-index: 99999;
            box-shadow: 0 0 10px rgba(0, 255, 255, 1), 0 0 20px rgba(0, 255, 255, 0.6);
            mix-blend-mode: screen;
            transform-origin: center;
        }

        /* Glowing text */
        .cyber-text-glow {
            text-shadow: 0 0 8px rgba(0, 255, 255, 0.6), 0 0 15px rgba(0, 255, 255, 0.3) !important;
        }
    `;
    document.head.appendChild(style);

    // Add mouse trail
    const trails = [];
    const trailCount = 15;
    for (let i = 0; i < trailCount; i++) {
        const dot = document.createElement('div');
        dot.className = 'cyber-trail';
        dot.style.opacity = '0';
        document.body.appendChild(dot);
        trails.push({ element: dot, x: -100, y: -100, targetX: -100, targetY: -100 });
    }

    let mouseX = -100;
    let mouseY = -100;

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateTrails() {
        let x = mouseX;
        let y = mouseY;

        trails.forEach((trail, index) => {
            const nextTrail = trails[index + 1] || trails[0];
            trail.x += (x - trail.x) * 0.4;
            trail.y += (y - trail.y) * 0.4;

            trail.element.style.transform = `translate(${trail.x - 3}px, ${trail.y - 3}px) scale(${1 - index/trailCount})`;
            trail.element.style.opacity = (mouseX > -100) ? (1 - index/trailCount) : 0;

            x = trail.x;
            y = trail.y;
        });

        requestAnimationFrame(animateTrails);
    }
    requestAnimationFrame(animateTrails);

    // Apply interactive animations to buttons and cards
    function applyEnhancements() {
        // Buttons
        const buttons = document.querySelectorAll('button, .btn');
        buttons.forEach(btn => {
            if (!btn.classList.contains('cyber-enhanced')) {
                btn.classList.add('cyber-enhanced', 'cyber-glow-hover');

                // Add ripple container
                const rippleContainer = document.createElement('div');
                rippleContainer.className = 'ripple-container';
                btn.appendChild(rippleContainer);

                if (window.getComputedStyle(btn).position === 'static') {
                    btn.style.position = 'relative';
                }

                btn.addEventListener('click', function(e) {
                    const rect = btn.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;

                    const ripple = document.createElement('span');
                    ripple.className = 'ripple';
                    ripple.style.width = ripple.style.height = `${size}px`;
                    ripple.style.left = `${x}px`;
                    ripple.style.top = `${y}px`;

                    rippleContainer.appendChild(ripple);

                    setTimeout(() => {
                        ripple.remove();
                    }, 600);

                    // Web Animations API for click pop
                    const animation = btn.animate([
                        { transform: 'scale(0.95)' },
                        { transform: 'scale(1.02)' },
                        { transform: 'scale(1)' }
                    ], {
                        duration: 300,
                        easing: 'ease-out',
                        composite: 'add'
                    });
                    animation.onfinish = () => animation.cancel();
                });
            }
        });

        // Cards / Panels
        // Targeting elements that look like cards or containers but not the body or main layouts
        const cards = document.querySelectorAll('.card, .panel, .agent-card, div[class*="bg-gray-800"]:not(body), div[class*="bg-gray-900"]:not(body), div[class*="bg-slate-800"]:not(body), div[class*="bg-slate-900"]:not(body)');
        cards.forEach(card => {
            // Avoid applying to too large containers like full screen wrappers
            if (!card.classList.contains('cyber-enhanced') && card.tagName !== 'BODY') {
                const rect = card.getBoundingClientRect();
                if (rect.width < window.innerWidth * 0.9 && rect.height < window.innerHeight * 0.9) {
                    card.classList.add('cyber-enhanced', 'cyber-glass', 'cyber-glow-hover');
                }
            }
        });

        // Headings
        const headings = document.querySelectorAll('h1, h2, h3');
        headings.forEach(h => {
            if (!h.classList.contains('cyber-text-glow')) {
                h.classList.add('cyber-text-glow');
            }
        });
    }

    // Observe DOM for dynamic elements
    const observer = new MutationObserver((mutations) => {
        let shouldEnhance = false;
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length > 0) {
                // simple check to see if element nodes were added
                for(let node of mutation.addedNodes) {
                    if (node.nodeType === 1) {
                        shouldEnhance = true;
                        break;
                    }
                }
            }
        });
        if (shouldEnhance) {
            applyEnhancements();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Initial application
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyEnhancements);
    } else {
        applyEnhancements();
    }
    // Also run after a short delay to catch frameworks rendering
    setTimeout(applyEnhancements, 500);
})();