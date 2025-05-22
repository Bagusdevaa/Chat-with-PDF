document.addEventListener('DOMContentLoaded', function() {
    // References to DOM elements
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const pdfViewerCol = document.getElementById('pdfViewerCol');
    const pdfContent = document.getElementById('pdfContent');
    const zoomIn = document.getElementById('zoomIn');
    const zoomOut = document.getElementById('zoomOut');
    const toggleFullscreen = document.getElementById('toggleFullscreen');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    const pageIndicator = document.getElementById('pageIndicator');
    const clearChat = document.getElementById('clearChat');
    const exportChat = document.getElementById('exportChat');
    const attachFile = document.getElementById('attachFile');
    const toggleMicrophone = document.getElementById('toggleMicrophone');
    const typingIndicator = document.getElementById('typingIndicator');
    const suggestedQuestionsBtn = document.getElementById('suggestedQuestions');
    const fontSizeToggle = document.getElementById('fontSizeToggle');
    const toggleHighlighting = document.getElementById('toggleHighlighting');
    
    // PDF Viewer variables
    let scale = 1.0;
    let currentPage = 1;
    let pdfInstance = null;
    let totalPages = 0;
    
    // Chat variables
    let chatHistory = [];
    let isProcessing = false;
    let citationHighlightEnabled = true;
    let fontSizeMode = 'normal'; // normal, large, small
    
    // Get document_id from the URL or data attribute
    const documentId = document.body.getAttribute('data-document-id') || 'sample1';

    // Handle typing indicator
    function showTypingIndicator() {
        typingIndicator.classList.add('show');
        scrollToBottom();
    }
    
    function hideTypingIndicator() {
        typingIndicator.classList.remove('show');
    }
    
    // Handle suggested questions
    function toggleSuggestedQuestions() {
        let suggestedQuestionsContainer = document.querySelector('.suggested-questions');
        
        if (suggestedQuestionsContainer) {
            // Remove if already exists
            suggestedQuestionsContainer.remove();
        } else {
            // Create and add suggestions
            suggestedQuestionsContainer = document.createElement('div');
            suggestedQuestionsContainer.className = 'suggested-questions';
            
            // Sample suggested questions - these would be generated based on the document content
            const suggestions = [
                "What are the key findings?",
                "Summarize the main points",
                "What are the conclusions?",
                "What methodology was used?",
                "When was this published?"
            ];
            
            suggestions.forEach(question => {
                const pill = document.createElement('div');
                pill.className = 'suggested-question';
                pill.textContent = question;
                pill.addEventListener('click', () => {
                    userInput.value = question;
                    userInput.focus();
                    suggestedQuestionsContainer.remove();
                });
                suggestedQuestionsContainer.appendChild(pill);
            });
            
            // Insert before chat input
            document.querySelector('.chat-input').insertAdjacentElement('beforebegin', suggestedQuestionsContainer);
            
            // Add animation
            setTimeout(() => {
                document.querySelectorAll('.suggested-question').forEach((pill, index) => {
                    pill.style.transition = 'all 0.3s ease';
                    pill.style.transitionDelay = `${index * 0.05}s`;
                    pill.style.opacity = '1';
                    pill.style.transform = 'translateY(0)';
                });
            }, 10);
        }
    }
    
    // Font size toggle
    function toggleFontSize() {
        const chatMessagesElement = document.getElementById('chatMessages');
        
        switch (fontSizeMode) {
            case 'normal':
                chatMessagesElement.style.fontSize = '1.1rem';
                fontSizeMode = 'large';
                fontSizeToggle.innerHTML = '<i class="fas fa-text-height"></i> Large';
                break;
            case 'large':
                chatMessagesElement.style.fontSize = '0.9rem';
                fontSizeMode = 'small';
                fontSizeToggle.innerHTML = '<i class="fas fa-text-height"></i> Small';
                break;
            case 'small':
                chatMessagesElement.style.fontSize = '1rem';
                fontSizeMode = 'normal';
                fontSizeToggle.innerHTML = '<i class="fas fa-text-height"></i>';
                break;
        }
    }
    
    // Citation highlighting toggle
    function toggleCitationHighlighting() {
        citationHighlightEnabled = !citationHighlightEnabled;
        
        if (citationHighlightEnabled) {
            toggleHighlighting.classList.add('active');
            document.querySelectorAll('.citation').forEach(citation => {
                citation.style.backgroundColor = '';
                citation.style.borderColor = '';
            });
        } else {
            toggleHighlighting.classList.remove('active');
            document.querySelectorAll('.citation').forEach(citation => {
                citation.style.backgroundColor = 'transparent';
                citation.style.borderColor = 'transparent';
                citation.style.color = 'inherit';
            });
        }
    }

    // Load PDF with PDF.js if it's available
    function loadPdf(pdfUrl = '/static/uploads/sample.pdf') {
        if (typeof pdfjsLib !== 'undefined') {
            // Show loading indicator
            pdfContent.innerHTML = `
                <div class="pdf-loading d-flex flex-column align-items-center justify-content-center w-100 h-100">
                    <div class="spinner mb-3">
                        <i class="fas fa-spinner fa-spin fa-2x"></i>
                    </div>
                    <p>Loading document...</p>
                </div>
            `;
            
            // Using PDF.js to render the PDF
            const loadingTask = pdfjsLib.getDocument(pdfUrl);

            loadingTask.promise.then(function(pdf) {
                pdfInstance = pdf;
                totalPages = pdf.numPages;
                updatePageIndicator();
                renderPage(currentPage);
                
                // Enable/disable pagination buttons
                updatePaginationButtons();
            }).catch(function(error) {
                console.error('Error loading PDF:', error);
                pdfContent.innerHTML = `
                    <div class="alert alert-danger m-3">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Failed to load PDF: ${error.message}
                    </div>`;
            });
        } else {
            // Fallback to showing an image placeholder
            pdfContent.innerHTML = `
                <div class="d-flex flex-column align-items-center justify-content-center w-100 h-100">
                    <i class="fas fa-file-pdf fa-3x mb-3 text-danger"></i>
                    <p>PDF Viewer not available</p>
                    <p class="small text-muted">Please install PDF.js to view documents</p>
                </div>`;
        }
    }

    // Render a specific page of the PDF
    function renderPage(pageNumber) {
        if (!pdfInstance) return;
        
        // Show loading spinner inside the current canvas area
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        loadingOverlay.innerHTML = '<i class="fas fa-spinner fa-spin fa-2x"></i>';
        loadingOverlay.style.backgroundColor = 'rgba(0,0,0,0.2)';
        
        if (pdfContent.querySelector('canvas')) {
            const canvasContainer = document.createElement('div');
            canvasContainer.className = 'position-relative';
            canvasContainer.appendChild(pdfContent.querySelector('canvas'));
            canvasContainer.appendChild(loadingOverlay);
            pdfContent.innerHTML = '';
            pdfContent.appendChild(canvasContainer);
        }

        pdfInstance.getPage(pageNumber).then(function(page) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            const viewport = page.getViewport({ scale: scale });

            canvas.height = viewport.height;
            canvas.width = viewport.width;

            // Clear the pdfContent div and add the canvas
            pdfContent.innerHTML = '';
            pdfContent.appendChild(canvas);

            // Render the PDF page on the canvas with animation
            canvas.style.opacity = '0';
            canvas.style.transform = 'scale(0.98)';
            
            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };

            const renderTask = page.render(renderContext);
            renderTask.promise.then(() => {
                // Fade in the rendered page
                setTimeout(() => {
                    canvas.style.transition = 'all 0.3s ease';
                    canvas.style.opacity = '1';
                    canvas.style.transform = 'scale(1)';
                }, 50);
                
                currentPage = pageNumber;
                updatePageIndicator();
                updatePaginationButtons();
            });
        });
    }

    // Zoom controls
    if (zoomIn) {
        zoomIn.addEventListener('click', function() {
            if (scale < 3.0) {
                scale += 0.2;
                if (pdfInstance) renderPage(currentPage);
            }
        });
    }

    if (zoomOut) {
        zoomOut.addEventListener('click', function() {
            if (scale > 0.5) {
                scale -= 0.2;
                if (pdfInstance) renderPage(currentPage);
            }
        });
    }

    // Fullscreen toggle
    if (toggleFullscreen) {
        toggleFullscreen.addEventListener('click', function() {
            if (document.fullscreenElement) {
                document.exitFullscreen();
                toggleFullscreen.innerHTML = '<i class="fas fa-expand"></i>';
            } else {
                pdfContent.requestFullscreen();
                toggleFullscreen.innerHTML = '<i class="fas fa-compress"></i>';
            }
        });
    }
    
    // Citation click handler
    function setupCitationHandlers() {
        document.querySelectorAll('.citation').forEach(citation => {
            citation.addEventListener('click', function() {
                const page = parseInt(this.getAttribute('data-page'));
                if (pdfInstance && page && page <= pdfInstance.numPages) {
                    renderPage(page);
                }
            });
        });
    }    // Chat functionality
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '' || isProcessing) return;
        
        isProcessing = true;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Add to chat history
        chatHistory.push({role: 'user', content: message});
        
        // In a real app, you would send the message to your backend API
        // For now, we'll simulate a response after a delay
        setTimeout(() => {
            // Hide typing indicator
            hideTypingIndicator();
            
            // Add bot response based on user query
            let botResponse = '';
            
            if (message.toLowerCase().includes('revenue') || message.toLowerCase().includes('financial') || message.toLowerCase().includes('growth')) {
                botResponse = `<p>Based on the financial data in this document, the company's revenue increased by 15% in Q2 2025 compared to the same period last year. This growth exceeds the industry average of 8.2% <span class='citation' data-page='4'>p.4</span>.</p>
                <p>Key factors contributing to this growth include:</p>
                <ul>
                    <li>New product launches (+7.5%) <span class='citation' data-page='6'>p.6</span></li>
                    <li>Expansion into Asian markets (+4.8%) <span class='citation' data-page='9'>p.9</span></li>
                    <li>Increased digital service offerings (+2.7%) <span class='citation' data-page='12'>p.12</span></li>
                </ul>
                <p>The projection for FY2025 indicates sustained growth at 12-14% <span class='citation' data-page='18'>p.18</span>.</p>`;
            } 
            else if (message.toLowerCase().includes('timeline') || message.toLowerCase().includes('schedule') || message.toLowerCase().includes('deadline')) {
                botResponse = `The project timeline outlined in the document shows the following key dates:
                <ul>
                    <li>Phase 1 completion: March 2025 <span class='citation' data-page='15'>p.15</span></li>
                    <li>Mid-project review: July 2025 <span class='citation' data-page='16'>p.16</span></li>
                    <li>Final implementation: October 2025 <span class='citation' data-page='16'>p.16</span></li>
                    <li>Project evaluation: December 2025 <span class='citation' data-page='17'>p.17</span></li>
                </ul>
                Note that the timeline has been extended by 2 months from the original plan due to expanded scope requirements <span class='citation' data-page='12'>p.12</span>.`;
            }
            else if (message.toLowerCase().includes('summary') || message.toLowerCase().includes('overview') || message.toLowerCase().includes('main points')) {
                botResponse = `According to the executive summary <span class='citation' data-page='1'>p.1</span>, this report focuses on three main areas:
                <ol>
                    <li>Sustainable growth initiatives across global markets</li>
                    <li>Technological innovation and digital transformation</li>
                    <li>Strategic partnerships and acquisition opportunities</li>
                </ol>
                The key findings suggest that the company is well-positioned to achieve its 5-year strategic goals, with particular strength in the North American and European markets <span class='citation' data-page='2'>p.2</span>.`;
            }
            else {
                botResponse = `Based on my analysis of the document, the information you're looking for appears to be on pages 8-12 <span class='citation' data-page='8'>p.8-12</span>. 
                
                The document highlights several important points related to your question:
                <ul>
                    <li>Strategic focus areas for 2025-2030 <span class='citation' data-page='10'>p.10</span></li>
                    <li>Market analysis of emerging trends <span class='citation' data-page='14'>p.14</span></li>
                    <li>Competitive positioning recommendations <span class='citation' data-page='22'>p.22</span></li>
                </ul>
                
                Would you like me to focus on any specific aspect of this information?`;
            }
            
            addMessage(botResponse, 'bot');
            
            // Add to chat history
            chatHistory.push({role: 'assistant', content: botResponse});
            
            // Setup citation handlers for the new message
            setupCitationHandlers();
            
            // Reset processing flag
            isProcessing = false;
        }, 2000 + Math.random() * 1000); // Randomize response time a bit for realism
    }
    
    // Add message to chat
    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        // Get current timestamp
        const now = new Date();
        let timeString = '';
        
        // Format timestamp based on how recent it is
        if (now.getDate() === new Date().getDate()) {
            // Today - show time only
            timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else {
            // Another day - show date and time
            timeString = now.toLocaleDateString([], { month: 'short', day: 'numeric' }) + 
                        ', ' + now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        
        // Appropriate icon based on message type
        const iconClass = type === 'user' ? 'fas fa-user' : 'fas fa-robot';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${content}
            </div>
            <div class="message-timestamp">
                ${timeString}
            </div>
            <div class="message-avatar">
                <i class="${iconClass}"></i>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listeners
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Focus input on page load
        setTimeout(() => userInput.focus(), 500);
        
        // Add input field animations
        userInput.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
        });
        
        userInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
        });
    }
    
    // Clear chat functionality
    if (clearChat) {
        clearChat.addEventListener('click', function() {
            // Show confirmation dialog
            showConfirmationDialog('Clear conversation', 'Are you sure you want to clear the entire conversation? This cannot be undone.', function() {
                // Keep only the first welcome message
                const welcomeMessage = chatMessages.querySelector('.message');
                
                // Clear chat container
                chatMessages.innerHTML = '';
                
                if (welcomeMessage) {
                    chatMessages.appendChild(welcomeMessage);
                }
                
                // Reset chat history
                chatHistory = [];
                
                // Add system message
                const systemMessage = document.createElement('div');
                systemMessage.className = 'system-message';
                systemMessage.textContent = 'Conversation cleared';
                chatMessages.appendChild(systemMessage);
                
                // Auto-remove system message after a few seconds
                setTimeout(() => {
                    systemMessage.classList.add('fade-out');
                    setTimeout(() => {
                        if (systemMessage.parentElement === chatMessages) {
                            chatMessages.removeChild(systemMessage);
                        }
                    }, 500);
                }, 3000);
            });
        });
    }
    
    // Export chat functionality
    if (exportChat) {
        exportChat.addEventListener('click', function() {
            showExportOptions();
        });
    }
    
    // Function to show export options
    function showExportOptions() {
        // Create modal container if it doesn't exist
        let modal = document.getElementById('exportModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'exportModal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Export Conversation</h3>
                        <button class="modal-close"><i class="fas fa-times"></i></button>
                    </div>
                    <div class="modal-body">
                        <p>Choose your preferred export format:</p>
                        <div class="export-options">
                            <div class="export-option" data-format="text">
                                <i class="fas fa-file-alt"></i>
                                <span>Plain Text</span>
                            </div>
                            <div class="export-option" data-format="html">
                                <i class="fas fa-file-code"></i>
                                <span>HTML</span>
                            </div>
                            <div class="export-option" data-format="pdf">
                                <i class="fas fa-file-pdf"></i>
                                <span>PDF</span>
                            </div>
                            <div class="export-option" data-format="json">
                                <i class="fas fa-file-code"></i>
                                <span>JSON</span>
                            </div>
                        </div>
                        <div class="export-options-detail mt-3">
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" id="includePdfInfo" checked>
                                <label class="form-check-label" for="includePdfInfo">Include document metadata</label>
                            </div>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" id="includeTimestamps" checked>
                                <label class="form-check-label" for="includeTimestamps">Include timestamps</label>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary modal-cancel">Cancel</button>
                        <button class="btn btn-primary" id="exportConfirm">Export</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Add event listeners to the modal
            modal.querySelector('.modal-close').addEventListener('click', () => {
                modal.classList.remove('show');
                setTimeout(() => modal.remove(), 300);
            });
            
            modal.querySelector('.modal-cancel').addEventListener('click', () => {
                modal.classList.remove('show');
                setTimeout(() => modal.remove(), 300);
            });
            
            // Handle export option selection
            modal.querySelectorAll('.export-option').forEach(option => {
                option.addEventListener('click', function() {
                    modal.querySelectorAll('.export-option').forEach(o => o.classList.remove('selected'));
                    this.classList.add('selected');
                });
            });
            
            // Handle export button click
            modal.querySelector('#exportConfirm').addEventListener('click', () => {
                const selectedFormat = modal.querySelector('.export-option.selected')?.getAttribute('data-format') || 'text';
                const includeMeta = modal.querySelector('#includePdfInfo').checked;
                const includeTimestamps = modal.querySelector('#includeTimestamps').checked;
                
                exportChatHistory(selectedFormat, includeMeta, includeTimestamps);
                modal.classList.remove('show');
                setTimeout(() => modal.remove(), 300);
            });
        }
        
        // Show the first option as selected by default
        setTimeout(() => {
            const firstOption = modal.querySelector('.export-option');
            if (firstOption) firstOption.classList.add('selected');
        }, 10);
        
        // Show the modal with animation
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 10);
    }
    
    // Function to export chat history
    function exportChatHistory(format = 'text', includeMeta = true, includeTimestamps = true) {
        let content = '';
        const filename = `chat-export-${new Date().toISOString().slice(0, 10)}`;
        
        // Create document title and metadata
        if (includeMeta) {
            content += `Chat with document: ${documentId}\n`;
            content += `Date: ${new Date().toLocaleDateString()}\n`;
            content += `-------------------------------\n\n`;
        }
        
        // Process each message
        document.querySelectorAll('.message').forEach(msg => {
            const isUser = msg.classList.contains('user');
            const role = isUser ? 'You' : 'Assistant';
            const messageContent = msg.querySelector('.message-content').textContent.trim();
            const timestamp = includeTimestamps ? msg.querySelector('.message-timestamp').textContent.trim() : '';
            
            if (format === 'text') {
                content += `${role}: ${messageContent}\n`;
                if (includeTimestamps) content += `[${timestamp}]\n`;
                content += '\n';
            }
            else if (format === 'html') {
                content += `<p><strong>${role}:</strong> ${messageContent}</p>`;
                if (includeTimestamps) content += `<p class="timestamp">${timestamp}</p>`;
            }
            else if (format === 'json') {
                if (!content) content = '{"messages":[';
                else content += ',';
                content += `{"role":"${role.toLowerCase()}","content":"${messageContent.replace(/"/g, '\\"')}"`;
                if (includeTimestamps) content += `,"timestamp":"${timestamp}"`;
                content += `}`;
            }
        });
        
        if (format === 'json') content += ']}';
        
        // Create download link
        const element = document.createElement('a');
        let fileExtension = format;
        if (format === 'text') fileExtension = 'txt';
        
        const file = new Blob([content], {type: `text/${fileExtension}`});
        element.href = URL.createObjectURL(file);
        element.download = `${filename}.${fileExtension}`;
        
        // Trigger download
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        // Show success message
        showToast('Conversation exported successfully!');
    }
    
    // Confirmation dialog
    function showConfirmationDialog(title, message, confirmCallback) {
        // Create modal container
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary modal-cancel">Cancel</button>
                    <button class="btn btn-danger modal-confirm">Confirm</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show with animation
        setTimeout(() => modal.classList.add('show'), 10);
        
        // Add event listeners
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        });
        
        modal.querySelector('.modal-cancel').addEventListener('click', () => {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        });
        
        modal.querySelector('.modal-confirm').addEventListener('click', () => {
            if (typeof confirmCallback === 'function') {
                confirmCallback();
            }
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        });
    }
    
    // Toast notification
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close"><i class="fas fa-times"></i></button>
        `;
        
        // Create container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Show with animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Auto close after 5 seconds
        const timeout = setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            clearTimeout(timeout);
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });
    }
});
