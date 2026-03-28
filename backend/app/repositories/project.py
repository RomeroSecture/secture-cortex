"""Database operations for Project and ProjectUser models."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectRole, ProjectUser


async def create_project(db: AsyncSession, *, name: str, description: str | None) -> Project:
    """Create a new project."""
    project = Project(name=name, description=description)
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


async def add_project_member(
    db: AsyncSession,
    *,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    role: ProjectRole,
) -> ProjectUser:
    """Add a user to a project with a specific role."""
    membership = ProjectUser(project_id=project_id, user_id=user_id, role_in_project=role)
    db.add(membership)
    await db.flush()
    return membership


async def get_projects_for_user(db: AsyncSession, user_id: uuid.UUID) -> list[Project]:
    """Get all projects a user is a member of."""
    result = await db.execute(
        select(Project)
        .join(ProjectUser, ProjectUser.project_id == Project.id)
        .where(ProjectUser.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


async def get_project_by_id(db: AsyncSession, project_id: uuid.UUID) -> Project | None:
    """Get a project by ID."""
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.members))
        .where(Project.id == project_id)
    )
    return result.scalar_one_or_none()


async def get_user_project_role(
    db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID
) -> ProjectRole | None:
    """Check if a user is a member of a project and return their role."""
    result = await db.execute(
        select(ProjectUser.role_in_project)
        .where(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_project_members(db: AsyncSession, project_id: uuid.UUID) -> list[ProjectUser]:
    """Get all members of a project with user info."""
    result = await db.execute(
        select(ProjectUser)
        .options(selectinload(ProjectUser.user))
        .where(ProjectUser.project_id == project_id)
    )
    return list(result.scalars().all())


async def delete_project(db: AsyncSession, project: Project) -> None:
    """Delete a project and all associated data (cascade)."""
    await db.delete(project)
    await db.flush()
