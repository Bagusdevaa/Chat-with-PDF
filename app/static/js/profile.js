/**
 * Profile Management Handler
 * Manages user profile operations including personal information updates,
 * password changes, avatar uploads, and account settings.
 */
class ProfileHandler {
    constructor() {
        this.api = new APIHandler();
        this.currentUser = null;
        this.init();
    }

    async init() {
        try {
            // Check authentication
            if (!this.api.isAuthenticated()) {
                window.location.href = '/login';
                return;
            }

            // Load user profile data
            await this.loadUserProfile();
            this.bindEvents();
            this.updateUI();
        } catch (error) {
            console.error('Profile initialization error:', error);
            this.showNotification('Failed to load profile', 'error');
        }
    }    async loadUserProfile() {
        try {
            // Get user profile from API
            const response = await this.api.get('/api/auth/profile');
            this.currentUser = response.user;
        } catch (error) {
            console.error('Failed to load user profile:', error);
            // Use mock data for now if API endpoint doesn't exist
            this.currentUser = {
                id: 1,
                first_name: 'John',
                last_name: 'Doe',
                email: 'john.doe@example.com',
                avatar: null,
                created_at: '2025-05-15',
                documents_count: 12,
                storage_used: '45.8 MB'
            };
        }
    }

    updateUI() {
        if (!this.currentUser) return;

        // Update avatar and user info
        const avatarElement = document.querySelector('.user-avatar');
        if (avatarElement) {
            if (this.currentUser.avatar) {
                avatarElement.innerHTML = `<img src="${this.currentUser.avatar}" alt="Avatar" class="w-full h-full object-cover rounded-full">`;
            } else {
                const initials = `${this.currentUser.first_name[0]}${this.currentUser.last_name[0]}`.toUpperCase();
                avatarElement.textContent = initials;
            }
        }

        // Update user name and email
        const nameElement = document.querySelector('.user-name');
        if (nameElement) {
            nameElement.textContent = `${this.currentUser.first_name} ${this.currentUser.last_name}`;
        }

        const emailElement = document.querySelector('.user-email');
        if (emailElement) {
            emailElement.textContent = this.currentUser.email;
        }

        // Update form fields
        const firstNameInput = document.getElementById('first-name');
        const lastNameInput = document.getElementById('last-name');
        const emailInput = document.getElementById('email');

        if (firstNameInput) firstNameInput.value = this.currentUser.first_name;
        if (lastNameInput) lastNameInput.value = this.currentUser.last_name;
        if (emailInput) emailInput.value = this.currentUser.email;

        // Update account stats
        const memberSinceElement = document.querySelector('.member-since');
        if (memberSinceElement) {
            const date = new Date(this.currentUser.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            memberSinceElement.textContent = date;
        }

        const documentsCountElement = document.querySelector('.documents-count');
        if (documentsCountElement) {
            documentsCountElement.textContent = this.currentUser.documents_count;
        }

        const storageUsedElement = document.querySelector('.storage-used');
        if (storageUsedElement) {
            storageUsedElement.textContent = this.currentUser.storage_used;
        }
    }

    bindEvents() {
        // Personal information form
        const personalInfoForm = document.getElementById('personal-info-form');
        if (personalInfoForm) {
            personalInfoForm.addEventListener('submit', (e) => this.handlePersonalInfoSubmit(e));
        }

        // Password change form
        const passwordForm = document.getElementById('password-form');
        if (passwordForm) {
            passwordForm.addEventListener('submit', (e) => this.handlePasswordChangeSubmit(e));
        }

        // Avatar upload
        const avatarUpload = document.getElementById('avatar-upload');
        if (avatarUpload) {
            avatarUpload.addEventListener('change', (e) => this.handleAvatarUpload(e));
        }

        // Notification preferences
        const notificationForm = document.getElementById('notification-form');
        if (notificationForm) {
            notificationForm.addEventListener('submit', (e) => this.handleNotificationSubmit(e));
        }

        // Delete account
        const deleteAccountBtn = document.getElementById('delete-account-btn');
        if (deleteAccountBtn) {
            deleteAccountBtn.addEventListener('click', (e) => this.handleDeleteAccount(e));
        }

        // Logout functionality
        const logoutBtns = document.querySelectorAll('a[href="/logout"]');
        logoutBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });
        });

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
    }

    async handlePersonalInfoSubmit(e) {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            this.setLoading(submitBtn, true);

            const formData = new FormData(e.target);
            const data = {
                first_name: formData.get('first_name') || document.getElementById('first-name').value,
                last_name: formData.get('last_name') || document.getElementById('last-name').value,
                email: formData.get('email') || document.getElementById('email').value
            };            // Update profile via API
            await this.api.put('/api/auth/profile', data);
            
            // Update local user data
            this.currentUser = { ...this.currentUser, ...data };
            this.updateUI();
            
            this.showNotification('Profile updated successfully!', 'success');
        } catch (error) {
            console.error('Profile update error:', error);
            this.showNotification(error.message || 'Failed to update profile', 'error');
        } finally {
            this.setLoading(submitBtn, false, originalText);
        }
    }

    async handlePasswordChangeSubmit(e) {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            this.setLoading(submitBtn, true);

            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            // Validation
            if (!currentPassword || !newPassword || !confirmPassword) {
                throw new Error('All password fields are required');
            }

            if (newPassword !== confirmPassword) {
                throw new Error('New passwords do not match');
            }

            if (newPassword.length < 6) {
                throw new Error('New password must be at least 6 characters long');
            }

            const data = {
                current_password: currentPassword,
                new_password: newPassword
            };

            await this.api.put('/api/auth/change-password', data);
            
            // Clear form
            e.target.reset();
            
            this.showNotification('Password updated successfully!', 'success');
        } catch (error) {
            console.error('Password change error:', error);
            this.showNotification(error.message || 'Failed to update password', 'error');
        } finally {
            this.setLoading(submitBtn, false, originalText);
        }
    }

    async handleAvatarUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file
        if (!file.type.startsWith('image/')) {
            this.showNotification('Please select an image file', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) { // 5MB limit
            this.showNotification('Image file must be less than 5MB', 'error');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('avatar', file);            // Upload avatar
            const response = await this.api.upload('/api/auth/avatar', formData);
            
            // Update UI with new avatar
            this.currentUser.avatar = response.avatar_url;
            this.updateUI();
            
            this.showNotification('Avatar updated successfully!', 'success');
        } catch (error) {
            console.error('Avatar upload error:', error);
            this.showNotification('Failed to upload avatar', 'error');
        }
    }

    async handleNotificationSubmit(e) {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            this.setLoading(submitBtn, true);

            const formData = new FormData(e.target);
            const preferences = {
                email_notifications: formData.has('email_notifications'),
                push_notifications: formData.has('push_notifications'),
                marketing_emails: formData.has('marketing_emails')
            };

            await this.api.put('/api/auth/notification-preferences', preferences);
            
            this.showNotification('Notification preferences updated!', 'success');
        } catch (error) {
            console.error('Notification preferences error:', error);
            this.showNotification('Failed to update preferences', 'error');
        } finally {
            this.setLoading(submitBtn, false, originalText);
        }
    }

    async handleDeleteAccount(e) {
        e.preventDefault();
        
        const confirmed = confirm(
            'Are you sure you want to delete your account? This action cannot be undone and will permanently delete all your documents and data.'
        );
        
        if (!confirmed) return;

        try {
            await this.api.delete('/api/auth/account');
            
            // Clear local storage and redirect
            this.api.clearAuth();
            this.showNotification('Account deleted successfully', 'success');
            
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } catch (error) {
            console.error('Account deletion error:', error);
            this.showNotification('Failed to delete account', 'error');
        }
    }

    async handleLogout() {
        try {
            await this.api.logout();
            window.location.href = '/';
        } catch (error) {
            console.error('Logout error:', error);
            // Clear local storage anyway
            this.api.clearAuth();
            window.location.href = '/';
        }
    }

    setLoading(button, isLoading, originalText = 'Save Changes') {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Saving...
            `;
        } else {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.className = 'fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full';
            document.body.appendChild(notification);
        }

        // Set notification content and style
        const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform ${bgColor} text-white`;
        notification.textContent = message;

        // Show notification
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);

        // Hide notification after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
        }, 5000);
    }
}

// Initialize profile handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProfileHandler();
});
