/**
 * Authentication Handler
 * Handles login, registration, and password reset functionality
 */

class AuthHandler {
    constructor() {
        this.init();
    }

    /**
     * Initialize authentication handler
     */
    init() {
        this.bindEvents();
        this.checkAuthStatus();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Login form
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }

        // Registration form
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', this.handleRegister.bind(this));
        }

        // Forgot password form
        const forgotPasswordForm = document.getElementById('forgot-password-form');
        if (forgotPasswordForm) {
            forgotPasswordForm.addEventListener('submit', this.handleForgotPassword.bind(this));
        }

        // Reset password form
        const resetPasswordForm = document.getElementById('reset-password-form');
        if (resetPasswordForm) {
            resetPasswordForm.addEventListener('submit', this.handleResetPassword.bind(this));
        }

        // Logout buttons
        const logoutButtons = document.querySelectorAll('[data-action="logout"]');
        logoutButtons.forEach(button => {
            button.addEventListener('click', this.handleLogout.bind(this));
        });
    }

    /**
     * Check authentication status and redirect if needed
     */
    checkAuthStatus() {
        const isAuthenticated = window.api.isAuthenticated();
        const currentPath = window.location.pathname;
        
        // Define protected routes
        const protectedRoutes = ['/documents', '/conversation', '/profile'];
        const authRoutes = ['/login', '/register'];

        // Redirect authenticated users away from auth pages
        if (isAuthenticated && authRoutes.includes(currentPath)) {
            window.location.href = '/documents';
            return;
        }

        // Redirect unauthenticated users to login for protected routes
        if (!isAuthenticated && protectedRoutes.some(route => currentPath.startsWith(route))) {
            window.location.href = '/login';
            return;
        }
    }

    /**
     * Handle login form submission
     * @param {Event} e - Form submit event
     */
    async handleLogin(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const email = formData.get('email');
        const password = formData.get('password');

        // Show loading state
        this.setFormLoading(form, true);
        this.clearFormErrors(form);

        try {
            const response = await window.api.login(email, password);

            if (response.status === 'success') {
                this.showSuccess('Login successful! Redirecting...');
                
                // Small delay before redirect for UX
                setTimeout(() => {
                    window.location.href = '/documents';
                }, 1000);
            } else {
                this.showError(response.message || 'Login failed');
            }
        } catch (error) {
            this.showError(error.message || 'Login failed. Please try again.');
        } finally {
            this.setFormLoading(form, false);
        }
    }

    /**
     * Handle registration form submission
     * @param {Event} e - Form submit event
     */
    async handleRegister(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        
        const userData = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            email: formData.get('email'),
            password: formData.get('password')
        };

        const confirmPassword = formData.get('confirm_password');

        // Validate passwords match
        if (userData.password !== confirmPassword) {
            this.showError('Passwords do not match');
            return;
        }

        // Show loading state
        this.setFormLoading(form, true);
        this.clearFormErrors(form);

        try {
            const response = await window.api.register(userData);

            if (response.status === 'success') {
                this.showSuccess('Registration successful! Please login.');
                
                // Clear form and redirect to login
                form.reset();
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                this.showError(response.message || 'Registration failed');
            }
        } catch (error) {
            this.showError(error.message || 'Registration failed. Please try again.');
        } finally {
            this.setFormLoading(form, false);
        }
    }

    /**
     * Handle forgot password form submission
     * @param {Event} e - Form submit event
     */
    async handleForgotPassword(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const email = formData.get('email');

        // Show loading state
        this.setFormLoading(form, true);
        this.clearFormErrors(form);

        try {
            const response = await window.api.forgotPassword(email);

            if (response.status === 'success') {
                this.showSuccess('Password reset link sent! Check your email.');
                form.reset();
            } else {
                this.showError(response.message || 'Failed to send reset link');
            }
        } catch (error) {
            this.showError(error.message || 'Failed to send reset link. Please try again.');
        } finally {
            this.setFormLoading(form, false);
        }
    }

    /**
     * Handle reset password form submission
     * @param {Event} e - Form submit event
     */
    async handleResetPassword(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        const token = formData.get('token');

        // Validate passwords match
        if (password !== confirmPassword) {
            this.showError('Passwords do not match');
            return;
        }

        // Show loading state
        this.setFormLoading(form, true);
        this.clearFormErrors(form);

        try {
            // For now, we'll use a direct form submission since the reset endpoint might not be JWT-based
            form.submit();
        } catch (error) {
            this.showError(error.message || 'Password reset failed. Please try again.');
            this.setFormLoading(form, false);
        }
    }

    /**
     * Handle logout
     * @param {Event} e - Click event
     */
    async handleLogout(e) {
        e.preventDefault();

        try {
            await window.api.logout();
        } catch (error) {
            console.error('Logout error:', error);
            // Still redirect even if API call fails
            window.location.href = '/';
        }
    }

    /**
     * Set form loading state
     * @param {HTMLFormElement} form - Form element
     * @param {boolean} loading - Loading state
     */
    setFormLoading(form, loading) {
        const submitButton = form.querySelector('button[type="submit"]');
        const inputs = form.querySelectorAll('input, button');

        if (loading) {
            // Disable form elements
            inputs.forEach(input => input.disabled = true);
            
            // Update submit button text
            if (submitButton) {
                submitButton.dataset.originalText = submitButton.textContent;
                submitButton.innerHTML = `
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                `;
            }
        } else {
            // Enable form elements
            inputs.forEach(input => input.disabled = false);
            
            // Restore submit button text
            if (submitButton && submitButton.dataset.originalText) {
                submitButton.textContent = submitButton.dataset.originalText;
            }
        }
    }

    /**
     * Clear form errors
     * @param {HTMLFormElement} form - Form element
     */
    clearFormErrors(form) {
        // Remove existing error messages
        const errorElements = form.querySelectorAll('.error-message');
        errorElements.forEach(el => el.remove());

        // Remove error styling from inputs
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.classList.remove('border-red-500', 'ring-red-500');
        });
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
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification fixed top-4 right-4 max-w-sm p-4 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full`;
        
        // Set notification styling based on type
        switch (type) {
            case 'success':
                notification.classList.add('bg-green-500', 'text-white');
                break;
            case 'error':
                notification.classList.add('bg-red-500', 'text-white');
                break;
            default:
                notification.classList.add('bg-blue-500', 'text-white');
        }

        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('translate-x-full');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
}

// Initialize authentication handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.authHandler = new AuthHandler();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthHandler;
}
