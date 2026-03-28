import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate, Easing } from "remotion";
import { BRAND } from "../../constants/brand";

/**
 * Animated visualization of the multi-agent LangGraph pipeline:
 * Audio → Deepgram → Buffer → RAG → Supervisor → [Tech Lead, PM, Commercial, Dev] → Synthesizer → Insights
 */
export const Scene4Pipeline: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 15], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Pipeline nodes
  const nodes = [
    { label: "Audio", icon: "🎙️", x: 540, y: 420, delay: 10, color: BRAND.textMuted },
    { label: "Deepgram", icon: "🔊", x: 540, y: 530, delay: 18, color: BRAND.primary },
    { label: "Buffer + RAG", icon: "🔍", x: 540, y: 640, delay: 26, color: BRAND.cortexSuggestion },
    { label: "Supervisor", icon: "🧠", x: 540, y: 770, delay: 34, color: BRAND.cortexAlert },
  ];

  // Agent nodes (fan out from supervisor)
  const agents = [
    { label: "Tech Lead", icon: "⚙️", x: 200, y: 940, delay: 50, color: BRAND.primary, subtypes: "dependencies, architecture" },
    { label: "PM", icon: "📋", x: 400, y: 940, delay: 55, color: BRAND.cortexAlert, subtypes: "scope, budget, risk" },
    { label: "Commercial", icon: "💼", x: 640, y: 940, delay: 60, color: BRAND.cortexScope, subtypes: "upsell, opportunities" },
    { label: "Dev", icon: "💻", x: 840, y: 940, delay: 65, color: BRAND.cortexSuggestion, subtypes: "code refs, patterns" },
  ];

  // Final nodes
  const synthesizer = { label: "Synthesizer", icon: "🔬", x: 540, y: 1080, delay: 80, color: BRAND.primary };
  const output = { label: "Insights", icon: "💡", x: 540, y: 1200, delay: 92, color: BRAND.cortexAlert };

  // Conversation intel (parallel branch)
  const convoIntel = { label: "Conv. Intel", icon: "💬", x: 200, y: 1080, delay: 70, color: BRAND.textMuted };

  // Data particle animation
  const renderParticle = (startY: number, endY: number, startX: number, endX: number, triggerFrame: number, duration: number, color: string) => {
    if (frame < triggerFrame || frame > triggerFrame + duration) return null;
    const progress = interpolate(frame, [triggerFrame, triggerFrame + duration], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.quad),
    });
    const x = startX + (endX - startX) * progress;
    const y = startY + (endY - startY) * progress;
    return (
      <div
        style={{
          position: "absolute",
          left: x - 3,
          top: y - 3,
          width: 6,
          height: 6,
          borderRadius: "50%",
          backgroundColor: color,
          boxShadow: `0 0 10px ${color}80`,
        }}
      />
    );
  };

  const renderNode = (node: { label: string; icon: string; x: number; y: number; delay: number; color: string; subtypes?: string }, size: number = 80) => {
    const s = spring({ frame: frame - node.delay, fps, config: { damping: 12, stiffness: 160 } });
    const isActive = frame > node.delay + 20;
    const glow = isActive ? 0.3 + 0.3 * Math.sin((frame - node.delay) * 0.08) : 0;

    return (
      <div
        key={node.label}
        style={{
          position: "absolute",
          left: node.x - size / 2,
          top: node.y - size / 2,
          width: size,
          height: size,
          borderRadius: 16,
          backgroundColor: BRAND.bgSurface,
          border: `1px solid ${isActive ? node.color + "50" : BRAND.borderSubtle}`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 3,
          transform: `scale(${s})`,
          boxShadow: isActive ? `0 0 ${12 + glow * 10}px ${node.color}25` : "none",
        }}
      >
        <span style={{ fontSize: size > 70 ? 22 : 18 }}>{node.icon}</span>
        <span style={{
          fontFamily: "Inter, sans-serif",
          fontSize: size > 70 ? 10 : 8,
          fontWeight: 600,
          color: node.color,
          textAlign: "center",
          lineHeight: 1.1,
        }}>
          {node.label}
        </span>
        {node.subtypes && (
          <span style={{
            fontFamily: "Inter, sans-serif",
            fontSize: 7,
            color: BRAND.textFaint,
            textAlign: "center",
            maxWidth: size - 10,
          }}>
            {node.subtypes}
          </span>
        )}
      </div>
    );
  };

  // Connection lines
  const renderLine = (x1: number, y1: number, x2: number, y2: number, delay: number) => {
    const progress = interpolate(frame, [delay, delay + 12], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    if (progress <= 0) return null;

    const dx = x2 - x1;
    const dy = y2 - y1;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * (180 / Math.PI);

    return (
      <div
        style={{
          position: "absolute",
          left: x1,
          top: y1,
          width: length * progress,
          height: 1,
          backgroundColor: `${BRAND.primary}30`,
          transformOrigin: "0 0",
          transform: `rotate(${angle}deg)`,
        }}
      />
    );
  };

  // Post-meeting outputs
  const outputs = [
    { label: "Acta", delay: 105 },
    { label: "Handoff", delay: 110 },
    { label: "Email", delay: 115 },
    { label: "Sprint", delay: 120 },
  ];

  return (
    <div style={{
      width: "100%",
      height: "100%",
      backgroundColor: BRAND.bgBase,
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Subtle grid */}
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)`,
        backgroundSize: "40px 40px",
      }} />

      {/* Title */}
      <div style={{
        position: "absolute",
        top: 60,
        left: 0,
        right: 0,
        textAlign: "center",
        opacity: titleOpacity,
        transform: `translateY(${titleY}px)`,
      }}>
        <div style={{ fontFamily: "Inter, sans-serif", fontSize: 42, fontWeight: 700, color: BRAND.textPrimary }}>
          Pipeline Multi-Agente
        </div>
        <div style={{ fontFamily: "Inter, sans-serif", fontSize: 18, color: BRAND.textMuted, marginTop: 8 }}>
          LangGraph • 4 especialistas • Síntesis inteligente
        </div>
      </div>

      {/* Connection lines */}
      {renderLine(540, 460, 540, 530, 16)}
      {renderLine(540, 570, 540, 640, 24)}
      {renderLine(540, 680, 540, 770, 32)}
      {/* Fan out from supervisor to agents */}
      {renderLine(540, 810, 200, 900, 42)}
      {renderLine(540, 810, 400, 900, 44)}
      {renderLine(540, 810, 640, 900, 46)}
      {renderLine(540, 810, 840, 900, 48)}
      {/* Agents to synthesizer */}
      {renderLine(200, 980, 540, 1040, 72)}
      {renderLine(400, 980, 540, 1040, 74)}
      {renderLine(640, 980, 540, 1040, 76)}
      {renderLine(840, 980, 540, 1040, 78)}
      {/* Conversation intel to synthesizer */}
      {renderLine(200, 1080, 500, 1080, 75)}
      {/* Synthesizer to output */}
      {renderLine(540, 1120, 540, 1200, 88)}

      {/* Data particles flowing through pipeline */}
      {renderParticle(460, 530, 540, 540, 20, 10, BRAND.primary)}
      {renderParticle(570, 640, 540, 540, 28, 10, BRAND.primary)}
      {renderParticle(680, 770, 540, 540, 36, 10, BRAND.cortexAlert)}
      {renderParticle(810, 900, 540, 200, 48, 12, BRAND.primary)}
      {renderParticle(810, 900, 540, 400, 50, 12, BRAND.cortexAlert)}
      {renderParticle(810, 900, 540, 640, 52, 12, BRAND.cortexScope)}
      {renderParticle(810, 900, 540, 840, 54, 12, BRAND.cortexSuggestion)}
      {renderParticle(980, 1040, 200, 540, 74, 12, BRAND.primary)}
      {renderParticle(980, 1040, 400, 540, 76, 12, BRAND.cortexAlert)}
      {renderParticle(980, 1040, 640, 540, 78, 12, BRAND.cortexScope)}
      {renderParticle(980, 1040, 840, 540, 80, 12, BRAND.cortexSuggestion)}
      {renderParticle(1120, 1200, 540, 540, 90, 10, BRAND.cortexAlert)}

      {/* Pipeline nodes */}
      {nodes.map((n) => renderNode(n))}
      {agents.map((a) => renderNode({ ...a }, 100))}
      {renderNode(convoIntel, 85)}
      {renderNode(synthesizer)}
      {renderNode(output)}

      {/* Post-meeting outputs badges */}
      <div style={{
        position: "absolute",
        bottom: 240,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        gap: 12,
      }}>
        {outputs.map((o) => {
          const s = spring({ frame: frame - o.delay, fps, config: { damping: 15, stiffness: 150 } });
          return (
            <div key={o.label} style={{
              transform: `scale(${s})`,
              fontFamily: "Inter, sans-serif",
              fontSize: 11,
              fontWeight: 500,
              color: BRAND.textPrimary,
              backgroundColor: BRAND.bgSurface,
              border: `1px solid ${BRAND.borderSubtle}`,
              borderRadius: 6,
              padding: "6px 14px",
            }}>
              {o.label}
            </div>
          );
        })}
      </div>

      {/* Bottom label */}
      <div style={{
        position: "absolute",
        bottom: 180,
        left: 0,
        right: 0,
        textAlign: "center",
        opacity: interpolate(frame, [110, 125], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      }}>
        <span style={{ fontFamily: "Inter, sans-serif", fontSize: 13, color: BRAND.textFaint }}>
          + 6 outputs post-reunión: acta, handoff, email, sprint impact, briefing, retro
        </span>
      </div>
    </div>
  );
};
