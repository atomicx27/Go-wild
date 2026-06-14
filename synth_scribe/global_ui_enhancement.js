(function() {
    // Modern UI/UX Global Enhancements
    // Using Web Animations API and event delegation to prevent breaking existing styles.

    let currentAnimations = new WeakMap();

    document.addEventListener('mouseover', function(e) {
        const target = e.target.closest('button, a, input, .card, .task, .node, .btn');
        if (target) {
            if (currentAnimations.has(target)) {
                currentAnimations.get(target).pause();
            }
            const anim = target.animate([
                { filter: 'brightness(1.2) drop-shadow(0 0 6px rgba(0, 255, 255, 0.4))', transform: 'scale(1.02)' }
            ], {
                duration: 200,
                fill: 'forwards',
                easing: 'ease-out'
            });
            currentAnimations.set(target, anim);
        }
    });

    document.addEventListener('mouseout', function(e) {
        const target = e.target.closest('button, a, input, .card, .task, .node, .btn');
        if (target) {
            if (currentAnimations.has(target)) {
                currentAnimations.get(target).pause();
            }
            const anim = target.animate([
                { filter: 'brightness(1)', transform: 'scale(1)' }
            ], {
                duration: 200,
                fill: 'forwards',
                easing: 'ease-out'
            });
            currentAnimations.set(target, anim);
        }
    });

    document.addEventListener('mousedown', function(e) {
        const target = e.target.closest('button, a, .task, .btn');
        if (target) {
            createRipple(e, target);
        }
    });

    function createRipple(event, element) {
        const circle = document.createElement('span');
        const diameter = Math.max(element.clientWidth, element.clientHeight);
        const radius = diameter / 2;

        const rect = element.getBoundingClientRect();

        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - rect.left - radius}px`;
        circle.style.top = `${event.clientY - rect.top - radius}px`;
        circle.style.position = 'absolute';
        circle.style.borderRadius = '50%';
        circle.style.backgroundColor = 'rgba(0, 255, 255, 0.3)';
        circle.style.transform = 'scale(0)';
        circle.style.pointerEvents = 'none';
        circle.style.zIndex = '9999';

        const computedStyle = window.getComputedStyle(element);
        const originalPosition = element.style.position;
        const originalOverflow = element.style.overflow;

        if (computedStyle.position === 'static') {
            element.style.position = 'relative';
        }
        element.style.overflow = 'hidden';

        element.appendChild(circle);

        const animation = circle.animate([
            { transform: 'scale(0)', opacity: 1 },
            { transform: 'scale(2)', opacity: 0 }
        ], {
            duration: 600,
            easing: 'ease-out'
        });

        animation.onfinish = () => {
            circle.remove();
            element.style.position = originalPosition;
            element.style.overflow = originalOverflow;
        };
    }

    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) { // ELEMENT_NODE
                    if (node.classList && (node.classList.contains('task') || node.classList.contains('card') || node.classList.contains('column') || node.classList.contains('node'))) {
                        node.animate([
                            { opacity: 0, transform: 'translateY(15px) scale(0.98)' },
                            { opacity: 1, transform: 'translateY(0) scale(1)' }
                        ], {
                            duration: 400,
                            easing: 'ease-out'
                        });
                    }

                    if (node.querySelectorAll) {
                        const elements = node.querySelectorAll('.task, .card, .column, .node');
                        elements.forEach(el => {
                            el.animate([
                                { opacity: 0, transform: 'translateY(15px) scale(0.98)' },
                                { opacity: 1, transform: 'translateY(0) scale(1)' }
                            ], {
                                duration: 400,
                                easing: 'ease-out'
                            });
                        });
                    }
                }
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    const initAnimations = () => {
        const elements = document.querySelectorAll('.task, .card, .column, .node, button, input, .btn');
        elements.forEach((el, index) => {
            el.animate([
                { opacity: 0, transform: 'translateY(10px)' },
                { opacity: 1, transform: 'translateY(0)' }
            ], {
                duration: 500,
                delay: Math.min(index * 30, 800),
                easing: 'ease-out',
                fill: 'both'
            });
        });
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAnimations);
    } else {
        initAnimations();
    }
})();
