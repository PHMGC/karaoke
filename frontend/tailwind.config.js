module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'], // Tailwind 3.x
  darkMode: 'media', // Altere para 'media' ou remova completamente
  theme: {
    extend: {
      fontFamily: {
        jetbrains: ['JetBrains Mono', 'monospace'], // Adicionando JetBrains Mono como fonte
      },      
    },
  },
  plugins: [],
};



