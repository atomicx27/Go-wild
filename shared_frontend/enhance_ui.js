
(function() {
    // 1. Mouse Trail Animation
    const trailDots = [];
    const numDots = 15;

    for (let i = 0; i < numDots; i++) {
        const dot = document.createElement('div');
        dot.className = 'mouse-trail-dot';
        document.body.appendChild(dot);
        trailDots.push({
            element: dot,
            x: 0, y: 0
        });
    }

    let mouseX = 0;
    let mouseY = 0;
    let isMouseMoving = false;
    let mouseMoveTimeout;
    let animationFrameId = null;

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        isMouseMoving = true;

        clearTimeout(mouseMoveTimeout);
        mouseMoveTimeout = setTimeout(() => {
            isMouseMoving = false;
        }, 100);

        if (!animationFrameId) {
            animateTrail();
        }
    });

    function animateTrail() {
        let x = mouseX;
        let y = mouseY;
        let anyVisible = false;

        trailDots.forEach((dot, index) => {
            dot.x += (x - dot.x) * 0.3;
            dot.y += (y - dot.y) * 0.3;

            dot.element.style.transform = `translate(${dot.x}px, ${dot.y}px) scale(${(numDots - index) / numDots})`;

            if (isMouseMoving) {
                dot.element.style.opacity = (1 - (index / numDots)) * 0.5;
                anyVisible = true;
            } else {
                const currentOpacity = parseFloat(dot.element.style.opacity) || 0;
                if (currentOpacity > 0.01) {
                    dot.element.style.opacity = currentOpacity - 0.02;
                    anyVisible = true;
                } else {
                    dot.element.style.opacity = 0;
                }
            }

            x = dot.x;
            y = dot.y;
        });

        if (anyVisible) {
            animationFrameId = requestAnimationFrame(animateTrail);
        } else {
            animationFrameId = null;
        }
    }

    // 2. Enhance Buttons and Inputs
    function enhanceButton(btn) {
        if (btn.dataset.enhanced) return;
        btn.dataset.enhanced = 'true';

        if (!btn.classList.contains('enhanced-hover-target')) {
            btn.classList.add('enhanced-hover-target');
        }

        btn.addEventListener('mousedown', () => {
            // Ripple effect using box-shadow to avoid overflow clipping issues
            const anim = btn.animate([
                { transform: 'scale(0.95)', boxShadow: '0 0 0 0 rgba(139, 92, 246, 0.4)' },
                { transform: 'scale(0.95)', boxShadow: '0 0 0 10px rgba(139, 92, 246, 0)' }
            ], {
                duration: 300,
                fill: 'forwards',
                easing: 'ease-out',
                composite: 'add'
            });

            const upHandler = () => {
                anim.onfinish = null;
                btn.animate([
                    { transform: 'scale(1)' }
                ], {
                    duration: 150,
                    easing: 'ease-out',
                    composite: 'add'
                });
                anim.cancel();

                btn.removeEventListener('mouseup', upHandler);
                btn.removeEventListener('mouseleave', upHandler);
            };

            btn.addEventListener('mouseup', upHandler);
            btn.addEventListener('mouseleave', upHandler);
        });
    }

    function applyEnhancements() {
        document.querySelectorAll('button, .btn, a.button').forEach(enhanceButton);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyEnhancements);
    } else {
        applyEnhancements();
    }

    // Enhance dynamically added buttons
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    if (node.matches && node.matches('button, .btn, a.button')) {
                        enhanceButton(node);
                    }
                    node.querySelectorAll('button, .btn, a.button').forEach(enhanceButton);
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Fade-in for main containers
    document.addEventListener('DOMContentLoaded', () => {
        const containers = document.querySelectorAll('.container, main, .app-container');
        containers.forEach(container => {
            container.animate([
                { opacity: 0, transform: 'translateY(10px)' },
                { opacity: 1, transform: 'translateY(0)' }
            ], {
                duration: 800,
                easing: 'cubic-bezier(0.25, 1, 0.5, 1)',
                fill: 'both'
            });
        });
    });
})();
