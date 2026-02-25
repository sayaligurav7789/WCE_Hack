document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('messages-container');
    const welcomeScreen = document.getElementById('welcome-screen');
    const newChatBtn = document.getElementById('new-chat-btn');
    const historyList = document.getElementById('history-list');
    const sidebar = document.querySelector('.sidebar');
    
    let currentChatId = Date.now().toString();
    let messageHistory = [];
    let chats = {};

    // Load chat history from localStorage
    loadChatHistory();

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 200) + 'px';
        sendBtn.disabled = userInput.value.trim() === '';
    });

    // Handle Enter key
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    userInput.focus();
    sendBtn.addEventListener('click', sendMessage);

    newChatBtn.addEventListener('click', () => {
        startNewChat();
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('open');
        }
    });

    // Mobile menu toggle
    const chatHeader = document.querySelector('.chat-header');
    chatHeader.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            sidebar.classList.toggle('open');
        }
    });

    function startNewChat() {
        fetch('/clear', { method: 'POST' })
            .then(() => {
                messagesContainer.innerHTML = '';
                messagesContainer.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                
                currentChatId = Date.now().toString();
                messageHistory = [];
                
                userInput.value = '';
                userInput.style.height = 'auto';
                sendBtn.disabled = true;
                
                updateHistorySidebar();
            });
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        if (welcomeScreen && welcomeScreen.style.display !== 'none') {
            welcomeScreen.style.display = 'none';
        }

        appendMessage('user', text);
        messageHistory.push({ role: 'user', content: text });
        
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.disabled = true;

        const typingId = showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: text,
                    chat_id: currentChatId 
                })
            });
            
            const data = await response.json();
            removeTypingIndicator(typingId);
            
            if (data.error) {
                appendMessage('assistant', '❌ ' + data.error);
                messageHistory.push({ role: 'assistant', content: 'Error: ' + data.error });
            } else {
                const formattedContent = formatResponse(data.content);
                appendMessage('assistant', formattedContent, false, data.references);
                messageHistory.push({ 
                    role: 'assistant', 
                    content: data.content,
                    references: data.references 
                });
                
                // Add to history sidebar only once per chat
                if (messageHistory.length === 2) {
                    addChatToHistory(text);
                }
                
                saveChatToStorage();
            }
        } catch (err) {
            removeTypingIndicator(typingId);
            const errorMsg = '⚠️ Connection error. Please try again.';
            appendMessage('assistant', errorMsg);
            messageHistory.push({ role: 'assistant', content: errorMsg });
        }
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = id;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        
        contentDiv.appendChild(typingIndicator);
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(contentDiv);
        
        messagesContainer.appendChild(typingDiv);
        scrollToBottom();
        
        return id;
    }

    function removeTypingIndicator(id) {
        const indicator = document.getElementById(id);
        if (indicator) indicator.remove();
    }

    function appendMessage(role, content, isHtml = false, references = null) {
        const id = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.id = id;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        
        if (role === 'user') {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        } else {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        if (isHtml) {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.innerHTML = formatResponse(content);
        }

        if (references && (references.sections?.length > 0 || references.pages?.length > 0)) {
            const refDiv = document.createElement('div');
            refDiv.className = 'references';
            let refText = '<b>📚 References</b><br>';
            if (references.sections?.length > 0) {
                refText += `📖 Sections: ${references.sections.join(', ')}<br>`;
            }
            if (references.pages?.length > 0) {
                refText += `📄 Pages: ${references.pages.join(', ')}`;
            }
            refDiv.innerHTML = refText;
            contentDiv.appendChild(refDiv);
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);
        messagesContainer.appendChild(msgDiv);
        
        scrollToBottom();
        
        return id;
    }

    function formatResponse(text) {
        if (!text) return '';
        
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        text = text.replace(/\n/g, '<br>');
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/`(.*?)`/g, '<code>$1</code>');
        text = text.replace(/^&gt; (.*$)/gm, '<blockquote>$1</blockquote>');
        
        return text;
    }

    function addChatToHistory(firstMessage) {
        // Check if chat already exists
        const existingChat = document.querySelector(`.history-item[data-chat-id="${currentChatId}"]`);
        if (existingChat) {
            return;
        }

        const historyItem = createHistoryItem(currentChatId, firstMessage);
        historyList.prepend(historyItem);
        
        // Limit history items to 50
        while (historyList.children.length > 50) {
            historyList.removeChild(historyList.lastChild);
        }
    }

    function createHistoryItem(chatId, previewText) {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.setAttribute('data-chat-id', chatId);
        
        // Create content container
        const contentDiv = document.createElement('div');
        contentDiv.className = 'history-item-content';
        
        const icon = document.createElement('i');
        icon.className = 'far fa-comment';
        
        const textSpan = document.createElement('span');
        const displayText = previewText.length > 30 ? previewText.substring(0, 30) + '...' : previewText;
        textSpan.textContent = displayText;
        
        contentDiv.appendChild(icon);
        contentDiv.appendChild(textSpan);
        
        // Create delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-chat-btn';
        deleteBtn.innerHTML = '<i class="fas fa-ellipsis-v"></i>';
        deleteBtn.setAttribute('aria-label', 'Delete chat');
        
        // Add click handler for delete
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering the chat load
            showDeleteConfirmation(chatId, historyItem);
        });
        
        historyItem.appendChild(contentDiv);
        historyItem.appendChild(deleteBtn);
        
        // Add click handler for loading chat
        historyItem.addEventListener('click', (e) => {
            // Don't load chat if clicking delete button
            if (!e.target.closest('.delete-chat-btn')) {
                loadChat(chatId);
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('open');
                }
            }
        });
        
        return historyItem;
    }

    function showDeleteConfirmation(chatId, historyItem) {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'confirmation-overlay';
        
        // Create confirmation dialog
        const dialog = document.createElement('div');
        dialog.className = 'delete-confirmation';
        dialog.innerHTML = `
            <h3>Delete Chat?</h3>
            <p>Are you sure you want to delete this conversation? This action cannot be undone.</p>
            <div class="confirmation-buttons">
                <button class="cancel-btn">Cancel</button>
                <button class="confirm-btn">Delete</button>
            </div>
        `;
        
        document.body.appendChild(overlay);
        document.body.appendChild(dialog);
        
        // Handle cancel
        const cancelBtn = dialog.querySelector('.cancel-btn');
        cancelBtn.addEventListener('click', () => {
            overlay.remove();
            dialog.remove();
        });
        
        // Handle confirm
        const confirmBtn = dialog.querySelector('.confirm-btn');
        confirmBtn.addEventListener('click', () => {
            deleteChat(chatId, historyItem);
            overlay.remove();
            dialog.remove();
        });
        
        // Click outside to cancel
        overlay.addEventListener('click', () => {
            overlay.remove();
            dialog.remove();
        });
    }

    function deleteChat(chatId, historyItem) {
        // Remove from DOM
        historyItem.remove();
        
        // Remove from localStorage
        const storedChats = JSON.parse(localStorage.getItem('psych-chats') || '{}');
        delete storedChats[chatId];
        localStorage.setItem('psych-chats', JSON.stringify(storedChats));
        
        // Update local chats object
        chats = storedChats;
        
        // If current chat is deleted, start new chat
        if (chatId === currentChatId) {
            startNewChat();
        }
    }

    function updateHistorySidebar() {
        document.querySelectorAll('.history-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeItem = document.querySelector(`.history-item[data-chat-id="${currentChatId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    function saveChatToStorage() {
        if (messageHistory.length === 0) return;
        
        const storedChats = JSON.parse(localStorage.getItem('psych-chats') || '{}');
        
        storedChats[currentChatId] = {
            id: currentChatId,
            messages: messageHistory,
            timestamp: Date.now(),
            preview: messageHistory[0]?.content || 'New chat'
        };
        
        localStorage.setItem('psych-chats', JSON.stringify(storedChats));
        chats = storedChats;
    }

    function loadChatHistory() {
        chats = JSON.parse(localStorage.getItem('psych-chats') || '{}');
        historyList.innerHTML = '';
        
        const sortedChats = Object.values(chats).sort((a, b) => b.timestamp - a.timestamp);
        
        sortedChats.forEach(chat => {
            const historyItem = createHistoryItem(chat.id, chat.preview);
            historyList.appendChild(historyItem);
        });
    }

    function loadChat(chatId) {
        const chat = chats[chatId];
        
        if (!chat) return;
        
        currentChatId = chatId;
        messageHistory = chat.messages;
        
        messagesContainer.innerHTML = '';
        
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }
        
        messageHistory.forEach(msg => {
            if (msg.role === 'user') {
                appendMessage('user', msg.content);
            } else {
                appendMessage('assistant', msg.content, false, msg.references);
            }
        });
        
        updateHistorySidebar();
        scrollToBottom();
    }

    function scrollToBottom() {
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }

    // Click outside handler for mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !e.target.closest('.chat-header')) {
                sidebar.classList.remove('open');
            }
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            userInput.focus();
        }
        
        if (e.key === 'Escape') {
            userInput.value = '';
            userInput.style.height = 'auto';
            sendBtn.disabled = true;
        }
    });
});