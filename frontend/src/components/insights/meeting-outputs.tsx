"use client";

import { useCallback, useEffect, useState } from "react";
import type { MeetingOutput } from "@/types/project";
import { fetchMeetingOutputs } from "@/lib/api";

interface MeetingOutputsProps {
  projectId: string;
  meetingId: string;
  token: string;
}

const OUTPUT_LABELS: Record<string, { label: string; icon: string }> = {
  minutes: { label: "Acta de Reunión", icon: "📋" },
  handoff: { label: "Paquete de Transición", icon: "📦" },
  sprint_impact: { label: "Impacto en Sprint", icon: "🎯" },
  email_draft: { label: "Borrador de Email", icon: "✉️" },
  briefing: { label: "Briefing Interno", icon: "📄" },
  retrospective: { label: "Retrospectiva", icon: "📊" },
};

/** Translate known JSON keys to Spanish labels. */
const KEY_LABELS: Record<string, string> = {
  attendees: "Asistentes",
  topics_covered: "Temas tratados",
  decisions: "Decisiones",
  action_items: "Tareas pendientes",
  client_requests: "Peticiones del cliente",
  risks_detected: "Riesgos detectados",
  unanswered_questions: "Preguntas sin respuesta",
  next_steps: "Próximos pasos",
  summary: "Resumen",
  topic_status: "Estado de los temas",
  pending_commitments: "Compromisos pendientes",
  open_questions: "Preguntas abiertas",
  context_for_next: "Contexto para la próxima reunión",
  total_requests: "Total de peticiones",
  estimated_days: "Días estimados",
  displaced_stories: "Stories desplazadas",
  recommendation: "Recomendación",
  subject: "Asunto",
  greeting: "Saludo",
  body: "Cuerpo",
  commitments: "Compromisos",
  closing: "Cierre",
  changes_for_team: "Cambios para el equipo",
  relevant_action_items: "Tareas relevantes",
  key_decisions: "Decisiones clave",
  duration_minutes: "Duración (minutos)",
  scope_ratio: "Ratio de scope",
  insights_generated: "Insights generados",
  action_items_count: "Cantidad de tareas",
  sentiment_summary: "Resumen de sentimiento",
  comparison_note: "Nota comparativa",
};

function getLabel(key: string): string {
  return KEY_LABELS[key] || key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Convert a dict item to a readable string. */
function dictToText(obj: Record<string, unknown>): string {
  return Object.entries(obj)
    .filter(([, v]) => v !== null && v !== undefined && v !== "")
    .map(([k, v]) => `${getLabel(k)}: ${v}`)
    .join(" | ");
}

/** Check if an output has any meaningful content. */
function hasContent(content: Record<string, unknown>): boolean {
  return Object.values(content).some((v) => {
    if (v === null || v === undefined || v === "" || v === 0) return false;
    if (Array.isArray(v)) return v.length > 0;
    if (typeof v === "object") {
      return Object.values(v as Record<string, unknown>).some(
        (inner) => inner !== null && inner !== undefined && inner !== "",
      );
    }
    return true;
  });
}

/** Render a text string that may contain markdown-like formatting. */
function FormattedText({ text }: { text: string }) {
  // Split by newlines, render bold (**text**) and list items (- item)
  const lines = text.split("\n");
  return (
    <div className="space-y-1 text-sm leading-relaxed text-foreground">
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={i} className="h-2" />;

        // List item
        if (trimmed.startsWith("- ") || trimmed.startsWith("* ") || /^\d+\.\s/.test(trimmed)) {
          const content = trimmed.replace(/^[-*]\s|^\d+\.\s/, "");
          return (
            <div key={i} className="flex gap-2 pl-2">
              <span className="text-muted-foreground">•</span>
              <span dangerouslySetInnerHTML={{ __html: boldify(content) }} />
            </div>
          );
        }

        return (
          <p key={i} dangerouslySetInnerHTML={{ __html: boldify(trimmed) }} />
        );
      })}
    </div>
  );
}

/** Convert **bold** markers to <strong> tags. */
function boldify(text: string): string {
  return text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

/** Convert structured output content to markdown string. */
function contentToMarkdown(content: Record<string, unknown>, outputType: string): string {
  const lines: string[] = [];
  const title = OUTPUT_LABELS[outputType]?.label || outputType;
  lines.push(`# ${title}\n`);

  for (const [key, value] of Object.entries(content)) {
    if (value === null || value === undefined || value === "" || value === 0) continue;

    const label = getLabel(key);

    if (Array.isArray(value)) {
      if (value.length === 0) continue;
      lines.push(`## ${label}\n`);
      for (const item of value) {
        if (typeof item === "object" && item !== null) {
          lines.push(`- ${dictToText(item as Record<string, unknown>)}`);
        } else {
          lines.push(`- ${String(item)}`);
        }
      }
      lines.push("");
    } else if (typeof value === "object" && value !== null) {
      lines.push(`## ${label}\n`);
      lines.push(dictToText(value as Record<string, unknown>));
      lines.push("");
    } else {
      lines.push(`## ${label}\n`);
      lines.push(String(value));
      lines.push("");
    }
  }

  return lines.join("\n");
}

/** Render markdown-like content as formatted HTML. */
function RenderedContent({
  content,
  outputType,
}: {
  content: Record<string, unknown>;
  outputType: string;
}) {
  const sections: Array<{ label: string; items: string[] | null; text: string | null }> = [];

  for (const [key, value] of Object.entries(content)) {
    if (value === null || value === undefined || value === "" || value === 0) continue;

    const label = getLabel(key);

    if (Array.isArray(value) && value.length > 0) {
      const items = value.map((item) =>
        typeof item === "object" && item !== null
          ? dictToText(item as Record<string, unknown>)
          : String(item),
      );
      sections.push({ label, items, text: null });
    } else if (typeof value === "object" && value !== null) {
      sections.push({ label, items: null, text: dictToText(value as Record<string, unknown>) });
    } else {
      sections.push({ label, items: null, text: String(value) });
    }
  }

  return (
    <div className="space-y-4">
      {sections.map((section, i) => (
        <div key={i}>
          <h4 className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-primary/70">
            {section.label}
          </h4>
          {section.items ? (
            <ul className="space-y-1 pl-4">
              {section.items.map((item, j) => (
                <li
                  key={j}
                  className="list-disc text-sm leading-relaxed text-foreground marker:text-muted-foreground"
                >
                  <span dangerouslySetInnerHTML={{ __html: boldify(item) }} />
                </li>
              ))}
            </ul>
          ) : section.text && section.text.includes("\n") ? (
            <FormattedText text={section.text} />
          ) : (
            <p className="text-sm leading-relaxed text-foreground">
              {section.text}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

export function MeetingOutputsPanel({ projectId, meetingId, token }: MeetingOutputsProps) {
  const [outputs, setOutputs] = useState<MeetingOutput[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    fetchMeetingOutputs(projectId, meetingId, token)
      .then((res) => setOutputs(res.data as unknown as MeetingOutput[]))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [projectId, meetingId, token]);

  const handleCopy = useCallback(async (output: MeetingOutput) => {
    const md = contentToMarkdown(output.content, output.type);
    await navigator.clipboard.writeText(md);
    setCopiedId(output.id);
    setTimeout(() => setCopiedId(null), 2000);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">Cargando resultados...</p>
      </div>
    );
  }

  // Filter out outputs with no meaningful content
  const validOutputs = outputs.filter((o) => hasContent(o.content));

  if (validOutputs.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">
          Los resultados se generan automáticamente al finalizar la reunión.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2 p-3">
      {validOutputs.map((output) => {
        const config = OUTPUT_LABELS[output.type] || {
          label: output.type,
          icon: "📄",
        };
        const isExpanded = expandedId === output.id;
        const isCopied = copiedId === output.id;

        return (
          <div
            key={output.id}
            className="rounded-lg border border-border/30 bg-surface/40"
          >
            {/* Header */}
            <div className="flex items-center">
              <button
                className="flex flex-1 items-center gap-2 px-3 py-2.5 text-left transition-colors hover:bg-surface-hover"
                onClick={() => setExpandedId(isExpanded ? null : output.id)}
              >
                <span className="text-sm">{config.icon}</span>
                <span className="flex-1 text-sm font-medium text-foreground">
                  {config.label}
                </span>
                <span className="text-[10px] text-muted-foreground">
                  {new Date(output.created_at).toLocaleTimeString("es", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </button>
              {/* Copy button */}
              <button
                className="shrink-0 px-3 py-2.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
                onClick={() => handleCopy(output)}
                title="Copiar como markdown"
              >
                {isCopied ? "✓ Copiado" : "Copiar"}
              </button>
            </div>

            {/* Expanded content */}
            {isExpanded && (
              <div className="border-t border-border/20 px-4 py-4">
                <RenderedContent
                  content={output.content}
                  outputType={output.type}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
