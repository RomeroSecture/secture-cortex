"use client";

import { useEffect, useRef } from "react";
import type { TranscriptionSegment } from "@/types/meeting";

interface LiveTranscriptProps {
  segments: TranscriptionSegment[];
  preview?: string;
}

const SPEAKER_COLORS: string[] = [
  "slate",
  "emerald",
  "amber",
  "violet",
  "rose",
];

const SPEAKER_BG: Record<string, string> = {
  slate: "bg-slate-400",
  emerald: "bg-emerald-400",
  amber: "bg-amber-400",
  violet: "bg-violet-400",
  rose: "bg-rose-400",
};

const SPEAKER_BORDER: Record<string, string> = {
  slate: "border-l-slate-400",
  emerald: "border-l-emerald-400",
  amber: "border-l-amber-400",
  violet: "border-l-violet-400",
  rose: "border-l-rose-400",
};

const SPEAKER_TEXT: Record<string, string> = {
  slate: "text-slate-400",
  emerald: "text-emerald-400",
  amber: "text-amber-400",
  violet: "text-violet-400",
  rose: "text-rose-400",
};

function getSpeakerColorKey(speaker: string): string {
  // Extract number from "Speaker N" or use hash
  const match = speaker.match(/\d+/);
  const index = match ? parseInt(match[0], 10) : speaker.length;
  return SPEAKER_COLORS[index % SPEAKER_COLORS.length];
}

function getSpeakerInitial(speaker: string): string {
  // "Speaker 0" -> "S0", "Juan" -> "J"
  const parts = speaker.split(" ");
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return speaker[0].toUpperCase();
}

interface GroupedMessages {
  speaker: string;
  segments: TranscriptionSegment[];
}

function groupBySpeaker(segments: TranscriptionSegment[]): GroupedMessages[] {
  const groups: GroupedMessages[] = [];
  for (const seg of segments) {
    if (!seg.is_final) continue;
    const last = groups[groups.length - 1];
    if (last && last.speaker === seg.speaker) {
      last.segments.push(seg);
    } else {
      groups.push({ speaker: seg.speaker, segments: [seg] });
    }
  }
  return groups;
}

export function LiveTranscript({ segments, preview }: LiveTranscriptProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const userScrolledRef = useRef(false);

  // Auto-scroll to bottom unless user has scrolled up
  useEffect(() => {
    const el = containerRef.current;
    if (!el || userScrolledRef.current) return;
    el.scrollTop = el.scrollHeight;
  }, [segments, preview]);

  const handleScroll = () => {
    const el = containerRef.current;
    if (!el) return;
    const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 50;
    userScrolledRef.current = !isAtBottom;
  };

  if (segments.length === 0 && !preview) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        <p className="text-sm">Esperando transcripcion...</p>
      </div>
    );
  }

  const groups = groupBySpeaker(segments);

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 space-y-3 overflow-y-auto p-4"
    >
      {groups.map((group, groupIdx) => {
        const colorKey = getSpeakerColorKey(group.speaker);
        const initial = getSpeakerInitial(group.speaker);

        return (
          <div key={groupIdx} className="flex items-start gap-3 animate-fade-in-up">
            {/* Avatar */}
            <div
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[10px] font-medium text-background ${SPEAKER_BG[colorKey]}`}
            >
              {initial}
            </div>

            {/* Messages */}
            <div className="min-w-0 flex-1">
              <p className={`mb-1 text-xs font-medium ${SPEAKER_TEXT[colorKey]}`}>
                {group.speaker}
              </p>
              <div
                className={`rounded-lg border-l-2 bg-surface px-3 py-2 ${SPEAKER_BORDER[colorKey]}`}
              >
                {group.segments.map((seg, segIdx) => (
                  <p key={seg.id} className={`text-sm text-foreground ${segIdx > 0 ? "mt-1" : ""}`}>
                    {seg.text}
                  </p>
                ))}
              </div>
            </div>
          </div>
        );
      })}

      {/* Typing indicator for preview */}
      {preview && (
        <div className="flex items-start gap-3">
          <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-muted text-[10px] font-medium text-muted-foreground">
            ...
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1 rounded-lg bg-surface px-3 py-2">
              <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-typing-dot typing-dot-1" />
              <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-typing-dot typing-dot-2" />
              <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-typing-dot typing-dot-3" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
