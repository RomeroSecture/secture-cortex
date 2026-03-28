import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { InsightCard, type InsightData } from "@/components/insights/insight-card";

const alertInsight: InsightData = {
  id: "1",
  type: "alert",
  content: "NotificationDispatcher requires migration to v3 API",
  confidence: 0.92,
  sources: ["architecture.md chunk 3"],
};

const scopeInsight: InsightData = {
  id: "2",
  type: "scope",
  content: "Feature classified as scope actual — requires effort estimation",
  confidence: 0.85,
  sources: [],
};

const suggestionInsight: InsightData = {
  id: "3",
  type: "suggestion",
  content: "Consider rate limiting discussed in meeting 3",
  confidence: 0.78,
  sources: ["meeting-3 chunk 1", "meeting-3 chunk 2"],
};

describe("InsightCard", () => {
  it("renders alert insight with correct badge", () => {
    render(<InsightCard insight={alertInsight} />);
    expect(screen.getByText("Alert")).toBeInTheDocument();
    expect(screen.getByText("92%")).toBeInTheDocument();
    expect(screen.getByText(alertInsight.content)).toBeInTheDocument();
  });

  it("renders scope insight with correct badge", () => {
    render(<InsightCard insight={scopeInsight} />);
    expect(screen.getByText("Scope")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
  });

  it("renders suggestion insight with correct badge", () => {
    render(<InsightCard insight={suggestionInsight} />);
    expect(screen.getByText("Suggestion")).toBeInTheDocument();
    expect(screen.getByText(suggestionInsight.content)).toBeInTheDocument();
  });

  it("shows source count when sources exist", () => {
    render(<InsightCard insight={suggestionInsight} />);
    expect(screen.getByText("Sources: 2 context chunks")).toBeInTheDocument();
  });

  it("does not show sources when empty", () => {
    render(<InsightCard insight={scopeInsight} />);
    expect(screen.queryByText(/Sources/)).not.toBeInTheDocument();
  });
});
