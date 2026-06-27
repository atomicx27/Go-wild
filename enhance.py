import os

html_files = [
    './neuro_clash/static/index.html',
    './ollama_thought_weaver/public/index.html',
    './cosmic_synesthesia/index.html',
    './zen_kanban/index.html',
    './nexus_forge/web/index.html',
    './synth_scribe/template.html',
    './code_metropolis/public/index.html',
    './neural_kanban/frontend/index.html',
    './concept_weaver/index.html',
    './code_oracle/static/index.html',
    './ollama_monolith/public/index.html',
    './synapse_forge/static/index.html',
    './snake_game/index.html',
    './nexus_core/static/index.html',
    './ollama_overdrive/public/index.html'
]

js_content = """(function() {
    // Mouse trail effect
    const numParticles = 20;
    const particles = [];

    for (let i = 0; i < numParticles; i++) {
        const p = document.createElement('div');
        p.className = 'global-mouse-trail-particle';
        document.body.appendChild(p);
        particles.push({el: p, x: 0, y: 0, targetX: 0, targetY: 0});
    }

    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animate() {
        let x = mouseX;
        let y = mouseY;
        particles.forEach((p, index) => {
            p.x += (x - p.x) * 0.3;
            p.y += (y - p.y) * 0.3;
            p.el.style.transform = `translate(${p.x}px, ${p.y}px) scale(${1 - index/numParticles})`;
            x = p.x;
            y = p.y;
        });
        requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);

    // Ripple effect for interactive elements
    document.addEventListener('click', (e) => {
        const target = e.target.closest('button, .btn, a, input[type="submit"]');
        if (target) {
            const rect = target.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const rippleContainer = document.createElement('div');
            rippleContainer.className = 'global-ripple-container';

            const ripple = document.createElement('div');
            ripple.className = 'global-ripple';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            rippleContainer.appendChild(ripple);

            if(window.getComputedStyle(target).position === 'static') {
                target.style.position = 'relative';
            }
            target.appendChild(rippleContainer);

            const animation = ripple.animate([
                { transform: 'scale(0) translate(-50%, -50%)', opacity: 0.8 },
                { transform: 'scale(20) translate(-50%, -50%)', opacity: 0 }
            ], {
                duration: 600,
                easing: 'ease-out',
                composite: 'add'
            });

            animation.onfinish = () => {
                animation.cancel();
                rippleContainer.remove();
            };
        }
    });

    // Add generic interactive classes for styling
    document.querySelectorAll('button, .btn, input[type="submit"]').forEach(el => {
        if (!el.classList.contains('global-interactive-el')) {
            el.classList.add('global-interactive-el');
        }
    });

})();
"""

css_content = """.global-mouse-trail-particle {
    position: fixed;
    top: 0;
    left: 0;
    width: 8px;
    height: 8px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.8) 0%, rgba(139, 92, 246, 0) 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9999;
    mix-blend-mode: screen;
}

.global-ripple-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    border-radius: inherit;
    pointer-events: none;
    z-index: 0;
}

.global-ripple {
    position: absolute;
    width: 20px;
    height: 20px;
    background: rgba(255, 255, 255, 0.4);
    border-radius: 50%;
    pointer-events: none;
    transform-origin: 0 0;
}

.global-interactive-el {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.global-interactive-el:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.global-interactive-el:active {
    transform: translateY(0);
    box-shadow: 0 2px 6px rgba(139, 92, 246, 0.2);
}
"""

for filepath in html_files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue

    dir_name = os.path.dirname(filepath)
    js_path = os.path.join(dir_name, 'ui_enhancement.js')
    css_path = os.path.join(dir_name, 'ui_enhancement.css')

    with open(js_path, 'w') as f:
        f.write(js_content)

    with open(css_path, 'w') as f:
        f.write(css_content)

    with open(filepath, 'r') as f:
        html_content = f.read()

    css_link = '\n    <link rel="stylesheet" href="ui_enhancement.css">\n'
    if 'ui_enhancement.css' not in html_content:
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', f'{css_link}</head>')
        else:
            html_content = css_link + html_content

    js_link = '\n    <script src="ui_enhancement.js"></script>\n'
    if 'ui_enhancement.js' not in html_content:
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{js_link}</body>')
        else:
            html_content = html_content + js_link

    with open(filepath, 'w') as f:
        f.write(html_content)

    print(f"Enhanced {filepath}")
