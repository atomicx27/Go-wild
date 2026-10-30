(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        // Event delegation for dynamically added buttons
        document.body.addEventListener('mousedown', (e) => {
            const button = e.target.closest('button, .btn');
            if (!button) return;

            // Using Web Animations API for a subtle click pop
            const animation = button.animate([
                { transform: 'scale(1)', filter: 'brightness(1)' },
                { transform: 'scale(0.95)', filter: 'brightness(1.2)', offset: 0.5 },
                { transform: 'scale(1)', filter: 'brightness(1)' }
            ], {
                duration: 300,
                easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                composite: 'add' // ensures seamless blending with CSS hover transforms
            });

            // Clean up animation on finish to prevent memory leaks
            animation.onfinish = () => animation.cancel();
        });

        // Add intersection observer for scroll animations
        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        const processAnimatableElement = (el) => {
            if (!el.classList.contains('modern-ui-scroll-processed') && !el.closest('.no-scroll-reveal')) {
                el.classList.add('modern-ui-scroll-processed');
                // Initial state for scroll reveal
                if(window.getComputedStyle(el).opacity !== '0') {
                    // Only apply if not already handled by another animation
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(20px)';
                    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
                    observer.observe(el);
                }
            }
        };

        // Apply scroll reveal to common card/section elements if they exist initially
        const animatableElements = document.querySelectorAll('.agent-card, .card, section, article');
        animatableElements.forEach(processAnimatableElement);

        // MutationObserver for dynamically added animatable elements
        const mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if the added node itself is animatable
                        if (node.matches('.agent-card, .card, section, article')) {
                            processAnimatableElement(node);
                        }
                        // Check if it contains animatable children
                        const nestedElements = node.querySelectorAll('.agent-card, .card, section, article');
                        nestedElements.forEach(processAnimatableElement);
                    }
                });
            });
        });

        mutationObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
})();
