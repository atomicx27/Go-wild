// shared/modern-ui.js

(function() {
    'use strict';

    // Prevent running multiple times if the script is loaded twice
    if (window.modernUiProcessed) {
        return;
    }
    window.modernUiProcessed = true;

    // --- 1. Click Pulse Effect for Buttons ---
    function addPulseEffect(event) {
        const btn = event.currentTarget;

        // Create pulse animation
        const rect = btn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        const pulse = document.createElement('span');
        pulse.style.position = 'absolute';
        pulse.style.width = `${size}px`;
        pulse.style.height = `${size}px`;
        pulse.style.left = `${x}px`;
        pulse.style.top = `${y}px`;
        pulse.style.background = 'rgba(255, 255, 255, 0.4)';
        pulse.style.borderRadius = '50%';
        pulse.style.pointerEvents = 'none'; // Don't block clicks

        btn.appendChild(pulse);

        // Animate
        const animation = pulse.animate([
            { transform: 'scale(0)', opacity: 1 },
            { transform: 'scale(2)', opacity: 0 }
        ], {
            duration: 500,
            easing: 'ease-out',
            composite: 'add'
        });

        animation.onfinish = () => {
            animation.cancel();
            pulse.remove();
        };
    }

    function initButtons() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (!btn.classList.contains('modern-ui-btn-processed')) {
                btn.classList.add('modern-ui-btn-processed');
                // Ensure the button has relative positioning for the absolute pulse span
                if (getComputedStyle(btn).position === 'static') {
                    btn.style.position = 'relative';
                }
                // Ensure overflow hidden so pulse stays inside
                btn.style.overflow = 'hidden';
                btn.addEventListener('click', addPulseEffect);
            }
        });
    }

    // --- 2. Scroll Reveal Animations ---
    function initScrollReveal() {
        // Find elements to reveal. For now, let's grab major sections/cards
        // We'll target typical container elements if they don't already have the reveal class
        const selectorsToReveal = ['.container', '.card', 'section', '.agent-card', '.module', 'header'];

        const elementsToReveal = document.querySelectorAll(selectorsToReveal.join(', '));

        elementsToReveal.forEach(el => {
            // Don't add to body or html, or elements already processed
            if (el.tagName !== 'BODY' && el.tagName !== 'HTML' && !el.classList.contains('modern-ui-reveal-processed')) {
                 el.classList.add('modern-ui-reveal');
                 el.classList.add('modern-ui-reveal-processed');
            }
        });

        const revealElements = document.querySelectorAll('.modern-ui-reveal');

        if (revealElements.length === 0) return;

        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1 // Trigger when 10% visible
        };

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('modern-ui-active');
                    // Stop observing once revealed
                    obs.unobserve(entry.target);
                }
            });
        }, observerOptions);

        revealElements.forEach(el => {
            observer.observe(el);
        });
    }


    // --- Initialization ---
    function init() {
        initButtons();
        initScrollReveal();
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Also run on dynamic updates (simple MutationObserver)
    const observer = new MutationObserver((mutations) => {
        let shouldInit = false;
        for (let mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                shouldInit = true;
                break;
            }
        }
        if (shouldInit) {
            // Slight delay to avoid thrashing
            setTimeout(() => {
                initButtons();
                // Not re-initing scroll reveal on mutations to avoid jumping,
                // but could be added if needed.
            }, 100);
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

})();
