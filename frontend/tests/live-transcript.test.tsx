import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { LiveTranscript } from "@/components/transcription/live-transcript";
import type { TranscriptionSegment } from "@/types/meeting";

const segments: TranscriptionSegment[] = [
  { id: "1", speaker: "Speaker 0", text: "Queremos cambiar las notificaciones", is_final: true, timestamp: "2026-03-27T10:00:00Z" },
  { id: "2", speaker: "Speaker 1", text: "Eso requiere migrar el dispatcher", is_final: true, timestamp: "2026-03-27T10:00:05Z" },
  { id: "3", speaker: "Speaker 0", text: "Hmm...", is_final: false, timestamp: "2026-03-27T10:00:10Z" },
];

describe("LiveTranscript", () => {
  it("renders all segments", () => {
    render(<LiveTranscript segments={segments} />);
    expect(screen.getByText("Queremos cambiar las notificaciones")).toBeInTheDocument();
    expect(screen.getByText("Eso requiere migrar el dispatcher")).toBeInTheDocument();
  });

  it("shows speaker labels", () => {
    render(<LiveTranscript segments={segments} />);
    expect(screen.getAllByText("Speaker 0:")).toHaveLength(2);
    expect(screen.getByText("Speaker 1:")).toBeInTheDocument();
  });

  it("shows waiting message when no segments", () => {
    render(<LiveTranscript segments={[]} />);
    expect(screen.getByText("Waiting for transcription...")).toBeInTheDocument();
  });

  it("applies reduced opacity to non-final segments", () => {
    const { container } = render(<LiveTranscript segments={segments} />);
    const nonFinal = container.querySelectorAll(".opacity-60");
    expect(nonFinal.length).toBeGreaterThan(0);
  });
});
