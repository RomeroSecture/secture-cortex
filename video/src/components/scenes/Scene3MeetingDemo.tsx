import React from "react";
import { useCurrentFrame, interpolate, Easing } from "remotion";
import { BRAND } from "../../constants/brand";
import { TranscriptionLine } from "../shared/TranscriptionLine";
import { InsightCard } from "../shared/InsightCard";

interface Transcription {
  speaker: string;
  text: string;
  speakerIndex: number;
}

interface Insight {
  type: "alert" | "scope" | "suggestion";
  title: string;
  body: string;
  confidence: number;
}

interface Scene3MeetingDemoProps {
  transcription: Transcription[];
  insights: Insight[];
}

export const Scene3MeetingDemo: React.FC<Scene3MeetingDemoProps> = ({
  transcription,
  insights,
}) => {
  const frame = useCurrentFrame();

  // Container entrance
  const containerY = interpolate(frame, [0, 18], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const containerOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const recordPulse = 0.4 + 0.6 * Math.abs(Math.sin(frame * 0.08));
  const seconds = Math.floor(frame / 30);
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  const duration = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

  // KPI counters animate
  const insightCount = Math.min(insights.length, Math.floor(interpolate(frame, [80, 200], [0, 3], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })));
  const decisionCount = Math.floor(interpolate(frame, [160, 220], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const actionCount = Math.floor(interpolate(frame, [180, 240], [0, 2], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const questionCount = Math.floor(interpolate(frame, [120, 180], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));

  // Tab switching — show "Inteligencia" tab after frame 200
  const activeTab = frame < 200 ? "insights" : "intelligence";
  const tabSwitchProgress = interpolate(frame, [198, 210], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Meeting end overlay (last 30 frames)
  const showEndOverlay = frame > 260;
  const endOpacity = interpolate(frame, [260, 272], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const endY = interpolate(frame, [262, 278], [8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Conversation events data
  const events = [
    { icon: "⚡", text: "Decidido: Migrar API v2 → v3 antes de WhatsApp", time: "05:12", color: BRAND.cortexAlert },
    { icon: "✓", text: "Action: Laura investiga esfuerzo migración", time: "05:45", color: BRAND.cortexScope },
    { icon: "?", text: "Pendiente: ¿Timeline factible para Q2?", time: "06:02", color: BRAND.cortexSuggestion },
  ];

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: BRAND.bgBase,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* App mockup */}
      <div
        style={{
          opacity: containerOpacity,
          transform: `translateY(${containerY}px)`,
          width: 1010,
          height: 1780,
          backgroundColor: BRAND.bgBase,
          borderRadius: 16,
          border: `1px solid ${BRAND.borderSubtle}`,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          position: "relative",
        }}
      >
        {/* ===== MEETING HEADER ===== */}
        <div
          style={{
            height: 44,
            backgroundColor: BRAND.bgBase,
            borderBottom: `1px solid ${BRAND.borderSubtle}`,
            display: "flex",
            alignItems: "center",
            padding: "0 12px",
            gap: 8,
            flexShrink: 0,
          }}
        >
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 11, color: BRAND.textMuted }}>
            &larr; E-commerce Plus
          </span>
          <div style={{ width: 1, height: 14, backgroundColor: BRAND.borderSubtle }} />
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 12, fontWeight: 500, color: BRAND.textPrimary }}>
            Sprint Review — Semana 12
          </span>
          <div style={{ flex: 1 }} />
          {/* REC pill */}
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 5,
            backgroundColor: `${BRAND.destructive}12`, borderRadius: 99, padding: "3px 10px",
          }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: BRAND.destructive, opacity: recordPulse }} />
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 10, color: BRAND.destructive, fontWeight: 500 }}>REC</span>
          </div>
          <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 10, color: BRAND.textMuted }}>{duration}</span>
          {/* WS dot */}
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", backgroundColor: BRAND.success }} />
            <span style={{ fontFamily: "Inter, sans-serif", fontSize: 9, color: BRAND.textMuted }}>Conectado</span>
          </div>
        </div>

        {/* ===== KPIs BAR ===== */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "6px 12px",
            borderBottom: `1px solid ${BRAND.borderSubtle}`,
            opacity: interpolate(frame, [40, 55], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          {[
            { label: "INSIGHTS", value: insightCount, color: BRAND.primary },
            { label: "DECISIONES", value: decisionCount, color: BRAND.cortexAlert },
            { label: "ACTIONS", value: actionCount, color: BRAND.cortexScope },
            { label: "PREGUNTAS", value: questionCount, color: BRAND.cortexSuggestion },
            { label: "SPEAKERS", value: 2, color: BRAND.textPrimary },
          ].map((kpi, i) => (
            <div key={i} style={{
              display: "flex", flexDirection: "column", alignItems: "center", gap: 1,
              backgroundColor: BRAND.bgSurface, borderRadius: 6, padding: "4px 10px", flex: 1,
            }}>
              <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 16, fontWeight: 600, color: kpi.color }}>
                {kpi.value}
              </span>
              <span style={{ fontFamily: "Inter, sans-serif", fontSize: 7, color: BRAND.textMuted, textTransform: "uppercase", letterSpacing: 0.8 }}>
                {kpi.label}
              </span>
            </div>
          ))}
          {/* Top speaker */}
          <div style={{
            fontFamily: "Inter, sans-serif", fontSize: 8, color: BRAND.textFaint,
            display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 1,
          }}>
            <span>Más activo:</span>
            <span style={{ color: BRAND.textMuted }}>Cliente (4 seg.)</span>
          </div>
        </div>

        {/* ===== MAIN CONTENT ===== */}
        <div style={{ flex: 1, display: "flex", overflow: "hidden", gap: 1, padding: 3 }}>

          {/* LEFT: LiveTranscript */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", borderRadius: 8 }}>
            {/* Transcript header */}
            <div style={{
              display: "flex", alignItems: "center", gap: 5, padding: "8px 10px",
              opacity: interpolate(frame, [8, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke={BRAND.primary} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              </svg>
              <span style={{ fontFamily: "Inter, sans-serif", fontSize: 9, fontWeight: 600, color: BRAND.primary, textTransform: "uppercase", letterSpacing: 1 }}>
                Transcripción en vivo
              </span>
              <div style={{ flex: 1 }} />
              <div style={{
                display: "inline-flex", alignItems: "center", gap: 3,
                backgroundColor: `${BRAND.success}12`, borderRadius: 3, padding: "1px 6px",
              }}>
                <div style={{ width: 4, height: 4, borderRadius: "50%", backgroundColor: BRAND.success, opacity: recordPulse }} />
                <span style={{ fontFamily: "Inter, sans-serif", fontSize: 7, color: BRAND.success, fontWeight: 600 }}>LIVE</span>
              </div>
            </div>

            {/* Messages */}
            <div style={{ flex: 1, padding: "2px 10px", overflowY: "hidden" }}>
              {transcription.map((t, i) => (
                <TranscriptionLine
                  key={i}
                  speaker={t.speaker}
                  text={t.text}
                  speakerIndex={t.speakerIndex}
                  delay={16 + i * 45}
                />
              ))}
              {/* Typing dots */}
              {frame > 150 && frame < 220 && (
                <div style={{
                  display: "flex", alignItems: "center", gap: 3, marginLeft: 36, marginTop: 4,
                  opacity: interpolate(frame, [150, 156], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
                }}>
                  <div style={{ backgroundColor: BRAND.bgSurface, borderRadius: 8, padding: "5px 10px", display: "flex", gap: 3 }}>
                    {[0, 1, 2].map((i) => {
                      const phase = ((frame - 150) * 0.18 + i * 1.2) % (Math.PI * 2);
                      return (
                        <div key={i} style={{
                          width: 4, height: 4, borderRadius: "50%",
                          backgroundColor: BRAND.textMuted,
                          opacity: 0.2 + 0.8 * Math.max(0, Math.sin(phase)),
                          transform: `translateY(${Math.max(0, Math.sin(phase)) * -3}px)`,
                        }} />
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Waveform */}
            <div style={{
              display: "flex", alignItems: "center", justifyContent: "center", gap: 1.5,
              padding: "5px 10px", borderTop: `1px solid ${BRAND.borderSubtle}`,
            }}>
              {Array.from({ length: 55 }, (_, i) => {
                const h = 3 + Math.abs(Math.sin((frame + i * 4) * 0.07)) * 12;
                return (
                  <div key={i} style={{
                    width: 2, height: h, borderRadius: 1,
                    backgroundColor: BRAND.primary,
                    opacity: 0.25 + Math.abs(Math.sin((frame + i * 3) * 0.09)) * 0.45,
                  }} />
                );
              })}
            </div>
          </div>

          {/* RIGHT: Insight/Intelligence Panel */}
          <div style={{
            width: 370, display: "flex", flexDirection: "column", overflow: "hidden",
            borderRadius: 8, borderLeft: `1px solid ${BRAND.borderSubtle}`,
          }}>
            {/* Tab switcher */}
            <div style={{
              display: "flex", borderBottom: `1px solid rgba(255,255,255,0.04)`, padding: "0 10px",
              opacity: interpolate(frame, [10, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}>
              {[
                { id: "insights", label: "Copiloto IA", count: insightCount },
                { id: "intelligence", label: "Inteligencia", count: decisionCount + actionCount },
              ].map((tab) => (
                <button
                  key={tab.id}
                  style={{
                    fontFamily: "Inter, sans-serif", fontSize: 10, fontWeight: 500,
                    padding: "6px 10px",
                    color: activeTab === tab.id ? BRAND.textPrimary : BRAND.textMuted,
                    borderBottom: activeTab === tab.id ? `2px solid ${BRAND.primary}` : "2px solid transparent",
                    background: "none", border: "none", cursor: "default",
                  }}
                >
                  {tab.label}
                  {tab.count > 0 && (
                    <span style={{ marginLeft: 4, fontSize: 8, color: BRAND.textMuted }}>{tab.count}</span>
                  )}
                </button>
              ))}
            </div>

            {/* Panel content */}
            <div style={{ flex: 1, padding: "6px 8px", overflowY: "hidden" }}>
              {/* === Copiloto IA Tab === */}
              {activeTab === "insights" && (
                <>
                  {/* Empty state */}
                  {frame < 60 && (
                    <div style={{
                      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                      height: "100%", gap: 6,
                      opacity: interpolate(frame, [18, 28, 50, 60], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
                    }}>
                      <span style={{ fontFamily: "Inter, sans-serif", fontSize: 11, color: BRAND.textMuted, textAlign: "center" }}>
                        Escuchando...
                      </span>
                      <span style={{ fontFamily: "Inter, sans-serif", fontSize: 9, color: BRAND.textFaint, textAlign: "center", lineHeight: 1.4, maxWidth: 200 }}>
                        Los insights aparecerán cuando detecte algo relevante
                      </span>
                    </div>
                  )}
                  {insights.map((insight, i) => (
                    <InsightCard
                      key={i}
                      type={insight.type}
                      title={insight.title}
                      body={insight.body}
                      confidence={insight.confidence}
                      delay={60 + i * 45}
                    />
                  ))}
                </>
              )}

              {/* === Inteligencia Tab === */}
              {activeTab === "intelligence" && (
                <div style={{ opacity: tabSwitchProgress }}>
                  {events.map((event, i) => {
                    const eventDelay = 205 + i * 15;
                    const eventOpacity = interpolate(frame, [eventDelay, eventDelay + 8], [0, 1], {
                      extrapolateLeft: "clamp",
                      extrapolateRight: "clamp",
                    });
                    const eventY = interpolate(frame, [eventDelay, eventDelay + 8], [6, 0], {
                      extrapolateLeft: "clamp",
                      extrapolateRight: "clamp",
                      easing: Easing.out(Easing.cubic),
                    });
                    return (
                      <div
                        key={i}
                        style={{
                          opacity: eventOpacity,
                          transform: `translateY(${eventY}px)`,
                          borderLeft: `2px solid ${event.color}`,
                          backgroundColor: `${BRAND.bgSurface}80`,
                          borderRadius: 6,
                          padding: "6px 9px",
                          marginBottom: 6,
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "flex-start", gap: 5 }}>
                          <span style={{ fontSize: 11 }}>{event.icon}</span>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <p style={{ fontFamily: "Inter, sans-serif", fontSize: 10, fontWeight: 500, color: BRAND.textPrimary, lineHeight: 1.3 }}>
                              {event.text}
                            </p>
                          </div>
                          <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 8, color: BRAND.textFaint, flexShrink: 0 }}>
                            {event.time}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ===== AUDIO CONTROLS ===== */}
        <div style={{
          height: 42, borderTop: `1px solid ${BRAND.borderSubtle}`,
          display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 12px", flexShrink: 0,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {/* Stop btn */}
            <div style={{
              display: "flex", alignItems: "center", gap: 5,
              height: 26, borderRadius: 13, backgroundColor: `${BRAND.destructive}18`, padding: "0 10px",
            }}>
              <div style={{ width: 7, height: 7, borderRadius: 1, backgroundColor: BRAND.destructive }} />
              <span style={{ fontFamily: "Inter, sans-serif", fontSize: 9, color: BRAND.destructive, fontWeight: 500 }}>Detener</span>
            </div>
            {/* Mic + Tab indicators */}
            {[
              { color: BRAND.success, label: "Mic" },
              { color: BRAND.blue400, label: "Tab" },
            ].map((ind, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 3 }}>
                <div style={{ width: 5, height: 5, borderRadius: "50%", backgroundColor: ind.color }} />
                <span style={{ fontFamily: "Inter, sans-serif", fontSize: 8, color: BRAND.textMuted }}>{ind.label}</span>
              </div>
            ))}
          </div>
          <span style={{ fontFamily: "Inter, sans-serif", fontSize: 10, color: BRAND.destructive, fontWeight: 500 }}>
            Finalizar reunión
          </span>
        </div>

        {/* ===== MEETING END OVERLAY ===== */}
        {showEndOverlay && (
          <div style={{
            position: "absolute", inset: 0, zIndex: 50,
            display: "flex", alignItems: "center", justifyContent: "center",
            backgroundColor: `${BRAND.bgBase}E6`,
            backdropFilter: "blur(8px)",
            opacity: endOpacity,
          }}>
            <div style={{ textAlign: "center", transform: `translateY(${endY}px)` }}>
              <div style={{ fontFamily: "Inter, sans-serif", fontSize: 18, fontWeight: 500, color: BRAND.textPrimary }}>
                Reunión finalizada
              </div>
              <div style={{ fontFamily: "Inter, sans-serif", fontSize: 12, color: BRAND.textMuted, marginTop: 8 }}>
                Guardando transcripción e insights...
              </div>
              <div style={{ fontFamily: "Inter, sans-serif", fontSize: 10, color: BRAND.textFaint, marginTop: 4 }}>
                Redirigiendo en unos segundos
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
