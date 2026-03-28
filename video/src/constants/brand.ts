// Secture Cortex — "Quiet Intelligence" warm dark theme
// Hex approximations of the real app's OKLCH color system

export const BRAND = {
  // Backgrounds (warm dark blue-gray, not cold black)
  bgBase: "#1c1d2e",
  bgSurface: "#26273a",
  bgSurfaceHover: "#2e2f42",
  bgCard: "#26273a",
  bgNav: "#1c1d2e",

  // Text
  textPrimary: "#edece8",
  textSecondary: "#a3a4ae",
  textMuted: "#808490",
  textFaint: "#5a5d6a",

  // Borders (subtle translucent white)
  borderSubtle: "rgba(255,255,255,0.06)",
  borderDefault: "rgba(255,255,255,0.10)",

  // Brand — Teal primary (oklch 0.72 0.12 165)
  primary: "#2ec4a2",
  primaryDark: "#219e82",
  primaryLight: "#45d4b4",

  // Cortex semantic insight colors (the REAL ones)
  cortexAlert: "#d9a840",       // golden yellow (oklch 0.78 0.15 55)
  cortexScope: "#a07ed6",       // purple/violet (oklch 0.70 0.12 290)
  cortexSuggestion: "#3ab897",  // teal-green (oklch 0.72 0.11 155)

  // Status
  destructive: "#e8654c",
  success: "#34d399",        // emerald-400

  // Speaker colors (exact Tailwind values used in real app)
  speakerSlate: "#94a3b8",   // slate-400
  speakerEmerald: "#34d399", // emerald-400
  speakerAmber: "#fbbf24",   // amber-400
  speakerViolet: "#a78bfa",  // violet-400
  speakerRose: "#fb7185",    // rose-400

  // Utility
  blue400: "#60a5fa",
} as const;

export const SPEAKER_COLORS = [
  BRAND.speakerSlate,
  BRAND.speakerEmerald,
  BRAND.speakerAmber,
  BRAND.speakerViolet,
  BRAND.speakerRose,
] as const;

export const INSIGHT_TYPES = {
  alert: { color: BRAND.cortexAlert, label: "ALERTA" },
  scope: { color: BRAND.cortexScope, label: "SCOPE" },
  suggestion: { color: BRAND.cortexSuggestion, label: "SUGERENCIA" },
} as const;
