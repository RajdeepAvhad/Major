/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'green': 'var(--green)',
        'green-dark': 'var(--green-dark)',
        'green-glow': 'var(--green-glow)',
      },
    },
  },
  plugins: [],
}
