(function() {
    // Inject global styles
    const style = document.createElement('style');
    style.innerHTML = `
        .ripple-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            border-radius: inherit;
            pointer-events: none;
        }
        .ripple-effect {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.4);
            transform: scale(0);
            animation: ripple-animation 600ms linear;
            pointer-events: none;
        }
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }

        .mouse-trail {
            position: fixed;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            pointer-events: none;
            background: rgba(100, 150, 255, 0.5);
            z-index: 9999;
            transform: translate(-50%, -50%);
            transition: opacity 0.5s ease-out, transform 0.5s ease-out;
        }

        /* Hover enhancement using class */
        .hover-enhance {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .hover-enhance:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
    `;
    document.head.appendChild(style);

    // Add ripple effect to buttons
    document.addEventListener('click', function(e) {
        const target = e.target.closest('button, .btn, .button, a[role="button"]');
        if (!target) return;

        // Make sure target is positioned relatively
        if (getComputedStyle(target).position === 'static') {
            target.style.position = 'relative';
        }

        // Add ripple container if not exists
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
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;

        container.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    });

    // Mouse Trail Effect
    let mouseTrails = [];
    const maxTrails = 10;
    let trailIndex = 0;

    for (let i = 0; i < maxTrails; i++) {
        const trail = document.createElement('div');
        trail.className = 'mouse-trail';
        trail.style.opacity = '0';
        document.body.appendChild(trail);
        mouseTrails.push(trail);
    }

    let mouseX = 0, mouseY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateTrails() {
        if (mouseTrails.length > 0) {
            const trail = mouseTrails[trailIndex];
            trail.style.left = mouseX + 'px';
            trail.style.top = mouseY + 'px';
            trail.style.opacity = '1';
            trail.style.transform = 'translate(-50%, -50%) scale(1)';

            const animation = trail.animate([
                { opacity: 1, transform: 'translate(-50%, -50%) scale(1)' },
                { opacity: 0, transform: 'translate(-50%, -50%) scale(0.2)' }
            ], {
                duration: 500,
                easing: 'ease-out',
                composite: 'add'
            });

            animation.onfinish = () => {
                trail.style.opacity = '0';
                animation.cancel();
            };

            trailIndex = (trailIndex + 1) % maxTrails;
        }
        requestAnimationFrame(animateTrails);
    }

    requestAnimationFrame(animateTrails);

    // Apply hover-enhance class to all interactive elements on load and mutations
    function enhanceElements() {
        const elements = document.querySelectorAll('button:not(.hover-enhance), .btn:not(.hover-enhance), input[type="submit"]:not(.hover-enhance), .card:not(.hover-enhance)');
        elements.forEach(el => {
            // Don't add to specific elements that might break
            if(el.closest('.no-enhance')) return;
            el.classList.add('hover-enhance');
        });
    }

    // Initial enhancement
    enhanceElements();

    // Observer for dynamically added elements
    const observer = new MutationObserver((mutations) => {
        let shouldEnhance = false;
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                shouldEnhance = true;
                break;
            }
        }
        if (shouldEnhance) {
            enhanceElements();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

})();
