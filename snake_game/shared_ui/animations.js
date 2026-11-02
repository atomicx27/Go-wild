(function() {
    // Add click ripple effect
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.classList.contains('btn')) {
            const button = e.target;
            const rect = button.getBoundingClientRect();

            // Check if position is relative or absolute, if not, set to relative
            const style = window.getComputedStyle(button);
            if (style.position === 'static') {
                button.style.position = 'relative';
            }
            // Ensure overflow is hidden
            if (style.overflow !== 'hidden') {
                button.style.overflow = 'hidden';
            }

            const circle = document.createElement('span');
            const diameter = Math.max(rect.width, rect.height);
            const radius = diameter / 2;

            circle.style.width = circle.style.height = `${diameter}px`;
            circle.style.left = `${e.clientX - rect.left - radius}px`;
            circle.style.top = `${e.clientY - rect.top - radius}px`;
            circle.classList.add('ripple');

            const ripple = button.getElementsByClassName('ripple')[0];
            if (ripple) {
                ripple.remove();
            }

            button.appendChild(circle);

            circle.animate([
                { transform: 'scale(0)', opacity: 0.5 },
                { transform: 'scale(4)', opacity: 0 }
            ], {
                duration: 600,
                easing: 'ease-out',
                composite: 'add'
            }).onfinish = () => circle.remove();
        }
    });
})();
