import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { BRAND, INSIGHT_TYPES } from "../../constants/brand";

interface InsightCardProps {
  type: "alert" | "scope" | "suggestion";
  title: string;
  body: string;
  confidence: number; // 0-100
  delay: number;
}

/**
 * Matches real app InsightCard:
 * - Collapsible card with type dot + truncated summary
 * - Confidence bar (h-1 w-8)
 * - Expanded: full content + sources + feedback buttons + disclaimer
 * - border-cortex-{type}
 */
export const InsightCard: React.FC<InsightCardProps> = ({
  type,
  title,
  body,
  confidence,
  delay,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const config = INSIGHT_TYPES[type];

  // Entrance animation
  const scale = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, stiffness: 160 },
  });

  // Auto-expand after appearing
  const isExpanded = frame > delay + 15;
  const expandProgress = interpolate(frame, [delay + 15, delay + 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Typewriter for body
  const charsVisible = interpolate(
    frame,
    [delay + 18, delay + 18 + body.length * 0.22],
    [0, body.length],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const visibleBody = body.slice(0, Math.floor(charsVisible));

  // Confidence bar fill
  const barFill = interpolate(frame, [delay + 10, delay + 30], [0, confidence], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        borderLeft: `2px solid ${config.color}`,
        backgroundColor: BRAND.bgSurface,
        borderRadius: 8,
        overflow: "hidden",
        marginBottom: 8,
      }}
    >
      {/* Header row — always visible */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "8px 12px",
        }}
      >
        {/* Type dot — h-1.5 w-1.5 rounded-full */}
        <div
          style={{
            width: 6,
            height: 6,
            minWidth: 6,
            borderRadius: "50%",
            backgroundColor: config.color,
          }}
        />

        {/* Title / summary */}
        <span style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 12,
          fontWeight: 500,
          color: BRAND.textPrimary,
          flex: 1,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: isExpanded ? "normal" : "nowrap",
        }}>
          {title}
        </span>

        {/* Confidence bar — h-1 w-8 */}
        <div style={{
          width: 32,
          height: 4,
          borderRadius: 2,
          backgroundColor: BRAND.bgSurfaceHover,
          flexShrink: 0,
        }}>
          <div style={{
            width: `${barFill}%`,
            height: "100%",
            borderRadius: 2,
            backgroundColor: config.color,
          }} />
        </div>

        {/* Chevron */}
        <svg
          width="12" height="12" viewBox="0 0 24 24" fill="none"
          stroke={BRAND.textMuted} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          style={{
            transform: `rotate(${isExpanded ? 180 : 0}deg)`,
            flexShrink: 0,
          }}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div
          style={{
            opacity: expandProgress,
            borderTop: `1px solid ${BRAND.borderSubtle}`,
            padding: "8px 12px 10px",
          }}
        >
          {/* Full body text */}
          <div style={{
            fontFamily: "Inter, sans-serif",
            fontSize: 11,
            lineHeight: 1.6,
            color: BRAND.textPrimary,
            marginBottom: 8,
          }}>
            {visibleBody}
          </div>

          {/* Feedback buttons row */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
            {/* ThumbsUp */}
            <div style={{
              height: 24, paddingLeft: 6, paddingRight: 6,
              borderRadius: 4,
              backgroundColor: "transparent",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={BRAND.textMuted} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
              </svg>
            </div>
            {/* ThumbsDown */}
            <div style={{
              height: 24, paddingLeft: 6, paddingRight: 6,
              borderRadius: 4,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={BRAND.textMuted} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 15V19a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17" />
              </svg>
            </div>
            {/* Dismiss X */}
            <div style={{
              height: 24, paddingLeft: 6, paddingRight: 6,
              borderRadius: 4,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={BRAND.textMuted} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </div>
          </div>

          {/* Disclaimer — italic text-[10px] */}
          <div style={{
            fontFamily: "Inter, sans-serif",
            fontSize: 9,
            fontStyle: "italic",
            color: BRAND.textFaint,
          }}>
            Sugerencia IA — verificar antes de actuar
          </div>
        </div>
      )}
    </div>
  );
};
