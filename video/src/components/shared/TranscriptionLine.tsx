import React from "react";
import { useCurrentFrame, interpolate, Easing } from "remotion";
import { BRAND, SPEAKER_COLORS } from "../../constants/brand";

interface TranscriptionLineProps {
  speaker: string;
  text: string;
  speakerIndex: number;
  delay: number;
}

/**
 * Matches real app LiveTranscript:
 * - h-7 w-7 rounded-full avatar with 2-letter initials
 * - border-left-2 colored by speaker
 * - bg-surface px-3 py-2 rounded-lg
 * - text-sm text-foreground
 */
export const TranscriptionLine: React.FC<TranscriptionLineProps> = ({
  speaker,
  text,
  speakerIndex,
  delay,
}) => {
  const frame = useCurrentFrame();
  const color = SPEAKER_COLORS[speakerIndex % SPEAKER_COLORS.length];

  // Entrance: fade-in-up (matches real app animate-fade-in-up)
  const progress = interpolate(frame, [delay, delay + 9], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const translateY = interpolate(progress, [0, 1], [8, 0]);

  // Typewriter
  const charsVisible = interpolate(
    frame,
    [delay + 5, delay + 5 + text.length * 0.28],
    [0, text.length],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const visibleText = text.slice(0, Math.floor(charsVisible));
  const isTyping = Math.floor(charsVisible) < text.length;

  // Initials
  const initials = speaker.slice(0, 2).toUpperCase();

  return (
    <div
      style={{
        opacity: progress,
        transform: `translateY(${translateY}px)`,
        display: "flex",
        alignItems: "flex-start",
        gap: 10,
        marginBottom: 10,
      }}
    >
      {/* Avatar circle — h-7 w-7 rounded-full */}
      <div
        style={{
          width: 28,
          height: 28,
          minWidth: 28,
          borderRadius: "50%",
          backgroundColor: color,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        <span style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 11,
          fontWeight: 600,
          color: "white",
        }}>
          {initials}
        </span>
      </div>

      {/* Message bubble — border-left-2 bg-surface rounded-lg */}
      <div
        style={{
          borderLeft: `2px solid ${color}`,
          backgroundColor: BRAND.bgSurface,
          borderRadius: 8,
          padding: "8px 12px",
          flex: 1,
        }}
      >
        {/* Speaker name */}
        <div style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 11,
          fontWeight: 600,
          color,
          marginBottom: 3,
        }}>
          {speaker}
        </div>

        {/* Message text */}
        <span
          style={{
            fontFamily: "Inter, sans-serif",
            fontSize: 13,
            lineHeight: 1.5,
            color: BRAND.textPrimary,
          }}
        >
          {visibleText}
          {/* Typing cursor */}
          {isTyping && frame > delay + 5 && (
            <span
              style={{
                display: "inline-block",
                width: 2,
                height: 13,
                backgroundColor: BRAND.primary,
                marginLeft: 1,
                opacity: frame % 16 < 8 ? 1 : 0.3,
                verticalAlign: "text-bottom",
              }}
            />
          )}
        </span>
      </div>
    </div>
  );
};
