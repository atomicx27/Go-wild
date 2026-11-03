// shared_ui.js
(function() {
    // Add ripple effect using Web Animations API
    document.body.addEventListener('click', function(e) {
        const btn = e.target.closest('button, .btn');
        if (!btn) return;

        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const ripple = document.createElement('div');
        ripple.style.position = 'absolute';
        ripple.style.width = '20px';
        ripple.style.height = '20px';
        ripple.style.background = 'rgba(255, 255, 255, 0.4)';
        ripple.style.borderRadius = '50%';
        ripple.style.pointerEvents = 'none';
        ripple.style.left = `${x - 10}px`;
        ripple.style.top = `${y - 10}px`;
        ripple.style.zIndex = '9999';

        const computedStyle = window.getComputedStyle(btn);
        if (computedStyle.position === 'static') {
            btn.style.position = 'relative';
        }

        btn.appendChild(ripple);

        const animation = ripple.animate([
            { transform: 'scale(1)', opacity: 1 },
            { transform: 'scale(15)', opacity: 0 }
        ], {
            duration: 600,
            easing: 'ease-out',
            composite: 'add'
        });

        animation.onfinish = () => {
            animation.cancel();
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        };
    });
})();
