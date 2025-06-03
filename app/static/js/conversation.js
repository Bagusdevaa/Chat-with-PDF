/**
 * Conversation Handler - Manages chat functionality in the conversation page
 * Handles message sending, receiving, and conversation management
 */

class ConversationHandler {
    constructor() {
        this.api = new APIHandler();
        this.conversationId = null;
        this.documentId = null;
        this.isLoading = false;
        
        // DOM elements
        this.chatForm = null;
        this.messageInput = null;
        this.chatMessages = null;
        this.sendButton = null;
        
        // User info for avatars
        this.userInitials = 'U';
        this.userName = 'User';
    }

    /**
     * Initialize the conversation handler
     */
    init() {
        this.initializeElements();
        this.attachEventListeners();
        this.loadUserInfo();
        this.extractPageData();
        this.loadConversationMessages();
        this.adjustChatHeight();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.chatForm = document.getElementById('chat-form');
        this.messageInput = document.getElementById('message-input');
        this.chatMessages = document.getElementById('chat-messages');
        this.sendButton = this.chatForm?.querySelector('button[type="submit"]');
        
        if (!this.chatForm || !this.messageInput || !this.chatMessages) {
            console.error('Required chat elements not found');
            return;
        }
    }    /**
     * Extract conversation and document data from URL or page
     */
    extractPageData() {
        // Extract from URL path like /conversation/<id>
        const pathParts = window.location.pathname.split('/');
        const conversationIndex = pathParts.indexOf('conversation');
        
        if (conversationIndex !== -1 && pathParts[conversationIndex + 1]) {
            this.conversationId = parseInt(pathParts[conversationIndex + 1]);
        }

        // Extract document ID from data attributes
        this.documentId = document.body.dataset.documentId;
        
        if (!this.documentId) {
            // Try to get from URL params as fallback
            const urlParams = new URLSearchParams(window.location.search);
            this.documentId = urlParams.get('doc_id');
        }
        
        console.log('Extracted data:', {
            conversationId: this.conversationId,
            documentId: this.documentId
        });
    }

    /**
     * Load user information for display
     */
    loadUserInfo() {
        const token = this.api.getToken();
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                this.userName = payload.name || 'User';
                this.userInitials = this.getUserInitials(this.userName);
            } catch (error) {
                console.warn('Could not decode user info from token:', error);
            }
        }
    }

    /**
     * Get user initials from name
     */
    getUserInitials(name) {
        return name
            .split(' ')
            .map(part => part[0])
            .join('')
            .toUpperCase()
            .slice(0, 2) || 'U';
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        if (!this.chatForm) return;

        // Form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Enter key handling (Enter to send, Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });

        // Download chat button
        const downloadBtn = document.getElementById('download-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.downloadChatHistory();
            });
        }

        // Window resize handler
        window.addEventListener('resize', () => {
            this.adjustChatHeight();
        });
    }    /**
     * Load conversation messages
     */
    async loadConversationMessages() {
        if (!this.conversationId) {
            console.log('No conversation ID, ready for new conversation');
            // Clear messages and show only welcome message
            this.clearMessages();
            return;
        }

        try {
            const response = await this.api.getConversationMessages(this.conversationId);
            
            if (response.status === 'success') {
                this.displayMessages(response.data);
            } else {
                this.showError('Failed to load conversation messages');
            }
        } catch (error) {
            console.error('Error loading conversation messages:', error);
            this.showError('Error loading conversation messages');
        }
    }

    /**
     * Clear messages and show welcome message only
     */
    clearMessages() {
        this.chatMessages.innerHTML = '';
        this.addWelcomeMessage();
    }

    /**
     * Add welcome message
     */
    addWelcomeMessage() {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message-ai p-4 rounded-lg mb-4';
        welcomeDiv.innerHTML = `
            <div class="flex items-start">
                <div class="bg-gradient-to-r from-[#4f46e5] to-[#9333ea] rounded-full w-8 h-8 flex items-center justify-center text-white mr-3 flex-shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
                    </svg>
                </div>
                <div>
                    <div class="font-medium mb-1">AI Assistant</div>
                    <div class="text-gray-700">
                        Hello! I'm your PDF Assistant. I've analyzed your document and I'm ready to answer any questions you might have about it. Feel free to ask anything!
                    </div>
                </div>
            </div>
        `;
        this.chatMessages.appendChild(welcomeDiv);
    }

    /**
     * Display messages in the chat
     */
    displayMessages(messages) {
        // Clear existing messages except welcome message
        const welcomeMessage = this.chatMessages.querySelector('.message-ai');
        this.chatMessages.innerHTML = '';
        
        // Re-add welcome message if it exists
        if (welcomeMessage) {
            this.chatMessages.appendChild(welcomeMessage);
        }

        // Add all messages
        messages.forEach(message => {
            this.addMessage(message.role, message.content, false);
        });

        this.scrollToBottom();
    }

    /**
     * Send a message
     */
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isLoading) {
            return;
        }

        // Check if we have a conversation ID
        if (!this.conversationId) {
            // Create new conversation first
            try {
                await this.createConversation();
            } catch (error) {
                this.showError('Failed to create conversation');
                return;
            }
        }

        this.isLoading = true;
        this.updateSendButton(true);

        // Add user message to UI immediately
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.autoResizeTextarea();

        try {
            // Send user message to API
            await this.api.sendMessage(this.conversationId, message, 'user');
              // Show AI thinking indicator
            const loadingMessageId = this.addLoadingMessage();            try {
                // Get AI response from the backend
                const aiResponseData = await this.api.getAIResponse(this.conversationId, message);
                
                // DEBUG: Log the full response to console
                console.log('🔍 DEBUG - Full AI Response:', aiResponseData);
                console.log('🔍 DEBUG - Response Data:', aiResponseData.data);
                console.log('🔍 DEBUG - AI Response Text:', aiResponseData.data?.response);
                
                this.removeLoadingMessage(loadingMessageId);
                
                if (aiResponseData.status === 'success') {
                    const aiResponse = aiResponseData.data.response;
                    
                    // DEBUG: Check if response contains raw chunk indicators
                    const rawIndicators = ['chunk', 'page_content', 'metadata', 'source'];
                    const hasRawChunks = rawIndicators.some(indicator => 
                        aiResponse.toLowerCase().includes(indicator));
                    
                    if (hasRawChunks) {
                        console.error('❌ DEBUG - Response contains raw chunks!');
                        console.error('Raw indicators found:', rawIndicators.filter(ind => 
                            aiResponse.toLowerCase().includes(ind)));
                    } else {
                        console.log('✅ DEBUG - Response appears to be natural language');
                    }
                    
                    // Send AI response to API to store it
                    await this.api.sendMessage(this.conversationId, aiResponse, 'assistant');
                    
                    // Add AI message to UI
                    this.addMessage('assistant', aiResponse);
                } else {
                    throw new Error(aiResponseData.message || 'Failed to get AI response');
                }
            } catch (error) {
                this.removeLoadingMessage(loadingMessageId);
                console.error('Error getting AI response:', error);
                
                // Fallback error message
                const errorMessage = "I apologize, but I encountered an error while processing your message. Please try again.";
                await this.api.sendMessage(this.conversationId, errorMessage, 'assistant');
                this.addMessage('assistant', errorMessage);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Failed to send message');
        } finally {
            this.isLoading = false;
            this.updateSendButton(false);
        }
    }

    /**
     * Create a new conversation
     */
    async createConversation() {
        if (!this.documentId) {
            throw new Error('No document ID available');
        }

        try {
            const response = await this.api.createConversation(this.documentId);
            
            if (response.success) {
                this.conversationId = response.data.id;
                
                // Update URL without reload
                const newUrl = `/conversation/${this.conversationId}`;
                window.history.pushState({}, '', newUrl);
            } else {
                throw new Error(response.message || 'Failed to create conversation');
            }
        } catch (error) {
            throw error;
        }
    }

    /**
     * Generate AI response (placeholder for actual AI integration)
     */
    async generateAIResponse(userMessage) {
        // This is a placeholder. In a real implementation, this would call
        // your AI service (OpenAI, Claude, etc.) with the document context
        
        const responses = [
            "Based on the document content, I can help you understand the key points discussed.",
            "That's an interesting question about the document. Let me analyze the relevant sections.",
            "I can see you're asking about specific details. The document provides information on this topic.",
            "Thank you for your question. The document contains relevant information that I can share with you.",
            "I'd be happy to help explain that concept from the document."
        ];

        // Simple keyword-based responses
        const lowerMessage = userMessage.toLowerCase();
        
        if (lowerMessage.includes('summary') || lowerMessage.includes('summarize')) {
            return "This document discusses key concepts and provides detailed analysis on the main topics. The content is structured to give comprehensive insights into the subject matter.";
        } else if (lowerMessage.includes('author') || lowerMessage.includes('who wrote')) {
            return "The document authorship information can be found in the document metadata or header sections.";
        } else if (lowerMessage.includes('conclusion') || lowerMessage.includes('end')) {
            return "The document concludes with important findings and recommendations based on the analysis presented throughout the text.";
        } else {
            return responses[Math.floor(Math.random() * responses.length)];
        }
    }

    /**
     * Add a message to the chat display
     */
    addMessage(role, content, scroll = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = role === 'user' ? 'message-user p-4 rounded-lg mb-4' : 'message-ai p-4 rounded-lg mb-4';

        let avatar;
        if (role === 'user') {
            avatar = `
                <div class="bg-gradient-to-r from-[#4f46e5] to-[#9333ea] rounded-full w-8 h-8 flex items-center justify-center text-white mr-3 flex-shrink-0">
                    <span class="text-sm font-medium">${this.userInitials}</span>
                </div>
            `;
        } else {
            avatar = `
                <div class="bg-gradient-to-r from-[#4f46e5] to-[#9333ea] rounded-full w-8 h-8 flex items-center justify-center text-white mr-3 flex-shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
                    </svg>
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="flex items-start">
                ${avatar}
                <div>
                    <div class="font-medium mb-1">${role === 'user' ? this.userName : 'AI Assistant'}</div>
                    <div class="text-gray-700">
                        ${this.formatMessageContent(content)}
                    </div>
                </div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        
        if (scroll) {
            this.scrollToBottom();
        }

        return messageDiv;
    }

    /**
     * Add loading message for AI thinking
     */
    addLoadingMessage() {
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.className = 'message-ai p-4 rounded-lg mb-4 loading-message';
        
        loadingDiv.innerHTML = `
            <div class="flex items-start">
                <div class="bg-gradient-to-r from-[#4f46e5] to-[#9333ea] rounded-full w-8 h-8 flex items-center justify-center text-white mr-3 flex-shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
                    </svg>
                </div>
                <div>
                    <div class="font-medium mb-1">AI Assistant</div>
                    <div class="text-gray-700 flex items-center">
                        <div class="animate-pulse flex space-x-1">
                            <div class="w-2 h-2 bg-gray-400 rounded-full"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.chatMessages.appendChild(loadingDiv);
        this.scrollToBottom();
        
        return loadingId;
    }

    /**
     * Remove loading message
     */
    removeLoadingMessage(loadingId) {
        const loadingDiv = document.getElementById(loadingId);
        if (loadingDiv) {
            this.chatMessages.removeChild(loadingDiv);
        }
    }    /**
     * Format message content (handle line breaks, etc.)
     */
    formatMessageContent(content) {
        // DEBUG: Log the raw content received
        console.log('🔍 DEBUG - Raw content length:', content.length);
        console.log('🔍 DEBUG - Raw content preview:', content.substring(0, 200));
        
        // Check if content looks like raw PDF chunks
        const isRawChunk = this.detectRawChunk(content);
        if (isRawChunk) {
            console.warn('⚠️ DEBUG - Detected raw chunk content, attempting to clean...');
            content = this.cleanRawChunk(content);
        }
        
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
    
    /**
     * Detect if content appears to be raw PDF chunks
     */
    detectRawChunk(content) {
        const rawIndicators = [
            'page_content',
            'metadata',
            'source:',
            /^\s*\d+\s*\n/,  // starts with page number
            /\n\s*\d+\s*$/,  // ends with page number
        ];
        
        return rawIndicators.some(indicator => {
            if (typeof indicator === 'string') {
                return content.toLowerCase().includes(indicator.toLowerCase());
            } else {
                return indicator.test(content);
            }
        });
    }
    
    /**
     * Clean raw chunk content to make it more readable
     */
    cleanRawChunk(content) {
        // Remove metadata patterns
        content = content.replace(/page_content[:\s]*['"]/gi, '');
        content = content.replace(/metadata[:\s]*\{[^}]*\}/gi, '');
        content = content.replace(/source[:\s]*['""][^'"]*['"]/gi, '');
        
        // Remove leading/trailing page numbers
        content = content.replace(/^\s*\d+\s*\n/, '');
        content = content.replace(/\n\s*\d+\s*$/, '');
        
        // Clean up extra whitespace and formatting
        content = content.replace(/\n\s*\n\s*\n/g, '\n\n');
        content = content.trim();
        
        console.log('✅ DEBUG - Cleaned content preview:', content.substring(0, 200));
        
        return content;
    }

    /**
     * Update send button state
     */
    updateSendButton(loading) {
        if (!this.sendButton) return;

        const buttonText = this.sendButton.querySelector('.sr-only') || this.sendButton;
        const spinner = this.sendButton.querySelector('.animate-spin');

        if (loading) {
            this.sendButton.disabled = true;
            if (spinner) spinner.classList.remove('hidden');
            if (buttonText !== this.sendButton) buttonText.textContent = 'Sending...';
        } else {
            this.sendButton.disabled = false;
            if (spinner) spinner.classList.add('hidden');
            if (buttonText !== this.sendButton) buttonText.textContent = 'Send';
        }
    }

    /**
     * Auto-resize textarea
     */
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = (this.messageInput.scrollHeight) + 'px';
        
        // Reset if empty
        if (this.messageInput.value === '') {
            this.messageInput.style.height = 'auto';
        }
        
        // Readjust chat area height when textarea changes size
        this.adjustChatHeight();
    }

    /**
     * Adjust chat messages height
     */
    adjustChatHeight() {
        const header = document.querySelector('header');
        const chatForm = this.chatForm?.closest('div');
        
        if (header && chatForm) {
            const availableHeight = window.innerHeight - header.offsetHeight - chatForm.offsetHeight - 20; // 20px margin
            this.chatMessages.style.height = `${availableHeight}px`;
        }
    }

    /**
     * Scroll to bottom of chat
     */
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    /**
     * Download chat history
     */
    downloadChatHistory() {
        const messages = this.chatMessages.querySelectorAll('.message-user, .message-ai');
        let chatText = "# Chat History with PDF Assistant\n\n";
        chatText += `Generated: ${new Date().toLocaleString()}\n\n`;
        
        messages.forEach(msg => {
            if (msg.classList.contains('loading-message')) return;
            
            const sender = msg.classList.contains('message-user') ? 'You' : 'AI Assistant';
            const content = msg.querySelector('.text-gray-700').textContent.trim();
            chatText += `## ${sender}:\n${content}\n\n`;
        });
        
        // Create blob and download
        const blob = new Blob([chatText], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-history-${Date.now()}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Show error message
     */
    showError(message) {
        // Create temporary error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50';
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (document.body.contains(errorDiv)) {
                document.body.removeChild(errorDiv);
            }
        }, 5000);
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const bgColor = type === 'error' ? 'bg-red-100 border-red-400 text-red-700' :
                       type === 'success' ? 'bg-green-100 border-green-400 text-green-700' :
                       'bg-blue-100 border-blue-400 text-blue-700';
        
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `fixed top-4 right-4 ${bgColor} px-4 py-3 rounded z-50 border`;
        notificationDiv.textContent = message;
        
        document.body.appendChild(notificationDiv);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (document.body.contains(notificationDiv)) {
                document.body.removeChild(notificationDiv);
            }
        }, 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const conversationHandler = new ConversationHandler();
    conversationHandler.init();
});
