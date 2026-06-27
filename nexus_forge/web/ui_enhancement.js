(function() {
    // Mouse trail effect
    const numParticles = 20;
    const particles = [];

    for (let i = 0; i < numParticles; i++) {
        const p = document.createElement('div');
        p.className = 'global-mouse-trail-particle';
        document.body.appendChild(p);
        particles.push({el: p, x: 0, y: 0, targetX: 0, targetY: 0});
    }

    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animate() {
        let x = mouseX;
        let y = mouseY;
        particles.forEach((p, index) => {
            p.x += (x - p.x) * 0.3;
            p.y += (y - p.y) * 0.3;
            p.el.style.transform = `translate(${p.x}px, ${p.y}px) scale(${1 - index/numParticles})`;
            x = p.x;
            y = p.y;
        });
        requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);

    // Ripple effect for interactive elements
    document.addEventListener('click', (e) => {
        const target = e.target.closest('button, .btn, a, input[type="submit"]');
        if (target) {
            const rect = target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const rippleContainer = document.createElement('div');
            rippleContainer.className = 'global-ripple-container';

            const ripple = document.createElement('div');
            ripple.className = 'global-ripple';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            rippleContainer.appendChild(ripple);

            if(window.getComputedStyle(target).position === 'static') {
                target.style.position = 'relative';
            }
            target.appendChild(rippleContainer);

            const animation = ripple.animate([
                { transform: 'scale(0) translate(-50%, -50%)', opacity: 0.8 },
                { transform: 'scale(20) translate(-50%, -50%)', opacity: 0 }
            ], {
                duration: 600,
                easing: 'ease-out',
                composite: 'add'
            });

            animation.onfinish = () => {
                animation.cancel();
                rippleContainer.remove();
            };
        }
    });

    // Add generic interactive classes for styling
    document.querySelectorAll('button, .btn, input[type="submit"]').forEach(el => {
        if (!el.classList.contains('global-interactive-el')) {
            el.classList.add('global-interactive-el');
        }
    });

})();
