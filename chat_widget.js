/*
Professional Floating Chat Assistant Widget
*/
class ChatAssistant {
    constructor(apiUrl = null) {
        // Auto-detect API URL based on environment
        if (!apiUrl) {
            if (window.location.protocol === 'file:' || window.location.port === '5500') {
                // Local file or Live Server - use localhost:5000 for API
                this.apiUrl = 'http://localhost:5000/api';
            } else {
                // Deployed - use relative path
                this.apiUrl = window.location.origin + '/api';
            }
        } else {
            this.apiUrl = apiUrl;
        }
        this.isOpen = false;
        this.isProcessing = false;
        this.setupChatWidget();
        this.checkSystemStatus();
    }

    setupChatWidget() {
        this.createChatWidget();
        this.setupEventListeners();
        this.addChatStyles();
    }

    createChatWidget() {
        // Create the floating chat widget HTML
        const chatHTML = `
            <!-- Floating Chat Button -->
            <div class="chat-widget-button" id="chatWidgetButton">
                <div class="chat-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 3.04 1.05 4.35L2 22l5.65-1.05C9.04 21.64 10.46 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm-1 14h-1v-1h1v1zm1-3h-1V7h1v6z"/>
                    </svg>
                </div>
                <div class="chat-close-icon" style="display: none;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </div>
                <div class="chat-pulse"></div>
            </div>

            <!-- Chat Window -->
            <div class="chat-widget-window" id="chatWidgetWindow" style="display: none;">
                <div class="chat-header">
                    <div class="chat-avatar">
                        <div class="avatar-img">🤖</div>
                        <div class="status-dot"></div>
                    </div>
                    <div class="chat-info">
                        <h4>AI Assistant</h4>
                        <span class="status-text">Ask about Ishika</span>
                    </div>
                    <button class="minimize-btn" id="minimizeChat">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19 13H5v-2h14v2z"/>
                        </svg>
                    </button>
                </div>

                <div class="chat-messages" id="chatMessages">
                    <div class="message bot-message">
                        <div class="message-avatar">🤖</div>
                        <div class="message-content">
                            <p>Hi! I'm Ishika's AI assistant. Ask me anything about her experience, skills, or projects!</p>
                            <div class="quick-actions">
                                <button class="quick-btn" data-question="What programming languages does Ishika know?">Programming Skills</button>
                                <button class="quick-btn" data-question="Tell me about Ishika's AI projects">AI Projects</button>
                                <button class="quick-btn" data-question="What work experience does Ishika have?">Experience</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="typing-indicator" id="typingIndicator" style="display: none;">
                    <div class="message-avatar">🤖</div>
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>

                <div class="chat-input-area">
                    <div class="input-container">
                        <input type="text" id="chatInput" placeholder="Ask about Ishika's experience..." />
                        <button id="sendButton" class="send-btn">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="input-footer">
                        <span class="powered-by">Powered by OpenAI</span>
                    </div>
                </div>
            </div>
        `;

        // Insert the chat widget into the page
        document.body.insertAdjacentHTML('beforeend', chatHTML);
    }

    addChatStyles() {
        const styles = `
            <style>
                /* Floating Chat Button */
                .chat-widget-button {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #00d9ff 0%, #ff006e 100%);
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    box-shadow: 0 8px 32px rgba(0, 217, 255, 0.4);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    z-index: 10000;
                    overflow: hidden;
                }

                .chat-widget-button:hover {
                    transform: scale(1.1);
                    box-shadow: 0 12px 40px rgba(0, 217, 255, 0.6);
                }

                .chat-widget-button.active {
                    background: linear-gradient(135deg, #ff006e 0%, #ffbe0b 100%);
                    border-radius: 50% 50% 50% 8px;
                }

                .chat-pulse {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #00d9ff 0%, #ff006e 100%);
                    animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
                    z-index: -1;
                }

                @keyframes pulse-ring {
                    0% { transform: scale(1); opacity: 0.8; }
                    100% { transform: scale(2); opacity: 0; }
                }

                .chat-icon, .chat-close-icon {
                    transition: all 0.3s ease;
                }

                .chat-widget-button.active .chat-icon {
                    transform: rotate(180deg);
                    opacity: 0;
                }

                .chat-widget-button.active .chat-close-icon {
                    display: block !important;
                    transform: rotate(0deg);
                    opacity: 1;
                }

                /* Chat Window */
                .chat-widget-window {
                    position: fixed;
                    bottom: 100px;
                    right: 20px;
                    width: 380px;
                    height: 500px;
                    background: rgba(26, 31, 58, 0.95);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    z-index: 9999;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    transform: translateY(20px);
                    opacity: 0;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .chat-widget-window.open {
                    opacity: 1;
                    transform: translateY(0);
                }

                /* Chat Header */
                .chat-header {
                    padding: 20px;
                    background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(255, 0, 110, 0.1) 100%);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }

                .chat-avatar {
                    position: relative;
                    width: 40px;
                    height: 40px;
                }

                .avatar-img {
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #00d9ff 0%, #ff006e 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                }

                .status-dot {
                    position: absolute;
                    bottom: 2px;
                    right: 2px;
                    width: 12px;
                    height: 12px;
                    background: #00ff88;
                    border: 2px solid rgba(26, 31, 58, 0.95);
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }

                .chat-info {
                    flex: 1;
                }

                .chat-info h4 {
                    margin: 0;
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: 600;
                }

                .status-text {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 12px;
                }

                .minimize-btn {
                    background: none;
                    border: none;
                    color: rgba(255, 255, 255, 0.7);
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                    transition: all 0.2s ease;
                }

                .minimize-btn:hover {
                    background: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                }

                /* Chat Messages */
                .chat-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 16px;
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }

                .chat-messages::-webkit-scrollbar {
                    width: 4px;
                }

                .chat-messages::-webkit-scrollbar-track {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 2px;
                }

                .chat-messages::-webkit-scrollbar-thumb {
                    background: rgba(0, 217, 255, 0.5);
                    border-radius: 2px;
                }

                .message {
                    display: flex;
                    gap: 10px;
                    align-items: flex-start;
                    animation: fadeInUp 0.3s ease;
                }

                .message.user-message {
                    flex-direction: row-reverse;
                }

                .message-avatar {
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                    flex-shrink: 0;
                }

                .bot-message .message-avatar {
                    background: linear-gradient(135deg, #00d9ff 0%, #ff006e 100%);
                }

                .user-message .message-avatar {
                    background: linear-gradient(135deg, #ffbe0b 0%, #ff006e 100%);
                }

                .message-content {
                    max-width: 250px;
                    padding: 12px 16px;
                    border-radius: 18px;
                    font-size: 14px;
                    line-height: 1.4;
                }

                .bot-message .message-content {
                    background: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                    border-bottom-left-radius: 4px;
                }

                .user-message .message-content {
                    background: linear-gradient(135deg, #00d9ff 0%, #ff006e 100%);
                    color: #ffffff;
                    border-bottom-right-radius: 4px;
                }

                .message-content p {
                    margin: 0 0 8px 0;
                }

                .message-content p:last-child {
                    margin-bottom: 0;
                }

                /* Quick Actions */
                .quick-actions {
                    margin-top: 12px;
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                }

                .quick-btn {
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    padding: 8px 12px;
                    color: #ffffff;
                    font-size: 12px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    text-align: left;
                }

                .quick-btn:hover {
                    background: rgba(0, 217, 255, 0.2);
                    border-color: rgba(0, 217, 255, 0.4);
                    transform: translateY(-1px);
                }

                /* Typing Indicator */
                .typing-indicator {
                    display: flex;
                    gap: 10px;
                    align-items: center;
                    padding: 0 16px 8px;
                    animation: fadeIn 0.3s ease;
                }

                .typing-dots {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 12px 16px;
                    border-radius: 18px 18px 18px 4px;
                    display: flex;
                    gap: 4px;
                }

                .typing-dots span {
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                    background: rgba(0, 217, 255, 0.8);
                    animation: typing 1.4s infinite;
                }

                .typing-dots span:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .typing-dots span:nth-child(3) {
                    animation-delay: 0.4s;
                }

                @keyframes typing {
                    0%, 60%, 100% { transform: translateY(0); }
                    30% { transform: translateY(-8px); }
                }

                /* Chat Input */
                .chat-input-area {
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    background: rgba(255, 255, 255, 0.05);
                }

                .input-container {
                    padding: 16px;
                    display: flex;
                    gap: 8px;
                    align-items: center;
                }

                #chatInput {
                    flex: 1;
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 20px;
                    padding: 10px 16px;
                    color: #ffffff;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                }

                #chatInput:focus {
                    background: rgba(255, 255, 255, 0.15);
                    border-color: rgba(0, 217, 255, 0.5);
                    box-shadow: 0 0 0 2px rgba(0, 217, 255, 0.1);
                }

                #chatInput::placeholder {
                    color: rgba(255, 255, 255, 0.5);
                }

                .send-btn {
                    width: 36px;
                    height: 36px;
                    background: linear-gradient(135deg, #00d9ff 0%, #ff006e 100%);
                    border: none;
                    border-radius: 50%;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                }

                .send-btn:hover {
                    transform: scale(1.1);
                    box-shadow: 0 4px 12px rgba(0, 217, 255, 0.3);
                }

                .send-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none;
                }

                .input-footer {
                    padding: 8px 16px;
                    text-align: center;
                }

                .powered-by {
                    color: rgba(255, 255, 255, 0.4);
                    font-size: 11px;
                }

                /* Animations */
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }

                /* Responsive Design */
                @media (max-width: 480px) {
                    .chat-widget-window {
                        width: calc(100vw - 40px);
                        right: 20px;
                        left: 20px;
                        bottom: 90px;
                        height: 70vh;
                        max-height: 500px;
                    }

                    .chat-widget-button {
                        bottom: 15px;
                        right: 15px;
                        width: 50px;
                        height: 50px;
                    }

                    .message-content {
                        max-width: 200px;
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    setupEventListeners() {
        // Toggle chat window
        const chatButton = document.getElementById('chatWidgetButton');
        const chatWindow = document.getElementById('chatWidgetWindow');
        const minimizeBtn = document.getElementById('minimizeChat');

        if (chatButton) {
            chatButton.addEventListener('click', () => this.toggleChat());
        }

        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', () => this.closeChat());
        }

        // Send message
        const sendButton = document.getElementById('sendButton');
        const chatInput = document.getElementById('chatInput');

        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Quick action buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-btn')) {
                const question = e.target.dataset.question;
                if (question) {
                    this.askQuestion(question);
                    // Hide quick actions after use
                    e.target.parentElement.style.display = 'none';
                }
            }
        });

        // Close chat when clicking outside (optional)
        document.addEventListener('click', (e) => {
            if (this.isOpen && !e.target.closest('.chat-widget-window') && !e.target.closest('.chat-widget-button')) {
                // Uncomment to enable click-outside-to-close
                // this.closeChat();
            }
        });
    }

    toggleChat() {
        const chatButton = document.getElementById('chatWidgetButton');
        const chatWindow = document.getElementById('chatWidgetWindow');

        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        const chatButton = document.getElementById('chatWidgetButton');
        const chatWindow = document.getElementById('chatWidgetWindow');

        if (chatButton && chatWindow) {
            this.isOpen = true;
            chatButton.classList.add('active');
            chatWindow.style.display = 'flex';
            
            // Trigger animation
            setTimeout(() => {
                chatWindow.classList.add('open');
            }, 10);

            // Focus input
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                setTimeout(() => chatInput.focus(), 300);
            }
        }
    }

    closeChat() {
        const chatButton = document.getElementById('chatWidgetButton');
        const chatWindow = document.getElementById('chatWidgetWindow');

        if (chatButton && chatWindow) {
            this.isOpen = false;
            chatButton.classList.remove('active');
            chatWindow.classList.remove('open');
            
            setTimeout(() => {
                chatWindow.style.display = 'none';
            }, 300);
        }
    }

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        if (!chatInput || !chatInput.value.trim() || this.isProcessing) return;

        const question = chatInput.value.trim();
        chatInput.value = '';

        await this.askQuestion(question);
    }

    async askQuestion(question) {
        if (this.isProcessing) return;

        this.isProcessing = true;
        this.addMessage(question, 'user');
        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.apiUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    question: question,
                    n_results: 3
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.addMessage(data.answer, 'bot', data.sources);
            } else {
                this.addMessage(`Sorry, I encountered an error: ${data.error}`, 'bot');
            }
        } catch (error) {
            this.addMessage('Sorry, I had trouble connecting. Please make sure the backend server is running.', 'bot');
            console.error('Chat error:', error);
        } finally {
            this.hideTypingIndicator();
            this.isProcessing = false;
        }
    }

    addMessage(content, type, sources = null) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const avatar = type === 'user' ? '👤' : '🤖';
        
        let sourceHTML = '';
        if (sources && sources.length > 0) {
            sourceHTML = `
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="font-size: 11px; color: rgba(255,255,255,0.6); margin-bottom: 4px;">Sources:</div>
                    ${sources.slice(0, 2).map(source => `
                        <div style="font-size: 10px; background: rgba(255,255,255,0.05); padding: 4px 8px; border-radius: 8px; margin: 2px 0;">
                            ${source.content.substring(0, 80)}...
                        </div>
                    `).join('')}
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${content}</p>
                ${sourceHTML}
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'flex';
            
            // Scroll to show typing indicator
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                setTimeout(() => {
                    chatMessages.scrollTop = chatMessages.scrollHeight + 100;
                }, 100);
            }
        }
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    async checkSystemStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/stats`);
            if (response.ok) {
                const data = await response.json();
                this.updateStatus('online', `${data.document_count || 0} docs loaded`);
            } else {
                this.updateStatus('offline', 'Backend not connected');
            }
        } catch (error) {
            this.updateStatus('offline', 'Backend not connected');
        }
    }

    updateStatus(status, text) {
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (statusText) {
            statusText.textContent = text;
        }
        
        if (statusDot) {
            if (status === 'online') {
                statusDot.style.background = '#00ff88';
            } else {
                statusDot.style.background = '#ff4444';
            }
        }
    }
}

// Initialize the chat assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're not on a page that already has a RAG interface
    if (!document.getElementById('rag-section')) {
        window.chatAssistant = new ChatAssistant();
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatAssistant;
}