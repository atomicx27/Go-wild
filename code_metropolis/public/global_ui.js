
/* global_ui.js */
(function() {
    // Pulse animation on click
    document.addEventListener('click', function(e) {
        if (e.target.tagName && e.target.tagName.toLowerCase() === 'button' || e.target.closest('button')) {
            const btn = e.target.closest('button') || e.target;
            const rect = btn.getBoundingClientRect();

            // Web Animations API
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const circle = document.createElement('span');
            circle.classList.add('ripple-container');
            circle.style.left = `${x}px`;
            circle.style.top = `${y}px`;

            if (getComputedStyle(btn).position === 'static') {
                btn.style.position = 'relative';
            }

            btn.appendChild(circle);

            const animation = circle.animate([
                { transform: 'scale(0)', opacity: 1 },
                { transform: 'scale(4)', opacity: 0 }
            ], {
                duration: 600,
                easing: 'linear',
                composite: 'add'
            });

            animation.onfinish = () => {
                circle.remove();
                animation.cancel();
            };
        }
    });

    // Mouse Trail
    let particles = [];
    let mouseX = 0;
    let mouseY = 0;

    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;

        const particle = document.createElement('div');
        particle.className = 'mouse-trail-particle';
        particle.style.left = `${mouseX - 4}px`;
        particle.style.top = `${mouseY - 4}px`;
        document.body.appendChild(particle);
        particles.push(particle);

        setTimeout(() => {
            particle.style.opacity = '0';
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
                particles = particles.filter(p => p !== particle);
            }, 400);
        }, 50);
    });

    // MutationObserver for adding hover effects to buttons or specific elements
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        if (node.tagName && node.tagName.toLowerCase() === 'button') {
                            node.classList.add('ui-hover-effect');
                        }
                        const buttons = node.querySelectorAll ? node.querySelectorAll('button') : [];
                        buttons.forEach(btn => btn.classList.add('ui-hover-effect'));
                    }
                });
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Initial setup for existing buttons
    document.querySelectorAll('button').forEach(btn => btn.classList.add('ui-hover-effect'));
})();
