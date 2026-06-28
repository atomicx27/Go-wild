(function() {
    // Inject global styles
    const style = document.createElement('style');
    style.textContent = `
        .ui-enhanced-hover {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .ui-enhanced-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .mouse-trail-particle {
            position: fixed;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: rgba(139, 92, 246, 0.6);
            pointer-events: none;
            z-index: 9999;
            will-change: transform, opacity;
            left: 0;
            top: 0;
        }
    `;
    document.head.appendChild(style);

    // Apply hover class to buttons and links (best effort without breaking existing)
    document.querySelectorAll('button, .btn, a.button').forEach(el => {
        el.classList.add('ui-enhanced-hover');
    });

    // Mouse Trail Effect using requestAnimationFrame and transform
    const trailCount = 10;
    const trails = [];
    for (let i = 0; i < trailCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'mouse-trail-particle';
        particle.style.opacity = '0';
        document.body.appendChild(particle);
        trails.push({ el: particle, x: -100, y: -100, targetX: -100, targetY: -100, active: false });
    }

    let mouseX = -100;
    let mouseY = -100;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if (!trails[0].active) {
            trails.forEach(t => t.active = true);
        }
    });

    function animateTrails() {
        if (trails[0].active) {
            let nextX = mouseX;
            let nextY = mouseY;

            trails.forEach((trail, index) => {
                const dx = nextX - trail.x;
                const dy = nextY - trail.y;

                trail.x += dx * 0.2;
                trail.y += dy * 0.2;

                trail.el.style.transform = `translate(${trail.x}px, ${trail.y}px) scale(${1 - index/trailCount})`;
                trail.el.style.opacity = Math.max(0, 1 - index/trailCount);

                nextX = trail.x;
                nextY = trail.y;
            });
        }
        requestAnimationFrame(animateTrails);
    }
    requestAnimationFrame(animateTrails);

    // Click Animations using Web Animations API
    document.addEventListener('click', (e) => {
        const target = e.target.closest('button, .btn, .card, a');
        if (target) {
            const animation = target.animate([
                { transform: 'scale(1)' },
                { transform: 'scale(0.95)' },
                { transform: 'scale(1)' }
            ], {
                duration: 200,
                easing: 'ease-out',
                composite: 'add'
            });
            animation.onfinish = () => animation.cancel();
        }
    });
})();
