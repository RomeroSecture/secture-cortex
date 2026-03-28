/** WebSocket message types matching backend protocol. */

export interface WsMessage {
  type: string;
  payload: Record<string, unknown>;
  timestamp?: string;
}

export interface AudioChunkMessage extends WsMessage {
  type: "audio_chunk";
  payload: {
    channel: "mic" | "tab";
    audio: string; // base64
  };
}

export interface TranscriptionMessage extends WsMessage {
  type: "transcription";
  payload: {
    speaker: string;
    text: string;
    is_final: boolean;
    timestamp: string;
  };
}

export interface InsightMessage extends WsMessage {
  type: "insight";
  payload: {
    type: "alert" | "scope" | "suggestion";
    summary?: string;
    content: string;
    confidence: number;
    sources: string[];
    agent_source?: string;
    subtype?: string;
    target_roles?: string[];
  };
}

export interface RoleInsightMessage extends WsMessage {
  type: "role_insight";
  payload: {
    agent_source: string;
    type: string;
    subtype: string;
    summary: string;
    content: string;
    confidence: number;
    sources: string[];
    target_roles: string[];
  };
}

export interface ConversationEventMessage extends WsMessage {
  type: "conversation_event";
  payload: {
    event_type: string;
    content: Record<string, unknown>;
    speaker?: string;
    timestamp: string;
  };
}

export interface SentimentUpdateMessage extends WsMessage {
  type: "sentiment_update";
  payload: {
    topic: string;
    sentiment: "positive" | "neutral" | "negative";
    score: number;
    timestamp: string;
  };
}

export interface MeetingOutputMessage extends WsMessage {
  type: "meeting_output";
  payload: {
    output_type: string;
    content: Record<string, unknown>;
  };
}

export interface MeetingStatusMessage extends WsMessage {
  type: "meeting_status";
  payload: {
    status: "recording" | "ended";
  };
}

export interface ErrorMessage extends WsMessage {
  type: "error";
  payload: {
    code: string;
    message: string;
  };
}
