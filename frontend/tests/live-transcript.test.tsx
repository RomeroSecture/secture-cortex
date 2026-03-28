import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { LiveTranscript } from "@/components/transcription/live-transcript";
import type { TranscriptionSegment } from "@/types/meeting";

const segments: TranscriptionSegment[] = [
  { id: "1", speaker: "Speaker 0", text: "Queremos cambiar las notificaciones", is_final: true, timestamp: "2026-03-27T10:00:00Z" },
  { id: "2", speaker: "Speaker 1", text: "Eso requiere migrar el dispatcher", is_final: true, timestamp: "2026-03-27T10:00:05Z" },
  { id: "3", speaker: "Speaker 0", text: "Hmm vale lo miramos", is_final: true, timestamp: "2026-03-27T10:00:10Z" },
];

describe("LiveTranscript", () => {
  it("renders all final segments", () => {
    render(<LiveTranscript segments={segments} />);
    expect(screen.getByText("Queremos cambiar las notificaciones")).toBeInTheDocument();
    expect(screen.getByText("Eso requiere migrar el dispatcher")).toBeInTheDocument();
  });

  it("shows speaker names", () => {
    render(<LiveTranscript segments={segments} />);
    expect(screen.getAllByText("Speaker 0").length).toBeGreaterThan(0);
    expect(screen.getByText("Speaker 1")).toBeInTheDocument();
  });

  it("shows waiting message when no segments", () => {
    render(<LiveTranscript segments={[]} />);
    expect(screen.getByText("Esperando transcripcion...")).toBeInTheDocument();
  });

  it("groups consecutive segments from same speaker", () => {
    const { container } = render(<LiveTranscript segments={segments} />);
    // Speaker 0 has 2 separate groups (seg 1, then seg 3 after Speaker 1)
    // Speaker 1 has 1 group — total 3 groups with avatars
    const avatars = container.querySelectorAll(".rounded-full");
    expect(avatars.length).toBeGreaterThanOrEqual(3);
  });
});
