import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate, Easing } from "remotion";
import { BRAND } from "../../constants/brand";

export const Scene2Pain: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{
      width: "100%", height: "100%", backgroundColor: "#0d0e18",
      display: "flex", alignItems: "center", justifyContent: "center",
      position: "relative", overflow: "hidden",
    }}>
      {/* Subtle vignette */}
      <div style={{
        position: "absolute", inset: 0,
        background: `radial-gradient(ellipse at center, transparent 50%, ${BRAND.destructive}08 100%)`,
      }} />

      <div style={{
        position: "relative", zIndex: 1,
        display: "flex", alignItems: "center", gap: 100, padding: "0 120px",
      }}>
        {/* Left: quote */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
          <div style={{
            opacity: interpolate(frame, [10, 35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `scale(${spring({ frame: frame - 12, fps, config: { damping: 15, stiffness: 120 } })})`,
            fontFamily: "Inter, sans-serif", fontSize: 52, fontWeight: 900,
            color: BRAND.textPrimary, textAlign: "center", lineHeight: 1.2,
          }}>
            «Déjame mirarlo
            <br />y te digo»
          </div>

          <div style={{
            opacity: interpolate(frame, [45, 65], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke={BRAND.textMuted} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="9" cy="12" r="1" /><circle cx="15" cy="12" r="1" />
              <path d="M8 20h8M12 20v-4" />
              <path d="M4 10a8 8 0 1 1 16 0c0 4-2 6-2 10H6c0-4-2-6-2-10z" />
            </svg>
          </div>
        </div>

        {/* Right: stat */}
        <div style={{
          opacity: interpolate(frame, [70, 95], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          transform: `translateY(${interpolate(frame, [70, 95], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })}px)`,
          display: "flex", flexDirection: "column", gap: 16, alignItems: "center",
        }}>
          <div style={{
            fontFamily: "JetBrains Mono, monospace", fontSize: 72, fontWeight: 800,
            color: BRAND.destructive,
          }}>
            1–2 días
          </div>
          <div style={{
            fontFamily: "Inter, sans-serif", fontSize: 22, color: BRAND.textMuted,
            textAlign: "center", maxWidth: 400,
          }}>
            perdidos post-reunión evaluando impacto técnico
          </div>

          <div style={{
            opacity: interpolate(frame, [130, 155], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `scale(${spring({ frame: frame - 135, fps, config: { damping: 15, stiffness: 120 } })})`,
            display: "flex", alignItems: "center", gap: 8,
            fontFamily: "Inter, sans-serif", fontSize: 18, fontWeight: 700,
            color: BRAND.destructive, backgroundColor: `${BRAND.destructive}08`,
            borderRadius: 99, padding: "8px 22px", border: `1px solid ${BRAND.destructive}15`,
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={BRAND.destructive} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="1 4 1 10 7 10" /><polyline points="23 20 23 14 17 14" />
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" />
            </svg>
            cada. reunión.
          </div>
        </div>
      </div>
    </div>
  );
};
