/** Meeting and transcription types. */

export interface Meeting {
  id: string;
  project_id: string;
  title: string;
  status: "recording" | "ended";
  started_at: string;
  ended_at: string | null;
  created_at: string;
}

export interface TranscriptionSegment {
  id: string;
  speaker: string;
  text: string;
  is_final: boolean;
  timestamp: string;
}
