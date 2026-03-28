import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate, Easing, Img, staticFile } from "remotion";
import { BRAND } from "../../constants/brand";

export const Scene3Enter: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const plotTwistOpacity = interpolate(frame, [40, 55], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const logoScale = spring({ frame: frame - 55, fps, config: { damping: 14, stiffness: 120 } });
  const nameOpacity = interpolate(frame, [75, 100], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{
      width: "100%", height: "100%", backgroundColor: BRAND.bgBase,
      display: "flex", alignItems: "center", justifyContent: "center",
      position: "relative", overflow: "hidden",
    }}>
      {/* Subtle glow */}
      <div style={{
        position: "absolute", top: "50%", left: "50%",
        width: 800, height: 800, borderRadius: "50%",
        background: `radial-gradient(circle, ${BRAND.primary}10 0%, transparent 60%)`,
        transform: "translate(-50%, -50%)",
        opacity: interpolate(frame, [50, 75], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      }} />

      <div style={{
        position: "relative", zIndex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 60,
      }}>
        {/* "Pero espera..." */}
        <div style={{
          position: "absolute", top: -100,
          opacity: interpolate(frame, [5, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          transform: `scale(${spring({ frame: frame - 8, fps, config: { damping: 15, stiffness: 120 } })})`,
          display: "flex", alignItems: "center", gap: 12,
          fontFamily: "Inter, sans-serif", fontSize: 44, fontWeight: 900, color: BRAND.primary,
        }}>
          <span style={{ opacity: plotTwistOpacity }}>
            Pero espera...
          </span>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: plotTwistOpacity }}>
            <polyline points="23 4 23 10 17 10" /><polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
        </div>

        {/* Logo */}
        {frame > 50 && (
          <div style={{ transform: `scale(${logoScale})` }}>
            <Img src={staticFile("cortex-logo.png")} style={{
              width: 170, height: 170, borderRadius: 42,
            }} />
          </div>
        )}

        {/* Name + tagline */}
        {frame > 70 && (
          <div style={{
            opacity: nameOpacity,
            transform: `translateX(${interpolate(frame, [75, 100], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })}px)`,
            display: "flex", flexDirection: "column", gap: 8,
          }}>
            <div style={{ fontFamily: "Inter, sans-serif", fontSize: 30, fontWeight: 400, color: BRAND.textPrimary, letterSpacing: 3 }}>
              Secture
            </div>
            <div style={{
              fontFamily: "Inter, sans-serif", fontSize: 86, fontWeight: 800,
              color: BRAND.primary, lineHeight: 1,
            }}>
              Cortex
            </div>
            <div style={{
              opacity: interpolate(frame, [120, 148], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              fontFamily: "Inter, sans-serif", fontSize: 22, color: BRAND.textSecondary, marginTop: 10,
            }}>
              El copiloto que escucha, cruza y responde
            </div>

            <div style={{
              opacity: interpolate(frame, [170, 200], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              display: "flex", alignItems: "center", gap: 8,
              fontFamily: "Inter, sans-serif", fontSize: 15, fontWeight: 700,
              color: BRAND.primary, backgroundColor: `${BRAND.primary}08`,
              borderRadius: 99, padding: "6px 16px", border: `1px solid ${BRAND.primary}15`,
              width: "fit-content", marginTop: 6,
            }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
              </svg>
              esto es otro nivel
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
