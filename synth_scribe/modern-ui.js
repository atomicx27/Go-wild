/* modern-ui.js */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Mouse trail effect using requestAnimationFrame and CSS transform
    const trailElements = [];
    const trailLength = 10;

    for (let i = 0; i < trailLength; i++) {
        const div = document.createElement('div');
        div.className = 'mouse-trail';
        document.body.appendChild(div);
        trailElements.push({
            el: div,
            x: 0,
            y: 0
        });
    }

    let mouseX = 0;
    let mouseY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateTrail() {
        let x = mouseX;
        let y = mouseY;

        trailElements.forEach((trail, index) => {
            const next = trailElements[index + 1] || trailElements[0];

            trail.x = x;
            trail.y = y;

            trail.el.style.transform = `translate(${x}px, ${y}px) scale(${(trailLength - index) / trailLength})`;
            trail.el.style.opacity = (trailLength - index) / trailLength;

            x += (next.x - x) * 0.4;
            y += (next.y - y) * 0.4;
        });

        requestAnimationFrame(animateTrail);
    }
    animateTrail();

    // 2. Ripple effect on buttons
    const buttons = document.querySelectorAll('button, .btn');
    buttons.forEach(btn => {
        // Prevent duplicate processing
        if (btn.classList.contains('modern-ui-processed')) return;
        btn.classList.add('modern-ui-processed');

        btn.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.className = 'ripple-container';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            // Size of ripple
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = `${size}px`;
            ripple.style.height = `${size}px`;

            // Adjust to center the ripple origin
            ripple.style.marginLeft = `-${size/2}px`;
            ripple.style.marginTop = `-${size/2}px`;

            this.appendChild(ripple);

            // Cleanup
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });

        // 3. Web Animations API for entrance animation
        if (btn.animate) {
            const animation = btn.animate([
                { opacity: 0, transform: 'scale(0.9)' },
                { opacity: 1, transform: 'scale(1)' }
            ], {
                duration: 500,
                easing: 'ease-out',
                composite: 'add'
            });

            animation.onfinish = () => animation.cancel();
        }
    });
});
