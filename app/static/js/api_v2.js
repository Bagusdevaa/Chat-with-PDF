/**
 * API Handler - Central API communication module
 * Handles all communication with backend API endpoints
 */

class APIHandler {
    constructor() {
        this.baseURL = window.location.origin;
        this.token = localStorage.getItem('access_token');
    }    /**
     * Get authentication token
     * @returns {string|null} JWT token
     */
    getToken() {
        return this.token;
    }

    /**
     * Set authentication token
     * @param {string} token - JWT token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    /**
     * Remove authentication token
     */
    removeToken() {
        this.token = null;
        localStorage.removeItem('access_token');
    }

    /**
     * Get authentication headers
     * @returns {Object} Headers object
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Get authentication headers for form data
     * @returns {Object} Headers object
     */
    getFormHeaders() {
        const headers = {};

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Make API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} Response promise
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: options.headers || this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @returns {Promise} Response promise
     */
    async get(endpoint) {
        return this.request(endpoint, {
            method: 'GET'
        });
    }

    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise} Response promise
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * POST request with form data
     * @param {string} endpoint - API endpoint
     * @param {FormData} formData - Form data
     * @returns {Promise} Response promise
     */
    async postForm(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            headers: this.getFormHeaders(),
            body: formData
        });
    }

    /**
     * DELETE request
     * @param {string} endpoint - API endpoint
     * @returns {Promise} Response promise
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    // ========== AUTHENTICATION ENDPOINTS ==========

    /**
     * Login user
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise} Login response
     */
    async login(email, password) {
        try {
            const response = await this.post('/login', {
                email,
                password
            });

            if (response.status === 'success' && response.data.access_token) {
                this.setToken(response.data.access_token);
            }

            return response;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    /**
     * Register new user
     * @param {Object} userData - User registration data
     * @returns {Promise} Registration response
     */
    async register(userData) {
        try {
            const response = await this.post('/register', userData);
            return response;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }

    /**
     * Logout user
     * @returns {Promise} Logout response
     */
    async logout() {
        try {
            // Call logout endpoint if exists
            // await this.post('/logout', {});
            
            // Remove token from local storage
            this.removeToken();
            
            // Redirect to home page
            window.location.href = '/';
            
            return { status: 'success', message: 'Logged out successfully' };
        } catch (error) {
            console.error('Logout failed:', error);
            // Still remove token and redirect even if API call fails
            this.removeToken();
            window.location.href = '/';
            throw error;
        }
    }

    /**
     * Send password reset request
     * @param {string} email - User email
     * @returns {Promise} Reset response
     */
    async forgotPassword(email) {
        try {
            const response = await this.post('/forgot-password', { email });
            return response;
        } catch (error) {
            console.error('Password reset request failed:', error);
            throw error;
        }
    }

    // ========== DOCUMENT ENDPOINTS ==========

    /**
     * Upload document
     * @param {File} file - PDF file to upload
     * @param {Function} progressCallback - Progress callback function
     * @returns {Promise} Upload response
     */
    async uploadDocument(file, progressCallback = null) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            // Custom fetch for upload progress
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();

                // Progress tracking
                if (progressCallback) {
                    xhr.upload.addEventListener('progress', (e) => {
                        if (e.lengthComputable) {
                            const percentComplete = (e.loaded / e.total) * 100;
                            progressCallback(percentComplete);
                        }
                    });
                }

                xhr.addEventListener('load', () => {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (xhr.status >= 200 && xhr.status < 300) {
                            resolve(response);
                        } else {
                            reject(new Error(response.message || `HTTP ${xhr.status}`));
                        }
                    } catch (error) {
                        reject(new Error('Invalid response format'));
                    }
                });

                xhr.addEventListener('error', () => {
                    reject(new Error('Upload failed'));
                });

                xhr.open('POST', `${this.baseURL}/api/documents/upload`);
                
                // Set authorization header
                if (this.token) {
                    xhr.setRequestHeader('Authorization', `Bearer ${this.token}`);
                }

                xhr.send(formData);
            });
        } catch (error) {
            console.error('Document upload failed:', error);
            throw error;
        }
    }

    /**
     * Get all user documents
     * @returns {Promise} Documents response
     */
    async getDocuments() {
        try {
            const response = await this.get('/api/documents');
            return response;
        } catch (error) {
            console.error('Failed to fetch documents:', error);
            throw error;
        }
    }

    /**
     * Get single document by ID
     * @param {number} documentId - Document ID
     * @returns {Promise} Document response
     */
    async getDocument(documentId) {
        try {
            const response = await this.get(`/api/documents/${documentId}`);
            return response;
        } catch (error) {
            console.error('Failed to fetch document:', error);
            throw error;
        }
    }

    /**
     * Delete document
     * @param {number} documentId - Document ID
     * @returns {Promise} Delete response
     */
    async deleteDocument(documentId) {
        try {
            const response = await this.delete(`/api/documents/${documentId}`);
            return response;
        } catch (error) {
            console.error('Failed to delete document:', error);
            throw error;
        }    }

    // ========== CONVERSATION ENDPOINTS ==========

    /**
     * Get existing conversations for a document
     * @param {number} documentId - Document ID
     * @returns {Promise} Conversations response
     */
    async getDocumentConversations(documentId) {
        try {
            const response = await this.get(`/api/conversations/${documentId}`);
            return response;
        } catch (error) {
            console.error('Failed to get document conversations:', error);
            throw error;
        }
    }

    /**
     * Create new conversation
     * @param {number} documentId - Document ID
     * @param {string} title - Conversation title
     * @returns {Promise} Conversation response
     */
    async createConversation(documentId, title = 'New Conversation') {
        try {
            const response = await this.post('/api/conversations', {
                document_id: documentId,
                title
            });
            return response;
        } catch (error) {
            console.error('Failed to create conversation:', error);
            throw error;
        }
    }

    /**
     * Get or create conversation for a document (preserves chat history)
     * @param {number} documentId - Document ID
     * @param {string} title - Conversation title (for new conversations)
     * @returns {Promise} Conversation response
     */
    async getOrCreateConversation(documentId, title = 'New Conversation') {
        try {
            // First, try to get existing conversations for the document
            const existingConversations = await this.getDocumentConversations(documentId);
            
            if (existingConversations.status === 'success' && existingConversations.data.length > 0) {
                // Use the most recent conversation (first in the list since they're ordered by created_at desc)
                console.log('Found existing conversation, preserving chat history');
                return {
                    status: 'success',
                    data: existingConversations.data[0],
                    message: 'Using existing conversation'
                };
            } else {
                // No existing conversation found, create a new one
                console.log('No existing conversation found, creating new one');
                return await this.createConversation(documentId, title);
            }
        } catch (error) {
            console.error('Failed to get or create conversation:', error);
            // Fallback to creating new conversation
            try {
                return await this.createConversation(documentId, title);
            } catch (createError) {
                console.error('Failed to create fallback conversation:', createError);
                throw createError;
            }        }
    }

    /**
     * Get conversation messages
     * @param {number} conversationId - Conversation ID
     * @returns {Promise} Messages response
     */
    async getConversationMessages(conversationId) {
        try {
            const response = await this.get(`/api/conversation/${conversationId}/messages`);
            return response;
        } catch (error) {
            console.error('Failed to fetch messages:', error);
            throw error;
        }
    }

    /**
     * Get conversation messages (alias for compatibility)
     * @param {number} conversationId - Conversation ID
     * @returns {Promise} Messages response
     */
    async getMessages(conversationId) {
        return this.getConversationMessages(conversationId);
    }

    /**
     * Send message to conversation
     * @param {number} conversationId - Conversation ID
     * @param {string} content - Message content
     * @param {string} role - Message role (user/assistant)
     * @returns {Promise} Message response
     */
    async sendMessage(conversationId, content, role = 'user') {
        try {
            const response = await this.post(`/api/conversation/${conversationId}/message`, {
                content,
                role
            });
            return response;
        } catch (error) {
            console.error('Failed to send message:', error);
            throw error;
        }
    }

    /**
     * Get AI response for a user message
     * @param {number} conversationId - Conversation ID
     * @param {string} message - User message
     * @returns {Promise} AI response
     */
    async getAIResponse(conversationId, message) {
        try {
            const response = await this.post('/api/chat/ai-response', {
                conversation_id: conversationId,
                message: message
            });
            return response;
        } catch (error) {
            console.error('Failed to get AI response:', error);
            throw error;
        }
    }

    // ========== UTILITY METHODS ==========

    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isAuthenticated() {
        return !!this.token;
    }

    /**
     * Ping API to test connectivity
     * @returns {Promise} Ping response
     */
    async ping() {
        try {
            const response = await this.get('/api/ping');
            return response;
        } catch (error) {
            console.error('API ping failed:', error);
            throw error;
        }
    }
}

// Create global API instance
window.api = new APIHandler();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIHandler;
}
