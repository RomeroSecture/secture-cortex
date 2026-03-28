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

interface Scene2LogoRevealProps {
  tagline: string;
}

export const Scene2LogoReveal: React.FC<Scene2LogoRevealProps> = ({ tagline }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoScale = spring({ frame, fps, config: { damping: 8, stiffness: 200 } });

  const glowOpacity = interpolate(frame, [0, 30], [0, 0.35], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Orbiting particles
  const particles = Array.from({ length: 24 }, (_, i) => {
    const baseAngle = (i / 24) * Math.PI * 2;
    const angle = baseAngle + frame * 0.008;
    const delay = 6 + i * 1.5;
    const dist = interpolate(frame, [delay, delay + 40], [0, 200 + (i % 5) * 50], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    });
    const opacity = interpolate(
      frame,
      [delay, delay + 8, delay + 35, delay + 50],
      [0, 0.7, 0.7, 0],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    const colors = [BRAND.primary, BRAND.cortexAlert, BRAND.cortexScope, BRAND.cortexSuggestion];
    return { angle, dist, opacity, size: 2 + (i % 4) * 1.5, color: colors[i % 4] };
  });

  // "Secture" text
  const sectureOpacity = spring({ frame: frame - 20, fps, config: { damping: 200 } });

  // "Cortex" letters
  const letters = "Cortex".split("");

  // Tagline
  const taglineOpacity = interpolate(frame, [85, 105], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const taglineY = interpolate(frame, [85, 105], [16, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Separator
  const lineWidth = interpolate(frame, [100, 125], [0, 280], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Glow ring pulse
  const ringPulse = 0.3 + 0.7 * Math.abs(Math.sin(frame * 0.04));

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: BRAND.bgBase,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Radial glow */}
      <div
        style={{
          position: "absolute",
          top: "42%",
          left: "50%",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${BRAND.primary}40 0%, transparent 65%)`,
          transform: "translate(-50%, -50%)",
          opacity: glowOpacity,
        }}
      />

      {/* Orbiting particles */}
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            top: "42%",
            left: "50%",
            width: p.size,
            height: p.size,
            borderRadius: "50%",
            backgroundColor: p.color,
            opacity: p.opacity,
            transform: `translate(${Math.cos(p.angle) * p.dist}px, ${Math.sin(p.angle) * p.dist}px)`,
            boxShadow: `0 0 ${p.size * 2}px ${p.color}80`,
          }}
        />
      ))}

      <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", alignItems: "center" }}>
        {/* Real cortex-logo.png */}
        <div style={{ transform: `scale(${logoScale})`, marginBottom: 32, position: "relative" }}>
          {/* Glow ring */}
          <div style={{
            position: "absolute",
            inset: -20,
            borderRadius: "50%",
            border: `2px solid rgba(46,196,162,${0.1 + ringPulse * 0.2})`,
            boxShadow: `0 0 30px ${BRAND.primary}20`,
          }} />
          <Img
            src={staticFile("cortex-logo.png")}
            style={{
              width: 160,
              height: 160,
              borderRadius: 40,
              filter: `drop-shadow(0 0 40px ${BRAND.primary}50)`,
            }}
          />
        </div>

        {/* "Secture" — foreground, light weight */}
        <div style={{ marginBottom: 0 }}>
          <span
            style={{
              fontFamily: "Inter, sans-serif",
              fontSize: 36,
              fontWeight: 400,
              color: BRAND.textPrimary,
              letterSpacing: 3,
              opacity: sectureOpacity,
            }}
          >
            Secture
          </span>
        </div>

        {/* "Cortex" — primary bold, letter stagger */}
        <div style={{ display: "flex", alignItems: "baseline", marginBottom: 20 }}>
          {letters.map((letter, i) => {
            const ls = spring({
              frame: frame - (24 + i * 3),
              fps,
              config: { damping: 12, stiffness: 200 },
            });
            return (
              <span
                key={i}
                style={{
                  fontFamily: "Inter, sans-serif",
                  fontSize: 100,
                  fontWeight: 700,
                  color: BRAND.primary,
                  opacity: ls,
                  transform: `translateY(${interpolate(ls, [0, 1], [12, 0])}px)`,
                  display: "inline-block",
                }}
              >
                {letter}
              </span>
            );
          })}
        </div>

        {/* Gradient separator */}
        <div
          style={{
            width: lineWidth,
            height: 2,
            background: `linear-gradient(90deg, transparent, ${BRAND.primary}80, transparent)`,
            marginBottom: 20,
          }}
        />

        {/* Tagline */}
        <div
          style={{
            opacity: taglineOpacity,
            transform: `translateY(${taglineY}px)`,
            fontFamily: "Inter, sans-serif",
            fontSize: 28,
            color: BRAND.textMuted,
            textAlign: "center",
            maxWidth: 700,
          }}
        >
          {tagline}
        </div>

        {/* Secondary */}
        <div
          style={{
            opacity: interpolate(frame, [118, 138], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            fontFamily: "Inter, sans-serif",
            fontSize: 20,
            fontStyle: "italic",
            color: BRAND.primaryLight,
            marginTop: 16,
            textAlign: "center",
          }}
        >
          Porque &lsquo;déjame mirarlo&rsquo; ya no es opción.
        </div>
      </div>
    </div>
  );
};
