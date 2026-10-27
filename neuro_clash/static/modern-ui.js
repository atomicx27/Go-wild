/* Modern UI Enhancements JavaScript */
(function() {
    if (window._modernUIInitialized) return;
    window._modernUIInitialized = true;

    // Ripple effect on buttons
    document.addEventListener('click', function(e) {
        let target = e.target.closest('button');
        if (!target) return;

        if (target.disabled) return;

        // Ensure button has position relative so absolute children align correctly
        const computedStyle = window.getComputedStyle(target);
        if (computedStyle.position === 'static') {
            target.style.position = 'relative';
        }

        // Find or create a ripple container to limit overflow
        let container = target.querySelector('.ripple-container');
        if (!container) {
            container = document.createElement('span');
            container.className = 'ripple-container';
            target.appendChild(container);
        }

        const rect = target.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        const ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;

        container.appendChild(ripple);

        const animation = ripple.animate([
            { transform: 'scale(0)', opacity: 1 },
            { transform: 'scale(2.5)', opacity: 0 }
        ], {
            duration: 600,
            easing: 'ease-out',
            composite: 'add'
        });

        animation.onfinish = () => {
            ripple.remove();
        };
    });
})();
