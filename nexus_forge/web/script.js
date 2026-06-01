document.addEventListener('DOMContentLoaded', () => {

    // UI Elements
    const listTodo = document.getElementById('list-todo');
    const listInProgress = document.getElementById('list-in-progress');
    const listDone = document.getElementById('list-done');

    const countTodo = document.querySelector('#col-todo .task-count');
    const countInProgress = document.querySelector('#col-in-progress .task-count');
    const countDone = document.querySelector('#col-done .task-count');

    // Matrix Rain Setup
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');
    let matrixInterval;
    let isMatrixActive = true;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*';
    const fontSize = 14;
    let columns = canvas.width / fontSize;
    let drops = [];
    for (let x = 0; x < columns; x++) {
        drops[x] = 1;
    }

    function drawMatrix() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#00f0ff'; // Neon blue for matrix
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            const text = letters.charAt(Math.floor(Math.random() * letters.length));
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    function toggleMatrix() {
        if (isMatrixActive) {
            clearInterval(matrixInterval);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            isMatrixActive = false;
        } else {
            // Re-calc columns in case of resize while paused
            columns = canvas.width / fontSize;
            drops = [];
            for (let x = 0; x < columns; x++) drops[x] = 1;
            matrixInterval = setInterval(drawMatrix, 33);
            isMatrixActive = true;
        }
    }

    document.querySelector('.matrix-rain-toggle').addEventListener('click', toggleMatrix);
    matrixInterval = setInterval(drawMatrix, 33);

    // Kanban Logic
    let lastTasksJSON = "";

    function createTaskCard(task) {
        return `
            <div class="task-card" data-status="${task.status}" id="task-${task.id}">
                <div class="task-spec">[ ${task.spec_file} ]</div>
                <div class="task-file">${task.filepath}</div>
                <div class="task-desc">${task.description}</div>
            </div>
        `;
    }

    async function fetchTasks() {
        try {
            const response = await fetch('/api/tasks');
            if (!response.ok) throw new Error('Network response was not ok');

            const tasks = await response.json();
            const currentTasksJSON = JSON.stringify(tasks);

            // Only re-render if data has changed to prevent UI jitter
            if (currentTasksJSON !== lastTasksJSON) {
                renderTasks(tasks);
                lastTasksJSON = currentTasksJSON;
            }

        } catch (error) {
            console.error('Error fetching tasks:', error);
        }
    }

    function renderTasks(tasks) {
        let todoHTML = '';
        let inProgressHTML = '';
        let doneHTML = '';

        let tCount = 0, pCount = 0, dCount = 0;

        tasks.forEach(task => {
            const card = createTaskCard(task);
            if (task.status === 'TODO') {
                todoHTML += card;
                tCount++;
            } else if (task.status === 'IN_PROGRESS') {
                inProgressHTML += card;
                pCount++;
            } else if (task.status === 'DONE') {
                doneHTML += card;
                dCount++;
            }
        });

        // Update DOM
        listTodo.innerHTML = todoHTML;
        listInProgress.innerHTML = inProgressHTML;
        listDone.innerHTML = doneHTML;

        countTodo.textContent = tCount;
        countInProgress.textContent = pCount;
        countDone.textContent = dCount;
    }

    // Initial fetch and set interval
    fetchTasks();
    setInterval(fetchTasks, 1000); // Poll every second
});