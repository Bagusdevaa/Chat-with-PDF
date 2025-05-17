// PDF.js initialization
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.4.120/build/pdf.worker.min.js';

// Global variables
let pdfDoc = null;
let currentPage = 1;
let zoomLevel = 1.0;
let sessionId = null;
let pdfPath = null;
let pdfName = null;
let canvas = null;
let ctx = null;

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const pdfUploadForm = document.getElementById('pdfUploadForm');
    const pdfFileInput = document.getElementById('pdfFileInput');
    const dropzone = document.getElementById('dropzone');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const uploadButton = document.getElementById('uploadButton');
    const removeFile = document.getElementById('removeFile');
    const uploadError = document.getElementById('uploadError');
    const uploadSection = document.getElementById('uploadSection');
    const mainContent = document.getElementById('mainContent');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingMessage = document.getElementById('loadingMessage');
    const testServerBtn = document.getElementById('testServerBtn');
    const pdfFileName = document.getElementById('pdfFileName');
    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const userQuestion = document.getElementById('userQuestion');
    const closeChat = document.getElementById('closeChat');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    const currentPageElement = document.getElementById('currentPage');
    const zoomIn = document.getElementById('zoomIn');
    const zoomOut = document.getElementById('zoomOut');
    canvas = document.getElementById('pdfCanvas');
    ctx = canvas.getContext('2d');    // Event Listeners
    
    // Test server connection
    testServerBtn.addEventListener('click', function() {
        testServerConnection();
    });
    
    // File selection and drag/drop
    pdfFileInput.addEventListener('change', handleFileSelect);
    
    dropzone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropzone.classList.add('active');
    });
    
    dropzone.addEventListener('dragleave', function() {
        dropzone.classList.remove('active');
    });
    
    dropzone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropzone.classList.remove('active');
        
        if (e.dataTransfer.files.length) {
            pdfFileInput.files = e.dataTransfer.files;
            handleFileSelect();
        }
    });
    
    removeFile.addEventListener('click', function() {
        pdfFileInput.value = '';
        fileInfo.classList.add('d-none');
        uploadButton.disabled = true;
    });
    
    // Form submission
    pdfUploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        uploadPDF();
    });
    
    // Chat form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    // Close chat button
    closeChat.addEventListener('click', function() {
        resetApplication();
    });
    
    // PDF Navigation
    prevPage.addEventListener('click', showPrevPage);
    nextPage.addEventListener('click', showNextPage);
    zoomIn.addEventListener('click', zoomInPdf);
    zoomOut.addEventListener('click', zoomOutPdf);

    
    // Functions
    
    function handleFileSelect() {
        const file = pdfFileInput.files[0];
        if (file && file.type === 'application/pdf') {
            fileName.textContent = file.name;
            fileInfo.classList.remove('d-none');
            uploadButton.disabled = false;
            uploadError.classList.add('d-none');
        } else {
            uploadError.textContent = 'Mohon pilih file PDF yang valid.';
            uploadError.classList.remove('d-none');
            fileInfo.classList.add('d-none');
        }
    }
    
    function uploadPDF() {
        const file = pdfFileInput.files[0];
        
        if (!file) {
            uploadError.textContent = 'Mohon pilih file PDF.';
            uploadError.classList.remove('d-none');
            return;
        }
        
        // Show loading overlay
        loadingOverlay.classList.remove('d-none');
        loadingMessage.textContent = 'Memproses dokumen...';
        
        const formData = new FormData();
        formData.append('pdf_file', file);
          fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Store session data
            sessionId = data.session_id;
            pdfPath = data.pdf_path;
            pdfName = data.pdf_name;
            
            // Load the PDF
            loadPDF(pdfPath);
            
            // Update UI
            pdfFileName.textContent = pdfName;
            uploadSection.classList.add('d-none');
            mainContent.classList.remove('d-none');
            
            // Add welcome message
            addBotMessage('Selamat datang di PDF Chat Assistant! Dokumen Anda telah berhasil diproses. Silakan ajukan pertanyaan tentang dokumen ini.');
            
            // Hide loading overlay
            loadingOverlay.classList.add('d-none');
        })
        .catch(error => {
            loadingOverlay.classList.add('d-none');
            uploadError.textContent = `Error: ${error.message}`;
            uploadError.classList.remove('d-none');
        });
    }    function loadPDF(url) {
        console.log("Loading PDF from:", url);
        
        // Add debugging info to the page
        addBotMessage(`Attempting to load PDF from: ${url}`);
        
        const loadingTask = pdfjsLib.getDocument(url);
        
        loadingTask.promise.then(function(pdf) {
            console.log("PDF loaded successfully with", pdf.numPages, "pages");
            pdfDoc = pdf;
            currentPage = 1;
            renderPage(currentPage);
            
            // Add success message
            addBotMessage(`PDF loaded successfully with ${pdf.numPages} pages`);
        }).catch(function(error) {
            console.error('Error loading PDF:', error);
            uploadError.textContent = `Error loading PDF: ${error.message}`;
            uploadError.classList.remove('d-none');
            loadingOverlay.classList.add('d-none');
            
            // Add error message to chat
            addBotMessage(`Failed to load PDF: ${error.message}. Please try uploading again.`);
            
            // Revert UI to upload state if PDF loading fails
            mainContent.classList.add('d-none');
            uploadSection.classList.remove('d-none');
        });
    }
    
    function renderPage(pageNumber) {
        pdfDoc.getPage(pageNumber).then(function(page) {
            const viewport = page.getViewport({ scale: zoomLevel });
            
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            
            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            
            page.render(renderContext);
            
            currentPageElement.textContent = `Halaman ${pageNumber} dari ${pdfDoc.numPages}`;
            
            // Enable/disable navigation buttons
            prevPage.disabled = pageNumber <= 1;
            nextPage.disabled = pageNumber >= pdfDoc.numPages;
        });
    }
    
    function showPrevPage() {
        if (currentPage > 1) {
            currentPage--;
            renderPage(currentPage);
        }
    }
    
    function showNextPage() {
        if (pdfDoc && currentPage < pdfDoc.numPages) {
            currentPage++;
            renderPage(currentPage);
        }
    }
    
    function zoomInPdf() {
        if (zoomLevel < 2.0) {
            zoomLevel += 0.1;
            renderPage(currentPage);
        }
    }
    
    function zoomOutPdf() {
        if (zoomLevel > 0.5) {
            zoomLevel -= 0.1;
            renderPage(currentPage);
        }
    }
    
    function formatTimestamp() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    
    function addUserMessage(message) {
        const time = formatTimestamp();
        const html = `
            <div class="message user">
                <div class="message-header">
                    <strong>Anda</strong>
                    <small>${time}</small>
                </div>
                <div class="message-content">${message}</div>
            </div>
        `;
        chatMessages.innerHTML += html;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addBotMessage(message, responseTime = null) {
        const time = formatTimestamp();
        let footer = '';
        
        if (responseTime) {
            footer = `<div class="message-footer">Response time: ${responseTime} detik</div>`;
        }
        
        const html = `
            <div class="message bot">
                <div class="message-header">
                    <strong>AI Assistant</strong>
                    <small>${time}</small>
                </div>
                <div class="message-content">${message}</div>
                ${footer}
            </div>
        `;
        chatMessages.innerHTML += html;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function showTypingIndicator() {
        const html = `
            <div class="message bot typing" id="typingIndicator">
                <div class="message-header">
                    <strong>AI Assistant</strong>
                    <small>${formatTimestamp()}</small>
                </div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        chatMessages.innerHTML += html;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function sendMessage() {
        const message = userQuestion.value.trim();
        
        if (!message || !sessionId) return;
        
        // Add user message to chat
        addUserMessage(message);
        
        // Show typing indicator
        showTypingIndicator();
        
        // Clear input field
        userQuestion.value = '';
        
        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                question: message
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Add bot message
            addBotMessage(data.response, data.response_time);
        })
        .catch(error => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Show error message
            addBotMessage(`Maaf, saya mengalami masalah saat memproses pertanyaan Anda. Error: ${error.message}`);
        });
    }
      function resetApplication() {
        // Reset to initial state
        uploadSection.classList.remove('d-none');
        mainContent.classList.add('d-none');
        pdfFileInput.value = '';
        fileInfo.classList.add('d-none');
        uploadButton.disabled = true;
        uploadError.classList.add('d-none');
        chatMessages.innerHTML = '';
        
        // Reset PDF variables
        pdfDoc = null;
        currentPage = 1;
        zoomLevel = 1.0;
        sessionId = null;
        pdfPath = null;
        pdfName = null;
    }
    
    function testServerConnection() {
        // Show loading state
        testServerBtn.disabled = true;
        testServerBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin me-2"></i>Testing...';
        
        // Clear any previous errors
        uploadError.classList.add('d-none');
        
        // Try to ping the server
        fetch('/ping')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Show success message
                uploadError.textContent = `Server connection successful! Message: ${data.message}`;
                uploadError.classList.remove('d-none');
                uploadError.classList.remove('alert-danger');
                uploadError.classList.add('alert-success');
                
                console.log("Server ping successful:", data);
            })
            .catch(error => {
                // Show error message
                uploadError.textContent = `Server connection failed: ${error.message}`;
                uploadError.classList.remove('d-none');
                uploadError.classList.add('alert-danger');
                uploadError.classList.remove('alert-success');
                
                console.error("Server ping failed:", error);
            })
            .finally(() => {
                // Reset button state
                testServerBtn.disabled = false;
                testServerBtn.innerHTML = '<i class="fas fa-server me-2"></i>Test Server Connection';
            });
    }
});
