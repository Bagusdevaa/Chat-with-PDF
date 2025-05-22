// Custom UI JavaScript - Replaces Bootstrap functionality

document.addEventListener('DOMContentLoaded', function() {
    initNavbar();
    initModals();
    initDropdowns();
    initFormValidation();
    initTooltips();
    initInteractiveCards();
    initTabs();
    
    // Document-wide click handler to close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        dropdowns.forEach(dropdown => {
            const dropdownToggle = document.querySelector(`[data-toggle="dropdown"][aria-expanded="true"][data-target="#${dropdown.id}"]`);
            if (dropdownToggle && !dropdownToggle.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.remove('show');
                dropdownToggle.setAttribute('aria-expanded', 'false');
            }
        });
    });
});

// Initialize navbar functionality
function initNavbar() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Toggle mobile menu
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
            
            // Update aria-expanded attribute
            const isExpanded = navbarCollapse.classList.contains('show');
            navbarToggler.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (navbarCollapse.classList.contains('show') && 
                !navbarToggler.contains(e.target) && 
                !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
                navbarToggler.setAttribute('aria-expanded', 'false');
            }
        });
    }
}

// Initialize modal functionality
function initModals() {
    document.querySelectorAll('[data-bs-toggle="modal"], [data-toggle="modal"]').forEach(button => {
        const targetSelector = button.getAttribute('data-bs-target') || button.getAttribute('data-target');
        const modal = document.querySelector(targetSelector);
        
        if (modal) {
            // Open modal
            button.addEventListener('click', function(e) {
                e.preventDefault();
                openModal(modal);
            });
            
            // Close modal with close buttons
            modal.querySelectorAll('[data-bs-dismiss="modal"], [data-dismiss="modal"], .close, .btn-close').forEach(closeBtn => {
                closeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    closeModal(modal);                });
            });
            
            // Close modal when clicking outside
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeModal(modal);
                }
            });
            
            // Close modal with escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && modal.classList.contains('show')) {
                    closeModal(modal);
                }
            });
        }
    });
}

// Open modal helper
function openModal(modal) {
    // Close any open modals first
    document.querySelectorAll('.modal.show').forEach(openModal => {
        if (openModal !== modal) {
            closeModal(openModal);
        }
    });
    
    // Open the modal
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('show');
    }, 10); // Small delay to ensure the transition works
    document.body.classList.add('modal-open');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
    
    // Focus the first focusable element inside modal
    setTimeout(() => {
        const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable.length) {
            focusable[0].focus();
        }
    }, 100);
}

// Close modal helper
function closeModal(modal) {
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300); // Wait for transition to complete
    document.body.classList.remove('modal-open');
    document.body.style.overflow = ''; // Restore scrolling
}

// Initialize dropdown functionality
function initDropdowns() {
    document.querySelectorAll('.dropdown-toggle').forEach(dropdownToggle => {
        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const targetId = this.getAttribute('data-target') || `#${this.nextElementSibling.id}`;
            const dropdownMenu = document.querySelector(targetId) || this.nextElementSibling;
            
            // Toggle aria-expanded attribute
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
              // Toggle the dropdown visibility
            dropdownMenu.classList.toggle('show');
        });
    });
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('form.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            form.classList.add('was-validated');
            
            // Handle custom validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                // Add validation state classes
                input.addEventListener('blur', function() {
                    if (this.checkValidity()) {
                        this.classList.add('is-valid');
                        this.classList.remove('is-invalid');
                    } else {
                        this.classList.add('is-invalid');
                        this.classList.remove('is-valid');
                    }
                });
            });
        }, false);
    });
}

// Tooltips
function initTooltips() {
    document.querySelectorAll('[data-toggle="tooltip"]').forEach(tooltipEl => {
        let tooltip = null;
        let tooltipText = tooltipEl.getAttribute('title') || tooltipEl.getAttribute('data-tooltip');
        
        if (!tooltipText) return;
        
        // Store the tooltip text and remove the title to prevent default tooltip
        tooltipEl.setAttribute('data-tooltip', tooltipText);
        tooltipEl.removeAttribute('title');
        
        // Create tooltip events
        tooltipEl.addEventListener('mouseenter', function() {
            // Create tooltip element
            tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);
            
            // Position the tooltip
            const rect = tooltipEl.getBoundingClientRect();
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            
            // Show tooltip with animation
            setTimeout(() => {
                tooltip.classList.add('show');
            }, 10);
        });
        
        tooltipEl.addEventListener('mouseleave', function() {
            if (tooltip) {
                tooltip.classList.remove('show');
                setTimeout(() => {
                    if (tooltip && tooltip.parentNode) {
                        tooltip.parentNode.removeChild(tooltip);
                    }
                    tooltip = null;
                }, 300);
            }
        });
    });
}

// Interactive card animations
function initInteractiveCards() {
    const cards = document.querySelectorAll('.card.interactive');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover');
        });
    });
}

// Handle tabs
function initTabs() {
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (!target) return;
            
            // Deactivate all tabs
            const tabList = this.closest('.nav-tabs');
            tabList.querySelectorAll('.nav-link').forEach(navLink => {
                navLink.classList.remove('active');
            });
            
            // Hide all tab content
            const tabContent = document.querySelector('.tab-content');
            if (tabContent) {
                tabContent.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
            }
              // Activate current tab and show content
            this.classList.add('active');
            target.classList.add('show', 'active');
        });
    });
}
