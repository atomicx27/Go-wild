
// modern-ui.js
(function() {
    'use strict';

    function initModernUI() {
        // Enhance buttons
        const buttons = document.querySelectorAll('button, .btn');
        buttons.forEach(btn => {
            if (!btn.classList.contains('modern-ui-enhanced-btn')) {
                btn.classList.add('modern-ui-enhanced-btn');

                // Add click ripple/bounce effect using Web Animations API
                btn.addEventListener('click', function(e) {
                    const animation = btn.animate([
                        { transform: 'scale(1)' },
                        { transform: 'scale(0.95)' },
                        { transform: 'scale(1)' }
                    ], {
                        duration: 300,
                        easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
                        composite: 'add'
                    });

                    animation.onfinish = () => animation.cancel();
                });
            }
        });

        // Enhance inputs
        const inputs = document.querySelectorAll('input[type="text"], input[type="password"], textarea, select');
        inputs.forEach(input => {
            if (!input.classList.contains('modern-ui-input')) {
                input.classList.add('modern-ui-input');
            }
        });

        // Enhance cards / containers (heuristic)
        const cards = document.querySelectorAll('.card, .panel, [class*="bg-gray-800"], [class*="bg-slate-800"]');
        cards.forEach(card => {
            if (!card.classList.contains('modern-ui-card') && card.tagName !== 'BODY') {
                card.classList.add('modern-ui-card');
            }
        });
    }

    // Run on load and observe DOM for new elements
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModernUI);
    } else {
        initModernUI();
    }

    // MutationObserver to apply enhancements to dynamically added elements
    const observer = new MutationObserver((mutations) => {
        let shouldInit = false;
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                shouldInit = true;
                break;
            }
        }
        if (shouldInit) {
            initModernUI();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

})();
