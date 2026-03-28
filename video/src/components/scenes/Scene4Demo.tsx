import React from "react";
import { useCurrentFrame, interpolate, Easing, spring, useVideoConfig } from "remotion";
import { BRAND } from "../../constants/brand";
import { TranscriptionLine } from "../shared/TranscriptionLine";
import { InsightCard } from "../shared/InsightCard";

interface Transcription { speaker: string; text: string; speakerIndex: number; }
interface Insight { type: "alert" | "scope" | "suggestion"; title: string; body: string; confidence: number; }
interface Scene4DemoProps { transcription: Transcription[]; insights: Insight[]; }

export const Scene4Demo: React.FC<Scene4DemoProps> = ({ transcription, insights }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const containerScale = interpolate(frame, [0, 25], [0.96, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const containerOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const recordPulse = 0.4 + 0.6 * Math.abs(Math.sin(frame * 0.06));
  const seconds = Math.floor(frame / 30);
  const duration = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;

  // Meme annotations — slower triggers
  const annotations = [
    { text: "Cortex ya lo sabía", trigger: 120, color: BRAND.primary },
    { text: "scope guardado", trigger: 210, color: BRAND.cortexScope },
    { text: "imposible sin Cortex", trigger: 310, color: BRAND.cortexAlert },
  ];

  const showEnd = frame > 385;
  const endOpacity = interpolate(frame, [385, 400], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div style={{
      width: "100%", height: "100%", backgroundColor: BRAND.bgBase,
      display: "flex", alignItems: "center", justifyContent: "center",
      position: "relative", overflow: "hidden",
    }}>
      {/* "mira esto" label */}
      <div style={{
        position: "absolute", top: 18, left: "50%",
        transform: `translateX(-50%)`,
        opacity: interpolate(frame, [5, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        fontFamily: "Inter, sans-serif", fontSize: 13, fontWeight: 700,
        color: BRAND.primary, backgroundColor: `${BRAND.primary}08`,
        borderRadius: 99, padding: "4px 14px", border: `1px solid ${BRAND.primary}12`,
        zIndex: 10, display: "flex", alignItems: "center", gap: 6,
      }}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19" /><polyline points="19 12 12 19 5 12" />
        </svg>
        mira esto
      </div>

      {/* Desktop mockup */}
      <div style={{
        opacity: containerOpacity, transform: `scale(${containerScale})`,
        width: 1760, height: 940,
        backgroundColor: BRAND.bgBase, borderRadius: 12,
        border: `1px solid ${BRAND.borderSubtle}`,
        display: "flex", flexDirection: "column", overflow: "hidden", position: "relative",
      }}>
        {/* Header */}
        <div style={{
          height: 40, borderBottom: `1px solid ${BRAND.borderSubtle}`,
          display: "flex", alignItems: "center", padding: "0 16px", gap: 10, flexShrink: 0,
        }}>
          <div style={{ display: "flex", gap: 5, marginRight: 10 }}>
            {["#e8654c", "#d9a840", "#34d399"].map((c, i) => (
              <div key={i} style={{ width: 10, height: 10, borderRadius: "50%", backgroundColor: c }} />
            ))}
          </div>
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 12, color: BRAND.textPrimary }}>Secture</span>
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 12, fontWeight: 700, color: BRAND.primary }}>Cortex</span>
          <div style={{ width: 1, height: 14, backgroundColor: BRAND.borderSubtle, margin: "0 6px" }} />
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 11, color: BRAND.textMuted }}>← E-commerce Plus</span>
          <div style={{ width: 1, height: 14, backgroundColor: BRAND.borderSubtle, margin: "0 6px" }} />
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 12, fontWeight: 500, color: BRAND.textPrimary }}>Sprint Review — S12</span>
          <div style={{ flex: 1 }} />
          <div style={{ display: "flex", alignItems: "center", gap: 5, backgroundColor: `${BRAND.destructive}08`, borderRadius: 99, padding: "3px 10px" }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: BRAND.destructive, opacity: recordPulse }} />
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 10, color: BRAND.destructive, fontWeight: 700 }}>REC</span>
          </div>
          <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 11, color: BRAND.textMuted }}>{duration}</span>
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: BRAND.success }} />
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 10, color: BRAND.textMuted }}>Conectado</span>
          </div>
        </div>

        {/* Main */}
        <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
          {/* Transcript */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", borderRight: `1px solid ${BRAND.borderSubtle}` }}>
            <div style={{
              display: "flex", alignItems: "center", gap: 6, padding: "8px 16px",
              opacity: interpolate(frame, [10, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              </svg>
              <span style={{ fontFamily: "Inter, sans-serif", fontSize: 11, fontWeight: 700, color: BRAND.primary, textTransform: "uppercase", letterSpacing: 1 }}>
                Transcripción en vivo
              </span>
              <div style={{ flex: 1 }} />
              <div style={{ display: "flex", alignItems: "center", gap: 3, backgroundColor: `${BRAND.success}08`, borderRadius: 3, padding: "2px 8px" }}>
                <div style={{ width: 4, height: 4, borderRadius: "50%", backgroundColor: BRAND.success, opacity: recordPulse }} />
                <span style={{ fontFamily: "Inter, sans-serif", fontSize: 8, color: BRAND.success, fontWeight: 700 }}>LIVE</span>
              </div>
            </div>
            <div style={{ flex: 1, padding: "4px 16px" }}>
              {transcription.map((t, i) => (
                <TranscriptionLine key={i} speaker={t.speaker} text={t.text} speakerIndex={t.speakerIndex} delay={30 + i * 70} />
              ))}
            </div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 2, padding: "6px 16px", borderTop: `1px solid ${BRAND.borderSubtle}` }}>
              {Array.from({ length: 80 }, (_, i) => (
                <div key={i} style={{
                  width: 2.5, height: 3 + Math.abs(Math.sin((frame + i * 3) * 0.05)) * 14,
                  borderRadius: 1, backgroundColor: BRAND.primary,
                  opacity: 0.15 + Math.abs(Math.sin((frame + i * 2) * 0.07)) * 0.3,
                }} />
              ))}
            </div>
          </div>

          {/* Copiloto IA */}
          <div style={{ width: 440, display: "flex", flexDirection: "column" }}>
            <div style={{
              display: "flex", alignItems: "center", gap: 6, padding: "8px 14px",
              borderBottom: `1px solid rgba(255,255,255,0.03)`,
              opacity: interpolate(frame, [12, 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a7 7 0 0 1 7 7c0 3-1.5 5.5-4 7.5V20H9v-3.5C6.5 14.5 5 12 5 9a7 7 0 0 1 7-7z" />
              </svg>
              <span style={{ fontFamily: "Inter, sans-serif", fontSize: 12, fontWeight: 600, color: BRAND.textPrimary }}>Copiloto IA</span>
              <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: BRAND.primary, opacity: recordPulse }} />
            </div>
            <div style={{ flex: 1, padding: "6px 12px" }}>
              {frame < 90 && (
                <div style={{
                  display: "flex", alignItems: "center", justifyContent: "center", height: "100%",
                  opacity: interpolate(frame, [28, 45, 75, 90], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
                }}>
                  <span style={{ fontFamily: "Inter, sans-serif", fontSize: 12, color: BRAND.textMuted }}>Escuchando...</span>
                </div>
              )}
              {insights.map((insight, i) => (
                <InsightCard key={i} type={insight.type} title={insight.title} body={insight.body} confidence={insight.confidence} delay={90 + i * 80} />
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{
          height: 38, borderTop: `1px solid ${BRAND.borderSubtle}`,
          display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 16px", flexShrink: 0,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 5, height: 26, borderRadius: 13, backgroundColor: `${BRAND.destructive}10`, padding: "0 12px" }}>
              <div style={{ width: 8, height: 8, borderRadius: 1, backgroundColor: BRAND.destructive }} />
              <span style={{ fontFamily: "Inter, sans-serif", fontSize: 10, color: BRAND.destructive, fontWeight: 600 }}>Detener</span>
            </div>
            {[{ c: BRAND.success, l: "Mic" }, { c: BRAND.blue400, l: "Tab" }].map((x, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <div style={{ width: 5, height: 5, borderRadius: "50%", backgroundColor: x.c }} />
                <span style={{ fontFamily: "Inter, sans-serif", fontSize: 9, color: BRAND.textMuted }}>{x.l}</span>
              </div>
            ))}
          </div>
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 11, color: BRAND.destructive, fontWeight: 500 }}>Finalizar reunión</span>
        </div>

        {/* Annotations — gentler style */}
        {annotations.map((ann, i) => {
          if (frame < ann.trigger) return null;
          const yPositions = [180, 360, 540];
          const opacity = interpolate(frame, [ann.trigger, ann.trigger + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const x = interpolate(frame, [ann.trigger, ann.trigger + 20], [-10, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
          const icons = [
            <svg key="b" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={ann.color} strokeWidth="2"><path d="M12 2a7 7 0 0 1 7 7c0 3-1.5 5.5-4 7.5V20H9v-3.5C6.5 14.5 5 12 5 9a7 7 0 0 1 7-7z" /></svg>,
            <svg key="s" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={ann.color} strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>,
            <svg key="a" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={ann.color} strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>,
          ];
          return (
            <div key={i} style={{
              position: "absolute", left: 30, top: yPositions[i],
              opacity, transform: `translateX(${x}px)`,
              display: "flex", alignItems: "center", gap: 6,
              fontFamily: "Inter, sans-serif", fontSize: 12, fontWeight: 700, color: ann.color,
              backgroundColor: `${BRAND.bgBase}DD`, borderRadius: 6,
              padding: "4px 12px", border: `1px solid ${ann.color}18`, zIndex: 20,
            }}>
              {icons[i]}
              {ann.text}
            </div>
          );
        })}

        {/* End overlay */}
        {showEnd && (
          <div style={{
            position: "absolute", inset: 0, zIndex: 50,
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            backgroundColor: `${BRAND.bgBase}E6`, opacity: endOpacity,
          }}>
            <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke={BRAND.success} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 20, fontWeight: 600, color: BRAND.textPrimary, marginTop: 12 }}>Reunión finalizada</span>
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 13, color: BRAND.textMuted, marginTop: 6 }}>Guardando transcripción e insights...</span>
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 13, color: BRAND.primary, marginTop: 8, fontWeight: 600 }}>sin mover un dedo</span>
          </div>
        )}
      </div>
    </div>
  );
};
