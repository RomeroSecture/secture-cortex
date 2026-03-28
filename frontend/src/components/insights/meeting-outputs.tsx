"use client";

import { useEffect, useState } from "react";
import type { MeetingOutput } from "@/types/project";
import { fetchMeetingOutputs } from "@/lib/api";

interface MeetingOutputsProps {
  projectId: string;
  meetingId: string;
  token: string;
}

const OUTPUT_LABELS: Record<string, { label: string; icon: string }> = {
  minutes: { label: "Acta de Reunion", icon: "📋" },
  handoff: { label: "Paquete Handoff", icon: "📦" },
  sprint_impact: { label: "Impacto Sprint", icon: "🎯" },
  email_draft: { label: "Borrador Email", icon: "✉️" },
  briefing: { label: "Briefing Interno", icon: "📄" },
  retrospective: { label: "Retrospectiva", icon: "📊" },
};

function renderContent(content: Record<string, unknown>): React.ReactNode {
  return Object.entries(content).map(([key, value]) => {
    if (value === null || value === undefined || value === "") return null;

    const label = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

    if (Array.isArray(value)) {
      if (value.length === 0) return null;
      return (
        <div key={key} className="mb-3">
          <h4 className="mb-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            {label}
          </h4>
          <ul className="space-y-1">
            {value.map((item, i) => (
              <li key={i} className="text-sm text-foreground">
                {typeof item === "object" ? JSON.stringify(item) : String(item)}
              </li>
            ))}
          </ul>
        </div>
      );
    }

    if (typeof value === "object") {
      return (
        <div key={key} className="mb-3">
          <h4 className="mb-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            {label}
          </h4>
          <pre className="rounded bg-muted/30 p-2 text-xs text-foreground whitespace-pre-wrap">
            {JSON.stringify(value, null, 2)}
          </pre>
        </div>
      );
    }

    return (
      <div key={key} className="mb-3">
        <h4 className="mb-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {label}
        </h4>
        <p className="text-sm text-foreground">{String(value)}</p>
      </div>
    );
  });
}

export function MeetingOutputsPanel({ projectId, meetingId, token }: MeetingOutputsProps) {
  const [outputs, setOutputs] = useState<MeetingOutput[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetchMeetingOutputs(projectId, meetingId, token)
      .then((res) => setOutputs(res.data as unknown as MeetingOutput[]))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [projectId, meetingId, token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">Cargando outputs...</p>
      </div>
    );
  }

  if (outputs.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-sm text-muted-foreground">
          Los outputs post-reunion se generan automaticamente al finalizar.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2 p-3">
      {outputs.map((output) => {
        const config = OUTPUT_LABELS[output.type] || {
          label: output.type,
          icon: "📄",
        };
        const isExpanded = expandedId === output.id;

        return (
          <div
            key={output.id}
            className="rounded-lg border border-border/30 bg-surface/40"
          >
            <button
              className="flex w-full items-center gap-2 px-3 py-2.5 text-left hover:bg-surface-hover transition-colors"
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
            {isExpanded && (
              <div className="border-t border-border/20 px-3 py-3">
                {renderContent(output.content)}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
