// Page transition animations
document.addEventListener('DOMContentLoaded', function() {
    // Apply fade-in animation to the main content
    const pageContainer = document.querySelector('.page-transition');
    
    if (pageContainer) {
        // Set initial state (hidden)
        pageContainer.style.opacity = '0';
        pageContainer.style.transform = 'translateY(10px)';
        
        // Start the animation after a small delay
        setTimeout(() => {
            pageContainer.classList.add('page-visible');
        }, 50);
    }
    
    // Handle internal navigation links - add smooth transitions
    document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not([data-no-transition])').forEach(link => {
        // Only handle internal links
        if (link.hostname === window.location.hostname) {
            
            link.addEventListener('click', function(e) {
                // Don't handle if modifier keys are pressed
                if (e.ctrlKey || e.metaKey || e.shiftKey) {
                    return;
                }
                
                const currentHref = this.getAttribute('href');
                
                // Don't animate if it's the same page
                if (currentHref === window.location.pathname) {
                    return;
                }
                
                e.preventDefault();
                const targetHref = this.href;
                  // Fade out
                pageContainer.classList.remove('page-visible');
                
                // Navigate after transition effect
                setTimeout(() => {
                    window.location.href = targetHref;
                }, 300);
            });
        }
    });
    
    // Add smooth scrolling to in-page links
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add exit animation when user navigates back/forward
    window.addEventListener('beforeunload', function() {
        if (pageContainer) {
            pageContainer.classList.remove('page-visible');
        }
    });
});
