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
  it("renders insight content as collapsed summary", () => {
    render(<InsightCard insight={alertInsight} />);
    expect(screen.getByText(alertInsight.content)).toBeInTheDocument();
  });

  it("renders scope insight content", () => {
    render(<InsightCard insight={scopeInsight} />);
    expect(screen.getByText(scopeInsight.content)).toBeInTheDocument();
  });

  it("renders suggestion insight content", () => {
    render(<InsightCard insight={suggestionInsight} />);
    expect(screen.getByText(suggestionInsight.content)).toBeInTheDocument();
  });

  it("renders confidence bar with correct width", () => {
    const { container } = render(<InsightCard insight={alertInsight} />);
    const bar = container.querySelector("[style*='width']");
    expect(bar).toBeInTheDocument();
    expect(bar?.getAttribute("style")).toContain("92%");
  });

  it("does not show sources section when empty", () => {
    render(<InsightCard insight={scopeInsight} />);
    expect(screen.queryByText("Fuentes")).not.toBeInTheDocument();
  });
});
