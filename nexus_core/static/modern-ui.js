// modern-ui.js
(function() {
    document.addEventListener('DOMContentLoaded', () => {
        // Enhance buttons
        const buttons = document.querySelectorAll('button, .btn, [role="button"]');
        buttons.forEach(btn => {
            if (!btn.classList.contains('mui-btn-enhance')) {
                btn.classList.add('mui-btn-enhance');
            }

            // Add click ripple/pulse effect using Web Animations API
            if (!btn.dataset.muiEnhanced) {
                btn.dataset.muiEnhanced = "true";
                btn.addEventListener('click', (e) => {
                    const animation = btn.animate([
                        { transform: 'scale(1)' },
                        { transform: 'scale(0.95)' },
                        { transform: 'scale(1)' }
                    ], {
                        duration: 300,
                        easing: 'ease-out',
                        composite: 'add'
                    });

                    animation.onfinish = () => {
                        animation.cancel();
                    };
                });
            }
        });

        // Form inputs enhancement
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
             input.style.transition = 'border-color 0.3s ease, box-shadow 0.3s ease';
             input.addEventListener('focus', () => {
                 input.style.boxShadow = '0 0 0 2px rgba(14, 165, 233, 0.2)';
             });
             input.addEventListener('blur', () => {
                 input.style.boxShadow = 'none';
             });
        });
    });
})();
