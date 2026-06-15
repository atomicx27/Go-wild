(function() {
    // 1. Inject global CSS for hover states and ripples to avoid JS animation leaks/bugs
    const style = document.createElement('style');
    style.textContent = `
        .global-hover-enhanced {
            transition: box-shadow 0.2s ease-out, transform 0.2s ease-out, filter 0.2s ease-out !important;
        }
        .global-hover-enhanced:hover {
            filter: brightness(1.2) !important;
            transform: scale(1.02) !important;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.5), 0 0 20px rgba(0, 255, 255, 0.3) !important;
        }
        .global-hover-enhanced:active {
            transform: scale(0.95) !important;
        }

        /* Ripple container and effect */
        .ripple-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            pointer-events: none;
            border-radius: inherit;
        }
        .ripple-effect {
            position: absolute;
            background: rgba(0, 255, 255, 0.4);
            border-radius: 50%;
            pointer-events: none;
            width: 10px;
            height: 10px;
            transform: translate(-50%, -50%) scale(1);
            animation: global-ripple-anim 0.6s ease-out forwards;
        }
        @keyframes global-ripple-anim {
            to {
                transform: translate(-50%, -50%) scale(40);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Apply hover class to interactive elements
    function applyHoverClass(element) {
        if (!element.classList.contains('global-hover-enhanced')) {
            element.classList.add('global-hover-enhanced');

            // Ensure element is positioned for ripple container
            const computedStyle = window.getComputedStyle(element);
            if (computedStyle.position === 'static') {
                element.style.position = 'relative';
            }
        }
    }

    // 2. Ripple Effect on Click
    document.addEventListener('mousedown', function(e) {
        const target = e.target.closest('button, .cyber-btn, .btn');
        if (target) {
            applyHoverClass(target); // Ensure class is present

            let rippleContainer = target.querySelector('.ripple-container');
            if (!rippleContainer) {
                rippleContainer = document.createElement('div');
                rippleContainer.className = 'ripple-container';
                target.appendChild(rippleContainer);
            }

            const rect = target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.className = 'ripple-effect';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            rippleContainer.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        }
    });

    // 3. MutationObserver for dynamically added elements (Entrance animations and hover class)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        // Apply entrance animation
                        if (node.matches && node.matches('.card, .panel, .log-entry, .message, li, tr, .task-item')) {
                            // Ensure element starts hidden to prevent flash before animation
                            const originalOpacity = window.getComputedStyle(node).opacity || '1';
                            node.animate([
                                { opacity: 0, transform: 'translateY(10px) scale(0.98)' },
                                { opacity: originalOpacity, transform: 'translateY(0) scale(1)' }
                            ], {
                                duration: 400,
                                easing: 'ease-out',
                                fill: 'forwards'
                            });
                        }

                        // Apply hover class to new interactive elements
                        if (node.matches && node.matches('button, a, input[type="submit"], input[type="button"], .card, .panel, .cyber-btn, .btn, .item')) {
                            applyHoverClass(node);
                        }

                        // Also check children of added nodes
                        const interactives = node.querySelectorAll('button, a, input[type="submit"], input[type="button"], .card, .panel, .cyber-btn, .btn, .item');
                        interactives.forEach(applyHoverClass);
                    }
                });
            }
        });
    });

    window.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, { childList: true, subtree: true });

        // Apply hover class to existing elements
        const interactives = document.querySelectorAll('button, a, input[type="submit"], input[type="button"], .card, .panel, .cyber-btn, .btn, .item');
        interactives.forEach(applyHoverClass);

        // 4. Initial load animations for existing structural elements
        const elements = document.querySelectorAll('.card, .panel, header, main, section');
        elements.forEach((el, index) => {
            el.animate([
                { opacity: 0, transform: 'translateY(20px)' },
                { opacity: 1, transform: 'translateY(0)' }
            ], {
                duration: 600,
                delay: index * 50,
                easing: 'ease-out',
                fill: 'forwards'
            });
        });

        // 5. Subtle mouse trail effect using translate
        const glow = document.createElement('div');
        glow.style.position = 'fixed';
        glow.style.top = '0';
        glow.style.left = '0';
        glow.style.width = '300px';
        glow.style.height = '300px';
        glow.style.borderRadius = '50%';
        glow.style.background = 'radial-gradient(circle, rgba(0, 255, 255, 0.05) 0%, rgba(0, 0, 0, 0) 70%)';
        glow.style.pointerEvents = 'none';
        glow.style.zIndex = '9999';
        // Initialize off-screen
        glow.style.transform = 'translate(-1000px, -1000px)';
        document.body.appendChild(glow);

        let ticking = false;
        let mouseX = -1000;
        let mouseY = -1000;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    glow.style.transform = `translate(${mouseX - 150}px, ${mouseY - 150}px)`;
                    ticking = false;
                });
                ticking = true;
            }
        });
    });

})();
