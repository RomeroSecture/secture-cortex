"""Pydantic v2 schemas for project CRUD and membership."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Request schema for creating a project."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    """Request schema for updating a project (partial update)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    """Response schema for a single project."""

    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Response wrapper for project list."""

    data: list[ProjectResponse]


class ProjectDetailResponse(BaseModel):
    """Response wrapper for a single project."""

    data: ProjectResponse


# --- Membership ---


class MemberAdd(BaseModel):
    """Request schema for adding a member to a project by email."""

    email: str = Field(description="Email of the user to add")
    role: str = Field(pattern=r"^(admin|tech_lead|developer|pm|commercial)$")


class MemberResponse(BaseModel):
    """Response schema for a project member."""

    user_id: uuid.UUID
    email: str
    name: str
    role_in_project: str

    model_config = ConfigDict(from_attributes=True)


class MemberListResponse(BaseModel):
    """Response wrapper for member list."""

    data: list[MemberResponse]
