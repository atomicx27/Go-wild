document.addEventListener("DOMContentLoaded", () => {
    // State
    let modules = [];
    let currentModule = null;
    let currentFlashcardIndex = 0;
    let chatHistory = [];

    // DOM Elements
    const moduleListEl = document.getElementById("module-list");
    const noModuleSelectedEl = document.getElementById("no-module-selected");
    const moduleViewEl = document.getElementById("module-view");

    // UI Elements
    const moduleTitleEl = document.getElementById("module-title");
    const personaNameEl = document.getElementById("persona-name");
    const moduleSummaryEl = document.getElementById("module-summary");

    // Tabs
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    // Flashcards
    const flashcardDeckEl = document.getElementById("flashcard-deck");
    const prevCardBtn = document.getElementById("prev-card");
    const nextCardBtn = document.getElementById("next-card");
    const cardCounterEl = document.getElementById("card-counter");

    // Quiz
    const quizContainerEl = document.getElementById("quiz-container");
    const submitQuizBtn = document.getElementById("submit-quiz");
    const quizResultsEl = document.getElementById("quiz-results");

    // Chat
    const chatHistoryEl = document.getElementById("chat-history");
    const chatInputEl = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");

    // Fetch Modules
    async function fetchModules() {
        try {
            const response = await fetch("/api/modules");
            const data = await response.json();
            modules = data.modules;
            renderModuleList();
        } catch (err) {
            console.error("Error fetching modules:", err);
            moduleListEl.innerHTML = "<li class='error'>ERR: KNOWLEDGEBASE OFFLINE</li>";
        }
    }

    // Render Module List Sidebar
    function renderModuleList() {
        moduleListEl.innerHTML = "";
        if (modules.length === 0) {
            moduleListEl.innerHTML = "<li>No engrams found. Upload .txt files to /inbox</li>";
            return;
        }

        modules.forEach(mod => {
            const li = document.createElement("li");
            li.className = "module-item";
            li.innerHTML = `<span class="module-item-title">${mod.title}</span><br><small>${mod.id}</small>`;
            li.addEventListener("click", () => loadModule(mod, li));
            moduleListEl.appendChild(li);
        });
    }

    // Load a specific module
    function loadModule(mod, listItemEl) {
        // UI updates
        document.querySelectorAll(".module-item").forEach(el => el.classList.remove("active"));
        if(listItemEl) listItemEl.classList.add("active");

        noModuleSelectedEl.classList.add("hidden");
        moduleViewEl.classList.remove("hidden");

        // Set State
        currentModule = mod;
        chatHistory = []; // Reset chat history for new module

        // Populate Header/Summary
        moduleTitleEl.textContent = mod.title || "Unknown Module";
        personaNameEl.textContent = mod.persona_name || "Unknown Persona";
        moduleSummaryEl.textContent = mod.summary || "No data.";

        // Render sections
        renderFlashcards();
        renderQuiz();
        renderChatInit();

        // Reset to first tab
        tabBtns[0].click();
    }

    // Tab Navigation
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active", "hidden"));
            tabPanes.forEach(p => p.classList.add("hidden"));

            btn.classList.add("active");
            document.getElementById(btn.dataset.target).classList.remove("hidden");
            document.getElementById(btn.dataset.target).classList.add("active");
        });
    });

    // --- FLASHCARDS ---
    function renderFlashcards() {
        flashcardDeckEl.innerHTML = "";
        currentFlashcardIndex = 0;

        if (!currentModule.flashcards || currentModule.flashcards.length === 0) {
            flashcardDeckEl.innerHTML = "<div class='card-face'>No flashcards available.</div>";
            cardCounterEl.textContent = "0 / 0";
            return;
        }

        currentModule.flashcards.forEach((card, idx) => {
            const cardEl = document.createElement("div");
            cardEl.className = `flashcard ${idx === 0 ? "active" : ""}`;
            cardEl.innerHTML = `
                <div class="card-face">${card.question}</div>
                <div class="card-face card-back">${card.answer}</div>
            `;
            // Flip logic
            cardEl.addEventListener("click", () => cardEl.classList.toggle("flipped"));
            flashcardDeckEl.appendChild(cardEl);
        });

        updateFlashcardControls();
    }

    function updateFlashcardControls() {
        if (!currentModule.flashcards) return;
        cardCounterEl.textContent = `${currentFlashcardIndex + 1} / ${currentModule.flashcards.length}`;
        const cards = document.querySelectorAll(".flashcard");
        cards.forEach((c, idx) => {
            c.classList.remove("active");
            c.classList.remove("flipped"); // reset flip
            if (idx === currentFlashcardIndex) c.classList.add("active");
        });
    }

    prevCardBtn.addEventListener("click", () => {
        if (!currentModule.flashcards || currentFlashcardIndex === 0) return;
        currentFlashcardIndex--;
        updateFlashcardControls();
    });

    nextCardBtn.addEventListener("click", () => {
        if (!currentModule.flashcards || currentFlashcardIndex === currentModule.flashcards.length - 1) return;
        currentFlashcardIndex++;
        updateFlashcardControls();
    });

    // --- QUIZ ---
    function renderQuiz() {
        quizContainerEl.innerHTML = "";
        quizResultsEl.classList.add("hidden");

        if (!currentModule.quiz || currentModule.quiz.length === 0) {
            quizContainerEl.innerHTML = "<p>No quiz available.</p>";
            submitQuizBtn.classList.add("hidden");
            return;
        }

        submitQuizBtn.classList.remove("hidden");

        currentModule.quiz.forEach((q, qIndex) => {
            const qDiv = document.createElement("div");
            qDiv.className = "quiz-question";
            qDiv.dataset.index = qIndex;

            const qText = document.createElement("div");
            qText.className = "question-text";
            qText.textContent = `${qIndex + 1}. ${q.question}`;
            qDiv.appendChild(qText);

            const optionsList = document.createElement("ul");
            optionsList.className = "options-list";

            q.options.forEach((opt, optIndex) => {
                const optLi = document.createElement("li");
                optLi.className = "option-item";
                optLi.textContent = opt;
                optLi.dataset.optIndex = optIndex;

                optLi.addEventListener("click", () => {
                    // Deselect others in this question
                    optionsList.querySelectorAll(".option-item").forEach(i => i.classList.remove("selected"));
                    optLi.classList.add("selected");
                });

                optionsList.appendChild(optLi);
            });

            qDiv.appendChild(optionsList);
            quizContainerEl.appendChild(qDiv);
        });
    }

    submitQuizBtn.addEventListener("click", () => {
        let score = 0;
        const total = currentModule.quiz.length;

        document.querySelectorAll(".quiz-question").forEach(qDiv => {
            const qIndex = parseInt(qDiv.dataset.index);
            const correctIndex = currentModule.quiz[qIndex].correct_index;

            const options = qDiv.querySelectorAll(".option-item");
            options.forEach(opt => {
                const optIndex = parseInt(opt.dataset.optIndex);
                if (opt.classList.contains("selected")) {
                    if (optIndex === correctIndex) {
                        opt.classList.add("correct");
                        score++;
                    } else {
                        opt.classList.add("incorrect");
                    }
                }
                // Highlight correct answer if they missed it
                if (optIndex === correctIndex) {
                    opt.classList.add("correct");
                }
            });
        });

        quizResultsEl.textContent = `SYSTEM ANALYSIS: ${score} / ${total} ACCURACY`;
        quizResultsEl.classList.remove("hidden");
        submitQuizBtn.classList.add("hidden");
    });

    // --- CHAT ---
    function renderChatInit() {
        chatHistoryEl.innerHTML = "";
        const greeting = currentModule.persona_greeting || "Neural link established. How can I assist?";
        addChatMessage(greeting, "tutor");
    }

    function addChatMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-msg msg-${sender}`;
        msgDiv.textContent = text;
        chatHistoryEl.appendChild(msgDiv);
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    }

    async function handleChatSend() {
        const text = chatInputEl.value.trim();
        if (!text || !currentModule) return;

        addChatMessage(text, "user");
        chatInputEl.value = "";
        chatInputEl.disabled = true;
        sendBtn.disabled = true;

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    module_id: currentModule.id,
                    message: text,
                    history: chatHistory
                })
            });

            if (response.ok) {
                const data = await response.json();
                addChatMessage(data.reply, "tutor");

                // Update history state
                chatHistory.push({ role: "user", content: text });
                chatHistory.push({ role: "assistant", content: data.reply });
            } else {
                addChatMessage("[ERR_CONNECTION_LOST]", "tutor");
            }
        } catch (err) {
            console.error(err);
            addChatMessage("[SYSTEM_FAILURE_DETECTED]", "tutor");
        } finally {
            chatInputEl.disabled = false;
            sendBtn.disabled = false;
            chatInputEl.focus();
        }
    }

    sendBtn.addEventListener("click", handleChatSend);
    chatInputEl.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleChatSend();
    });

    // Initial Fetch (poll every few seconds to see new modules)
    fetchModules();
    setInterval(fetchModules, 5000);
});
