
// modern-ui.js
document.addEventListener('DOMContentLoaded', () => {
    // Add ripple effect to buttons
    document.querySelectorAll('button, .btn').forEach(btn => {
        if (!btn.classList.contains('modern-ui-processed')) {
            btn.classList.add('modern-ui-processed');
            // Ensure button has position relative for absolute positioning of ripple container
            const style = window.getComputedStyle(btn);
            if (style.position === 'static') {
                btn.style.position = 'relative';
            }

            // Create a dedicated container for the ripple to avoid overflow:hidden on the button itself
            let rippleContainer = btn.querySelector('.ripple-container');
            if (!rippleContainer) {
                rippleContainer = document.createElement('span');
                rippleContainer.className = 'ripple-container';
                btn.appendChild(rippleContainer);
            }

            btn.addEventListener('click', function (e) {
                const circle = document.createElement('span');
                const diameter = Math.max(btn.clientWidth, btn.clientHeight);
                const radius = diameter / 2;

                circle.style.width = circle.style.height = `${diameter}px`;

                // Calculate position relative to the button
                const rect = btn.getBoundingClientRect();
                circle.style.left = `${e.clientX - rect.left - radius}px`;
                circle.style.top = `${e.clientY - rect.top - radius}px`;
                circle.classList.add('ripple');

                // Remove existing ripples to keep DOM clean
                const ripple = rippleContainer.querySelector('.ripple');
                if (ripple) {
                    ripple.remove();
                }

                rippleContainer.appendChild(circle);

                // Clean up animation
                setTimeout(() => {
                    circle.remove();
                }, 600);
            });
        }
    });

    // Add fade-in to main containers or specific elements
    document.querySelectorAll('main, .container, section').forEach(el => {
        if (!el.classList.contains('fade-in')) {
            el.classList.add('fade-in');
        }
    });

    // Optimized Mouse trail
    const trailCount = 5;
    const trails = [];
    for (let i = 0; i < trailCount; i++) {
        const trail = document.createElement('div');
        trail.className = 'mouse-trail';
        document.body.appendChild(trail);
        trails.push({ el: trail, x: 0, y: 0, targetX: 0, targetY: 0 });
    }

    let isMouseMoving = false;
    let isStationary = false;
    let stationaryTimeout;

    document.addEventListener('mousemove', (e) => {
        isMouseMoving = true;
        isStationary = false;
        trails[0].targetX = e.clientX;
        trails[0].targetY = e.clientY;

        clearTimeout(stationaryTimeout);
        stationaryTimeout = setTimeout(() => {
            isStationary = true;
        }, 100);
    });

    function animateTrails() {
        if (isMouseMoving) {
            for (let i = 0; i < trailCount; i++) {
                const t = trails[i];
                if (i > 0) {
                    t.targetX = trails[i - 1].x;
                    t.targetY = trails[i - 1].y;
                }
                t.x += (t.targetX - t.x) * 0.3;
                t.y += (t.targetY - t.y) * 0.3;
                t.el.style.transform = `translate(${t.x}px, ${t.y}px)`;

                if (isStationary) {
                    t.el.style.opacity = 0;
                } else {
                    // Scale down trailing dots
                    const scale = 1 - (i / trailCount);
                    t.el.style.opacity = scale * 0.8;
                    t.el.style.width = `${10 * scale}px`;
                    t.el.style.height = `${10 * scale}px`;
                }
            }
        }
        requestAnimationFrame(animateTrails);
    }
    animateTrails();

});
