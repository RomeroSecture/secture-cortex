import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
  Img,
  staticFile,
} from "remotion";
import { BRAND } from "../../constants/brand";

interface Scene6CTAProps {
  ctaText: string;
  ctaUrl: string;
}

export const Scene6CTA: React.FC<Scene6CTAProps> = ({ ctaText, ctaUrl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const ctaSpring = spring({ frame: frame - 12, fps, config: { damping: 10, stiffness: 200 } });
  const urlOpacity = interpolate(frame, [28, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const logoScale = spring({ frame: frame - 3, fps, config: { damping: 12, stiffness: 200 } });

  const glowPulse = 0.5 + 0.5 * Math.sin(frame * 0.12);

  const taglineOpacity = interpolate(frame, [50, 62], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const taglineY = interpolate(frame, [50, 62], [12, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const teamOpacity = interpolate(frame, [72, 85], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={{
      width: "100%",
      height: "100%",
      backgroundColor: BRAND.bgBase,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Radial glow */}
      <div style={{
        position: "absolute", inset: 0,
        background: `radial-gradient(ellipse at 50% 45%, ${BRAND.primary}25 0%, ${BRAND.bgBase} 65%)`,
        opacity: interpolate(frame, [0, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      }} />

      {/* Grid */}
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px)`,
        backgroundSize: "80px 80px",
      }} />

      <div style={{
        position: "relative", zIndex: 1,
        display: "flex", flexDirection: "column", alignItems: "center", gap: 20, padding: "0 60px",
      }}>
        {/* Real cortex-logo.png */}
        <div style={{ transform: `scale(${logoScale})`, position: "relative" }}>
          <div style={{
            position: "absolute", inset: -16, borderRadius: "50%",
            border: `2px solid rgba(46,196,162,${0.12 + glowPulse * 0.2})`,
          }} />
          <Img
            src={staticFile("cortex-logo.png")}
            style={{
              width: 110,
              height: 110,
              borderRadius: 28,
              filter: `drop-shadow(0 0 40px ${BRAND.primary}40)`,
            }}
          />
        </div>

        {/* Brand */}
        <div style={{ transform: `scale(${ctaSpring})`, textAlign: "center" }}>
          <div style={{
            fontFamily: "Inter, sans-serif", fontSize: 28, fontWeight: 400,
            color: BRAND.textPrimary, letterSpacing: 2, marginBottom: 2,
          }}>
            Secture
          </div>
          <div style={{
            fontFamily: "Inter, sans-serif", fontSize: 76, fontWeight: 700,
            color: BRAND.primary, lineHeight: 1.1,
          }}>
            {ctaText}
          </div>
        </div>

        {/* URL */}
        <div style={{
          opacity: urlOpacity,
          fontFamily: "Inter, sans-serif", fontSize: 34, fontWeight: 500,
          color: BRAND.primaryLight, letterSpacing: 2,
        }}>
          {ctaUrl}
        </div>

        {/* Tagline */}
        <div style={{
          opacity: taglineOpacity,
          transform: `translateY(${taglineY}px)`,
          fontFamily: "Inter, sans-serif", fontSize: 22, fontStyle: "italic",
          color: BRAND.textSecondary, textAlign: "center", maxWidth: 650,
        }}>
          El copiloto que escucha, cruza y responde.
        </div>

        {/* Team + hackathon */}
        <div style={{
          opacity: teamOpacity,
          display: "flex", alignItems: "center", gap: 10, marginTop: 12,
        }}>
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 16, color: BRAND.textMuted }}>
            Hackathon Secture 2026
          </span>
          <div style={{ width: 3, height: 3, borderRadius: "50%", backgroundColor: BRAND.primary }} />
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 16, color: BRAND.textMuted }}>
            Antonio & Gonzalo
          </span>
        </div>
      </div>
    </div>
  );
};
