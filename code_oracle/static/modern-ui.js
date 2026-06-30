// modern-ui.js
document.addEventListener('DOMContentLoaded', () => {
    const interactiveElements = document.querySelectorAll('button, .btn, .card');
    interactiveElements.forEach(el => {
        el.classList.add('modern-hover');

        let rippleContainer = el.querySelector('.ripple-container');
        if (!rippleContainer) {
            rippleContainer = document.createElement('div');
            rippleContainer.className = 'ripple-container';
            rippleContainer.style.position = 'absolute';
            rippleContainer.style.top = '0';
            rippleContainer.style.left = '0';
            rippleContainer.style.width = '100%';
            rippleContainer.style.height = '100%';
            rippleContainer.style.pointerEvents = 'none';
            rippleContainer.style.borderRadius = window.getComputedStyle(el).borderRadius || 'inherit';
            rippleContainer.style.overflow = 'hidden';

            const position = window.getComputedStyle(el).position;
            if (position === 'static' || !position) {
                el.style.position = 'relative';
            }
            el.appendChild(rippleContainer);
        }

        el.addEventListener('click', function (e) {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const circle = document.createElement('span');
            const diameter = Math.max(el.clientWidth, el.clientHeight);
            const radius = diameter / 2;

            circle.style.width = `${diameter}px`;
            circle.style.height = `${diameter}px`;
            circle.style.left = `${x - radius}px`;
            circle.style.top = `${y - radius}px`;
            circle.style.position = 'absolute';
            circle.style.borderRadius = '50%';
            circle.style.backgroundColor = 'rgba(255, 255, 255, 0.4)';
            circle.style.pointerEvents = 'none';

            rippleContainer.appendChild(circle);

            const animation = circle.animate([
                { transform: 'scale(0)', opacity: 1 },
                { transform: 'scale(4)', opacity: 0 }
            ], {
                duration: 600,
                easing: 'linear',
                composite: 'add'
            });

            animation.onfinish = () => {
                animation.cancel();
                circle.remove();
            };
        });
    });

    const trailCount = 10;
    const trails = [];
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;

    for (let i = 0; i < trailCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'mouse-trail-particle';
        document.body.appendChild(particle);
        trails.push({ element: particle, x: mouseX, y: mouseY });
    }

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateTrails() {
        let x = mouseX;
        let y = mouseY;

        trails.forEach((trail, index) => {

            trail.x += (x - trail.x) * 0.3;
            trail.y += (y - trail.y) * 0.3;

            trail.element.style.transform = `translate(${trail.x}px, ${trail.y}px) scale(${1 - index/trailCount})`;

            x = trail.x;
            y = trail.y;
        });

        requestAnimationFrame(animateTrails);
    }

    animateTrails();
});
