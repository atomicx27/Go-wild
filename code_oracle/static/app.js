document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('query-input');
    const chatContainer = document.getElementById('chat-container');
    const ragToggle = document.getElementById('rag-toggle');
    const submitBtn = document.getElementById('submit-btn');

    // Simple markdown to HTML formatter for code blocks and bold text
    function formatMarkdown(text) {
        let html = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\n/g, '<br>');
        return html;
    }

    function addMessage(sender, content, isHtml = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? 'USR' : 'ORC';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        if (isHtml) {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.textContent = content;
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        chatContainer.appendChild(msgDiv);

        chatContainer.scrollTop = chatContainer.scrollHeight;
        return contentDiv;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const query = input.value.trim();
        if (!query) return;

        const useRag = ragToggle.checked;

        // Add User Message
        addMessage('user', query);
        input.value = '';
        input.disabled = true;
        submitBtn.disabled = true;

        // Prepare Oracle Message Box
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message oracle';

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = 'ORC';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';

        const snippetsDiv = document.createElement('div');
        snippetsDiv.className = 'snippets';
        snippetsDiv.style.display = 'none';

        const textDiv = document.createElement('div');
        textDiv.className = 'text-response';
        textDiv.innerHTML = '<span class="loading-dots">Consulting the Oracle</span>';

        contentDiv.appendChild(snippetsDiv);
        contentDiv.appendChild(textDiv);

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query, use_rag: useRag })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let fullText = '';

            textDiv.innerHTML = ''; // Clear loading

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });

                // The chunk might contain multiple JSON objects separated by newlines
                const lines = chunk.split('\n').filter(line => line.trim());

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line);

                        if (data.type === 'snippets') {
                            if (data.data.length > 0) {
                                snippetsDiv.style.display = 'block';
                                snippetsDiv.innerHTML = '<strong>Sources:</strong><br>';
                                data.data.forEach(file => {
                                    snippetsDiv.innerHTML += `<span class="snippet-tag">${file}</span>`;
                                });
                            }
                        } else if (data.type === 'text') {
                            fullText += data.data;
                            // Re-format everything on each chunk to handle markdown correctly
                            textDiv.innerHTML = formatMarkdown(fullText);
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        } else if (data.type === 'done') {
                            // Finished
                        }
                    } catch (e) {
                        console.error('Error parsing chunk:', e, line);
                    }
                }
            }
        } catch (error) {
            console.error('Fetch error:', error);
            textDiv.innerHTML = `<span style="color: #ff5555;">Connection Error: ${error.message}</span>`;
        } finally {
            input.disabled = false;
            submitBtn.disabled = false;
            input.focus();
        }
    });
});