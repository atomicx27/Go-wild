(function() {
    // Add ripple effect
    document.addEventListener('click', function(e) {
        let target = e.target.closest('button, a, .card, .clickable');
        if (target) {
            // Only set position relative if it's currently static, but be careful not to break layout
            if (getComputedStyle(target).position === 'static') {
                target.style.position = 'relative';
            }
            target.style.overflow = 'hidden';

            const rect = target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const circle = document.createElement('span');
            circle.classList.add('cyber-ripple');

            const diameter = Math.max(target.clientWidth, target.clientHeight);
            circle.style.width = circle.style.height = `${diameter}px`;
            circle.style.left = `${x - diameter/2}px`;
            circle.style.top = `${y - diameter/2}px`;

            target.appendChild(circle);

            setTimeout(() => {
                circle.remove();
            }, 600);
        }
    });

    // Mouse Trail using requestAnimationFrame and transform
    const particles = [];
    const maxParticles = 10; // Reduced for performance

    for (let i = 0; i < maxParticles; i++) {
        const p = document.createElement('div');
        p.className = 'mouse-trail-particle';
        p.style.opacity = '0';
        document.body.appendChild(p);
        particles.push({
            el: p,
            x: -100,
            y: -100
        });
    }

    let mouseX = -100;
    let mouseY = -100;
    let isMoving = false;
    let animationFrameId = null;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if (!isMoving) {
            isMoving = true;
            animateParticles();
        }
    });

    function animateParticles() {
        let prevX = mouseX;
        let prevY = mouseY;
        let movingCount = 0;

        for (let i = 0; i < maxParticles; i++) {
            const p = particles[i];

            // easing
            p.x += (prevX - p.x) * 0.3;
            p.y += (prevY - p.y) * 0.3;

            if (Math.abs(prevX - p.x) > 0.1 || Math.abs(prevY - p.y) > 0.1) {
                movingCount++;
            }

            p.el.style.transform = `translate(${p.x - 4}px, ${p.y - 4}px) scale(${1 - i/maxParticles})`;
            p.el.style.opacity = 1 - (i / maxParticles);

            prevX = p.x;
            prevY = p.y;
        }

        if (movingCount > 0) {
            animationFrameId = requestAnimationFrame(animateParticles);
        } else {
            isMoving = false;
            cancelAnimationFrame(animationFrameId);
            // Hide particles
            for (let i = 0; i < maxParticles; i++) {
                particles[i].el.style.opacity = '0';
            }
        }
    }
})();
