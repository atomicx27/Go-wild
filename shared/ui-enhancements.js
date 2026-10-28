(function() {
    'use strict';

    /**
     * Modern UI Enhancements Script
     * Safely scoped using an IIFE.
     */

    // Function to add dynamic ripple effects to interactive elements
    function applyRippleEffect(element) {
        if (element.classList.contains('ripple-processed')) return;

        element.classList.add('ripple-processed');
        // We only add ripple-element if we actually need overflow hidden for the ripple.
        // Some elements might break with overflow: hidden, so we're careful.
        // But for buttons it's usually fine. Let's add it dynamically to buttons.
        if (element.tagName.toLowerCase() === 'button' || element.classList.contains('btn')) {
             element.classList.add('ripple-element');
        }

        element.addEventListener('mousedown', function(e) {
            const rect = this.getBoundingClientRect();
            // Calculate relative click coordinates
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.classList.add('ripple');

            // Set size based on the largest dimension to ensure it covers the element
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x - size / 2}px`;
            ripple.style.top = `${y - size / 2}px`;

            this.appendChild(ripple);

            // Clean up animation after it finishes (match CSS duration)
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    }

    // Function to add staggered fade-in animations to containers
    function applyFadeIn(element, index) {
        if (element.classList.contains('fade-processed')) return;

        element.classList.add('fade-processed');
        element.classList.add('fade-in-up');
        // Add a slight delay based on the index to create a staggered effect
        element.style.animationDelay = `${index * 0.1}s`;
    }

    // Apply enhancements to existing elements
    function initializeEnhancements() {
        // Buttons
        const buttons = document.querySelectorAll('button, .btn');
        buttons.forEach((btn) => applyRippleEffect(btn));

        // Cards (staggered animation)
        const cards = document.querySelectorAll('.card, [class*="card"]');
        cards.forEach((card, index) => applyFadeIn(card, index));

        // Let's also animate some main containers if they exist
        const containers = document.querySelectorAll('main, section, .container');
        containers.forEach((container, index) => applyFadeIn(container, index));
    }

    // Initial setup
    document.addEventListener('DOMContentLoaded', initializeEnhancements);

    // Fallback if already loaded
    if (document.readyState === 'interactive' || document.readyState === 'complete') {
        initializeEnhancements();
    }

    // Use MutationObserver to gracefully handle dynamically injected DOM elements
    const observer = new MutationObserver((mutations) => {
        let shouldProcess = false;
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                shouldProcess = true;
                break;
            }
        }

        if (shouldProcess) {
            // Slight delay to avoid thrashing
            setTimeout(() => {
                 const buttons = document.querySelectorAll('button:not(.ripple-processed), .btn:not(.ripple-processed)');
                 buttons.forEach(btn => applyRippleEffect(btn));

                 const cards = document.querySelectorAll('.card:not(.fade-processed), [class*="card"]:not(.fade-processed)');
                 cards.forEach((card, index) => applyFadeIn(card, index));
            }, 50);
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

})();
