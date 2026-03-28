/** Types for project-level analytics and multi-meeting intelligence. */

export interface HealthScore {
  score: number;
  trend: "improving" | "stable" | "declining";
  factors: {
    frequency: number;
    sentiment: number;
    engagement: number;
    recency: number;
    meetings_total: number;
    meetings_recent: number;
  };
}

export interface FreshnessItem {
  file_id: string;
  filename: string;
  age_days: number;
  status: "green" | "yellow" | "red";
  last_updated: string;
}

export interface KnowledgeGap {
  type: string;
  message: string;
  severity: "warning" | "critical";
}

export interface KBReport {
  total_chunks: number;
  file_chunks: number;
  meeting_chunks: number;
  total_files: number;
  total_meetings: number;
  coverage_ratio: number;
}

export interface ProjectAnalytics {
  health: HealthScore;
  freshness: FreshnessItem[];
  gaps: KnowledgeGap[];
  kb_report: KBReport;
}
