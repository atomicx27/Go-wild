(function() {
    // Inject global CSS for common animations and styling
    const style = document.createElement('style');
    style.textContent = `
        /* Glow animation for interactive elements */
        @keyframes globalPulseGlow {
            0% { box-shadow: 0 0 5px rgba(0, 255, 255, 0.2); }
            50% { box-shadow: 0 0 20px rgba(0, 255, 255, 0.6); }
            100% { box-shadow: 0 0 5px rgba(0, 255, 255, 0.2); }
        }

        /* Smooth transition for buttons and cards */
        button, .card, a {
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        /* Hover effect for clickable elements */
        .global-hover-effect:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5) !important;
            z-index: 10;
        }

        /* Click ripple effect */
        .ripple {
            position: absolute;
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-anim 600ms linear;
            background-color: rgba(255, 255, 255, 0.4);
        }

        @keyframes ripple-anim {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Add classes to existing interactive elements
    function enhanceElements(rootNode = document) {
        const interactives = rootNode.querySelectorAll('button, a, .card, input[type="button"], input[type="submit"]');
        interactives.forEach(el => {
            if (!el.classList.contains('global-hover-effect')) {
                el.classList.add('global-hover-effect');

                // Add ripple effect on click
                el.addEventListener('click', function(e) {
                    // Make sure element is positioned relative for the absolute ripple
                    if (getComputedStyle(this).position === 'static') {
                        this.style.position = 'relative';
                    }
                    this.style.overflow = 'hidden';

                    const circle = document.createElement('span');
                    const diameter = Math.max(this.clientWidth, this.clientHeight);
                    const radius = diameter / 2;

                    circle.style.width = circle.style.height = `${diameter}px`;
                    circle.style.left = `${e.clientX - this.getBoundingClientRect().left - radius}px`;
                    circle.style.top = `${e.clientY - this.getBoundingClientRect().top - radius}px`;
                    circle.classList.add('ripple');

                    const ripple = this.querySelector('.ripple');
                    if (ripple) {
                        ripple.remove();
                    }

                    this.appendChild(circle);
                });
            }
        });
    }

    // Run initially
    enhanceElements();

    // Observe for dynamically added elements to enhance them too
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        enhanceElements(node);
                        if (node.matches && node.matches('button, a, .card, input[type="button"], input[type="submit"]')) {
                            enhanceElements(node.parentNode); // Ensure the node itself gets enhanced if it's the root
                        }
                    }
                });
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Subtle entrance animation using Web Animations API
    document.addEventListener('DOMContentLoaded', () => {
        document.body.animate([
            { opacity: 0, filter: 'blur(10px)' },
            { opacity: 1, filter: 'blur(0px)' }
        ], {
            duration: 800,
            easing: 'ease-out',
            fill: 'forwards'
        });
    });
})();
