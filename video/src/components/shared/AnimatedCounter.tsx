import React from "react";
import { useCurrentFrame, interpolate, Easing } from "remotion";
import { BRAND } from "../../constants/brand";

interface AnimatedCounterProps {
  value: string;
  label: string;
  accent: string;
  delay: number;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  label,
  accent,
  delay,
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [delay, delay + 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const translateY = interpolate(frame, [delay, delay + 12], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const scale = interpolate(frame, [delay + 5, delay + 15], [0.8, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div style={{ opacity, transform: `translateY(${translateY}px)`, textAlign: "center" }}>
      <div style={{
        fontFamily: "JetBrains Mono, monospace",
        fontSize: 96,
        fontWeight: 700,
        color: accent,
        lineHeight: 1,
        transform: `scale(${scale})`,
      }}>
        {value}
      </div>
      <div style={{
        fontFamily: "Inter, sans-serif",
        fontSize: 22,
        color: BRAND.textSecondary,
        marginTop: 8,
        letterSpacing: 0.5,
      }}>
        {label}
      </div>
    </div>
  );
};
