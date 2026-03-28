"""Project CRUD endpoints."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.project import ProjectRole
from app.models.user import User
from app.repositories.project import (
    add_project_member,
    create_project,
    delete_project,
    get_project_by_id,
    get_project_members,
    get_projects_for_user,
    get_user_project_role,
)
from app.repositories.user import get_user_by_email
from app.schemas.project import (
    MemberAdd,
    MemberListResponse,
    MemberResponse,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
async def create(
    payload: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectDetailResponse:
    """Create a new project. The creator is auto-assigned as admin."""
    project = await create_project(db, name=payload.name, description=payload.description)
    await add_project_member(
        db, project_id=project.id, user_id=current_user.id, role=ProjectRole.ADMIN
    )
    await db.commit()
    await db.refresh(project)
    logger.info("project_created", project_id=str(project.id), user_id=str(current_user.id))
    return ProjectDetailResponse(data=ProjectResponse.model_validate(project))


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectListResponse:
    """List all projects the authenticated user has access to."""
    projects = await get_projects_for_user(db, current_user.id)
    return ProjectListResponse(
        data=[ProjectResponse.model_validate(p) for p in projects]
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectDetailResponse:
    """Get a single project by ID. User must be a member."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    project = await get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectDetailResponse(data=ProjectResponse.model_validate(project))


@router.patch("/{project_id}", response_model=ProjectDetailResponse)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectDetailResponse:
    """Update a project. Only admins can edit."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role != ProjectRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    project = await get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    logger.info("project_updated", project_id=str(project_id))
    return ProjectDetailResponse(data=ProjectResponse.model_validate(project))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a project and all associated data. Only admins can delete."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role != ProjectRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    project = await get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    await delete_project(db, project)
    await db.commit()
    logger.info("project_deleted", project_id=str(project_id), user_id=str(current_user.id))


# --- Membership endpoints ---


@router.post(
    "/{project_id}/members",
    response_model=MemberListResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_member(
    project_id: uuid.UUID,
    payload: MemberAdd,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MemberListResponse:
    """Assign a user to a project with a role. Only admins can assign."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role != ProjectRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    project = await get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    target_user = await get_user_by_email(db, payload.email)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with email '{payload.email}'",
        )
    existing_role = await get_user_project_role(db, project_id, target_user.id)
    if existing_role is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already a member",
        )
    await add_project_member(
        db,
        project_id=project_id,
        user_id=target_user.id,
        role=ProjectRole(payload.role),
    )
    await db.commit()
    logger.info(
        "member_assigned",
        project_id=str(project_id),
        email=payload.email,
        role=payload.role,
    )
    members = await get_project_members(db, project_id)
    return MemberListResponse(
        data=[
            MemberResponse(
                user_id=m.user_id,
                email=m.user.email,
                name=m.user.name,
                role_in_project=m.role_in_project.value,
            )
            for m in members
        ]
    )


@router.get("/{project_id}/members", response_model=MemberListResponse)
async def list_members(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MemberListResponse:
    """List all members of a project. User must be a member."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    members = await get_project_members(db, project_id)
    return MemberListResponse(
        data=[
            MemberResponse(
                user_id=m.user_id,
                email=m.user.email,
                name=m.user.name,
                role_in_project=m.role_in_project.value,
            )
            for m in members
        ]
    )
