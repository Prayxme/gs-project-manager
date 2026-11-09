/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'gemini-dark': '#131314',
        'gemini-panel': '#1E1F20',
        'gemini-blue': '#A8C7FA',
        'gemini-border': '#444746'
      }
    },
  },
  plugins: [],
}