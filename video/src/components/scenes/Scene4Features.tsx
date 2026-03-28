import React from "react";
import { useCurrentFrame, interpolate, Easing } from "remotion";
import { BRAND } from "../../constants/brand";
import { FeatureCard } from "../shared/FeatureCard";

interface Feature {
  title: string;
  subtitle: string;
  accent: string;
}

interface Scene4FeaturesProps {
  features: Feature[];
}

const MicIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
  </svg>
);

const ShieldIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    <path d="M9 12l2 2 4-4" />
  </svg>
);

const DatabaseIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
  </svg>
);

const BrainIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a7 7 0 0 1 7 7c0 3-1.5 5.5-4 7.5V20H9v-3.5C6.5 14.5 5 12 5 9a7 7 0 0 1 7-7z" />
    <path d="M9 22h6" />
  </svg>
);

const ICONS = [<MicIcon />, <ShieldIcon />, <DatabaseIcon />, <BrainIcon />];

export const Scene4Features: React.FC<Scene4FeaturesProps> = ({ features }) => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 15], [24, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
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
        padding: 60,
        position: "relative",
      }}
    >
      {/* Background glow */}
      <div style={{
        position: "absolute",
        top: "35%", left: "50%",
        width: 600, height: 600, borderRadius: "50%",
        background: `radial-gradient(circle, ${BRAND.primary}10 0%, transparent 70%)`,
        transform: "translate(-50%, -50%)",
      }} />

      {/* Title */}
      <div
        style={{
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          fontFamily: "Inter, sans-serif",
          fontSize: 52,
          fontWeight: 700,
          color: BRAND.textPrimary,
          marginBottom: 60,
          textAlign: "center",
          position: "relative",
        }}
      >
        Inteligencia en cada reunión
      </div>

      {/* 2x2 grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, position: "relative" }}>
        {features.map((feature, i) => (
          <FeatureCard
            key={i}
            title={feature.title}
            subtitle={feature.subtitle}
            accent={feature.accent}
            icon={ICONS[i]}
            delay={15 + i * 12}
          />
        ))}
      </div>
    </div>
  );
};
