module.exports = {
  content: ["./app/templates/**/*.html"],
  theme: {
    extend: {
      backgroundImage: {
        'custom-gradient': 'linear-gradient(to right, #4f46e5, #9333ea)',
        'custom-gradient-light': 'linear-gradient(to right, rgba(79, 70, 229, 0.15), rgba(147, 51, 234, 0.15))'
      },
      textColor: {
        'gradient': {
          'primary': '#4f46e5',
          'secondary': '#9333ea'
        }
      },
      backgroundColor: {
        'gradient': {
          'primary': '#4f46e5',
          'secondary': '#9333ea'
        }
      }
    }
  }
}
