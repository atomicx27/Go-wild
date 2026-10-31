(function() {
    // Prevent duplicate initializations
    if (window._uiEnhancementsInitialized) return;
    window._uiEnhancementsInitialized = true;

    // Wait for DOM to load
    document.addEventListener('DOMContentLoaded', () => {
        // Add fade-in animation to main containers if they exist
        const containers = document.querySelectorAll('.container, main, #app, .app-container, .wrapper');
        containers.forEach(container => {
            if (!container.classList.contains('animate-fade-in')) {
                container.classList.add('animate-fade-in');
            }
        });

        // Initialize Mouse Trail
        let lastMouseParticleTime = 0;
        document.addEventListener('mousemove', (e) => {
            const now = Date.now();
            if (now - lastMouseParticleTime > 50) { // Limit particle creation rate
                createMouseParticle(e.clientX, e.clientY);
                lastMouseParticleTime = now;
            }
        });

        // Event delegation for click ripple effect on buttons
        document.body.addEventListener('click', (e) => {
            // Check if clicked element or its parent is a button
            const btn = e.target.closest('button, .btn, input[type="button"], input[type="submit"]');

            // Create ripple at click position
            createClickRipple(e.clientX, e.clientY);

            if (btn) {
                // Optional: Additional button-specific click animation
                if (typeof btn.animate === 'function') {
                    const animation = btn.animate([
                        { transform: 'scale(0.95)' },
                        { transform: 'scale(1)' }
                    ], {
                        duration: 150,
                        easing: 'cubic-bezier(0.25, 0.8, 0.25, 1)',
                        composite: 'add'
                    });

                    animation.onfinish = () => animation.cancel();
                }
            }
        });
    });

    function createMouseParticle(x, y) {
        const particle = document.createElement('div');
        particle.className = 'mouse-particle';
        particle.style.left = `${x}px`;
        particle.style.top = `${y}px`;
        document.body.appendChild(particle);

        const animation = particle.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 0.8 },
            { transform: `translate(${(Math.random() - 0.5) * 20}px, ${(Math.random() - 0.5) * 20 + 20}px) scale(0)`, opacity: 0 }
        ], {
            duration: 800 + Math.random() * 400,
            easing: 'cubic-bezier(0.25, 0.8, 0.25, 1)'
        });

        animation.onfinish = () => {
            particle.remove();
        };
    }

    function createClickRipple(x, y) {
        const ripple = document.createElement('div');
        ripple.className = 'click-ripple';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        document.body.appendChild(ripple);

        const animation = ripple.animate([
            { transform: 'translate(-50%, -50%) scale(0)', opacity: 1, borderWidth: '3px' },
            { transform: 'translate(-50%, -50%) scale(3)', opacity: 0, borderWidth: '0px' }
        ], {
            duration: 400,
            easing: 'ease-out'
        });

        animation.onfinish = () => {
            ripple.remove();
        };
    }
})();
