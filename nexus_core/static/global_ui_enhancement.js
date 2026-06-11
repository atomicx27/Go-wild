(function() {
    // Inject global cyberpunk styles dynamically
    const style = document.createElement('style');
    style.textContent = `
        /* Global Cyberpunk & Neon Enhancements */
        :root {
            --cyber-neon: #0ff;
            --cyber-pink: #f0f;
            --cyber-bg: rgba(10, 10, 15, 0.95);
            --glass-bg: rgba(20, 20, 30, 0.4);
            --glass-border: rgba(0, 255, 255, 0.2);
        }

        body {
            transition: background-color 0.5s ease;
        }

        /* Glassmorphism for containers */
        .glass-panel {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            border-radius: 10px;
        }

        /* Neon Text Glow */
        .neon-text {
            color: #fff;
            text-shadow: 0 0 5px var(--cyber-neon), 0 0 10px var(--cyber-neon), 0 0 20px var(--cyber-neon);
        }

        /* Interactive Hover Glow */
        .interactive-element {
            transition: all 0.3s ease;
        }

        .interactive-element:hover {
            box-shadow: 0 0 15px var(--cyber-neon);
            border-color: var(--cyber-neon);
            transform: translateY(-2px);
        }

        /* Particle Trail Canvas */
        #cyber-particle-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9999;
        }

        /* Glow effect for buttons */
        button, .btn {
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        button::after, .btn::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.3s, height 0.3s;
        }

        button:active::after, .btn:active::after {
            width: 200px;
            height: 200px;
        }
    `;
    document.head.appendChild(style);

    // Particle cursor trail
    const canvas = document.createElement('canvas');
    canvas.id = 'cyber-particle-canvas';
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];

    class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.size = Math.random() * 3 + 1;
            this.speedX = Math.random() * 2 - 1;
            this.speedY = Math.random() * 2 - 1;
            this.life = 1;
            this.color = Math.random() > 0.5 ? '#0ff' : '#f0f';
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.life -= 0.02;
            this.size = Math.max(0, this.size - 0.05);
        }

        draw() {
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.life;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    let mouseX = width / 2;
    let mouseY = height / 2;
    let isMouseMoving = false;

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        isMouseMoving = true;
        for (let i = 0; i < 2; i++) {
            particles.push(new Particle(mouseX, mouseY));
        }
    });

    function animateParticles() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            if (particles[i].life <= 0 || particles[i].size <= 0) {
                particles.splice(i, 1);
                i--;
            }
        }
        requestAnimationFrame(animateParticles);
    }
    animateParticles();

    // Event Delegation for hover effects and interactions
    document.body.addEventListener('mouseover', (e) => {
        const target = e.target;
        if (target.tagName === 'BUTTON' || target.tagName === 'A' || target.classList.contains('card') || target.closest('.interactive-element')) {
            target.classList.add('interactive-element');
        }
    });

    document.body.addEventListener('mouseout', (e) => {
        const target = e.target;
        // Keep interactive-element class if we want the transition to reverse smoothly,
        // or we could let the CSS handle it based on hover state.
    });

    // MutationObserver to apply glassmorphism to main containers
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        applyGlassmorphism(node);
                    }
                });
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    function applyGlassmorphism(rootNode) {
        // Apply to likely container elements
        const containers = rootNode.querySelectorAll ? rootNode.querySelectorAll('.container, main, .panel, .card, .chat-container') : [];
        const processNode = (node) => {
            if (node.classList && (node.classList.contains('container') ||
                node.tagName === 'MAIN' ||
                node.classList.contains('panel') ||
                node.classList.contains('card') ||
                node.classList.contains('chat-container'))) {
                node.classList.add('glass-panel');
            }
        }

        processNode(rootNode);
        containers.forEach(processNode);
    }

    // Initial apply
    applyGlassmorphism(document.body);

    // Add neon text to main headings
    const headings = document.querySelectorAll('h1, h2');
    headings.forEach(h => h.classList.add('neon-text'));

})();
