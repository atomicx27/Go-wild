// Modern UI Enhancements JavaScript

// Mouse trail effect
const particles = [];
const numParticles = 15;
for (let i = 0; i < numParticles; i++) {
    const p = document.createElement('div');
    p.classList.add('mouse-trail-particle');
    document.body.appendChild(p);
    particles.push({ element: p, x: 0, y: 0 });
}

let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;

document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

function animateTrails() {
    let x = mouseX;
    let y = mouseY;

    particles.forEach((p, index) => {
        p.x += (x - p.x) * 0.3;
        p.y += (y - p.y) * 0.3;

        p.element.style.transform = `translate(${p.x}px, ${p.y}px) scale(${1 - index/numParticles})`;

        x = p.x;
        y = p.y;
    });

    requestAnimationFrame(animateTrails);
}

requestAnimationFrame(animateTrails);

// Apply modern-hover class to interactive elements
function setupModernUI() {
    document.querySelectorAll('button, a, input[type="button"], input[type="submit"], .btn').forEach(el => {
        if (!el.classList.contains('modern-ui-applied')) {
            el.classList.add('modern-ui-applied');
            if (!el.classList.contains('modern-hover')) {
                el.classList.add('modern-hover');
            }

            const style = window.getComputedStyle(el);
        if (style.position === 'static') {
            el.style.position = 'relative';
        }

        el.addEventListener('mousedown', function(e) {
            let rippleContainer = el.querySelector('.ripple-container');
            if (!rippleContainer) {
                rippleContainer = document.createElement('div');
                rippleContainer.classList.add('ripple-container');
                el.appendChild(rippleContainer);
            }

            const ripple = document.createElement('div');
            ripple.classList.add('ripple-effect');

            const rect = el.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);

            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - size/2}px`;
            ripple.style.top = `${e.clientY - rect.top - size/2}px`;

            rippleContainer.appendChild(ripple);

            const animation = ripple.animate([
                { transform: 'scale(0)', opacity: 0.5 },
                { transform: 'scale(2.5)', opacity: 0 }
            ], {
                duration: 600,
                easing: 'ease-out',
                composite: 'add'
            });

            animation.onfinish = () => {
                animation.cancel();
                ripple.remove();
            };
        });
        } // end of modern-ui-applied check
    });
}

// Initial setup
document.addEventListener('DOMContentLoaded', setupModernUI);
// If already loaded
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    setupModernUI();
}

// Observe DOM for newly added elements (like dynamically loaded content)
const observer = new MutationObserver((mutations) => {
    let shouldSetup = false;
    for (let mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
            shouldSetup = true;
            break;
        }
    }
    if (shouldSetup) {
        setupModernUI();
    }
});
observer.observe(document.body, { childList: true, subtree: true });