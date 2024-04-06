/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js}", "./node_modules/tw-elements/js/**/*.js"],
  theme: {
    extend: {
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateY(-50%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      animation: {
        slideIn: 'slideIn 0.3s ease-out',
      },
      colors: {
        "main-bg": "#1E1C1C",
        "button-bg": "rgba(239, 241, 246, 0.75)",
        "button-text": "rgba(255, 255, 255, 0.1)",
        "text-color": "#ffffff",
        "primary-green": "#00b8a3",
        "primary-red": "#ef4743",
        "primary-purple": "#5b40ec",
        orange: {
          800: "#ffa116",
          500: "#ffc01e",
          300: "#ffc926",
          200: "#ffd699",
        },
        lc: {
          900: "#262626",
          800: "#323232",
          700: "#2a2a2a",
          500: "#252525",
          300: "#595959",
          200: "#5c5c5c",
        },
      },
    },
  },
  darkMode: "class",
  plugins: [require("tw-elements/plugin.cjs")],
};
