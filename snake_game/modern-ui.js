// Modern UI Enhancements JavaScript

document.addEventListener('DOMContentLoaded', () => {
  // 1. Add fade-in effect to main containers or body if no main containers exist
  const containers = document.querySelectorAll('.container, main, #app, .app-container');
  if (containers.length > 0) {
    containers.forEach(el => el.classList.add('mui-fade-in'));
  } else {
    document.body.classList.add('mui-fade-in');
  }

  // 2. Ripple effect on buttons
  const buttons = document.querySelectorAll('button, .btn');
  buttons.forEach(btn => {
    // Ensure button is positioned relatively for the ripple container
    if (window.getComputedStyle(btn).position === 'static') {
      btn.style.position = 'relative';
    }

    // Add isolated ripple container
    const rippleContainer = document.createElement('div');
    rippleContainer.classList.add('mui-ripple-container');
    btn.appendChild(rippleContainer);

    btn.addEventListener('mousedown', function (e) {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const ripple = document.createElement('span');
      ripple.classList.add('mui-ripple');

      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${x - size / 2}px`;
      ripple.style.top = `${y - size / 2}px`;

      rippleContainer.appendChild(ripple);

      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });

  // 3. Mouse trail optimization using requestAnimationFrame and transform
  const trailCount = 5;
  const trails = [];

  for (let i = 0; i < trailCount; i++) {
    const trail = document.createElement('div');
    trail.classList.add('mui-trail');
    document.body.appendChild(trail);
    trails.push({ el: trail, x: 0, y: 0, targetX: 0, targetY: 0 });
  }

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function animateTrails() {
    let prevX = mouseX;
    let prevY = mouseY;

    trails.forEach((trail, index) => {
      // Lerp for smooth following
      const ease = 0.2 + (index * 0.05);
      trail.x += (prevX - trail.x) * ease;
      trail.y += (prevY - trail.y) * ease;

      trail.el.style.transform = `translate(${trail.x - 4}px, ${trail.y - 4}px) scale(${1 - index * 0.15})`;

      prevX = trail.x;
      prevY = trail.y;
    });

    requestAnimationFrame(animateTrails);
  }

  animateTrails();
});
