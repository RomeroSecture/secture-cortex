import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { BRAND } from "../../constants/brand";

const MicIcon = ({ color }: { color: string }) => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /></svg>;
const BrainIcon = ({ color }: { color: string }) => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a7 7 0 0 1 7 7c0 3-1.5 5.5-4 7.5V20H9v-3.5C6.5 14.5 5 12 5 9a7 7 0 0 1 7-7z" /><path d="M9 22h6" /></svg>;
const TargetIcon = ({ color }: { color: string }) => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" /></svg>;
const ShieldIcon = ({ color }: { color: string }) => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /><path d="M9 12l2 2 4-4" /></svg>;
const RefreshIcon = ({ color }: { color: string }) => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" /></svg>;
const UsersIcon = ({ color }: { color: string }) => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>;
const FileIcon = ({ color }: { color: string }) => <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>;

export const Scene5SpeedRun: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const stats = [
    { value: "<2s", label: "audio → texto", Icon: MicIcon, color: BRAND.primary, delay: 15 },
    { value: "<10s", label: "texto → insight", Icon: BrainIcon, color: BRAND.cortexAlert, delay: 45 },
    { value: "95%", label: "precisión RAG", Icon: TargetIcon, color: BRAND.cortexSuggestion, delay: 75 },
  ];

  const features = [
    { text: "4 agentes IA analizando", Icon: UsersIcon, delay: 110 },
    { text: "Scope Guardian automático", Icon: ShieldIcon, delay: 128 },
    { text: "Memoria entre reuniones", Icon: RefreshIcon, delay: 146 },
    { text: "6 outputs post-reunión", Icon: FileIcon, delay: 164 },
  ];

  const techs = ["FastAPI", "LangGraph", "pgvector", "Deepgram", "Groq", "Jina"];

  return (
    <div style={{
      width: "100%", height: "100%", backgroundColor: BRAND.bgBase,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      position: "relative", overflow: "hidden", gap: 28,
    }}>
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px)`,
        backgroundSize: "50px 50px",
      }} />

      {/* Title */}
      <div style={{
        opacity: interpolate(frame, [5, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        display: "flex", alignItems: "center", gap: 12,
        fontFamily: "Inter, sans-serif", fontSize: 36, fontWeight: 900, color: BRAND.textPrimary,
        position: "relative", zIndex: 1,
      }}>
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
        en resumen
      </div>

      {/* Stats */}
      <div style={{ display: "flex", gap: 24, position: "relative", zIndex: 1 }}>
        {stats.map((stat, i) => {
          const s = spring({ frame: frame - stat.delay, fps, config: { damping: 14, stiffness: 120 } });
          return (
            <div key={i} style={{
              transform: `scale(${s})`,
              backgroundColor: BRAND.bgSurface, border: `1px solid ${stat.color}12`,
              borderRadius: 16, padding: "24px 40px", textAlign: "center", minWidth: 280,
            }}>
              <stat.Icon color={stat.color} />
              <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 52, fontWeight: 800, color: stat.color, lineHeight: 1, marginTop: 10 }}>
                {stat.value}
              </div>
              <div style={{ fontFamily: "Inter, sans-serif", fontSize: 14, color: BRAND.textMuted, marginTop: 8 }}>
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>

      {/* Features */}
      <div style={{ display: "flex", gap: 12, position: "relative", zIndex: 1 }}>
        {features.map((feat, i) => {
          const opacity = interpolate(frame, [feat.delay, feat.delay + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const y = interpolate(frame, [feat.delay, feat.delay + 18], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={i} style={{
              opacity, transform: `translateY(${y}px)`,
              backgroundColor: BRAND.bgSurface, border: `1px solid ${BRAND.borderSubtle}`,
              borderRadius: 10, padding: "10px 18px", display: "flex", alignItems: "center", gap: 10,
            }}>
              <feat.Icon color={BRAND.primary} />
              <span style={{ fontFamily: "Inter, sans-serif", fontSize: 14, fontWeight: 600, color: BRAND.textPrimary }}>{feat.text}</span>
            </div>
          );
        })}
      </div>

      {/* Tech stack */}
      <div style={{
        display: "flex", gap: 8, position: "relative", zIndex: 1,
        opacity: interpolate(frame, [185, 210], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      }}>
        {techs.map((tech) => (
          <span key={tech} style={{
            fontFamily: "JetBrains Mono, monospace", fontSize: 11,
            color: BRAND.textFaint, backgroundColor: BRAND.bgSurface,
            border: `1px solid ${BRAND.borderSubtle}`, borderRadius: 4, padding: "4px 10px",
          }}>{tech}</span>
        ))}
      </div>

      {/* Badge */}
      <div style={{
        opacity: interpolate(frame, [215, 240], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        display: "flex", alignItems: "center", gap: 8,
        fontFamily: "Inter, sans-serif", fontSize: 16, fontWeight: 700,
        color: BRAND.primary, backgroundColor: `${BRAND.primary}08`,
        borderRadius: 99, padding: "8px 20px", border: `1px solid ${BRAND.primary}12`,
        position: "relative", zIndex: 1,
      }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
        dato real, sin bait
      </div>
    </div>
  );
};
