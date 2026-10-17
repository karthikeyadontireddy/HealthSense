export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      boxShadow: {
        soft: '0 20px 45px -20px rgba(15, 23, 42, 0.25)',
      },
      colors: {
        brand: {
          50: '#eefaf7',
          100: '#d8f4eb',
          500: '#13a57d',
          600: '#0e8b68',
          700: '#0d7159',
        },
      },
    },
  },
  plugins: [],
}
