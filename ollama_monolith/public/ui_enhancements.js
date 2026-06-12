(function() {
    const selectorHover = 'button, .btn, a, .card, .task, .board-column, .item, li';
    const selectorFocus = 'input, textarea, select';

    document.body.addEventListener('mouseover', function(e) {
        const target = e.target.closest(selectorHover);
        if (target) {
            if (target._isHovered) return;
            target._isHovered = true;

            target._hoverAnim = target.animate([
                { transform: 'scale(1) translateY(0px)', filter: 'brightness(1)' },
                { transform: 'scale(1.02) translateY(-2px)', filter: 'brightness(1.1)' }
            ], {
                duration: 250,
                easing: 'cubic-bezier(0.25, 0.8, 0.25, 1)',
                fill: 'forwards',
                composite: 'add'
            });

            target._shadowAnim = target.animate([
                { boxShadow: '0 0 0px rgba(0,255,255,0)' },
                { boxShadow: '0 4px 15px rgba(0, 255, 255, 0.3), 0 0 20px rgba(255, 0, 255, 0.2)' }
            ], {
                duration: 250,
                easing: 'cubic-bezier(0.25, 0.8, 0.25, 1)',
                fill: 'forwards'
            });
        }
    });

    document.body.addEventListener('mouseout', function(e) {
        const target = e.target.closest(selectorHover);
        if (target && target._isHovered) {
            target._isHovered = false;
            if (target._hoverAnim) target._hoverAnim.reverse();
            if (target._shadowAnim) target._shadowAnim.reverse();
        }
    });

    document.body.addEventListener('mousedown', function(e) {
        const target = e.target.closest(selectorHover);
        if (target) {
            target.animate([
                { transform: 'scale(1)' },
                { transform: 'scale(0.95)' },
                { transform: 'scale(1)' }
            ], {
                duration: 200,
                easing: 'ease-out',
                composite: 'add'
            });
        }
    });

    document.body.addEventListener('focusin', function(e) {
        const target = e.target.closest(selectorFocus);
        if (target) {
            target._focusAnim = target.animate([
                { boxShadow: '0 0 0px rgba(0,255,255,0)' },
                { boxShadow: '0 0 10px rgba(0, 255, 255, 0.5), 0 0 20px rgba(255, 0, 255, 0.3)' }
            ], {
                duration: 250,
                easing: 'ease',
                fill: 'forwards'
            });
        }
    });

    document.body.addEventListener('focusout', function(e) {
        const target = e.target.closest(selectorFocus);
        if (target && target._focusAnim) {
            target._focusAnim.reverse();
        }
    });

    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) {
                        if (node.matches && node.matches('.task, .card, .item, li')) {
                            node.animate([
                                { opacity: 0, transform: 'translateY(10px)' },
                                { opacity: 1, transform: 'translateY(0)' }
                            ], {
                                duration: 400,
                                easing: 'ease-out',
                                fill: 'both',
                                composite: 'add'
                            });
                        }
                    }
                });
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

})();
