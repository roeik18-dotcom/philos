/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: '#F9F7F2',
        foreground: '#4A4238',
        card: {
          DEFAULT: '#FFFFFF',
          foreground: '#4A4238',
        },
        popover: {
          DEFAULT: '#FFFFFF',
          foreground: '#4A4238',
        },
        primary: {
          DEFAULT: '#4A4238',
          foreground: '#F9F7F2',
        },
        secondary: {
          DEFAULT: '#E6E2DD',
          foreground: '#4A4238',
        },
        muted: {
          DEFAULT: '#EFEBE6',
          foreground: '#8C867D',
        },
        accent: {
          DEFAULT: '#E6E2DD',
          foreground: '#4A4238',
        },
        destructive: {
          DEFAULT: '#D4A5A5',
          foreground: '#F9F7F2',
        },
        border: '#E6E2DD',
        input: '#E6E2DD',
        ring: '#A7C4BC',
        chart: {
          1: '#A7C4BC',
          2: '#D4A5A5',
          3: '#A0C1D1',
          4: '#E6CBA5',
          5: '#9E9E9E',
        },
        category: {
          body: {
            bg: '#E8F0ED',
            text: '#2C4A40',
            accent: '#A7C4BC',
          },
          emotion: {
            bg: '#F7EBEB',
            text: '#5A3A3A',
            accent: '#D4A5A5',
          },
          mind: {
            bg: '#EBF4F8',
            text: '#2A4550',
            accent: '#A0C1D1',
          },
        },
      },
      borderRadius: {
        lg: '1.5rem',
        md: '1rem',
        sm: '0.75rem',
      },
      fontFamily: {
        rubik: ['Rubik', 'sans-serif'],
        heebo: ['Heebo', 'sans-serif'],
      },
      animation: {
        'breathe': 'pulse 4s ease-in-out infinite',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
