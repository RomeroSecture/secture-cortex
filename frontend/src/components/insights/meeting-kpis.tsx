"use client";

import type { MeetingKPIs } from "@/types/agent";

interface MeetingKPIsProps {
  kpis: MeetingKPIs;
}

function KpiCard({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className="flex flex-col items-center gap-0.5 rounded-md bg-surface/50 px-2.5 py-1.5">
      <span className={`text-lg font-semibold tabular-nums ${color || "text-foreground"}`}>
        {value}
      </span>
      <span className="text-[9px] uppercase tracking-wider text-muted-foreground">{label}</span>
    </div>
  );
}

export function MeetingKPIsBar({ kpis }: MeetingKPIsProps) {
  const speakers = Object.keys(kpis.speaker_counts).length;
  const topSpeaker = Object.entries(kpis.speaker_counts).sort((a, b) => b[1] - a[1])[0];

  return (
    <div className="flex items-center gap-2 overflow-x-auto px-3 py-1.5">
      <KpiCard label="Insights" value={kpis.total_insights} color="text-primary" />
      <KpiCard label="Decisiones" value={kpis.total_decisions} color="text-cortex-alert" />
      <KpiCard label="Action Items" value={kpis.total_action_items} color="text-cortex-scope" />
      <KpiCard label="Preguntas" value={kpis.total_questions_pending} color="text-cortex-suggestion" />
      <KpiCard label="Speakers" value={speakers} />
      {topSpeaker && (
        <div className="ml-auto flex items-center gap-1 text-[10px] text-muted-foreground">
          <span>Más activo:</span>
          <span className="font-medium text-foreground">{topSpeaker[0]}</span>
          <span>({topSpeaker[1]} seg.)</span>
        </div>
      )}
    </div>
  );
}
