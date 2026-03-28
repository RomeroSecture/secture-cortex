"""Pydantic v2 schemas for transcription data."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TranscriptionSegmentResponse(BaseModel):
    """Response schema for a transcription segment."""

    id: uuid.UUID
    speaker: str
    text: str
    is_final: bool
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingDetailFullResponse(BaseModel):
    """Full meeting detail: transcription + insights."""

    meeting_id: uuid.UUID
    title: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    transcription: list[TranscriptionSegmentResponse]
    insight_count: int
