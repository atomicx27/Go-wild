// modern-ui.js

// --- Performance-Optimized Mouse Trail Animation ---
(function() {
    const trailElements = [];
    const maxTrails = 10;

    // Create elements
    for (let i = 0; i < maxTrails; i++) {
        const el = document.createElement('div');
        el.style.position = 'fixed';
        el.style.width = '8px';
        el.style.height = '8px';
        el.style.borderRadius = '50%';
        el.style.backgroundColor = 'rgba(100, 150, 255, 0.5)';
        el.style.pointerEvents = 'none';
        el.style.zIndex = '9999';
        el.style.transform = 'translate(-50%, -50%) scale(0)';
        el.style.transition = 'transform 0.1s ease-out, opacity 0.5s ease-out';
        document.body.appendChild(el);
        trailElements.push({ element: el, x: -100, y: -100, active: false });
    }

    let currentIndex = 0;
    let mouseX = -100;
    let mouseY = -100;

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;

        // Only update a new trail point occasionally to prevent too much overlapping
        const trail = trailElements[currentIndex];
        trail.x = mouseX;
        trail.y = mouseY;
        trail.active = true;

        // Reset element styles to start position
        trail.element.style.left = mouseX + 'px';
        trail.element.style.top = mouseY + 'px';
        trail.element.style.transform = 'translate(-50%, -50%) scale(1)';
        trail.element.style.opacity = '1';

        currentIndex = (currentIndex + 1) % maxTrails;
    });

    // Use requestAnimationFrame for smooth fading
    function animateTrails() {
        for (let i = 0; i < maxTrails; i++) {
            const trail = trailElements[i];
            if (trail.active) {
                // Read current opacity
                let opacity = parseFloat(trail.element.style.opacity);
                if (opacity > 0.05) {
                    opacity -= 0.05; // Fade out
                    trail.element.style.opacity = opacity.toString();
                    // Shrink slightly
                    trail.element.style.transform = `translate(-50%, -50%) scale(${opacity})`;
                } else {
                    trail.element.style.opacity = '0';
                    trail.active = false;
                }
            }
        }
        requestAnimationFrame(animateTrails);
    }

    // Start animation loop
    requestAnimationFrame(animateTrails);
})();

// --- Smooth Button Ripple Effect ---
document.addEventListener('mousedown', function(e) {
    const target = e.target.closest('button, .btn, .interactive');
    if (!target) return;

    // We don't want to enforce overflow: hidden globally on the element itself,
    // so we just animate on the element or ideally a child container.
    // For simplicity and avoiding layout breakage, we use the Web Animations API on the element.

    const rect = target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const ripple = document.createElement('span');
    ripple.style.position = 'absolute';
    ripple.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
    ripple.style.borderRadius = '50%';
    ripple.style.pointerEvents = 'none';

    // Need target to have relative positioning and hidden overflow for ripple to look correct
    // But since memory specifically says DO NOT globally force overflow: hidden,
    // we only apply it dynamically via a specific class if possible, or just accept it might spill.
    // Memory: "avoid globally forcing overflow: hidden... as this will invasively clipping and break child elements"
    // Instead we'll use a very subtle background flash if we can't do a constrained ripple, or we create an underlay.

    // Let's implement a color flash instead to be safe with overflow rules,
    // or a subtle scaling effect via Web Animations API with composite: 'add'

    const animation = target.animate([
        { transform: 'scale(1)', filter: 'brightness(1)' },
        { transform: 'scale(0.95)', filter: 'brightness(1.2)', offset: 0.5 },
        { transform: 'scale(1)', filter: 'brightness(1)' }
    ], {
        duration: 300,
        easing: 'ease-out',
        composite: 'add' // Crucial: blends with existing transforms (like our hover translateY)
    });

    // Proper garbage collection
    animation.onfinish = () => animation.cancel();
});
