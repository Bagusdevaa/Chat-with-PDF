// Dark/light mode toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const toggleDarkMode = document.getElementById('toggleDarkMode');
    
    if (toggleDarkMode) {
        // Check stored preference or default to dark
        let currentTheme = localStorage.getItem('theme') || 'dark';
        
        // Initial setup
        applyTheme(currentTheme);
        
        toggleDarkMode.addEventListener('click', function() {
            // Toggle theme
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Save preference
            localStorage.setItem('theme', currentTheme);
            
            // Apply theme
            applyTheme(currentTheme);
        });
    }
  // Function to apply theme
    function applyTheme(theme) {
        const htmlRoot = document.documentElement;
        const moonIcon = document.querySelector('#toggleDarkMode i');
        const navbar = document.querySelector('.navbar');
        const footer = document.querySelector('.footer');
        const cards = document.querySelectorAll('.card');
        const textMuted = document.querySelectorAll('.text-muted');
        const contactLinks = document.querySelectorAll('.contact-link');
        const featureCards = document.querySelectorAll('.feature-card');
        const stepCards = document.querySelectorAll('.step-card');
        
        // Add transition class
        htmlRoot.classList.add('theme-transition');
        document.body.classList.add('theme-transition');
        
        // Force a repaint before changing the theme
        const repaint = htmlRoot.offsetHeight;
        
        if (theme === 'light') {
            // Set light theme attribute
            htmlRoot.setAttribute('data-theme', 'light');
            
            // Update icon
            if (moonIcon) {
                moonIcon.classList.remove('fa-moon');
                moonIcon.classList.add('fa-sun');
            }
            
            // Apply styling to main elements
            if (navbar) {
                navbar.style.backgroundColor = 'var(--dark-bg-lighter)';
            }
            
            if (footer) {
                footer.style.backgroundColor = 'var(--dark-bg-lighter)';
            }
            
            // Cards
            cards.forEach(card => {
                card.style.backgroundColor = 'var(--card-bg)';
                card.style.borderColor = 'var(--border-color)';
                card.style.color = 'var(--text-light)';
            });
            
            // Fix text colors
            textMuted.forEach(el => {
                el.style.color = 'var(--hero-subtitle-color)';
            });
            
            // Apply to feature cards
            featureCards.forEach(card => {
                card.style.backgroundColor = 'var(--feature-card-bg)';
                card.style.borderColor = 'var(--feature-card-border)';
            });
            
            // Apply to step cards
            stepCards.forEach(card => {
                card.style.backgroundColor = 'var(--step-card-bg)';
                card.style.borderColor = 'var(--step-card-border)';
            });
            
        } else {
            // Remove light theme attribute to switch back to dark
            htmlRoot.removeAttribute('data-theme');
            
            // Update icon
            if (moonIcon) {
                moonIcon.classList.remove('fa-sun');
                moonIcon.classList.add('fa-moon');
            }
            
            // Reset styles
            if (navbar) {
                navbar.style.backgroundColor = '';
            }
            
            if (footer) {
                footer.style.backgroundColor = '';
            }
            
            // Cards
            cards.forEach(card => {
                card.style.backgroundColor = 'var(--card-bg)';
                card.style.borderColor = 'var(--border-color)';
                card.style.color = '';
            });
            
            // Reset text colors
            textMuted.forEach(el => {
                el.style.color = '';
            });
            
            // Apply dark theme to feature cards
            featureCards.forEach(card => {
                card.style.backgroundColor = 'var(--feature-card-bg)';
                card.style.borderColor = 'var(--feature-card-border)';
            });
            
            // Apply dark theme to step cards
            stepCards.forEach(card => {
                card.style.backgroundColor = 'var(--step-card-bg)';
                card.style.borderColor = 'var(--step-card-border)';
            });
        }
        
        // Remove the transition class after a delay
        setTimeout(() => {
            htmlRoot.classList.remove('theme-transition');
        }, 50);
    }
});
