/**
 * Footer JavaScript functionality
 * Handles animations and subscription form
 */
document.addEventListener('DOMContentLoaded', function() {
    // Animate footer sections on scroll
    const footerSections = document.querySelectorAll('.footer .row > div');
    
    // Function to check if element is in viewport
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.bottom >= 0
        );
    }
    
    // Function to handle animation on scroll
    function handleScrollAnimations() {
        footerSections.forEach((section, index) => {
            if (isElementInViewport(section)) {
                // Use custom property for staggered animation
                section.style.setProperty('--animation-order', index);
                section.classList.add('animate-in');
            }
        });
    }
    
    // Initial check on page load
    handleScrollAnimations();
    
    // Check on scroll
    window.addEventListener('scroll', handleScrollAnimations);
    
    // Handle newsletter form submission
    const newsletterForm = document.querySelector('.footer form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            
            if (emailInput && emailInput.value) {
                // Show success message
                const successMessage = document.createElement('div');
                successMessage.className = 'alert-success p-2 mt-2 rounded';
                successMessage.textContent = 'Thank you for subscribing!';
                
                // Replace the form with the success message
                this.style.opacity = '0';
                setTimeout(() => {
                    this.parentNode.replaceChild(successMessage, this);
                    successMessage.style.opacity = '0';
                    setTimeout(() => {
                        successMessage.style.opacity = '1';
                    }, 10);
                }, 300);
                
                // You would normally send the data to the server here
                console.log('Subscription email:', emailInput.value);
            }
        });
    }
    
    // Add smooth scroll for footer links
    const footerLinks = document.querySelectorAll('.footer a[href^="#"]');
    footerLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const href = this.getAttribute('href');
            
            if (href !== '#' && document.querySelector(href)) {
                event.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
