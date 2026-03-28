"use client";

import { Mic, MicOff, Square } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AudioControlsProps {
  isCapturing: boolean;
  hasMic: boolean;
  hasTab: boolean;
  onStart: () => void;
  onStop: () => void;
  error: string | null;
}

export function AudioControls({
  isCapturing,
  hasMic,
  hasTab,
  onStart,
  onStop,
  error,
}: AudioControlsProps) {
  return (
    <div className="flex items-center gap-3">
      {/* Recording toggle */}
      {!isCapturing ? (
        <Button
          onClick={onStart}
          size="sm"
          className="h-8 gap-2 rounded-full bg-muted text-foreground hover:bg-muted/80 px-4 text-xs"
        >
          <Mic className="h-3.5 w-3.5" />
          Iniciar
        </Button>
      ) : (
        <Button
          onClick={onStop}
          size="sm"
          className="h-8 gap-2 rounded-full bg-destructive/15 text-destructive hover:bg-destructive/25 px-4 text-xs animate-pulse-recording"
        >
          <Square className="h-3 w-3" />
          Detener
        </Button>
      )}

      {/* Status indicators */}
      <div className="flex items-center gap-3">
        {hasMic && (
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            <span className="text-[10px] text-muted-foreground">Mic</span>
          </span>
        )}
        {hasTab && (
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
            <span className="text-[10px] text-muted-foreground">Tab</span>
          </span>
        )}
        {!isCapturing && !error && (
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <MicOff className="h-3 w-3" />
            <span className="text-[10px]">Sin captura</span>
          </span>
        )}
      </div>

      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
