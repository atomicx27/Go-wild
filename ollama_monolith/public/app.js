// --- THREE.JS SCENE SETUP ---
const container = document.getElementById('canvas-container');

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x000000, 0.001);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 30;

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
container.appendChild(renderer.domElement);

// --- THE MONOLITH ---
// Geometry: Tall, slightly deep box
const geometry = new THREE.BoxGeometry(8, 24, 4);

// Material: Dark, glossy obsidian
const material = new THREE.MeshStandardMaterial({
    color: 0x050505,
    roughness: 0.1,
    metalness: 0.8,
});

const monolith = new THREE.Mesh(geometry, material);
scene.add(monolith);

// --- LIGHTING ---
const ambientLight = new THREE.AmbientLight(0x222222);
scene.add(ambientLight);

// Main dramatic spotlight
const spotLight = new THREE.SpotLight(0xffffff, 2);
spotLight.position.set(20, 50, 50);
spotLight.angle = Math.PI / 4;
spotLight.penumbra = 0.5;
scene.add(spotLight);

// Deep purple/blue underlight for cosmic vibe
const pointLight = new THREE.PointLight(0x4b0082, 3, 100);
pointLight.position.set(-10, -20, -10);
scene.add(pointLight);

// --- PARTICLES (STARDUST) ---
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 2000;
const posArray = new Float32Array(particlesCount * 3);

for(let i = 0; i < particlesCount * 3; i++) {
    // Spread particles in a wide area
    posArray[i] = (Math.random() - 0.5) * 100;
}

particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
const particlesMaterial = new THREE.PointsMaterial({
    size: 0.05,
    color: 0x88ccff,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending
});

const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

// --- ANIMATION STATE ---
let isQuerying = false;
let baseRotationSpeed = 0.002;
let currentRotationSpeed = baseRotationSpeed;
let targetRotationSpeed = baseRotationSpeed;
let monolithFloatOffset = 0;

function animate() {
    requestAnimationFrame(animate);

    // Smoothly transition rotation speed
    currentRotationSpeed += (targetRotationSpeed - currentRotationSpeed) * 0.05;

    monolith.rotation.y += currentRotationSpeed;
    monolith.rotation.x += currentRotationSpeed * 0.2;

    // Slow floating effect
    monolithFloatOffset += 0.01;
    monolith.position.y = Math.sin(monolithFloatOffset) * 2;

    // Rotate particles slowly
    particlesMesh.rotation.y -= 0.0005;
    particlesMesh.rotation.x -= 0.0002;

    // Pulse lights if querying
    if (isQuerying) {
        pointLight.intensity = 3 + Math.sin(Date.now() * 0.01) * 2;
        pointLight.color.setHex(0xff0000); // Shift to red/aggressive
    } else {
        pointLight.intensity = 3;
        pointLight.color.setHex(0x4b0082); // Back to purple
    }

    renderer.render(scene, camera);
}
animate();

// Handle Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// --- UI INTERACTION LOGIC ---
const queryInput = document.getElementById('query-input');
const responseText = document.getElementById('response-text');

queryInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        const query = queryInput.value.trim();
        if (!query) return;

        // Reset UI
        queryInput.value = '';
        queryInput.blur();
        queryInput.placeholder = 'THE VOID IS CONTEMPLATING...';
        queryInput.disabled = true;

        responseText.classList.remove('visible');
        setTimeout(() => { responseText.innerHTML = ''; }, 500);

        // trigger aggressive animation
        isQuerying = true;
        targetRotationSpeed = 0.08;

        try {
            const res = await fetch('/api/oracle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await res.json();

            // Return animation to normal
            isQuerying = false;
            targetRotationSpeed = baseRotationSpeed;

            // Display Response
            responseText.classList.add('visible');
            await typeWriterEffect(responseText, data.response);

        } catch (error) {
            isQuerying = false;
            targetRotationSpeed = baseRotationSpeed;

            responseText.classList.add('visible');
            responseText.innerHTML = `[ERROR SCALAR] CONNECT TO THE LOCALHOST DEMON.`;
            queryInput.classList.add('shake');
            setTimeout(() => queryInput.classList.remove('shake'), 500);
        } finally {
            queryInput.placeholder = 'Whisper into the void...';
            queryInput.disabled = false;
        }
    }
});

async function typeWriterEffect(element, text, speed = 40) {
    element.innerHTML = '';
    element.classList.add('typing-cursor');

    // Initial dramatic pause
    await new Promise(r => setTimeout(r, 1000));

    for (let i = 0; i < text.length; i++) {
        element.innerHTML += text.charAt(i);
        // Slower for punctuation
        const currentSpeed = (text.charAt(i) === '.' || text.charAt(i) === ',') ? speed * 6 : speed + (Math.random() * 20 - 10);
        await new Promise(r => setTimeout(r, currentSpeed));
    }
    element.classList.remove('typing-cursor');
}
