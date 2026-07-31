/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        metroid: {
          dark: '#0d1117',
          stone: '#1a1f26',
          rune: '#00ffcc',
          runeHover: '#00cca3',
          accent: '#ff0055'
        }
      },
      fontFamily: {
        rune: ['"Courier New"', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
