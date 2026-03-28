import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate, Easing } from "remotion";
import { BRAND } from "../../constants/brand";

interface Scene1HookProps {
  text: string;
}

export const Scene1Hook: React.FC<Scene1HookProps> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const words = text.split(" ");
  const highlight = new Set(["'déjame", "mirarlo"]);

  const bgScale = interpolate(frame, [0, 120], [1.15, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const vignetteOpacity = interpolate(frame, [0, 40], [0.2, 0.5], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

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
      {/* Radial glow — teal primary */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at 50% 40%, ${BRAND.primary}10 0%, transparent 60%)`,
          transform: `scale(${bgScale})`,
        }}
      />

      {/* Vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at center, transparent 30%, ${BRAND.bgBase} 100%)`,
          opacity: vignetteOpacity,
        }}
      />

      {/* Grid pattern */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
          opacity: interpolate(frame, [0, 30], [0, 0.5], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
          padding: "0 70px",
        }}
      >
        {/* Badge pill */}
        <div
          style={{
            opacity: interpolate(frame, [5, 18], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            transform: `translateY(${interpolate(frame, [5, 18], [24, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            })}px)`,
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "8px 20px",
            borderRadius: 999,
            backgroundColor: "rgba(255,255,255,0.06)",
            border: `1px solid ${BRAND.borderDefault}`,
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a7 7 0 0 1 7 7c0 3-1.5 5.5-4 7.5V20H9v-3.5C6.5 14.5 5 12 5 9a7 7 0 0 1 7-7z" />
          </svg>
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 18, color: BRAND.textSecondary }}>
            Copiloto IA para reuniones
          </span>
        </div>

        {/* Main heading — word by word */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            gap: "8px 12px",
            maxWidth: 900,
          }}
        >
          {words.map((word, i) => {
            const delay = 15 + i * 6;
            const s = spring({ frame: frame - delay, fps, config: { damping: 200, stiffness: 300 } });
            const y = interpolate(s, [0, 1], [24, 0]);
            const isHighlight = highlight.has(word);

            return (
              <span
                key={i}
                style={{
                  fontFamily: "Inter, sans-serif",
                  fontSize: 72,
                  fontWeight: 700,
                  lineHeight: 1.15,
                  color: isHighlight ? BRAND.primary : BRAND.textPrimary,
                  opacity: s,
                  transform: `translateY(${y}px)`,
                  display: "inline-block",
                }}
              >
                {word}
              </span>
            );
          })}
        </div>

        {/* Subtitle */}
        <div
          style={{
            opacity: interpolate(frame, [70, 88], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            transform: `translateY(${interpolate(frame, [70, 88], [24, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            })}px)`,
            fontFamily: "Inter, sans-serif",
            fontSize: 26,
            color: BRAND.textMuted,
            textAlign: "center",
            maxWidth: 700,
          }}
        >
          Tu equipo técnico merece responder con datos, no con promesas
        </div>
      </div>

      {/* Scroll chevron */}
      {frame > 90 && (
        <div
          style={{
            position: "absolute",
            bottom: 80,
            left: "50%",
            transform: `translateX(-50%) translateY(${Math.sin(frame * 0.08) * 8}px)`,
            opacity: interpolate(frame, [90, 105], [0, 0.4], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={BRAND.textFaint} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      )}
    </div>
  );
};
