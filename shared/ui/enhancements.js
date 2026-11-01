(function() {
    // Event delegation for click animations (e.g., buttons, interactive elements)
    document.body.addEventListener('click', function(e) {
        const target = e.target.closest('button, .btn, a, .interactive');
        if (!target) return;

        // Prevent duplicate processing if needed (though click animations are ephemeral)
        // Ensure seamless blending with existing CSS transforms
        const animation = target.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(0.95)' },
            { transform: 'scale(1)' }
        ], {
            duration: 200,
            easing: 'ease-out',
            composite: 'add'
        });

        // Explicitly clean up animation to prevent memory leaks
        animation.onfinish = () => animation.cancel();
    });

    // Add enter animations using IntersectionObserver
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                if (!entry.target.classList.contains('ui-animated')) {
                    entry.target.classList.add('ui-animated');
                    const animation = entry.target.animate([
                        { opacity: 0, transform: 'translateY(20px)' },
                        { opacity: 1, transform: 'translateY(0)' }
                    ], {
                        duration: 500,
                        easing: 'ease-out',
                        fill: 'forwards',
                        composite: 'add'
                    });

                    animation.onfinish = () => {
                        // Keep the final state but cancel the active animation
                        entry.target.style.opacity = 1;
                        // Avoid overriding existing inline transforms explicitly
                        // Wait for any styling to compute if necessary, but composite: 'add' handles most cases smoothly.
                        animation.cancel();
                    };
                    observer.unobserve(entry.target);
                }
            }
        });
    }, { threshold: 0.1 });

    // Observe specific elements dynamically using a MutationObserver
    // since projects might dynamically generate DOM elements
    const observeNewElements = (mutationsList) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // Element node
                        if (node.matches('button, .btn, .card, .panel, section, input[type="submit"], input[type="button"]')) {
                            observer.observe(node);
                        }
                        node.querySelectorAll('button, .btn, .card, .panel, section, input[type="submit"], input[type="button"]').forEach(el => {
                            observer.observe(el);
                        });
                    }
                });
            }
        }
    };

    const mutationObserver = new MutationObserver(observeNewElements);
    mutationObserver.observe(document.body, { childList: true, subtree: true });

    // Initial observe for existing elements
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('button, .btn, .card, .panel, section, input[type="submit"], input[type="button"]').forEach(el => {
            observer.observe(el);
        });
    });
})();
