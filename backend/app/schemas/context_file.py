"""Pydantic v2 schemas for context file upload and management."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContextFileResponse(BaseModel):
    """Response schema for a context file."""

    id: uuid.UUID
    project_id: uuid.UUID
    filename: str
    file_size: int
    content_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContextFileListResponse(BaseModel):
    """Response wrapper for file list."""

    data: list[ContextFileResponse]


class ContextFileDetailResponse(BaseModel):
    """Response wrapper for single file."""

    data: ContextFileResponse
