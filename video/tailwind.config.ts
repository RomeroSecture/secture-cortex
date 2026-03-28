import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cortex: {
          DEFAULT: "#0EA5E9",
          dark: "#0284C7",
          light: "#38BDF8",
        },
        accent: {
          amber: "#F59E0B",
          emerald: "#10B981",
          rose: "#F43F5E",
          violet: "#8B5CF6",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
