/** API client for Secture Cortex backend. */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function apiUrl(path: string): string {
  return `${API_URL}${path}`;
}

export function wsUrl(path: string): string {
  return `${WS_URL}${path}`;
}

interface FetchOptions extends RequestInit {
  token?: string;
}

export async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, headers: customHeaders, ...rest } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((customHeaders as Record<string, string>) || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(apiUrl(path), { headers, ...rest });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const message = body?.error?.message || body?.detail || `HTTP ${response.status}`;
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

// ─── Epic 7 API helpers ───────────────────────────────────────

/** Fetch post-meeting outputs for a meeting. */
export function fetchMeetingOutputs(projectId: string, meetingId: string, token: string) {
  return apiFetch<{ data: Array<{ id: string; type: string; content: Record<string, unknown>; created_at: string }> }>(
    `/api/v1/projects/${projectId}/meetings/${meetingId}/outputs`,
    { token },
  );
}

/** Fetch conversation events for a meeting. */
export function fetchConversationEvents(projectId: string, meetingId: string, token: string) {
  return apiFetch<{ data: Array<{ id: string; type: string; content: Record<string, unknown>; resolved: boolean; detected_at: string }> }>(
    `/api/v1/projects/${projectId}/meetings/${meetingId}/events`,
    { token },
  );
}

/** Fetch meeting KPIs. */
export function fetchMeetingKPIs(projectId: string, meetingId: string, token: string) {
  return apiFetch<{ data: { total_insights: number; insights_by_type: Record<string, number>; total_decisions: number; total_action_items: number; total_questions_pending: number; speaker_counts: Record<string, number> } }>(
    `/api/v1/projects/${projectId}/meetings/${meetingId}/analytics/kpis`,
    { token },
  );
}

/** Fetch project analytics (health, freshness, gaps, KB report). */
export function fetchProjectAnalytics(projectId: string, token: string) {
  return apiFetch<{ health: { score: number; trend: string; factors: Record<string, number> }; freshness: Array<{ file_id: string; filename: string; age_days: number; status: string }>; gaps: Array<{ type: string; message: string; severity: string }>; kb_report: { total_chunks: number; file_chunks: number; meeting_chunks: number; coverage_ratio: number } }>(
    `/api/v1/projects/${projectId}/analytics`,
    { token },
  );
}
