/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#6EE7B7',
          DEFAULT: '#10B981',
          dark: '#047857',
        },
      },
    },
  },
  plugins: [],
}
