(function() {
  const trailDots = [];
  const numDots = 10;
  for (let i = 0; i < numDots; i++) {
    const dot = document.createElement('div');
    dot.className = 'mouse-trail-dot';
    document.body.appendChild(dot);
    trailDots.push({ el: dot, x: 0, y: 0 });
  }

  let mouseX = 0;
  let mouseY = 0;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function animateTrail() {
    let x = mouseX;
    let y = mouseY;
    trailDots.forEach((dot, index) => {
      const nextDot = trailDots[index + 1] || trailDots[0];
      dot.x += (x - dot.x) * 0.3;
      dot.y += (y - dot.y) * 0.3;
      dot.el.style.transform = `translate(${dot.x}px, ${dot.y}px) scale(${1 - index/numDots})`;
      x = dot.x;
      y = dot.y;
    });
    requestAnimationFrame(animateTrail);
  }
  animateTrail();

  function enhanceButtons() {
    const buttons = document.querySelectorAll('button, .btn');
    buttons.forEach(btn => {
      if (btn.classList.contains('modern-enhanced')) return;
      btn.classList.add('modern-enhanced');
      btn.classList.add('modern-hover-effect');

      if (getComputedStyle(btn).position === 'static') {
        btn.style.position = 'relative';
      }

      const rippleContainer = document.createElement('div');
      rippleContainer.className = 'ui-ripple-container';
      btn.appendChild(rippleContainer);

      btn.addEventListener('click', function(e) {
          const rect = btn.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;

          const ripple = document.createElement('span');
          ripple.className = 'ui-ripple';
          const size = Math.max(rect.width, rect.height);
          ripple.style.width = ripple.style.height = `${size}px`;
          ripple.style.left = `${x - size/2}px`;
          ripple.style.top = `${y - size/2}px`;

          rippleContainer.appendChild(ripple);
          ripple.addEventListener('animationend', () => {
              ripple.remove();
          });

          if (typeof btn.animate === 'function') {
              const animation = btn.animate([
                  { transform: 'scale(0.95)' },
                  { transform: 'scale(1)' }
              ], {
                  duration: 150,
                  composite: 'add'
              });
              if(animation) animation.onfinish = () => animation.cancel();
          }
      });
    });
  }

  enhanceButtons();
  const observer = new MutationObserver((mutations) => {
      let shouldEnhance = false;
      mutations.forEach(m => {
          if (m.addedNodes.length > 0) shouldEnhance = true;
      });
      if (shouldEnhance) enhanceButtons();
  });
  if(document.body) {
     observer.observe(document.body, { childList: true, subtree: true });
  } else {
     document.addEventListener('DOMContentLoaded', () => {
         observer.observe(document.body, { childList: true, subtree: true });
     });
  }
})();
