"""Pydantic v2 schemas for the multi-agent LangGraph pipeline."""

import operator
from typing import Annotated, TypedDict

from pydantic import BaseModel, Field


class AgentInsight(BaseModel):
    """Output from a specialist agent."""

    agent_source: str = Field(
        description="tech_lead, pm, commercial, dev, supervisor, conversation",
    )
    type: str = Field(
        description="alert, scope, suggestion, dependency_alert, etc.",
    )
    subtype: str = Field(default="", description="Specific insight subtype for filtering")
    summary: str = Field(default="", max_length=100, description="Max 15 words preview")
    content: str = Field(default="", description="Full explanation, max 3 sentences")
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    sources: list[str] = Field(default_factory=list)
    target_roles: list[str] = Field(
        default_factory=lambda: ["admin", "tech_lead", "developer", "pm", "commercial"],
        description="Which roles should see this insight",
    )
    metadata: dict = Field(default_factory=dict, description="Agent-specific metadata")

    def to_ws_message(self) -> dict:
        """Convert to WebSocket message format."""
        return {
            "type": "role_insight",
            "payload": {
                "agent_source": self.agent_source,
                "type": self.type,
                "subtype": self.subtype,
                "summary": self.summary,
                "content": self.content,
                "confidence": self.confidence,
                "sources": self.sources,
                "target_roles": self.target_roles,
            },
        }

    def to_legacy_insight(self) -> dict:
        """Convert to legacy insight format for backward compatibility."""
        legacy_type = self.type
        if legacy_type not in ("alert", "scope", "suggestion"):
            legacy_type = "suggestion"
        return {
            "type": legacy_type,
            "summary": self.summary,
            "content": self.content,
            "confidence": self.confidence,
            "sources": self.sources,
            "agent_source": self.agent_source,
            "subtype": self.subtype,
        }


class SupervisorDecision(BaseModel):
    """Structured output from the Supervisor node."""

    active_agents: list[str] = Field(
        description="Which agents to activate: tech_lead, pm, commercial, dev",
    )
    reasoning: str = Field(default="", description="Why these agents were selected")
    topic_classification: str = Field(default="general", description="Detected topic category")


class PipelineState(TypedDict):
    """State shared across all nodes in the LangGraph pipeline."""

    # Input (set by caller)
    transcription_chunk: str
    context_chunks: list[str]
    meeting_id: str
    project_id: str
    connected_roles: list[str]

    # Supervisor decision
    active_agents: list[str]

    # Accumulated by agents (reducer: merge lists)
    agent_insights: Annotated[list[AgentInsight], operator.add]

    # Final filtered insights (set by synthesizer, no reducer)
    final_insights: list[AgentInsight]

    # Meeting-level iteration tracking
    iteration_count: int

    # Feedback context for prompt tuning
    feedback_context: str

    # Previous insights for deduplication
    previous_insights: list[str]
