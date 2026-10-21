// modern-ui.js
(function() {
    document.addEventListener("DOMContentLoaded", () => {
        const interactiveElements = document.querySelectorAll('button, .btn, .card');
        interactiveElements.forEach(el => {
            if (!el.classList.contains('modern-ui-hover-effect')) {
                el.classList.add('modern-ui-hover-effect');
            }

            if (el.tagName.toLowerCase() === 'button' || el.classList.contains('btn')) {
                if (!el.classList.contains('modern-ui-ripple-bound')) {
                    el.classList.add('modern-ui-ripple-bound');
                    el.addEventListener('click', function(e) {
                        let rippleContainer = el.querySelector('.ripple-container');
                        if (!rippleContainer) {
                            rippleContainer = document.createElement('div');
                            rippleContainer.className = 'ripple-container';
                            rippleContainer.style.position = 'absolute';
                            rippleContainer.style.top = '0';
                            rippleContainer.style.left = '0';
                            rippleContainer.style.width = '100%';
                            rippleContainer.style.height = '100%';
                            rippleContainer.style.overflow = 'hidden';
                            rippleContainer.style.borderRadius = window.getComputedStyle(el).borderRadius || '8px';
                            rippleContainer.style.pointerEvents = 'none';
                            if (window.getComputedStyle(el).position === 'static') {
                                el.style.position = 'relative';
                            }
                            el.appendChild(rippleContainer);
                        }

                        const rect = el.getBoundingClientRect();
                        const x = e.clientX - rect.left;
                        const y = e.clientY - rect.top;

                        const ripple = document.createElement('span');
                        ripple.className = 'ripple-effect';
                        ripple.style.left = `${x}px`;
                        ripple.style.top = `${y}px`;

                        const size = Math.max(rect.width, rect.height);
                        ripple.style.width = ripple.style.height = `${size}px`;

                        rippleContainer.appendChild(ripple);

                        const animation = ripple.animate([
                            { transform: 'translate(-50%, -50%) scale(0)', opacity: 1 },
                            { transform: 'translate(-50%, -50%) scale(4)', opacity: 0 }
                        ], {
                            duration: 600,
                            easing: 'ease-out',
                            composite: 'add'
                        });

                        animation.onfinish = () => {
                            animation.cancel();
                            ripple.remove();
                        };
                    });
                }
            }
        });

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    if (!entry.target.classList.contains('modern-ui-animated')) {
                        entry.target.classList.add('modern-ui-animated');
                        entry.target.style.opacity = '1';
                        const animation = entry.target.animate([
                            { opacity: 0, transform: 'translateY(20px)' },
                            { opacity: 1, transform: 'translateY(0)' }
                        ], {
                            duration: 600,
                            easing: 'ease-out',
                            fill: 'forwards',
                            composite: 'add'
                        });
                        animation.onfinish = () => animation.cancel();
                    }
                }
            });
        }, { threshold: 0.05 });

        document.querySelectorAll('section, .card').forEach(section => {
            if (!section.classList.contains('modern-ui-animated-init')) {
                section.classList.add('modern-ui-animated-init');
                section.style.opacity = '0';
                observer.observe(section);
            }
        });

        const trailContainer = document.createElement('div');
        trailContainer.className = 'mouse-trail-container';
        document.body.appendChild(trailContainer);

        let dots = [];
        const numDots = 12;
        for (let i = 0; i < numDots; i++) {
            const dot = document.createElement('div');
            dot.style.position = 'absolute';
            dot.style.width = '8px';
            dot.style.height = '8px';
            dot.style.borderRadius = '50%';
            dot.style.backgroundColor = 'rgba(100, 200, 255, 0.5)';
            dot.style.pointerEvents = 'none';
            dot.style.willChange = 'transform';
            dot.style.transform = 'translate(-20px, -20px)';
            trailContainer.appendChild(dot);
            dots.push({ x: -20, y: -20, el: dot });
        }

        let mouseX = -20, mouseY = -20;
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        function animateDots() {
            let x = mouseX;
            let y = mouseY;

            dots.forEach((dot, index) => {
                const nextDot = dots[index + 1] || dots[0];
                dot.x = x;
                dot.y = y;
                dot.el.style.transform = `translate(${x}px, ${y}px) scale(${1 - index/numDots})`;
                x += (nextDot.x - x) * 0.4;
                y += (nextDot.y - y) * 0.4;
            });

            requestAnimationFrame(animateDots);
        }
        animateDots();
    });
})();
