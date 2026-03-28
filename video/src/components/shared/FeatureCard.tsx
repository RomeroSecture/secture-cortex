import React from "react";
import { useCurrentFrame, useVideoConfig, spring } from "remotion";
import { BRAND } from "../../constants/brand";

interface FeatureCardProps {
  title: string;
  subtitle: string;
  accent: string;
  icon: React.ReactNode;
  delay: number;
}

/**
 * Matches real app card style:
 * rounded-xl border border-border bg-card p-5
 */
export const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  subtitle,
  accent,
  icon,
  delay,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 180 },
  });

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        backgroundColor: BRAND.bgCard,
        border: `1px solid ${BRAND.borderSubtle}`,
        borderRadius: 12,
        padding: "24px 20px",
        display: "flex",
        flexDirection: "column",
        gap: 12,
        width: 440,
      }}
    >
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: 10,
          backgroundColor: `${accent}20`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: accent,
        }}
      >
        {icon}
      </div>
      <div>
        <div style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 26,
          fontWeight: 600,
          color: BRAND.textPrimary,
          marginBottom: 4,
        }}>
          {title}
        </div>
        <div style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 15,
          color: BRAND.textMuted,
          lineHeight: 1.4,
        }}>
          {subtitle}
        </div>
      </div>
    </div>
  );
};
