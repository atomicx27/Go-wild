(function() {
    // Subtle UI Enhancements Injection

    // 1. Add subtle interactive class to buttons and links safely
    const applySubtleEnhancements = () => {
        document.querySelectorAll('button, .btn, a.btn').forEach(el => {
            if (!el.classList.contains('enhanced-interactive')) {
                el.classList.add('enhanced-interactive');
            }
        });
    };

    // 2. Add Ripple effect listener
    document.addEventListener('click', function(e) {
        const target = e.target.closest('button, .btn, .ripple-wrapper');
        if (!target) return;

        // We ensure the target has position relative or absolute to contain the absolute ripple
        const style = window.getComputedStyle(target);
        if (style.position === 'static') {
             target.style.position = 'relative';
        }

        const rect = target.getBoundingClientRect();
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';

        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${e.clientY - rect.top - size / 2}px`;

        target.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    });

    // 3. Mouse Trail Effect - Properly initialized and looped
    const particles = [];
    const numParticles = 10;
    for(let i=0; i<numParticles; i++) {
        const p = document.createElement('div');
        p.className = 'mouse-trail-particle';
        p.style.display = 'none';
        document.body.appendChild(p);
        particles.push({ el: p, x: 0, y: 0 });
    }

    let mouseX = 0, mouseY = 0;
    let isMouseMoving = false;
    let trailTimeout;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        isMouseMoving = true;
        clearTimeout(trailTimeout);
        trailTimeout = setTimeout(() => isMouseMoving = false, 150);
    });

    let frame = 0;
    function animate() {
        if(isMouseMoving || frame % 2 === 0) {
            let px = mouseX;
            let py = mouseY;

            particles.forEach((p, i) => {
                p.x += (px - p.x) * 0.4;
                p.y += (py - p.y) * 0.4;

                if (isMouseMoving) {
                    p.el.style.display = 'block';
                } else if (Math.abs(p.x - mouseX) < 1 && Math.abs(p.y - mouseY) < 1) {
                    p.el.style.display = 'none'; // hide when stopped
                }

                p.el.style.transform = `translate(${p.x}px, ${p.y}px) scale(${1 - i/numParticles})`;

                px = p.x;
                py = p.y;
            });
        }
        frame++;
        requestAnimationFrame(animate);
    }

    // Observe DOM for newly added buttons
    const observer = new MutationObserver((mutations) => {
        let shouldApply = false;
        mutations.forEach(m => {
            if (m.addedNodes.length > 0) shouldApply = true;
        });
        if (shouldApply) applySubtleEnhancements();
    });

    // Start observation once body is available
    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
        applySubtleEnhancements();
        animate();
    } else {
        document.addEventListener('DOMContentLoaded', () => {
            observer.observe(document.body, { childList: true, subtree: true });
            applySubtleEnhancements();
            animate();
        });
    }

})();
