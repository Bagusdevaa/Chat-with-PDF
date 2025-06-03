/**
 * Landing Page Handler
 * Manages the landing page interactions including navigation,
 * mobile menu, and authentication redirects.
 */
class LandingHandler {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkAuthRedirect();
    }

    bindEvents() {
        // Mobile menu toggle
        const menuToggle = document.getElementById('menu-toggle');
        const mobileMenuContainer = document.getElementById('mobile-menu-container');
        const menuOverlay = document.getElementById('menu-overlay');

        if (menuToggle && mobileMenuContainer && menuOverlay) {
            const toggleMenu = () => {
                const isOpen = !mobileMenuContainer.classList.contains('translate-x-full');
                
                if (isOpen) {
                    mobileMenuContainer.classList.add('translate-x-full');
                    mobileMenuContainer.classList.remove('translate-x-0');
                    menuOverlay.classList.remove('opacity-50', 'pointer-events-auto');
                    menuOverlay.classList.add('opacity-0', 'pointer-events-none');
                } else {
                    mobileMenuContainer.classList.remove('translate-x-full');
                    mobileMenuContainer.classList.add('translate-x-0');
                    menuOverlay.classList.remove('opacity-0', 'pointer-events-none');
                    menuOverlay.classList.add('opacity-50', 'pointer-events-auto');
                }
            };

            menuToggle.addEventListener('click', toggleMenu);
            menuOverlay.addEventListener('click', toggleMenu);
        }

        // CTA buttons
        const ctaButtons = document.querySelectorAll('.cta-button');
        ctaButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Check if user is authenticated
                const api = new APIHandler();
                if (api.isAuthenticated()) {
                    window.location.href = '/documents';
                } else {
                    window.location.href = '/login';
                }
            });
        });

        // Smooth scrolling for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        anchorLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Login/Register navigation
        const loginLinks = document.querySelectorAll('a[href="/login"]');
        const registerLinks = document.querySelectorAll('a[href="/register"], a[href="/signup"]');

        loginLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/login';
            });
        });

        registerLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/signup';
            });
        });
    }

    checkAuthRedirect() {
        // If user is already authenticated, optionally redirect to dashboard
        try {
            const api = new APIHandler();
            if (api.isAuthenticated()) {
                // User is logged in, could redirect to documents page
                // Uncomment the following line if you want automatic redirect
                // window.location.href = '/documents';
                
                // Update navigation to show authenticated state
                this.updateNavigationForAuthenticatedUser();
            }
        } catch (error) {
            // API handler not available, continue with normal flow
            console.log('API handler not available on landing page');
        }
    }

    updateNavigationForAuthenticatedUser() {
        // Update navigation buttons for authenticated users
        const authButtons = document.querySelectorAll('.auth-button');
        authButtons.forEach(button => {
            if (button.textContent.includes('Login') || button.textContent.includes('Sign Up')) {
                button.textContent = 'Go to Dashboard';
                button.onclick = () => window.location.href = '/documents';
            }
        });
    }

    // Utility function to show notifications (if needed)
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full ${
            type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'
        } text-white`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.remove('translate-x-full'), 100);
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 5000);
    }
}

// Initialize landing handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LandingHandler();
});
