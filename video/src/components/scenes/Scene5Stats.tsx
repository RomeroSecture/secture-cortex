import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { BRAND } from "../../constants/brand";
import { AnimatedCounter } from "../shared/AnimatedCounter";

interface Scene5StatsProps {
  latency: string;
  insightTime: string;
  accuracy: string;
}

export const Scene5Stats: React.FC<Scene5StatsProps> = ({
  latency,
  insightTime,
  accuracy,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const badgeScale = spring({ frame: frame - 90, fps, config: { damping: 8, stiffness: 180 } });

  const lineHeight1 = interpolate(frame, [30, 50], [0, 50], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const lineHeight2 = interpolate(frame, [55, 75], [0, 50], {
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
        gap: 16,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div style={{
        position: "absolute",
        top: "50%", left: "50%",
        width: 800, height: 800, borderRadius: "50%",
        background: `radial-gradient(circle, ${BRAND.primary}12 0%, transparent 70%)`,
        transform: "translate(-50%, -50%)",
      }} />

      {/* Stat 1 — Latency */}
      <AnimatedCounter
        value={latency}
        label="Audio → Transcripción"
        accent={BRAND.primary}
        delay={8}
      />

      <div style={{
        width: 2, height: lineHeight1, borderRadius: 1,
        background: `linear-gradient(to bottom, ${BRAND.primary}40, ${BRAND.cortexAlert}40)`,
      }} />

      {/* Stat 2 — Insight time */}
      <AnimatedCounter
        value={insightTime}
        label="Transcripción → Insight"
        accent={BRAND.cortexAlert}
        delay={30}
      />

      <div style={{
        width: 2, height: lineHeight2, borderRadius: 1,
        background: `linear-gradient(to bottom, ${BRAND.cortexAlert}40, ${BRAND.cortexSuggestion}40)`,
      }} />

      {/* Stat 3 — Accuracy */}
      <AnimatedCounter
        value={accuracy}
        label="Precisión de contexto RAG"
        accent={BRAND.cortexSuggestion}
        delay={55}
      />

      {/* Badge */}
      <div
        style={{
          transform: `scale(${badgeScale})`,
          marginTop: 16,
          background: `linear-gradient(135deg, ${BRAND.primary}, ${BRAND.primaryDark})`,
          borderRadius: 8,
          padding: "14px 36px",
          boxShadow: `0 0 40px ${BRAND.primary}25`,
        }}
      >
        <span style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 26,
          fontWeight: 600,
          color: "white",
        }}>
          Respuestas en tiempo real
        </span>
      </div>
    </div>
  );
};
