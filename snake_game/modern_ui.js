
// Modern UI Enhancements
(function() {
    // 1. Global Page Fade In
    const style = document.createElement('style');
    style.innerHTML = `
        body {
            animation: globalFadeIn 0.8s ease-out forwards;
        }
        @keyframes globalFadeIn {
            from { opacity: 0; filter: blur(3px); }
            to { opacity: 1; filter: blur(0px); }
        }
        /* Cyberpunk Interactive Cursor */
        #cyberCursor {
            position: fixed;
            top: 0;
            left: 0;
            width: 20px;
            height: 20px;
            border: 2px solid #00ffcc;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 999999;
            transition: width 0.2s, height 0.2s, background-color 0.2s, border-color 0.2s, box-shadow 0.2s;
            box-shadow: 0 0 10px #00ffcc, inset 0 0 5px #00ffcc;
            mix-blend-mode: screen;
        }
        #cyberCursorTrail {
            position: fixed;
            top: 0;
            left: 0;
            width: 8px;
            height: 8px;
            background-color: #ff00ff;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 999998;
            box-shadow: 0 0 10px #ff00ff;
            transition: transform 0.1s;
        }
        /* Generic Button Enhancements (Safe, minimal) */
        button, .btn, .cyber-btn {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        button:hover, .btn:hover, .cyber-btn:hover {
            transform: translateY(-2px);
        }
    `;
    document.head.appendChild(style);

    // 2. Add Cursor Elements
    const cursor = document.createElement('div');
    cursor.id = 'cyberCursor';
    document.body.appendChild(cursor);

    const trail = document.createElement('div');
    trail.id = 'cyberCursorTrail';
    document.body.appendChild(trail);

    // 3. Cursor Logic
    let mouseX = 0;
    let mouseY = 0;
    let trailX = 0;
    let trailY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        cursor.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%, -50%)`;
    });

    function animateTrail() {
        trailX += (mouseX - trailX) * 0.15;
        trailY += (mouseY - trailY) * 0.15;
        trail.style.transform = `translate(${trailX}px, ${trailY}px) translate(-50%, -50%)`;
        requestAnimationFrame(animateTrail);
    }
    animateTrail();

    // 4. Hover Effects using Event Delegation (solves dynamic DOM element issue)
    document.addEventListener('mouseover', (e) => {
        const target = e.target;
        // Check if we hovered over something interactive
        const isInteractive = target.closest('button, a, input, select, textarea, .task, .node, .cyber-button');
        if (isInteractive) {
            cursor.style.width = '40px';
            cursor.style.height = '40px';
            cursor.style.backgroundColor = 'rgba(0, 255, 204, 0.2)';
            cursor.style.borderColor = '#ff00ff';
            cursor.style.boxShadow = '0 0 20px #ff00ff, inset 0 0 10px #ff00ff';
        }
    });

    document.addEventListener('mouseout', (e) => {
        const target = e.target;
        const isInteractive = target.closest('button, a, input, select, textarea, .task, .node, .cyber-button');
        if (isInteractive) {
            cursor.style.width = '20px';
            cursor.style.height = '20px';
            cursor.style.backgroundColor = 'transparent';
            cursor.style.borderColor = '#00ffcc';
            cursor.style.boxShadow = '0 0 10px #00ffcc, inset 0 0 5px #00ffcc';
        }
    });
})();
