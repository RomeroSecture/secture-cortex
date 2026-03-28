"use client";

import { useState } from "react";
import { ChevronDown, ThumbsDown, ThumbsUp, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

export interface InsightData {
  id: string;
  type: "alert" | "scope" | "suggestion";
  content: string;
  confidence: number;
  sources: string[];
  summary?: string;
  agent_source?: string;
  subtype?: string;
}

const TYPE_CONFIG = {
  alert: {
    label: "Alerta",
    borderColor: "border-l-cortex-alert",
    dotColor: "bg-cortex-alert",
    barColor: "bg-cortex-alert",
  },
  scope: {
    label: "Alcance",
    borderColor: "border-l-cortex-scope",
    dotColor: "bg-cortex-scope",
    barColor: "bg-cortex-scope",
  },
  suggestion: {
    label: "Sugerencia",
    borderColor: "border-l-cortex-suggestion",
    dotColor: "bg-cortex-suggestion",
    barColor: "bg-cortex-suggestion",
  },
};

interface InsightCardProps {
  insight: InsightData;
  onFeedback?: (insightId: string, rating: "useful" | "not_useful" | "dismissed") => void;
}

const AGENT_LABELS: Record<string, string> = {
  tech_lead: "Tech Lead",
  pm: "PM",
  commercial: "Comercial",
  dev: "Dev",
  supervisor: "Supervisor",
  conversation: "Intel",
};

function truncate(text: string, max: number): string {
  if (text.length <= max) return text;
  return text.slice(0, max).trimEnd() + "...";
}

export function InsightCard({ insight, onFeedback }: InsightCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const config = TYPE_CONFIG[insight.type];
  const collapsedText = insight.summary
    ? truncate(insight.summary, 80)
    : truncate(insight.content, 80);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div className={`rounded-lg bg-surface border-l-2 ${config.borderColor} animate-fade-in-up`}>
        <CollapsibleTrigger
          className="flex w-full items-center gap-2 px-3 py-2 text-left transition-colors hover:bg-surface-hover"
        >
          {/* Type dot */}
          <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${config.dotColor}`} />

          {/* Agent badge */}
          {insight.agent_source && (
            <span className="shrink-0 rounded bg-muted px-1 py-0.5 text-[9px] font-medium uppercase tracking-wider text-muted-foreground">
              {AGENT_LABELS[insight.agent_source] || insight.agent_source}
            </span>
          )}

          {/* Summary text */}
          <span className="flex-1 truncate text-sm text-foreground">{collapsedText}</span>

          {/* Confidence bar */}
          <div className="flex shrink-0 items-center gap-1.5">
            <div className="h-1 w-8 rounded-full bg-border overflow-hidden">
              <div
                className={`h-full rounded-full ${config.barColor}`}
                style={{ width: `${Math.round(insight.confidence * 100)}%` }}
              />
            </div>
          </div>

          {/* Chevron */}
          <ChevronDown
            className={`h-3.5 w-3.5 shrink-0 text-muted-foreground transition-transform duration-200 ${
              isOpen ? "rotate-180" : ""
            }`}
          />
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="border-t border-border px-3 pb-3 pt-2">
            <p className="text-sm text-foreground leading-relaxed">{insight.content}</p>

            {insight.sources.length > 0 && (
              <div className="mt-2">
                <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                  Fuentes
                </p>
                <ul className="mt-1 space-y-0.5">
                  {insight.sources.map((source, idx) => (
                    <li key={idx} className="text-xs text-muted-foreground">
                      {source}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {onFeedback && (
              <div className="mt-2 flex gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2 text-muted-foreground hover:text-foreground"
                  onClick={() => onFeedback(insight.id, "useful")}
                  title="Util"
                >
                  <ThumbsUp className="h-3 w-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2 text-muted-foreground hover:text-foreground"
                  onClick={() => onFeedback(insight.id, "not_useful")}
                  title="No util"
                >
                  <ThumbsDown className="h-3 w-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2 text-muted-foreground hover:text-foreground"
                  onClick={() => onFeedback(insight.id, "dismissed")}
                  title="Descartar"
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            )}

            <p className="mt-2 text-[10px] italic text-muted-foreground/60">
              Sugerencia IA — verificar antes de actuar
            </p>
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}
