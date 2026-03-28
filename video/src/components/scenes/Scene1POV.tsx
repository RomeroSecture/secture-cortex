import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate, Easing } from "remotion";
import { BRAND } from "../../constants/brand";

export const Scene1POV: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const shakeX = frame > 90 && frame < 115 ? Math.sin(frame * 0.8) * 2 : 0;
  const shakeY = frame > 90 && frame < 115 ? Math.cos(frame * 1.0) * 1.5 : 0;

  return (
    <div style={{
      width: "100%", height: "100%", backgroundColor: BRAND.bgBase,
      display: "flex", alignItems: "center", justifyContent: "center",
      position: "relative", overflow: "hidden",
    }}>
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)`,
        backgroundSize: "60px 60px",
      }} />

      <div style={{
        position: "relative", zIndex: 1, display: "flex", alignItems: "center", gap: 80,
        transform: `translate(${shakeX}px, ${shakeY}px)`, padding: "0 120px",
      }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 20, maxWidth: 800 }}>
          <div style={{
            opacity: interpolate(frame, [10, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: "Inter, sans-serif", fontSize: 20, fontWeight: 800,
            color: BRAND.cortexAlert, letterSpacing: 6, textTransform: "uppercase",
          }}>
            POV
          </div>

          <div style={{
            opacity: interpolate(frame, [25, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `translateY(${interpolate(frame, [25, 50], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })}px)`,
            fontFamily: "Inter, sans-serif", fontSize: 44, fontWeight: 800,
            color: BRAND.textPrimary, lineHeight: 1.2,
          }}>
            El cliente pide
          </div>

          <div style={{
            transform: `scale(${spring({ frame: frame - 55, fps, config: { damping: 12, stiffness: 150 } })})`,
            fontFamily: "Inter, sans-serif", fontSize: 80, fontWeight: 900,
            color: BRAND.cortexAlert, lineHeight: 1,
          }}>
            WhatsApp
          </div>

          <div style={{
            opacity: interpolate(frame, [80, 105], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `translateY(${interpolate(frame, [80, 105], [12, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })}px)`,
            fontFamily: "Inter, sans-serif", fontSize: 36, fontWeight: 700,
            color: BRAND.textPrimary,
          }}>
            en plena reunión
          </div>

          <div style={{
            opacity: interpolate(frame, [130, 160], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: "Inter, sans-serif", fontSize: 22, color: BRAND.textMuted, fontStyle: "italic",
          }}>
            y tú sin contexto técnico...
          </div>
        </div>

        {/* Warning icon */}
        <div style={{
          opacity: interpolate(frame, [90, 110], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          transform: `scale(${spring({ frame: frame - 95, fps, config: { damping: 15, stiffness: 120 } })})`,
          display: "flex", flexDirection: "column", alignItems: "center", gap: 16,
        }}>
          <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke={BRAND.cortexAlert} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <div style={{
            fontFamily: "Inter, sans-serif", fontSize: 16, fontWeight: 700,
            color: BRAND.cortexAlert, backgroundColor: `${BRAND.cortexAlert}0A`,
            borderRadius: 99, padding: "6px 18px", border: `1px solid ${BRAND.cortexAlert}18`,
          }}>
            tierra trágame
          </div>
        </div>
      </div>
    </div>
  );
};
