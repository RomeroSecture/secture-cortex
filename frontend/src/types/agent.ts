/** Types for the multi-agent pipeline and conversation intelligence. */

export interface AgentInsightPayload {
  agent_source: string;
  type: string;
  subtype: string;
  summary: string;
  content: string;
  confidence: number;
  sources: string[];
  target_roles: string[];
}

export interface ConversationEvent {
  id: string;
  meeting_id: string;
  type: "decision" | "action_item" | "question" | "commitment" | "contradiction" | "drift";
  content: Record<string, unknown>;
  resolved: boolean;
  detected_at: string;
}

export interface SentimentPoint {
  topic: string | null;
  sentiment: "positive" | "neutral" | "negative";
  score: number;
  timestamp: string;
}

export interface MeetingKPIs {
  total_insights: number;
  insights_by_type: Record<string, number>;
  total_transcription_segments: number;
  total_decisions: number;
  total_action_items: number;
  total_questions_pending: number;
  total_commitments: number;
  speaker_counts: Record<string, number>;
}
