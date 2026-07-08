/**
 * Modern UI Enhancements - Shared Scripts
 */

// 1. Mouse Trail Particle Effect
function initMouseTrail() {
    const particles = [];
    const poolSize = 20; // Reusable particles

    // Initialize pool
    for (let i = 0; i < poolSize; i++) {
        const p = document.createElement('div');
        p.className = 'mouse-particle';
        p.style.width = '6px';
        p.style.height = '6px';
        p.style.background = 'rgba(56, 189, 248, 0.6)';
        p.style.boxShadow = '0 0 8px rgba(56, 189, 248, 0.8)';
        p.style.opacity = '0';
        p.style.transform = 'translate(-100px, -100px)'; // Start off-screen
        document.body.appendChild(p);
        particles.push(p);
    }

    let currentIndex = 0;
    let isDrawing = false;
    let mouseX = 0;
    let mouseY = 0;
    let lastDrawTime = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;

        if (!isDrawing) {
            isDrawing = true;
            requestAnimationFrame(drawParticle);
        }
    }, { passive: true });

    function drawParticle(now) {
        if (now - lastDrawTime > 30) { // Throttle slightly
            const p = particles[currentIndex];
            currentIndex = (currentIndex + 1) % poolSize;

            // Set position immediately
            p.style.transform = `translate(${mouseX - 3}px, ${mouseY - 3}px)`;

            // Animate
            const anim = p.animate([
                { opacity: 0.8, transform: `translate(${mouseX - 3}px, ${mouseY - 3}px) scale(1)` },
                { opacity: 0, transform: `translate(${mouseX - 3}px, ${mouseY + 20}px) scale(0)` }
            ], {
                duration: 600,
                easing: 'cubic-bezier(0.25, 1, 0.5, 1)',
                fill: 'forwards'
            });

            lastDrawTime = now;
        }
        isDrawing = false;
    }
}

// 2. Button Interactive Effects (Ripple and Pop)
function initButtonEffects() {
    document.addEventListener('click', (e) => {
        const target = e.target.closest('button, .btn');
        if (!target) return;

        // Ensure target is relative if not already set, but don't force overflow hidden globally
        if (getComputedStyle(target).position === 'static') {
            target.style.position = 'relative';
        }

        // --- Ripple Effect ---
        const rect = target.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 2; // Make ripple big enough
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.top = `${y}px`;
        ripple.style.left = `${x}px`;
        ripple.style.width = `${size}px`;
        ripple.style.height = `${size}px`;
        ripple.style.background = 'rgba(255, 255, 255, 0.3)';
        ripple.style.borderRadius = '50%';
        ripple.style.pointerEvents = 'none';

        // Wrap content if needed to prevent text hiding, but keep it simple
        const contentZ = getComputedStyle(target).zIndex;
        if (contentZ === 'auto' || parseInt(contentZ) < 1) {
            // Need a container to clip ripple without clipping dropdowns
            // Instead of clipping on the button itself, just let it fade out quickly
            // This is a trade-off to avoid the global overflow:hidden issue.
            target.appendChild(ripple);

            const animation = ripple.animate([
                { transform: 'scale(0)', opacity: 0.5 },
                { transform: 'scale(1)', opacity: 0 }
            ], {
                duration: 400,
                easing: 'ease-out'
            });

            animation.onfinish = () => {
                animation.cancel();
                if (ripple.parentNode) {
                    ripple.parentNode.removeChild(ripple);
                }
            };
        }

        // --- Pop Effect (using composite: add) ---
        const popAnim = target.animate([
            { transform: 'scale(0.95)', filter: 'brightness(1.2)' },
            { transform: 'scale(1)', filter: 'brightness(1)' }
        ], {
            duration: 200,
            easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
            composite: 'add' // Crucial: blends with existing hover transforms!
        });

        popAnim.onfinish = () => popAnim.cancel(); // Cleanup memory
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initMouseTrail();
        initButtonEffects();
    });
} else {
    initMouseTrail();
    initButtonEffects();
}
