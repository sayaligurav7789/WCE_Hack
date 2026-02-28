document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('messages-container');
    const welcomeScreen = document.getElementById('welcome-screen');
    const newChatBtn = document.getElementById('new-chat-btn');
    const historyList = document.getElementById('history-list');
    const sidebar = document.querySelector('.sidebar');
    const searchInput = document.getElementById('search-chats');
    const downloadBtn = document.getElementById('download-chat-btn');
    
    let currentChatId = Date.now().toString();
    let messageHistory = [];
    let chats = {};

    // Load chat history from localStorage
    loadChatHistory();

    // ====================================
    // SEARCH FUNCTIONALITY
    // ====================================
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            filterChatHistory(searchTerm);
        }, 300));
    }

    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Filter chat history
    function filterChatHistory(searchTerm) {
        const historyItems = document.querySelectorAll('.history-item');
        let visibleCount = 0;
        
        historyItems.forEach(item => {
            const text = item.querySelector('.history-item-content span')?.textContent.toLowerCase() || '';
            const matches = text.includes(searchTerm) || searchTerm === '';
            
            if (matches) {
                item.style.display = 'flex';
                item.classList.add('search-match');
                visibleCount++;
            } else {
                item.style.display = 'none';
                item.classList.remove('search-match');
            }
        });
        
        const historyList = document.getElementById('history-list');
        const existingMessage = document.querySelector('.no-search-results');
        
        if (visibleCount === 0 && searchTerm !== '') {
            if (!existingMessage) {
                const noResults = document.createElement('div');
                noResults.className = 'no-search-results';
                noResults.innerHTML = `
                    <i class="fas fa-search"></i>
                    <p>No chats found matching "${searchTerm}"</p>
                `;
                historyList.appendChild(noResults);
            }
        } else if (existingMessage) {
            existingMessage.remove();
        }
    }

    // ====================================
    // DOWNLOAD CHAT FUNCTIONALITY
    // ====================================
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadChat);
    }

    function downloadChat() {
        const messages = document.querySelectorAll('.message');
        let content = `Psychology 2e Chat - ${new Date().toLocaleString()}\n`;
        content += '='.repeat(50) + '\n\n';
        
        messages.forEach(msg => {
            const role = msg.classList.contains('user') ? 'You' : 'Assistant';
            const text = msg.querySelector('.content')?.innerText || '';
            content += `${role}: ${text}\n\n`;
        });
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `psych-chat-${new Date().toISOString().slice(0,10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        showNotification('Chat downloaded successfully!', 'success');
    }

    // ====================================
    // NOTIFICATION SYSTEM
    // ====================================
    function showNotification(message, type = 'info') {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            document.body.appendChild(container);
        }
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';
        
        notification.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <div class="notification-content">${message}</div>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;
        
        container.appendChild(notification);
        
        const timeout = setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
        
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                clearTimeout(timeout);
                if (notification.parentNode) {
                    notification.remove();
                }
            });
        }
    }

    // ====================================
    // EXISTING CODE
    // ====================================
    
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
        if (window.innerWidth <= 768 && !e.target.closest('.download-btn')) {
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
            })
            .catch(() => {
                // Fallback if server not available
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
                appendMessage('assistant', formattedContent, data.references);
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

    // FIXED: Updated appendMessage with working action buttons
    function appendMessage(role, content, references = null) {
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
        contentDiv.innerHTML = content;

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
        
        // ADD ACTION BUTTONS for assistant messages - WITH SHARE BUTTON
        if (role === 'assistant') {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'message-actions';
            
            // Get plain text for copying (without HTML)
            const plainText = contentDiv.innerText;
            
            // Create copy button
            const copyBtn = document.createElement('button');
            copyBtn.className = 'action-btn copy-btn';
            copyBtn.title = 'Copy answer';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                copyToClipboard(plainText);
            });
            
            // Create speak button
            const speakBtn = document.createElement('button');
            speakBtn.className = 'action-btn speak-btn';
            speakBtn.title = 'Listen to answer';
            speakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
            speakBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                speakText(plainText);
            });
            
            // Create stop button
            const stopBtn = document.createElement('button');
            stopBtn.className = 'action-btn stop-btn';
            stopBtn.title = 'Stop speaking';
            stopBtn.innerHTML = '<i class="fas fa-stop-circle"></i>';
            stopBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                stopSpeaking();
            });
            
            // CREATE SHARE BUTTON
            const shareBtn = document.createElement('button');
            shareBtn.className = 'action-btn share-btn';
            shareBtn.title = 'Share answer';
            shareBtn.innerHTML = '<i class="fas fa-share-alt"></i>';
            shareBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                shareAnswer(plainText, question); // Pass question too for better context
            });
            
            actionsDiv.appendChild(copyBtn);
            actionsDiv.appendChild(speakBtn);
            actionsDiv.appendChild(stopBtn);
            actionsDiv.appendChild(shareBtn);
            msgDiv.appendChild(actionsDiv);
        }
        
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

    // MODIFIED: Added data-search-text attribute for search
    function createHistoryItem(chatId, previewText) {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.setAttribute('data-chat-id', chatId);
        historyItem.setAttribute('data-search-text', previewText.toLowerCase());
        
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
            e.stopPropagation();
            showDeleteConfirmation(chatId, historyItem);
        });
        
        historyItem.appendChild(contentDiv);
        historyItem.appendChild(deleteBtn);
        
        // Add click handler for loading chat
        historyItem.addEventListener('click', (e) => {
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
        
        showNotification('Chat deleted successfully', 'success');
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
                appendMessage('assistant', msg.content, msg.references);
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

// ====================================
// GLOBAL FUNCTIONS FOR ACTION BUTTONS
// ====================================

// Copy to clipboard
function copyToClipboard(text) {
    try {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Answer copied to clipboard!', 'success');
        }).catch(() => {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showNotification('Answer copied to clipboard!', 'success');
        });
    } catch (err) {
        showNotification('Failed to copy', 'error');
    }
}

// Text-to-speech
function speakText(text) {
    // Don't speak if it's just "Not found"
    if (text === "Not found in the provided textbook." || text.includes("Not found")) {
        showNotification('ℹ️ No answer available to speak', 'info');
        return;
    }
    
    try {
        // Stop any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        utterance.lang = 'en-US';
        
        utterance.onstart = function() {
            showNotification('🔊 Speaking... (click stop to cancel)', 'info');
        };
        
        utterance.onend = function() {
            showNotification('Finished speaking', 'success');
        };
        
        utterance.onerror = function() {
            showNotification('Speech failed', 'error');
        };
        
        window.speechSynthesis.speak(utterance);
    } catch (err) {
        showNotification('Speech not supported', 'error');
    }
}

// Stop speaking
function stopSpeaking() {
    try {
        window.speechSynthesis.cancel();
        showNotification('⏹️ Stopped speaking', 'info');
    } catch (err) {
        showNotification('Failed to stop', 'error');
    }
}

// Notification function
function showNotification(message, type = 'info') {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    
    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <div class="notification-content">${message}</div>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    container.appendChild(notification);
    
    const timeout = setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
    
    const closeBtn = notification.querySelector('.notification-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            clearTimeout(timeout);
            if (notification.parentNode) {
                notification.remove();
            }
        });
    }
}

// ====================================
// SHARE FUNCTIONALITY
// ====================================

// Share answer
function shareAnswer(text, question = '') {
    try {
        // Prepare share text
        let shareText = '';
        if (question) {
            shareText = `Q: ${question}\n\nA: ${text}`;
        } else {
            shareText = text;
        }
        
        // Truncate if too long (Twitter limit is 280)
        if (shareText.length > 280) {
            shareText = shareText.substring(0, 277) + '...';
        }
        
        // Check if Web Share API is supported
        if (navigator.share) {
            navigator.share({
                title: 'Psychology 2e Answer',
                text: shareText,
                url: window.location.href,
            })
            .then(() => {
                showNotification('Shared successfully!', 'success');
            })
            .catch((error) => {
                console.log('Share error:', error);
                if (error.name !== 'AbortError') {
                    // User didn't cancel, show fallback
                    showShareFallback(shareText);
                }
            });
        } else {
            // Fallback for browsers that don't support Web Share API
            showShareFallback(shareText);
        }
    } catch (err) {
        console.error('Share failed:', err);
        showShareFallback(text);
    }
}

// Fallback share method
function showShareFallback(text) {
    // Create a temporary textarea with share options
    const modal = document.createElement('div');
    modal.className = 'share-modal';
    modal.innerHTML = `
        <div class="share-modal-content">
            <div class="share-modal-header">
                <h3>Share Answer</h3>
                <button class="share-modal-close"><i class="fas fa-times"></i></button>
            </div>
            <div class="share-modal-body">
                <p>Choose how to share:</p>
                <div class="share-options">
                    <button class="share-option-btn" id="share-copy">
                        <i class="fas fa-copy"></i> Copy Text
                    </button>
                    <button class="share-option-btn" id="share-twitter">
                        <i class="fab fa-twitter"></i> Twitter
                    </button>
                    <button class="share-option-btn" id="share-whatsapp">
                        <i class="fab fa-whatsapp"></i> WhatsApp
                    </button>
                    <button class="share-option-btn" id="share-email">
                        <i class="fas fa-envelope"></i> Email
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Handle copy
    document.getElementById('share-copy').addEventListener('click', () => {
        copyToClipboard(text);
        modal.remove();
        showNotification('Answer copied to clipboard!', 'success');
    });
    
    // Handle Twitter
    document.getElementById('share-twitter').addEventListener('click', () => {
        const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
        window.open(twitterUrl, '_blank');
        modal.remove();
    });
    
    // Handle WhatsApp
    document.getElementById('share-whatsapp').addEventListener('click', () => {
        const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(text)}`;
        window.open(whatsappUrl, '_blank');
        modal.remove();
    });
    
    // Handle Email
    document.getElementById('share-email').addEventListener('click', () => {
        const emailUrl = `mailto:?subject=Psychology%20Answer&body=${encodeURIComponent(text)}`;
        window.location.href = emailUrl;
        modal.remove();
    });
    
    // Close modal
    modal.querySelector('.share-modal-close').addEventListener('click', () => {
        modal.remove();
    });
    
    // Click outside to close
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Make functions globally available

window.shareAnswer = shareAnswer;
window.copyToClipboard = copyToClipboard;
window.speakText = speakText;
window.stopSpeaking = stopSpeaking;
window.showNotification = showNotification;