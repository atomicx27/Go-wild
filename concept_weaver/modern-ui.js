// modern-ui.js
(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    // 1. Add ripple effect to buttons (Web Animations API)
    const buttons = document.querySelectorAll('button, .btn, .button');

    buttons.forEach(btn => {
      // Prevent attaching multiple times if script is loaded twice
      if (btn.classList.contains('modern-ui-processed')) return;
      btn.classList.add('modern-ui-processed');

      btn.addEventListener('click', function(e) {
        // Calculate click coordinates relative to button
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Create ripple element
        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.background = 'rgba(255, 255, 255, 0.3)';
        ripple.style.borderRadius = '50%';
        ripple.style.pointerEvents = 'none';

        // Ensure parent can contain the ripple visually if overflow hidden is acceptable,
        // but we avoid forcing overflow: hidden globally on buttons in CSS.
        // For the ripple to look best, the button should have position relative (set in CSS)
        // and ideally overflow hidden, but we do it dynamically on the ripple wrapper if needed.

        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x - size/2}px`;
        ripple.style.top = `${y - size/2}px`;

        // If the button itself isn't overflow hidden (to preserve tooltips),
        // the ripple might bleed. A trade-off for global scripts.
        // We'll just append it directly for a subtle flash effect.
        btn.appendChild(ripple);

        // Animate using Web Animations API
        const animation = ripple.animate([
          { transform: 'scale(0)', opacity: 1 },
          { transform: 'scale(2)', opacity: 0 }
        ], {
          duration: 600,
          easing: 'ease-out',
          composite: 'add'
        });

        // Cleanup
        animation.onfinish = () => {
          ripple.remove();
        };
      });
    });

    // 2. Add subtle entry animation to main containers (if they exist)
    const containers = document.querySelectorAll('.container, main, #app, #root');
    containers.forEach(container => {
      if (!container.classList.contains('modern-fade-in') && !container.classList.contains('modern-ui-processed-fade')) {
          container.classList.add('modern-fade-in');
          container.classList.add('modern-ui-processed-fade');
      }
    });
  });

})();
