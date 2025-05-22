/**
 * Navbar JavaScript functionality
 * Handles mobile menu toggle and user dropdown menu
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get navbar elements
    const navbarToggler = document.getElementById('navbarToggler');
    const navbarNav = document.getElementById('navbarNav');
    const userDropdownBtn = document.getElementById('userDropdownBtn');
    const userDropdownMenu = document.getElementById('userDropdownMenu');
    
    // Mobile menu toggle
    if (navbarToggler && navbarNav) {
        navbarToggler.addEventListener('click', function() {
            navbarNav.classList.toggle('show');
            
            // Accessibility
            const expanded = navbarNav.classList.contains('show');
            navbarToggler.setAttribute('aria-expanded', expanded);
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarNav.contains(event.target) && 
                !navbarToggler.contains(event.target) && 
                navbarNav.classList.contains('show')) {
                navbarNav.classList.remove('show');
                navbarToggler.setAttribute('aria-expanded', 'false');
            }
        });
    }
    
    // User dropdown menu toggle
    if (userDropdownBtn && userDropdownMenu) {
        userDropdownBtn.addEventListener('click', function(event) {
            event.stopPropagation();
            userDropdownMenu.classList.toggle('show');
            
            // Accessibility
            const expanded = userDropdownMenu.classList.contains('show');
            userDropdownBtn.setAttribute('aria-expanded', expanded);
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!userDropdownMenu.contains(event.target) && 
                !userDropdownBtn.contains(event.target) && 
                userDropdownMenu.classList.contains('show')) {
                userDropdownMenu.classList.remove('show');
                userDropdownBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }
    
    // Add animation classes for smooth transitions
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.classList.add('nav-link-hover');
        });
        
        link.addEventListener('mouseleave', function() {
            this.classList.remove('nav-link-hover');
        });
    });
    
    // Handle active link highlighting
    function setActiveNavItem() {
        const currentPath = window.location.pathname;
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            } else {
                // Don't remove active class if it was set by the server
                if (!link.classList.contains('active')) {
                    link.classList.remove('active');
                }
            }
        });
    }
    
    // Only run if we're not using server-side active class
    if (!document.querySelector('.nav-link.active')) {
        setActiveNavItem();
    }
    
    // Handle dropdown position based on available space
    function positionDropdown() {
        if (userDropdownMenu) {
            const viewportWidth = window.innerWidth;
            const dropdownRect = userDropdownMenu.getBoundingClientRect();
            const rightEdge = dropdownRect.right;
            
            if (rightEdge > viewportWidth) {
                userDropdownMenu.style.right = '0';
            } else {
                userDropdownMenu.style.right = 'auto';
            }
        }
    }
    
    // Update dropdown position on window resize
    window.addEventListener('resize', positionDropdown);
    
    // Initial positioning
    positionDropdown();
});
