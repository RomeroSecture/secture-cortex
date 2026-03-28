"""Pydantic v2 schemas for meeting management."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MeetingCreate(BaseModel):
    """Request schema for starting a meeting."""

    title: str = Field(min_length=1, max_length=500, default="Untitled Meeting")


class MeetingUpdate(BaseModel):
    """Request schema for updating a meeting."""

    title: str = Field(min_length=1, max_length=500)


class MeetingResponse(BaseModel):
    """Response schema for a meeting."""

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingDetailResponse(BaseModel):
    """Response wrapper for a single meeting."""

    data: MeetingResponse


class MeetingListResponse(BaseModel):
    """Response wrapper for meeting list."""

    data: list[MeetingResponse]
