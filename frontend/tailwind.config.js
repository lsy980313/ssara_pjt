/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'apple-gray': '#f5f5f7',
        'apple-text': '#1d1d1f',
        'apple-link': '#0066cc',
      },
      fontFamily: {
        'sf': ['-apple-system', 'BlinkMacSystemFont', 'Pretendard', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
