import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: "#17191c",
        canvas: "#ffffff",
        fog: "#f7f7f8",
        ash: "#4c4c4c",
        graphite: "#777b86",
        dove: "#a3a6af",
        rust: "#c0461e",
        "rust-dim": "#fbe1d1",
        sky: "#d3e3fc",
        "sky-deep": "#4a7fc1",
        success: "#1a7f4b",
        warning: "#b45309",
        "status-bg-success": "#f0fdf4",
        "status-bg-warn": "#fff7ed",
        
        dark: {
          bg: "#0A0A0B",
          "bg-elevated": "#111114",
          "bg-subtle": "#18181B",
          border: "#27272A",
          "border-subtle": "#1F1F23",
        },
        
        accent: {
          DEFAULT: "#DC2626",
          dim: "#FECACA",
          glow: "rgba(220, 38, 38, 0.12)",
          "glow-strong": "rgba(220, 38, 38, 0.25)",
        },
        
        fg: {
          DEFAULT: "#FAFAFA",
          muted: "#A1A1AA",
          subtle: "#71717A",
        },
      },
      fontFamily: {
        display: ["Geist", "Inter", "system-ui", "sans-serif"],
        serif: ["Fraunces", "Lora", "Georgia", "serif"],
        ui: ["Inter", "system-ui", "sans-serif"],
        mono: ["Geist Mono", "JetBrains Mono", "monospace"],
      },
      fontWeight: {
        '450': '450',
        '550': '550',
      },
      fontSize: {
        display: ["48px", { lineHeight: "1.1", letterSpacing: "-0.02em" }],
        heading: ["24px", { lineHeight: "1.2", letterSpacing: "-0.02em" }],
        subheading: ["18px", { lineHeight: "1.3", letterSpacing: "-0.01em" }],
        body: ["15px", { lineHeight: "1.5", letterSpacing: "0" }],
        label: ["13px", { lineHeight: "1.4", letterSpacing: "0.01em" }],
        caption: ["12px", { lineHeight: "1.5", letterSpacing: "0.02em" }],
        mono: ["13px", { lineHeight: "1.6", letterSpacing: "0" }],
      },
      spacing: {
        "1": "4px",
        "2": "8px",
        "3": "12px",
        "4": "16px",
        "5": "20px",
        "6": "24px",
        "8": "32px",
        "12": "48px",
        "16": "64px",
      },
      borderRadius: {
        card: "16px",
        button: "9999px",
        input: "10px",
        chip: "9999px",
        avatar: "9999px",
        item: "8px",
      },
      boxShadow: {
        card: "0px 0px 0px 1px rgba(255, 255, 255, 0.06), 0px 4px 12px -2px rgba(0, 0, 0, 0.3)",
        "card-hover": "0px 0px 0px 1px rgba(255, 255, 255, 0.08), 0px 8px 24px -4px rgba(0, 0, 0, 0.4)",
        panel: "0px 0px 0px 1px rgba(255, 255, 255, 0.08), 0px 16px 32px -8px rgba(0, 0, 0, 0.5)",
        glow: "0px 0px 40px -10px rgba(220, 38, 38, 0.3)",
        "glow-strong": "0px 0px 60px -12px rgba(220, 38, 38, 0.5)",
      },
      animation: {
        "fade-in": "fadeIn 400ms var(--ease-out) forwards",
        "slide-up": "slideUp 500ms var(--ease-out) forwards",
        "slide-in-right": "slideInRight 200ms var(--ease-out) forwards",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "stagger-in": "staggerIn 500ms var(--ease-out) forwards",
        "spin": "spin 1s linear infinite",
      },
      keyframes: {
        fadeIn: {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(24px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        slideInRight: {
          from: { opacity: "0", transform: "translateX(16px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0px 0px 20px rgba(220, 38, 38, 0.2)" },
          "50%": { boxShadow: "0px 0px 40px rgba(220, 38, 38, 0.4)" },
        },
        staggerIn: {
          from: { opacity: "0", transform: "translateY(20px) scale(0.98)" },
          to: { opacity: "1", transform: "translateY(0) scale(1)" },
        },
        spin: {
          from: { transform: "rotate(0deg)" },
          to: { transform: "rotate(360deg)" },
        },
      },
      transitionTimingFunction: {
        "out-expo": "cubic-bezier(0.16, 1, 0.3, 1)",
        "in-out-expo": "cubic-bezier(0.87, 0, 0.13, 1)",
      },
    },
  },
  plugins: [],
}

export default config
