// modern-ui.js

document.addEventListener('DOMContentLoaded', () => {
    // --- Mouse Trail Effect ---
    const trailCount = 15;
    const trails = [];
    let mouseX = 0;
    let mouseY = 0;

    for (let i = 0; i < trailCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'mouse-trail-particle';
        document.body.appendChild(particle);
        trails.push({
            element: particle,
            x: 0,
            y: 0
        });
    }

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateTrails() {
        let x = mouseX;
        let y = mouseY;

        trails.forEach((trail, index) => {
            const nextTrail = trails[index + 1] || trails[0];

            trail.x += (x - trail.x) * 0.3;
            trail.y += (y - trail.y) * 0.3;

            trail.element.style.left = `${trail.x}px`;
            trail.element.style.top = `${trail.y}px`;

            // Fade out based on index
            trail.element.style.opacity = 1 - (index / trailCount);
            // Shrink based on index
            const scale = 1 - (index / trailCount);
            trail.element.style.transform = `translate(-50%, -50%) scale(${scale})`;

            x = trail.x;
            y = trail.y;
        });

        requestAnimationFrame(animateTrails);
    }

    // Start animation if browser supports requestAnimationFrame
    if (window.requestAnimationFrame) {
        animateTrails();
    }

    // --- Modern Ripple Effect ---
    function createRipple(event) {
        const button = event.currentTarget;

        // Ensure the button has a ripple container
        let rippleContainer = button.querySelector('.ripple-container');
        if (!rippleContainer) {
            rippleContainer = document.createElement('div');
            rippleContainer.className = 'ripple-container';
            button.appendChild(rippleContainer);

            // Make sure button has position relative for container to work
            const computedStyle = window.getComputedStyle(button);
            if (computedStyle.position === 'static') {
                button.style.position = 'relative';
            }
        }

        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        const rect = button.getBoundingClientRect();

        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - rect.left - radius}px`;
        circle.style.top = `${event.clientY - rect.top - radius}px`;
        circle.style.position = 'absolute';
        circle.style.borderRadius = '50%';
        circle.style.backgroundColor = 'rgba(255, 255, 255, 0.4)';
        circle.style.transform = 'scale(0)';
        circle.style.pointerEvents = 'none';

        rippleContainer.appendChild(circle);

        // Use Web Animations API
        const animation = circle.animate([
            { transform: 'scale(0)', opacity: 1 },
            { transform: 'scale(2.5)', opacity: 0 }
        ], {
            duration: 600,
            easing: 'ease-out',
            composite: 'add'
        });

        animation.onfinish = () => {
            circle.remove();
        };
    }

    // Apply ripple to buttons and common interactive elements
    const interactiveElements = document.querySelectorAll('button, .btn, .interactive-btn, [role="button"]');
    interactiveElements.forEach(el => {
        // Prevent duplicate attachments if script runs multiple times
        if (!el.classList.contains('ripple-attached')) {
            el.addEventListener('click', createRipple);
            el.classList.add('ripple-attached');
            el.classList.add('hover-glow'); // add subtle hover effect
        }
    });
});
