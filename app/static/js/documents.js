/**
 * Document Handler
 * Handles document upload, display, and management functionality
 */

class DocumentHandler {
    constructor() {
        this.documents = [];
        this.filteredDocuments = [];
        this.currentSort = 'recent';
        this.searchQuery = '';
        this.init();
    }

    /**
     * Initialize document handler
     */
    init() {
        this.bindEvents();
        this.loadDocuments();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // File upload inputs
        const fileUploads = document.querySelectorAll('input[type="file"][accept=".pdf"]');
        fileUploads.forEach(input => {
            input.addEventListener('change', this.handleFileSelect.bind(this));
        });

        // Search input
        const searchInput = document.querySelector('input[placeholder*="Search documents"]');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleSearch.bind(this));
        }

        // Sort select
        const sortSelect = document.querySelector('select');
        if (sortSelect) {
            sortSelect.addEventListener('change', this.handleSort.bind(this));
        }

        // Document actions (delegated event handling)
        document.addEventListener('click', this.handleDocumentAction.bind(this));
    }

    /**
     * Load documents from API
     */
    async loadDocuments() {
        try {
            this.showDocumentLoading(true);
            
            const response = await window.api.getDocuments();
            
            if (response.status === 'success') {
                this.documents = response.data || [];
                this.filteredDocuments = [...this.documents];
                this.renderDocuments();
            } else {
                this.showError('Failed to load documents');
            }
        } catch (error) {
            console.error('Failed to load documents:', error);
            this.showError('Failed to load documents');
            
            // Show empty state if no documents could be loaded
            this.documents = [];
            this.filteredDocuments = [];
            this.renderDocuments();
        } finally {
            this.showDocumentLoading(false);
        }
    }

    /**
     * Handle file selection for upload
     * @param {Event} e - File input change event
     */
    async handleFileSelect(e) {
        const files = e.target.files;
        
        if (files.length === 0) return;

        const file = files[0];

        // Validate file type
        if (!file.type.includes('pdf')) {
            this.showError('Please select a PDF file');
            e.target.value = ''; // Clear the input
            return;
        }

        // Validate file size (max 50MB)
        const maxSize = 50 * 1024 * 1024; // 50MB in bytes
        if (file.size > maxSize) {
            this.showError('File size must be less than 50MB');
            e.target.value = ''; // Clear the input
            return;
        }

        await this.uploadDocument(file);
        e.target.value = ''; // Clear the input after upload
    }

    /**
     * Upload document to server
     * @param {File} file - PDF file to upload
     */
    async uploadDocument(file) {
        try {
            // Show upload modal/progress
            this.showUploadProgress(file.name, 0);

            const response = await window.api.uploadDocument(file, (progress) => {
                this.updateUploadProgress(progress);
            });

            if (response.status === 'success') {
                this.showSuccess('Document uploaded successfully!');
                this.hideUploadProgress();
                
                // Reload documents to show the new one
                await this.loadDocuments();
            } else {
                this.hideUploadProgress();
                this.showError(response.message || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            this.hideUploadProgress();
            this.showError(error.message || 'Upload failed. Please try again.');
        }
    }

    /**
     * Handle search input
     * @param {Event} e - Input event
     */
    handleSearch(e) {
        this.searchQuery = e.target.value.toLowerCase();
        this.filterDocuments();
    }

    /**
     * Handle sort selection
     * @param {Event} e - Change event
     */
    handleSort(e) {
        this.currentSort = e.target.value.toLowerCase().replace('sort by: ', '');
        this.sortDocuments();
    }

    /**
     * Handle document actions (chat, delete, etc.)
     * @param {Event} e - Click event
     */
    async handleDocumentAction(e) {
        const action = e.target.closest('[data-action]')?.dataset.action;
        const documentId = e.target.closest('[data-document-id]')?.dataset.documentId;

        if (!action || !documentId) return;

        e.preventDefault();

        switch (action) {
            case 'chat':
                await this.startChat(documentId);
                break;
            case 'delete':
                await this.deleteDocument(documentId);
                break;
            case 'download':
                await this.downloadDocument(documentId);
                break;
        }
    }    /**
     * Start chat with document
     * @param {string} documentId - Document ID
     */
    async startChat(documentId) {
        try {
            // Use getOrCreateConversation to preserve chat history
            const response = await window.api.getOrCreateConversation(parseInt(documentId));
            
            if (response.status === 'success') {
                // Redirect to conversation page
                window.location.href = `/conversation/${response.data.id}`;
            } else {
                this.showError('Failed to start conversation');
            }
        } catch (error) {
            console.error('Failed to start chat:', error);
            this.showError('Failed to start conversation');
        }
    }/**
     * Delete document
     * @param {string} documentId - Document ID
     */
    async deleteDocument(documentId) {
        // Find the document name for the confirmation dialog
        const document = this.documents.find(doc => doc.id === parseInt(documentId));
        const documentName = document ? document.filename : 'this document';
        
        if (!confirm(`Are you sure you want to delete "${documentName}"?\n\nThis will permanently delete:\n• The document file\n• All conversations with this document\n• All chat messages\n\nThis action cannot be undone.`)) {
            return;
        }

        try {
            console.log('Deleting document:', documentId);
            const response = await window.api.deleteDocument(parseInt(documentId));
            
            if (response.status === 'success') {
                this.showSuccess('Document deleted successfully');
                // Remove document from local array and re-render
                this.documents = this.documents.filter(doc => doc.id !== parseInt(documentId));
                this.filterDocuments();
            } else {
                this.showError(response.message || 'Failed to delete document');
            }
        } catch (error) {
            console.error('Failed to delete document:', error);
            this.showError(error.message || 'Failed to delete document');
        }
    }

    /**
     * Download document
     * @param {string} documentId - Document ID
     */
    async downloadDocument(documentId) {
        // This would need a download endpoint in the API
        this.showError('Download functionality not yet implemented');
    }

    /**
     * Filter documents based on search query
     */
    filterDocuments() {
        if (!this.searchQuery) {
            this.filteredDocuments = [...this.documents];
        } else {
            this.filteredDocuments = this.documents.filter(doc =>
                doc.filename.toLowerCase().includes(this.searchQuery)
            );
        }
        
        this.sortDocuments();
    }

    /**
     * Sort documents based on current sort option
     */
    sortDocuments() {
        switch (this.currentSort) {
            case 'name':
                this.filteredDocuments.sort((a, b) => a.filename.localeCompare(b.filename));
                break;
            case 'date added':
                this.filteredDocuments.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date));
                break;
            case 'size':
                // Note: API doesn't return file size yet, so this won't work
                this.filteredDocuments.sort((a, b) => (b.file_size || 0) - (a.file_size || 0));
                break;
            case 'recent':
            default:
                this.filteredDocuments.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date));
                break;
        }
        
        this.renderDocuments();
    }

    /**
     * Render documents in the grid
     */
    renderDocuments() {
        const documentGrid = document.querySelector('.grid');
        
        if (!documentGrid) return;

        // Clear existing documents (keep the grid structure)
        const existingCards = documentGrid.querySelectorAll('.document-card');
        existingCards.forEach(card => card.remove());

        if (this.filteredDocuments.length === 0) {
            this.showEmptyState();
            return;
        }

        // Hide empty state
        this.hideEmptyState();

        // Render each document
        this.filteredDocuments.forEach(doc => {
            const documentCard = this.createDocumentCard(doc);
            documentGrid.appendChild(documentCard);
        });
    }

    /**
     * Create document card element
     * @param {Object} doc - Document data
     * @returns {HTMLElement} Document card element
     */
    createDocumentCard(doc) {
        const card = document.createElement('div');
        card.className = 'document-card bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow border border-gray-100';
        card.dataset.documentId = doc.id;

        const uploadDate = new Date(doc.upload_date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        card.innerHTML = `
            <div class="p-4 flex flex-col h-full">
                <!-- PDF Icon -->
                <div class="mb-4 flex justify-center">
                    <div class="bg-red-50 p-3 rounded-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-10 h-10 text-red-500">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                        </svg>
                    </div>
                </div>
                
                <!-- Document Info -->
                <h2 class="font-semibold text-lg mb-1 line-clamp-2" title="${doc.filename}">${doc.filename}</h2>
                <p class="text-sm text-gray-500 mb-4">Uploaded on ${uploadDate}</p>
                  <!-- Processing Status -->
                <div class="mb-2">
                    ${doc.processed 
                        ? '<span class="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">✓ Ready for Chat</span>' 
                        : '<span class="inline-block bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">⏳ Processing...</span>'
                    }
                </div>
                  <!-- Actions -->
                <div class="mt-auto flex justify-between items-center">
                    <button data-action="chat" class="text-indigo-600 hover:text-white hover:bg-indigo-600 border border-indigo-600 px-4 py-2 rounded-lg text-sm font-medium flex items-center transition-all duration-200 shadow-sm hover:shadow-md">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 mr-2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
                        </svg>
                        Start Chat
                    </button>                    <div class="relative">
                        <button class="text-gray-600 hover:text-gray-800 hover:bg-gray-50 p-2 rounded-lg transition-all duration-200 options-btn border border-gray-200 hover:border-gray-300 shadow-sm hover:shadow-md" data-document-id="${doc.id}" title="More options">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />
                            </svg>
                        </button>
                        <div class="hidden absolute right-8 top-1/2 transform -translate-y-1/2 bg-white border border-gray-200 rounded-lg shadow-xl py-2 z-50 options-menu min-w-[160px]">
                            <div class="absolute right-0 top-1/2 transform translate-x-full -translate-y-1/2 w-0 h-0 border-l-8 border-l-white border-t-8 border-t-transparent border-b-8 border-b-transparent"></div>
                            <div class="absolute right-0 top-1/2 transform translate-x-full -translate-y-1/2 w-0 h-0 border-l-8 border-l-gray-200 border-t-8 border-t-transparent border-b-8 border-b-transparent translate-x-[1px]"></div>
                            <button data-action="delete" class="group flex items-center w-full text-left px-4 py-3 text-sm text-red-600 hover:bg-red-50 hover:text-red-700 transition-colors duration-200">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 mr-3 group-hover:scale-110 transition-transform duration-200">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                                </svg>
                                <span class="font-medium">Delete Document</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;        // Add options menu toggle
        const optionsBtn = card.querySelector('.options-btn');
        const optionsMenu = card.querySelector('.options-menu');
        
        optionsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            console.log('Options button clicked for document:', doc.id);
            
            // Hide other open menus first
            document.querySelectorAll('.options-menu').forEach(menu => {
                if (menu !== optionsMenu) {
                    menu.classList.add('hidden');
                    menu.style.opacity = '0';
                    menu.style.transform = 'translateX(10px) scale(0.95)';
                }
            });
            
            // Toggle current menu with slide animation from right
            const isHidden = optionsMenu.classList.contains('hidden');
            if (isHidden) {
                optionsMenu.classList.remove('hidden');
                // Add a small delay for animation
                setTimeout(() => {
                    optionsMenu.style.opacity = '1';
                    optionsMenu.style.transform = 'translateX(0) scale(1)';
                }, 10);
            } else {
                optionsMenu.style.opacity = '0';
                optionsMenu.style.transform = 'translateX(10px) scale(0.95)';
                setTimeout(() => {
                    optionsMenu.classList.add('hidden');
                }, 150);
            }
            
            console.log('Menu visibility:', !optionsMenu.classList.contains('hidden'));
        });

        // Initialize menu styles for slide-in effect from right
        optionsMenu.style.opacity = '0';
        optionsMenu.style.transform = 'translateX(10px) scale(0.95)';
        optionsMenu.style.transition = 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
        optionsMenu.style.transformOrigin = 'right center';

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!card.contains(e.target)) {
                optionsMenu.style.opacity = '0';
                optionsMenu.style.transform = 'translateX(10px) scale(0.95)';
                setTimeout(() => {
                    optionsMenu.classList.add('hidden');
                }, 150);
            }
        });

        return card;
    }

    /**
     * Show empty state
     */
    showEmptyState() {
        const documentGrid = document.querySelector('.grid');
        const emptyState = documentGrid.querySelector('.col-span-full');
        
        if (emptyState) {
            emptyState.classList.remove('hidden');
        }
    }

    /**
     * Hide empty state
     */
    hideEmptyState() {
        const documentGrid = document.querySelector('.grid');
        const emptyState = documentGrid.querySelector('.col-span-full');
        
        if (emptyState) {
            emptyState.classList.add('hidden');
        }
    }

    /**
     * Show document loading state
     * @param {boolean} loading - Loading state
     */
    showDocumentLoading(loading) {
        const documentGrid = document.querySelector('.grid');
        
        if (loading) {
            // Clear existing content
            const existingCards = documentGrid.querySelectorAll('.document-card');
            existingCards.forEach(card => card.remove());
            
            // Add loading skeleton
            for (let i = 0; i < 6; i++) {
                const skeleton = document.createElement('div');
                skeleton.className = 'document-skeleton bg-white rounded-xl shadow-md p-4 animate-pulse';
                skeleton.innerHTML = `
                    <div class="flex justify-center mb-4">
                        <div class="bg-gray-200 w-16 h-16 rounded-lg"></div>
                    </div>
                    <div class="bg-gray-200 h-4 rounded mb-2"></div>
                    <div class="bg-gray-200 h-3 rounded mb-4 w-3/4"></div>
                    <div class="flex justify-between">
                        <div class="bg-gray-200 h-3 rounded w-1/4"></div>
                        <div class="bg-gray-200 h-3 rounded w-3"></div>
                    </div>
                `;
                documentGrid.appendChild(skeleton);
            }
        } else {
            // Remove loading skeletons
            const skeletons = documentGrid.querySelectorAll('.document-skeleton');
            skeletons.forEach(skeleton => skeleton.remove());
        }
    }

    /**
     * Show upload progress modal
     * @param {string} filename - File name
     * @param {number} progress - Progress percentage
     */
    showUploadProgress(filename, progress) {
        // Remove existing upload modal
        const existingModal = document.getElementById('upload-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'upload-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                <h3 class="text-lg font-semibold mb-4">Uploading Document</h3>
                <div class="mb-4">
                    <p class="text-sm text-gray-600 mb-2">${filename}</p>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-indigo-600 h-2 rounded-full transition-all duration-300" style="width: ${progress}%"></div>
                    </div>
                    <p class="text-sm text-gray-500 mt-1 text-center">${Math.round(progress)}%</p>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    /**
     * Update upload progress
     * @param {number} progress - Progress percentage
     */
    updateUploadProgress(progress) {
        const modal = document.getElementById('upload-modal');
        if (modal) {
            const progressBar = modal.querySelector('.bg-indigo-600');
            const progressText = modal.querySelector('.text-center');
            
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
            if (progressText) {
                progressText.textContent = `${Math.round(progress)}%`;
            }
        }
    }

    /**
     * Hide upload progress modal
     */
    hideUploadProgress() {
        const modal = document.getElementById('upload-modal');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Show success message
     * @param {string} message - Success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Show notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, info)
     */
    showNotification(message, type = 'info') {
        // Use the same notification system as auth.js
        if (window.authHandler && window.authHandler.showNotification) {
            window.authHandler.showNotification(message, type);
        } else {
            // Fallback to simple alert
            alert(message);
        }
    }
}

// Initialize document handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on documents page
    if (window.location.pathname === '/documents') {
        window.documentHandler = new DocumentHandler();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DocumentHandler;
}
