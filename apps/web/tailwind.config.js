/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        nova: {
          950: '#07090e',
          900: '#0c1017',
          850: '#111722',
          800: '#171f2e',
          700: '#232f46',
          600: '#344565',
          accent: '#3b82f6',
          accentHover: '#2563eb',
          glow: '#60a5fa',
          cyan: '#06b6d4',
          emerald: '#10b981',
          rose: '#f43f5e',
          amber: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['Fira Code', 'JetBrains Mono', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'glow-sm': '0 0 15px -3px rgba(59, 130, 246, 0.25)',
        'glow-md': '0 0 25px -5px rgba(59, 130, 246, 0.35)',
        'glow-cyan': '0 0 25px -5px rgba(6, 182, 212, 0.35)',
      }
    },
  },
  plugins: [],
}
