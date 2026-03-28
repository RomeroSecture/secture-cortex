import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate, Easing, Img, staticFile } from "remotion";
import { BRAND } from "../../constants/brand";

interface Scene6CTAProps { ctaText: string; ctaUrl: string; }

export const Scene6CTA: React.FC<Scene6CTAProps> = ({ ctaText, ctaUrl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{
      width: "100%", height: "100%", backgroundColor: BRAND.bgBase,
      display: "flex", alignItems: "center", justifyContent: "center",
      position: "relative", overflow: "hidden",
    }}>
      {/* Subtle glow */}
      <div style={{
        position: "absolute", inset: 0,
        background: `radial-gradient(ellipse at 50% 50%, ${BRAND.primary}0A 0%, ${BRAND.bgBase} 65%)`,
        opacity: interpolate(frame, [0, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      }} />

      <div style={{
        position: "relative", zIndex: 1, display: "flex", alignItems: "center", gap: 60,
      }}>
        {/* Logo */}
        <div style={{
          opacity: interpolate(frame, [5, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          transform: `scale(${interpolate(frame, [8, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })})`,
        }}>
          <Img src={staticFile("cortex-logo.png")} style={{ width: 160, height: 160, borderRadius: 40 }} />
        </div>

        {/* Text */}
        <div style={{
          opacity: interpolate(frame, [20, 45], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          transform: `translateX(${interpolate(frame, [20, 45], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })}px)`,
          display: "flex", flexDirection: "column", gap: 8,
        }}>
          <div style={{ fontFamily: "Inter, sans-serif", fontSize: 28, fontWeight: 400, color: BRAND.textPrimary, letterSpacing: 2 }}>
            Secture
          </div>
          <div style={{ fontFamily: "Inter, sans-serif", fontSize: 80, fontWeight: 800, color: BRAND.primary, lineHeight: 1 }}>
            {ctaText}
          </div>

          <div style={{
            opacity: interpolate(frame, [55, 80], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: "Inter, sans-serif", fontSize: 28, fontWeight: 500, color: BRAND.primaryLight, letterSpacing: 1, marginTop: 6,
          }}>
            {ctaUrl}
          </div>

          <div style={{
            opacity: interpolate(frame, [90, 115], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: "Inter, sans-serif", fontSize: 18, fontStyle: "italic", color: BRAND.textSecondary, marginTop: 10,
          }}>
            Porque «déjame mirarlo» ya no es opción.
          </div>

          <div style={{
            opacity: interpolate(frame, [125, 150], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            display: "flex", alignItems: "center", gap: 10, marginTop: 14,
          }}>
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 15, color: BRAND.textMuted }}>Hackathon Secture 2026</span>
            <div style={{ width: 3, height: 3, borderRadius: "50%", backgroundColor: BRAND.primary }} />
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 15, color: BRAND.textMuted }}>Antonio & Gonzalo</span>
          </div>

          <div style={{
            opacity: interpolate(frame, [160, 190], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            display: "flex", alignItems: "center", gap: 8, marginTop: 8, width: "fit-content",
            fontFamily: "Inter, sans-serif", fontSize: 15, fontWeight: 700,
            color: BRAND.cortexAlert, backgroundColor: `${BRAND.cortexAlert}08`,
            borderRadius: 99, padding: "6px 16px", border: `1px solid ${BRAND.cortexAlert}15`,
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={BRAND.cortexAlert} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="8" r="7" /><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" />
            </svg>
            nos vemos en la final
          </div>
        </div>
      </div>
    </div>
  );
};
