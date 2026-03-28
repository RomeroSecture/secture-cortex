"use client";

interface TrackedEvent {
  id: string;
  type: string;
  summary: string;
  detail: string;
  timestamp: string;
}

interface ConversationTrackerProps {
  events: TrackedEvent[];
}

const EVENT_ICONS: Record<string, string> = {
  decision_detected: "⚡",
  action_item: "✓",
  question_pending: "?",
  commitment_detected: "🤝",
  jargon_translation: "💬",
  momentum_alert: "🔄",
};

const EVENT_COLORS: Record<string, string> = {
  decision_detected: "border-l-cortex-alert",
  action_item: "border-l-cortex-scope",
  question_pending: "border-l-cortex-suggestion",
  commitment_detected: "border-l-primary",
  jargon_translation: "border-l-muted-foreground",
  momentum_alert: "border-l-destructive",
};

function formatTime(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString("es", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

export function ConversationTracker({ events }: ConversationTrackerProps) {
  if (events.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center px-4">
        <p className="text-center text-xs text-muted-foreground">
          Las decisiones, tareas y preguntas aparecerán aquí
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-1 overflow-y-auto px-2 pb-2">
      {events.map((event) => (
        <div
          key={event.id}
          className={`rounded border-l-2 bg-surface/40 px-2.5 py-1.5 ${
            EVENT_COLORS[event.type] || "border-l-border"
          }`}
        >
          <div className="flex items-start gap-1.5">
            <span className="text-xs">
              {EVENT_ICONS[event.type] || "•"}
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-foreground leading-snug">
                {event.summary}
              </p>
              {event.detail && (
                <p className="mt-0.5 text-[10px] text-muted-foreground leading-tight">
                  {event.detail}
                </p>
              )}
            </div>
            <span className="shrink-0 text-[9px] tabular-nums text-muted-foreground">
              {formatTime(event.timestamp)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
