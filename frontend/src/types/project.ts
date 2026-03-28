/** Centralized project, context file, member, meeting, and insight types. */

export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContextFile {
  id: string;
  project_id: string;
  filename: string;
  file_size: number;
  file_type: string;
  content_type: string;
  status: "pending" | "indexing" | "indexed" | "error";
  created_at: string;
  updated_at: string;
}

export interface Member {
  user_id: string;
  email: string;
  name: string;
  role_in_project: string;
}

export interface MeetingItem {
  id: string;
  project_id: string;
  title: string;
  status: "recording" | "ended";
  started_at: string;
  ended_at: string | null;
  created_at: string;
}

export interface MeetingFull {
  meeting_id: string;
  title: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  transcription: TranscriptionSegment[];
  insight_count: number;
}

export interface TranscriptionSegment {
  id: string;
  speaker: string;
  text: string;
  is_final: boolean;
  timestamp: string;
}

export interface InsightItem {
  id: string;
  meeting_id: string;
  type: "alert" | "scope" | "suggestion";
  content: string;
  confidence: number;
  sources: string[];
  agent_source?: string;
  target_roles?: string[];
  insight_subtype?: string;
  created_at: string;
}

export type MeetingOutputType =
  | "minutes"
  | "handoff"
  | "sprint_impact"
  | "email_draft"
  | "briefing"
  | "retrospective";

export interface MeetingOutput {
  id: string;
  meeting_id: string;
  type: MeetingOutputType;
  content: Record<string, unknown>;
  created_at: string;
}

export type UserRole = "admin" | "tech_lead" | "developer" | "pm" | "commercial";

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: UserRole;
}

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: string;
  projects_count: number;
}
