/* cyber_enhancements.js */
(function() {
    document.addEventListener('DOMContentLoaded', () => {
        const buttons = document.querySelectorAll('button, .btn, a.button');
        buttons.forEach(btn => {
            const style = window.getComputedStyle(btn);
            if (style.position === 'static') {
                btn.style.position = 'relative';
            }
            btn.classList.add('cyber-hover-glow');

            let rippleContainer = btn.querySelector('.cyber-ripple-container');
            if (!rippleContainer) {
                rippleContainer = document.createElement('div');
                rippleContainer.className = 'cyber-ripple-container';
                btn.appendChild(rippleContainer);
            }

            btn.addEventListener('mousedown', function(e) {
                const rect = btn.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                const ripple = document.createElement('span');
                ripple.className = 'cyber-ripple';
                ripple.style.width = ripple.style.height = `${size}px`;
                ripple.style.left = `${x}px`;
                ripple.style.top = `${y}px`;

                rippleContainer.appendChild(ripple);

                ripple.addEventListener('animationend', () => {
                    ripple.remove();
                });
            });
        });

        const trailElements = [];
        const numTrails = 12;
        for (let i = 0; i < numTrails; i++) {
            const dot = document.createElement('div');
            dot.className = 'cyber-mouse-trail';
            const hue = (i * 30) % 360;
            dot.style.background = `hsl(${hue}, 100%, 70%)`;
            dot.style.boxShadow = `0 0 10px hsl(${hue}, 100%, 70%)`;
            dot.style.opacity = 0;
            document.body.appendChild(dot);
            trailElements.push({ element: dot, x: -100, y: -100 });
        }

        let targetX = -100, targetY = -100;
        let isMoving = false;

        document.addEventListener('mousemove', (e) => {
            targetX = e.clientX;
            targetY = e.clientY;
            if (!isMoving) {
                isMoving = true;
                requestAnimationFrame(updateTrail);
            }
        });

        function updateTrail() {
            let dx = targetX - trailElements[0].x;
            let dy = targetY - trailElements[0].y;

            trailElements[0].x += dx * 0.5;
            trailElements[0].y += dy * 0.5;

            if (Math.abs(dx) > 0.1 || Math.abs(dy) > 0.1) {
                trailElements[0].element.style.opacity = 1;
                trailElements[0].element.style.transform = `translate(${trailElements[0].x}px, ${trailElements[0].y}px)`;
            } else {
                trailElements[0].element.style.opacity = 0;
            }

            let allIdle = true;

            for (let i = 1; i < numTrails; i++) {
                let dx = trailElements[i-1].x - trailElements[i].x;
                let dy = trailElements[i-1].y - trailElements[i].y;
                trailElements[i].x += dx * 0.4;
                trailElements[i].y += dy * 0.4;

                if (Math.abs(dx) > 0.1 || Math.abs(dy) > 0.1) {
                    allIdle = false;
                    const scale = 1 - (i / numTrails);
                    trailElements[i].element.style.opacity = scale;
                    trailElements[i].element.style.transform = `translate(${trailElements[i].x}px, ${trailElements[i].y}px) scale(${scale})`;
                } else {
                    trailElements[i].element.style.opacity = 0;
                }
            }

            if (allIdle && Math.abs(targetX - trailElements[0].x) < 0.1) {
                isMoving = false;
            } else {
                requestAnimationFrame(updateTrail);
            }
        }

        const cards = document.querySelectorAll('.card, .agent-card, input, textarea, .message, .panel');
        cards.forEach((card, index) => {
            const animation = card.animate([
                { opacity: 0, transform: 'translateY(20px)' },
                { opacity: 1, transform: 'translateY(0)' }
            ], {
                duration: 600,
                delay: (index % 10) * 50,
                easing: 'ease-out',
                composite: 'add'
            });

            animation.onfinish = () => {
                animation.cancel();
            };
        });

    });
})();
