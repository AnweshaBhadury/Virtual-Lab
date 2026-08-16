/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 50px rgba(34, 211, 238, .12)",
      },
    },
  },
  plugins: [],
};