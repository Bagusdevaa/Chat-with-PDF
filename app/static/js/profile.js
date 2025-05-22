// User Profile functionality for PDF Chat Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and panes
            tabBtns.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to current button and pane
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
    
    // Password visibility toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordInput = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            // Toggle password visibility
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Theme toggle sync with system preference
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (darkModeToggle) {
        // Get current theme preference
        const currentTheme = localStorage.getItem('theme') || 'dark';
        
        // Set initial toggle state
        darkModeToggle.checked = currentTheme === 'dark';
        
        // Listen for changes
        darkModeToggle.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            localStorage.setItem('theme', newTheme);
            
            // Apply theme
            document.documentElement.setAttribute('data-theme', newTheme === 'light' ? 'light' : '');
            
            // Update main toggle as well (the one in the navbar)
            const mainToggle = document.getElementById('toggleDarkMode');
            if (mainToggle) {
                const moonIcon = mainToggle.querySelector('i');
                if (moonIcon) {
                    if (newTheme === 'dark') {
                        moonIcon.classList.remove('fa-sun');
                        moonIcon.classList.add('fa-moon');
                    } else {
                        moonIcon.classList.remove('fa-moon');
                        moonIcon.classList.add('fa-sun');
                    }
                }
            }
        });
    }
    
    // Form validation for account settings
    const accountForm = document.getElementById('accountForm');
    
    if (accountForm) {
        accountForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            
            // Basic validation
            if (!username) {
                showToast('Username cannot be empty', 'error');
                return;
            }
            
            if (!email || !validateEmail(email)) {
                showToast('Please enter a valid email address', 'error');
                return;
            }
            
            // If changing password, require current password
            if (newPassword && !currentPassword) {
                showToast('Current password is required to set a new password', 'error');
                return;
            }
            
            // Prepare data for API call
            const userData = {
                username: username,
                email: email
            };
            
            if (newPassword) {
                userData.current_password = currentPassword;
                userData.new_password = newPassword;
            }
            
            // Show loading state
            const submitBtn = accountForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Saving...';
            
            // Simulate API call (replace with actual API call)
            setTimeout(() => {
                // Reset form state
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                
                // Show success message
                showToast('Profile updated successfully', 'success');
                
                // Clear password fields
                document.getElementById('current-password').value = '';
                document.getElementById('new-password').value = '';
            }, 1500);
        });
    }
    
    // Handle preference changes
    const preferenceToggles = document.querySelectorAll('#preferences .switch input');
    
    preferenceToggles.forEach(toggle => {
        if (toggle.id !== 'darkModeToggle') { // We already handled the dark mode toggle
            toggle.addEventListener('change', function() {
                const prefName = this.id.replace('Toggle', '');
                const prefValue = this.checked;
                
                // Save preference (replace with actual saving mechanism)
                localStorage.setItem(prefName, prefValue);
                
                // Show feedback
                showToast(`${prefName} preference updated`, 'info');
            });
        }
    });
    
    // Document actions
    const documentActionButtons = document.querySelectorAll('.document-actions .btn-icon');
    
    documentActionButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const action = this.getAttribute('title');
            const documentCard = this.closest('.document-card');
            const documentTitle = documentCard.querySelector('.document-title').textContent;
            
            if (action.includes('Delete')) {
                // For delete, we should show a confirmation dialog
                showConfirmDialog(
                    'Delete Document', 
                    `Are you sure you want to delete "${documentTitle}"?`, 
                    () => {
                        // Delete action
                        documentCard.style.opacity = '0';
                        documentCard.style.height = '0';
                        documentCard.style.margin = '0';
                        documentCard.style.padding = '0';
                        documentCard.style.overflow = 'hidden';
                        
                        setTimeout(() => {
                            documentCard.remove();
                            showToast('Document deleted successfully', 'success');
                        }, 300);
                    }
                );
            } else if (action.includes('Chat')) {
                // Redirect to conversation page
                showToast('Opening conversation...', 'info');
                
                // Simulate redirect - replace with actual redirect
                setTimeout(() => {
                    window.location.href = '/conversation?document=' + encodeURIComponent(documentTitle);
                }, 500);
            } else if (action.includes('Download')) {
                showToast('Downloading document...', 'info');
                
                // Simulate download - replace with actual download
                setTimeout(() => {
                    showToast('Document downloaded successfully', 'success');
                }, 1500);
            }
        });
    });
});

// Helper function to validate email
function validateEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

// Toast notification system
function showToast(message, type = 'info') {
    // Check if toast container exists, create if not
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Icon based on type
    let icon;
    switch (type) {
        case 'success':
            icon = 'fa-check-circle';
            break;
        case 'error':
            icon = 'fa-exclamation-circle';
            break;
        case 'warning':
            icon = 'fa-exclamation-triangle';
            break;
        default:
            icon = 'fa-info-circle';
    }
    
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close"><i class="fas fa-times"></i></button>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Auto close after 5 seconds
    const autoCloseTimeout = setTimeout(() => {
        closeToast(toast);
    }, 5000);
    
    // Close button
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        clearTimeout(autoCloseTimeout);
        closeToast(toast);
    });
}

function closeToast(toast) {
    toast.classList.remove('show');
    
    // Remove after animation completes
    setTimeout(() => {
        if (toast.parentElement) {
            toast.parentElement.removeChild(toast);
            
            // Remove container if empty
            const toastContainer = document.querySelector('.toast-container');
            if (toastContainer && toastContainer.children.length === 0) {
                document.body.removeChild(toastContainer);
            }
        }
    }, 300);
}

// Confirmation dialog
function showConfirmDialog(title, message, confirmCallback) {
    // Check if modal container exists
    let modalContainer = document.querySelector('.modal-container');
    
    if (!modalContainer) {
        modalContainer = document.createElement('div');
        modalContainer.className = 'modal-container';
        document.body.appendChild(modalContainer);
    }
    
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
    
    modalContainer.appendChild(modal);
    
    // Show modal with animation
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // Event listeners
    const closeBtn = modal.querySelector('.modal-close');
    const cancelBtn = modal.querySelector('.modal-cancel');
    const confirmBtn = modal.querySelector('.modal-confirm');
    
    const closeModal = () => {
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentElement) {
                modal.parentElement.removeChild(modal);
                
                // Remove container if empty
                if (modalContainer.children.length === 0) {
                    document.body.removeChild(modalContainer);
                }
            }
        }, 300);
    };
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    confirmBtn.addEventListener('click', () => {
        if (typeof confirmCallback === 'function') {
            confirmCallback();
        }
        closeModal();
    });
}
