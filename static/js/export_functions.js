// Add functionality for downloading PDF and exporting chat
// Add this code at the end of your main.js file

// Add event listeners for PDF operations after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get download PDF button
    const downloadPdfBtn = document.getElementById('downloadPdf');
    
    // Add event listener for PDF download
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', function() {
            if (pdfPath) {
                // Create a link element
                const downloadLink = document.createElement('a');
                downloadLink.href = pdfPath;
                downloadLink.download = pdfName || 'document.pdf';
                
                // Append to body, click and remove
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
            }
        });
    }
    
    // Add functionality to export chat history
    function exportChatHistory() {
        // Get all messages
        const messages = document.querySelectorAll('.message');
        let exportText = `PDF Chat Assistant - Chat History (${new Date().toLocaleString()})\n\n`;
        exportText += `Document: ${pdfName || 'Unknown'}\n`;
        exportText += `Session ID: ${sessionId || 'Unknown'}\n\n`;
        exportText += `------------------------------------\n\n`;
        
        messages.forEach(msg => {
            const isBotMessage = msg.classList.contains('bot');
            const role = isBotMessage ? 'AI Assistant' : 'You';
            const header = msg.querySelector('.message-header');
            const time = header ? header.querySelector('small').textContent : '';
            const content = msg.querySelector('.message-content').textContent;
            
            exportText += `${role} (${time}):\n${content}\n\n`;
        });
        
        // Create a Blob and download link
        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-history-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    // Add export button to chat header
    const chatHeader = document.querySelector('.chat-header');
    if (chatHeader) {
        const exportBtn = document.createElement('button');
        exportBtn.className = 'btn btn-sm btn-outline-light ms-2';
        exportBtn.title = 'Export chat history';
        exportBtn.innerHTML = '<i class="fas fa-file-export"></i>';
        exportBtn.addEventListener('click', exportChatHistory);
        
        // Insert before close button
        const closeBtn = document.getElementById('closeChat');
        if (closeBtn) {
            chatHeader.insertBefore(exportBtn, closeBtn);
        } else {
            chatHeader.appendChild(exportBtn);
        }
    }
});
