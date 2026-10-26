(function() {
  // Add global class to enable smooth scrolling
  document.documentElement.style.scrollBehavior = 'smooth';

  document.addEventListener('DOMContentLoaded', () => {
    // Add fade-in animation to main containers
    const containers = document.querySelectorAll('.container, main, section, .card');
    containers.forEach((el, index) => {
      if (!el.classList.contains('fade-in')) {
        el.classList.add('fade-in');
        el.style.animationDelay = `${index * 0.1}s`;
      }
    });

    // Enhance buttons with modern styling and ripple effect
    const buttons = document.querySelectorAll('button:not(.btn-modern)');
    buttons.forEach(btn => {
      // Add click ripple effect
      btn.addEventListener('click', function(e) {
        if (btn.classList.contains('processed-ripple')) return;
        btn.classList.add('processed-ripple');

        let ripple = document.createElement('span');
        let rect = btn.getBoundingClientRect();
        let size = Math.max(rect.width, rect.height);

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = e.clientX - rect.left - size/2 + 'px';
        ripple.style.top = e.clientY - rect.top - size/2 + 'px';

        ripple.className = 'ripple-effect';

        // Add ripple styles dynamically
        ripple.style.position = 'absolute';
        ripple.style.background = 'rgba(255, 255, 255, 0.3)';
        ripple.style.borderRadius = '50%';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s linear';
        ripple.style.pointerEvents = 'none';

        // Make button relative for absolute ripple
        if (getComputedStyle(btn).position === 'static') {
          btn.style.position = 'relative';
        }

        // Ensure child elements like ripple don't exceed the button unless we don't want overflow hidden
        if (!btn.classList.contains('dropdown') && !btn.hasAttribute('data-bs-toggle') && !btn.classList.contains('no-overflow-hide')) {
             btn.style.overflow = 'hidden';
        }

        btn.appendChild(ripple);

        // Remove ripple after animation
        setTimeout(() => {
          ripple.remove();
          btn.classList.remove('processed-ripple');
        }, 600);
      });
    });

    // Add keyframes for ripple if not exists
    if (!document.getElementById('ripple-style')) {
      const style = document.createElement('style');
      style.id = 'ripple-style';
      style.textContent = `
        @keyframes ripple {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }

    // Enhance inputs
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"], textarea');
    inputs.forEach(input => {
      if(input.classList.contains('processed-input')) return;
      input.classList.add('processed-input');

      input.addEventListener('focus', () => {
        input.style.boxShadow = '0 0 10px rgba(0, 243, 255, 0.5)';
        input.style.borderColor = 'rgba(0, 243, 255, 0.8)';
        input.style.transition = 'all 0.3s ease';
      });
      input.addEventListener('blur', () => {
        input.style.boxShadow = '';
        input.style.borderColor = '';
      });
    });

    // Particle effect on background (subtle)
    createSubtleParticles();
  });

  function createSubtleParticles() {
    if(document.getElementById('modern-ui-particles')) return;

    const canvas = document.createElement('canvas');
    canvas.id = 'modern-ui-particles';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.3';
    document.body.prepend(canvas);

    const ctx = canvas.getContext('2d');
    let width, height;

    function resize() {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    const particles = [];
    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 2 + 1,
        dx: (Math.random() - 0.5) * 0.5,
        dy: (Math.random() - 0.5) * 0.5
      });
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = 'rgba(0, 243, 255, 0.5)';

      particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();

        p.x += p.dx;
        p.y += p.dy;

        if (p.x < 0 || p.x > width) p.dx *= -1;
        if (p.y < 0 || p.y > height) p.dy *= -1;
      });

      requestAnimationFrame(animate);
    }

    animate();
  }
})();
