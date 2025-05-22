# PDF Chat Assistant - UI Theme Documentation

## Overview

PDF Chat Assistant uses a custom theming system with CSS variables to provide consistent styling across all pages. The application supports both dark and light themes with proper transitions and visual consistency.

## Theme Variables

The theming system is built on CSS variables defined in the `:root` selector and overridden for the light theme using the `[data-theme="light"]` attribute.

### Core Color Variables

```css
/* Dark Theme */
:root {
    --primary-color: #7E57C2;      /* Main purple */
    --primary-light: #9575CD;      /* Lighter purple */
    --primary-dark: #5E35B1;       /* Darker purple */
    --secondary-color: #B39DDB;    /* Accent purple */
    --text-light: #F3E5F5;         /* Light text for dark background */
    --dark-bg: #121118;            /* Very dark background with slight purple tint */
    --dark-bg-lighter: #1E1A2B;    /* Slightly lighter dark background */
    --card-bg: #1D1925;            /* Card background color */
    --border-color: #2B2442;       /* Border color for cards and elements */
    --success-color: #4CAF50;
    --danger-color: #FF5252;
    --gradient-start: #EC73FF;     /* Gradient start - pink */
    --gradient-middle: #FF91A9;    /* Gradient middle */
    --gradient-end: #A409FE;       /* Gradient end - purple */
}

/* Light Theme */
:root[data-theme="light"] {
    --primary-color: #9575CD;      /* Main purple (lighter) */
    --primary-light: #B39DDB;      /* Even lighter purple */
    --primary-dark: #7E57C2;       /* Darker purple */
    --secondary-color: #5E35B1;    /* Accent color */
    --text-light: #311B92;         /* Dark purple text for light background */
    --dark-bg: #FFFFFF;            /* Pure white background */
    --dark-bg-lighter: #F8F5FE;    /* Very light purple tint */
    --card-bg: #FFFFFF;            /* Card background color */
    --border-color: #E2D8F3;       /* Lighter border color with purple tint */
}
```

## Using the Theme

### HTML Structure

Set up your HTML structure to support theme toggling by adding theme-related attributes and toggling script:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- CSS files -->
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="/static/css/custom-ui.css">
    <link rel="stylesheet" href="/static/css/responsive.css">
</head>
<body class="text-light">
    <!-- Theme toggle button in the navbar -->
    <button class="btn btn-outline-light" id="toggleDarkMode">
        <i class="fas fa-moon"></i>
    </button>
    
    <!-- Scripts -->
    <script src="/static/js/theme_toggle.js"></script>
</body>
</html>
```

### Theme Toggle Script

The `theme_toggle.js` script handles theme switching:

```javascript
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
    
    function applyTheme(theme) {
        const htmlRoot = document.documentElement;
        const moonIcon = document.querySelector('#toggleDarkMode i');
        
        // Add transition class
        htmlRoot.classList.add('theme-transition');
        
        // Apply theme
        if (theme === 'light') {
            htmlRoot.setAttribute('data-theme', 'light');
            if (moonIcon) {
                moonIcon.classList.replace('fa-moon', 'fa-sun');
            }
        } else {
            htmlRoot.removeAttribute('data-theme');
            if (moonIcon) {
                moonIcon.classList.replace('fa-sun', 'fa-moon');
            }
        }
    }
});
```

## Custom UI Components

PDF Chat Assistant uses a set of custom UI components defined in `custom-ui.css` to replace Bootstrap dependencies. These include:

1. Custom layout system (container, rows, columns)
2. Custom navigation with proper mobile support
3. Custom cards with interactive options
4. Custom buttons including gradient buttons
5. Custom forms with validation
6. Custom modals
7. Utility classes for spacing, display, text, etc.

### Example: Custom Card

```html
<div class="card interactive">
    <div class="card-body">
        <h5 class="card-title">Card Title</h5>
        <p class="card-text">Card content here</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-gradient">Action</button>
    </div>
</div>
```

## Responsive Design

The application uses a responsive design system with:

1. Mobile-first approach
2. Breakpoints for different device sizes
3. Proper navbar handling on small screens
4. Responsive typography
5. Media queries for specific components

## Additional Features

1. Smooth page transitions
2. Custom tooltips
3. Interactive card animations
4. Custom form validation
5. Theme-aware components

## Best Practices

1. Always use CSS variables for colors
2. Use the utility classes for spacing and layout
3. Set proper ARIA attributes for accessibility
4. Use the interactive class for clickable cards
5. Add page transitions for smoother navigation
