import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate, Easing } from "remotion";
import { BRAND } from "../../constants/brand";

interface Feature {
  title: string;
  subtitle: string;
  accent: string;
}

interface Scene5FeaturesProps {
  features: Feature[];
}

const ICONS = ["🎙️", "🛡️", "🔍", "🧠"];

const STATS = [
  { value: "<2s", label: "Latencia audio→texto", color: BRAND.primary },
  { value: "<10s", label: "Texto→insight", color: BRAND.cortexAlert },
  { value: "95%", label: "Precisión RAG", color: BRAND.cortexSuggestion },
];

export const Scene5Features: React.FC<Scene5FeaturesProps> = ({ features }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 12], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div style={{
      width: "100%",
      height: "100%",
      backgroundColor: BRAND.bgBase,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "40px 50px",
      position: "relative",
    }}>
      {/* Background glow */}
      <div style={{
        position: "absolute",
        top: "30%", left: "50%",
        width: 600, height: 600, borderRadius: "50%",
        background: `radial-gradient(circle, ${BRAND.primary}08 0%, transparent 70%)`,
        transform: "translate(-50%, -50%)",
      }} />

      {/* Title */}
      <div style={{
        opacity: titleOpacity,
        transform: `translateY(${titleY}px)`,
        fontFamily: "Inter, sans-serif",
        fontSize: 48,
        fontWeight: 700,
        color: BRAND.textPrimary,
        marginBottom: 40,
        textAlign: "center",
        position: "relative",
      }}>
        Inteligencia en cada reunión
      </div>

      {/* Features — vertical stack for more detail */}
      <div style={{ display: "flex", flexDirection: "column", gap: 12, width: "100%", maxWidth: 920, position: "relative" }}>
        {features.map((feature, i) => {
          const s = spring({ frame: frame - (12 + i * 10), fps, config: { damping: 14, stiffness: 160 } });
          return (
            <div key={i} style={{
              transform: `scale(${s})`,
              backgroundColor: BRAND.bgCard,
              border: `1px solid ${BRAND.borderSubtle}`,
              borderLeft: `3px solid ${feature.accent}`,
              borderRadius: 10,
              padding: "16px 20px",
              display: "flex",
              alignItems: "center",
              gap: 16,
            }}>
              <div style={{
                width: 44, height: 44, borderRadius: 10,
                backgroundColor: `${feature.accent}15`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 22, flexShrink: 0,
              }}>
                {ICONS[i]}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: "Inter, sans-serif", fontSize: 20, fontWeight: 600, color: BRAND.textPrimary, marginBottom: 2 }}>
                  {feature.title}
                </div>
                <div style={{ fontFamily: "Inter, sans-serif", fontSize: 13, color: BRAND.textMuted }}>
                  {feature.subtitle}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Stats row below features */}
      <div style={{ display: "flex", gap: 16, marginTop: 40 }}>
        {STATS.map((stat, i) => {
          const s = spring({ frame: frame - (60 + i * 10), fps, config: { damping: 12, stiffness: 160 } });
          return (
            <div key={i} style={{
              transform: `scale(${s})`,
              textAlign: "center",
              backgroundColor: BRAND.bgSurface,
              border: `1px solid ${BRAND.borderSubtle}`,
              borderRadius: 12,
              padding: "18px 28px",
              minWidth: 200,
            }}>
              <div style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: 44,
                fontWeight: 700,
                color: stat.color,
                lineHeight: 1,
              }}>
                {stat.value}
              </div>
              <div style={{
                fontFamily: "Inter, sans-serif",
                fontSize: 11,
                color: BRAND.textMuted,
                marginTop: 6,
              }}>
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Tech stack badge */}
      <div style={{
        marginTop: 30,
        display: "flex",
        gap: 8,
        opacity: interpolate(frame, [100, 115], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      }}>
        {["FastAPI", "LangGraph", "pgvector", "Deepgram", "Groq", "Jina"].map((tech) => (
          <span key={tech} style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: 9,
            color: BRAND.textFaint,
            backgroundColor: BRAND.bgSurface,
            border: `1px solid ${BRAND.borderSubtle}`,
            borderRadius: 4,
            padding: "3px 8px",
          }}>
            {tech}
          </span>
        ))}
      </div>
    </div>
  );
};
