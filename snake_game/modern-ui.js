// modern-ui.js
(function() {
    // Add ripple effect or subtle animation to buttons
    document.addEventListener('click', function(e) {
        const target = e.target.closest('button, .btn, .interactive');
        if (!target) return;

        // Prevent attaching multiple events if it's already processed, though this is dynamic
        // Web Animations API for click feedback
        const animation = target.animate([
            { transform: 'scale(1)', filter: 'brightness(1)' },
            { transform: 'scale(0.95)', filter: 'brightness(1.2)', offset: 0.5 },
            { transform: 'scale(1)', filter: 'brightness(1)' }
        ], {
            duration: 200,
            easing: 'ease-out',
            composite: 'add' // blend with existing transforms
        });

        // Cleanup to prevent memory leaks
        animation.onfinish = () => {
            animation.cancel();
        };
    });

    // Add entry animation to dynamically added elements (like tasks in a kanban board)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1 && (
                    node.classList.contains('task') ||
                    node.classList.contains('card') ||
                    node.classList.contains('item') ||
                    node.tagName === 'LI'
                )) {
                    // Check if already animated
                    if (!node.dataset.animated) {
                        node.dataset.animated = 'true';
                        const animation = node.animate([
                            { opacity: 0, transform: 'translateY(10px)' },
                            { opacity: 1, transform: 'translateY(0)' }
                        ], {
                            duration: 300,
                            easing: 'ease-out',
                            fill: 'both'
                        });

                        animation.onfinish = () => {
                            animation.commitStyles();
                            animation.cancel();
                        };
                    }
                }
            });
        });
    });

    // Start observing body for dynamically added elements
    // Wait for DOM content to be loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            observer.observe(document.body, { childList: true, subtree: true });
        });
    } else {
        observer.observe(document.body, { childList: true, subtree: true });
    }
})();
