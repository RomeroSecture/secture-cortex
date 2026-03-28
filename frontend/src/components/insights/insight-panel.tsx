"use client";

import { InsightCard, type InsightData } from "./insight-card";

interface InsightPanelProps {
  insights: InsightData[];
  isRecording?: boolean;
  onFeedback?: (insightId: string, rating: "useful" | "not_useful" | "dismissed") => void;
}

export function InsightPanel({ insights, isRecording, onFeedback }: InsightPanelProps) {
  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-foreground">Copiloto IA</span>
          {isRecording && (
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse-recording" />
          )}
        </div>
        {insights.length > 0 && (
          <span className="text-[10px] text-muted-foreground">
            {insights.length}
          </span>
        )}
      </div>

      {/* Content */}
      {insights.length === 0 ? (
        <div className="flex flex-1 items-center justify-center px-6">
          <p className="text-center text-sm text-muted-foreground leading-relaxed">
            Escuchando... Los insights apareceran cuando detecte algo relevante
          </p>
        </div>
      ) : (
        <div className="flex-1 space-y-2 overflow-y-auto px-3 pb-3">
          {insights.map((insight) => (
            <InsightCard
              key={insight.id}
              insight={insight}
              onFeedback={onFeedback}
            />
          ))}
        </div>
      )}
    </div>
  );
}
