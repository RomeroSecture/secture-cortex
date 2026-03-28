"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";

interface MeetingHeaderProps {
  title: string;
  status: "recording" | "ended";
  startedAt: string;
  isWsConnected: boolean;
  onRename?: (newTitle: string) => void;
  projectId?: string;
}

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function MeetingHeader({ title, status, startedAt, isWsConnected, onRename, projectId }: MeetingHeaderProps) {
  const [elapsed, setElapsed] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (status !== "recording") return;
    const start = new Date(startedAt).getTime();
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [status, startedAt]);

  useEffect(() => {
    setEditValue(title);
  }, [title]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const commitRename = () => {
    setIsEditing(false);
    const trimmed = editValue.trim();
    if (trimmed && trimmed !== title && onRename) {
      onRename(trimmed);
    } else {
      setEditValue(title);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      commitRename();
    } else if (e.key === "Escape") {
      setIsEditing(false);
      setEditValue(title);
    }
  };

  return (
    <div className="flex h-12 items-center justify-between px-4">
      <div className="flex items-center gap-3 min-w-0">
        {/* Back link */}
        {projectId && (
          <>
            <Link
              href={`/projects/${projectId}`}
              className="shrink-0 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              &larr;
            </Link>
            <div className="h-4 w-px bg-border shrink-0" />
          </>
        )}

        {/* Editable title */}
        {isEditing ? (
          <input
            ref={inputRef}
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onBlur={commitRename}
            onKeyDown={handleKeyDown}
            className="min-w-0 bg-transparent text-sm font-medium border-b border-primary outline-none text-foreground"
          />
        ) : (
          <span
            className={`truncate text-sm font-medium text-foreground ${
              onRename ? "cursor-pointer hover:underline decoration-muted-foreground/30 underline-offset-4" : ""
            }`}
            onClick={() => onRename && setIsEditing(true)}
            title={onRename ? "Click para renombrar" : undefined}
          >
            {title}
          </span>
        )}

        {/* Status pill */}
        {status === "recording" ? (
          <span className="flex shrink-0 items-center gap-1.5 rounded-full bg-destructive/10 px-2 py-0.5">
            <span className="h-1.5 w-1.5 rounded-full bg-destructive animate-pulse-recording" />
            <span className="text-[10px] font-medium text-destructive">REC</span>
          </span>
        ) : (
          <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
            FIN
          </span>
        )}

        {/* Duration */}
        {status === "recording" && (
          <span className="shrink-0 font-mono text-xs text-muted-foreground">
            {formatDuration(elapsed)}
          </span>
        )}
      </div>

      {/* Connection indicator */}
      <div className="flex shrink-0 items-center gap-1.5">
        <span
          className={`h-1.5 w-1.5 rounded-full ${isWsConnected ? "bg-emerald-400" : "bg-destructive"}`}
        />
        <span className="text-[10px] text-muted-foreground">
          {isWsConnected ? "Conectado" : "Desconectado"}
        </span>
      </div>
    </div>
  );
}
