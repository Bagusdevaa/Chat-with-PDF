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
        
        if (theme === 'light') {
            htmlRoot.setAttribute('data-theme', 'light');
            if (moonIcon) {
                moonIcon.classList.remove('fa-moon');
                moonIcon.classList.add('fa-sun');
            }
        } else {
            htmlRoot.removeAttribute('data-theme');
            if (moonIcon) {
                moonIcon.classList.remove('fa-sun');
                moonIcon.classList.add('fa-moon');
            }
        }
    }
});
