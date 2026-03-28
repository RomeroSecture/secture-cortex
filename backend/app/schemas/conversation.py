"""Pydantic v2 schemas for conversation intelligence detection."""

from pydantic import BaseModel, Field


class DetectedDecision(BaseModel):
    """A decision detected in the conversation."""

    description: str = Field(description="What was decided")
    speaker: str = Field(default="", description="Who made/announced it")
    context: str = Field(default="", description="Surrounding context")


class DetectedActionItem(BaseModel):
    """An action item extracted from the conversation."""

    task: str = Field(description="Task description")
    owner: str = Field(default="", description="Who is responsible")
    deadline: str = Field(default="sin fecha", description="Deadline if mentioned")


class DetectedQuestion(BaseModel):
    """A question detected in the conversation."""

    question: str = Field(description="The question asked")
    speaker: str = Field(default="", description="Who asked")


class SentimentDetection(BaseModel):
    """Sentiment detected for a topic segment."""

    topic: str = Field(default="general")
    sentiment: str = Field(description="positive, neutral, or negative")
    score: float = Field(ge=-1.0, le=1.0, default=0.0)


class ConversationIntelOutput(BaseModel):
    """Structured output from the conversation intelligence node.

    A single LLM call detects all patterns simultaneously.
    """

    decision: DetectedDecision | None = None
    action_item: DetectedActionItem | None = None
    question: DetectedQuestion | None = None
    topic_label: str = Field(default="general", description="Current topic")
    sentiment: SentimentDetection | None = None
    momentum_keyword: str = Field(
        default="",
        description="Repeated keyword if momentum detected",
    )
    jargon_detected: str = Field(
        default="",
        description="Technical term with business translation",
    )
