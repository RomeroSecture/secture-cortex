"""Admin endpoints: system stats, user management, global project view."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.context_file import ContextFile
from app.models.insight import Insight
from app.models.meeting import Meeting
from app.models.project import Project, ProjectUser
from app.models.user import User, UserRole
from app.repositories.user import get_user_by_id
from app.schemas.user import UserResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["admin"])


# --- Schemas ---


class SystemStats(BaseModel):
    """System-wide statistics."""

    total_users: int
    total_projects: int
    total_meetings: int
    total_insights: int
    total_context_files: int
    users_by_role: dict[str, int]


class SystemStatsResponse(BaseModel):
    """Wrapped response for system stats."""

    data: SystemStats


class AdminUserResponse(BaseModel):
    """User with project count for admin view."""

    id: uuid.UUID
    email: str
    name: str
    role: str
    projects_count: int

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    """Wrapped response for admin user list."""

    data: list[AdminUserResponse]


class AdminProjectResponse(BaseModel):
    """Project with member count for admin view."""

    id: uuid.UUID
    name: str
    description: str | None
    member_count: int
    meeting_count: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class AdminProjectListResponse(BaseModel):
    """Wrapped response for admin project list."""

    data: list[AdminProjectResponse]


class RoleUpdate(BaseModel):
    """Request schema for changing a user's role."""

    role: str = Field(pattern=r"^(admin|tech_lead|developer|pm|commercial)$")


# --- Helpers ---


def _require_admin(user: User) -> None:
    """Raise 403 if user is not an admin."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


# --- Endpoints ---


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SystemStatsResponse:
    """Get system-wide statistics. Admin only."""
    _require_admin(current_user)

    users_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    projects_count = (await db.execute(select(func.count(Project.id)))).scalar() or 0
    meetings_count = (await db.execute(select(func.count(Meeting.id)))).scalar() or 0
    insights_count = (await db.execute(select(func.count(Insight.id)))).scalar() or 0
    files_count = (await db.execute(select(func.count(ContextFile.id)))).scalar() or 0

    role_rows = await db.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    )
    users_by_role = {row[0].value: row[1] for row in role_rows}

    return SystemStatsResponse(
        data=SystemStats(
            total_users=users_count,
            total_projects=projects_count,
            total_meetings=meetings_count,
            total_insights=insights_count,
            total_context_files=files_count,
            users_by_role=users_by_role,
        )
    )


@router.get("/users", response_model=AdminUserListResponse)
async def list_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AdminUserListResponse:
    """List all users with project counts. Admin only."""
    _require_admin(current_user)

    stmt = (
        select(
            User.id,
            User.email,
            User.name,
            User.role,
            func.count(ProjectUser.id).label("projects_count"),
        )
        .outerjoin(ProjectUser, ProjectUser.user_id == User.id)
        .group_by(User.id)
        .order_by(User.created_at.desc())
    )
    rows = await db.execute(stmt)

    data = [
        AdminUserResponse(
            id=row.id,
            email=row.email,
            name=row.name,
            role=row.role.value,
            projects_count=row.projects_count,
        )
        for row in rows
    ]
    return AdminUserListResponse(data=data)


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: uuid.UUID,
    payload: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Change any user's role. Admin only."""
    _require_admin(current_user)

    target = await get_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role via admin endpoint",
        )

    target.role = UserRole(payload.role)
    await db.commit()
    await db.refresh(target)

    logger.info(
        "admin_role_changed",
        admin_id=str(current_user.id),
        target_id=str(target.id),
        new_role=payload.role,
    )
    return UserResponse.model_validate(target)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a user. Admin only. Cannot delete yourself."""
    _require_admin(current_user)

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    target = await get_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(target)
    await db.commit()

    logger.info(
        "admin_user_deleted",
        admin_id=str(current_user.id),
        deleted_id=str(user_id),
        deleted_email=target.email,
    )


@router.get("/projects", response_model=AdminProjectListResponse)
async def list_all_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AdminProjectListResponse:
    """List all projects with member and meeting counts. Admin only."""
    _require_admin(current_user)

    member_sub = (
        select(
            ProjectUser.project_id,
            func.count(ProjectUser.id).label("member_count"),
        )
        .group_by(ProjectUser.project_id)
        .subquery()
    )

    meeting_sub = (
        select(
            Meeting.project_id,
            func.count(Meeting.id).label("meeting_count"),
        )
        .group_by(Meeting.project_id)
        .subquery()
    )

    stmt = (
        select(
            Project.id,
            Project.name,
            Project.description,
            Project.created_at,
            func.coalesce(member_sub.c.member_count, 0).label("member_count"),
            func.coalesce(meeting_sub.c.meeting_count, 0).label("meeting_count"),
        )
        .outerjoin(member_sub, member_sub.c.project_id == Project.id)
        .outerjoin(meeting_sub, meeting_sub.c.project_id == Project.id)
        .order_by(Project.created_at.desc())
    )
    rows = await db.execute(stmt)

    data = [
        AdminProjectResponse(
            id=row.id,
            name=row.name,
            description=row.description,
            member_count=row.member_count,
            meeting_count=row.meeting_count,
            created_at=row.created_at.isoformat() if row.created_at else "",
        )
        for row in rows
    ]
    return AdminProjectListResponse(data=data)
