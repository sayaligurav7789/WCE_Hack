document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('messages-container');
    const welcomeScreen = document.getElementById('welcome-screen');
    const newChatBtn = document.getElementById('new-chat-btn');
    const historyList = document.getElementById('history-list');

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
        sendBtn.disabled = userInput.value.trim() === '';
    });

    // Handle Enter key
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    newChatBtn.addEventListener('click', () => {
        fetch('/clear', { method: 'POST' })
            .then(() => {
                messagesContainer.innerHTML = '';
                messagesContainer.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                historyList.innerHTML = '';
            });
    });

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Hide welcome screen on first message
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }

        // Add user message to UI
        appendMessage('user', text);
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.disabled = true;

        // Add typing indicator
        const typingId = appendMessage('assistant', '<i class="fas fa-circle-notch fa-spin"></i> Thinking...', true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            
            // Remove typing indicator and add response
            document.getElementById(typingId).remove();
            
            if (data.error) {
                appendMessage('assistant', 'Error: ' + data.error);
            } else {
                appendMessage('assistant', data.content, false, data.references);
                addToHistory(text);
            }
        } catch (err) {
            document.getElementById(typingId).remove();
            appendMessage('assistant', 'Error connecting to server.');
        }
    }

    function appendMessage(role, content, isHtml = false, references = null) {
        const id = 'msg-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.id = id;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '🧠';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        if (isHtml) {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.textContent = content;
        }

        if (references && (references.sections.length > 0 || references.pages.length > 0)) {
            const refDiv = document.createElement('div');
            refDiv.className = 'references';
            let refText = '';
            if (references.sections.length > 0) {
                refText += `<b>Sections:</b> ${references.sections.join(', ')}<br>`;
            }
            if (references.pages.length > 0) {
                refText += `<b>Pages:</b> ${references.pages.join(', ')}`;
            }
            refDiv.innerHTML = refText;
            contentDiv.appendChild(refDiv);
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        messagesContainer.appendChild(msgDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        return id;
    }

    function addToHistory(text) {
        const historyItem = document.createElement('div');
        historyItem.className = 'new-chat-btn'; // Reusing style
        historyItem.style.marginBottom = '5px';
        historyItem.style.fontSize = '0.85rem';
        historyItem.style.whiteSpace = 'nowrap';
        historyItem.style.overflow = 'hidden';
        historyItem.style.textOverflow = 'ellipsis';
        historyItem.innerHTML = `<i class="far fa-comment"></i> ${text}`;
        historyList.prepend(historyItem);
    }
});
