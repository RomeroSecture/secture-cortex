"""Authentication endpoints: register, login, profile, admin."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.repositories.user import create_user, get_all_users, get_user_by_email
from app.schemas.user import (
    AuthResponse,
    TokenResponse,
    UserDetailResponse,
    UserListResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Register a new user with email, name and password."""
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    hashed = hash_password(payload.password)
    user = await create_user(db, email=payload.email, name=payload.name, hashed_password=hashed)
    await db.commit()
    token = create_access_token(subject=str(user.id), role=user.role.value)
    logger.info("user_registered", user_id=str(user.id), email=user.email)
    return AuthResponse(
        data=TokenResponse(access_token=token),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Authenticate with email and password, receive JWT token."""
    user = await get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(subject=str(user.id), role=user.role.value)
    logger.info("user_logged_in", user_id=str(user.id), email=user.email)
    return AuthResponse(
        data=TokenResponse(access_token=token),
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserDetailResponse)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserDetailResponse:
    """Get current user profile."""
    return UserDetailResponse(data=UserResponse.model_validate(current_user))


@router.patch("/me", response_model=UserDetailResponse)
async def update_profile(
    payload: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserDetailResponse:
    """Update current user profile (role)."""
    if payload.role:
        current_user.role = UserRole(payload.role)
    await db.commit()
    await db.refresh(current_user)
    logger.info("user_profile_updated", user_id=str(current_user.id), role=payload.role)
    return UserDetailResponse(data=UserResponse.model_validate(current_user))


@router.get("/users", response_model=UserListResponse)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserListResponse:
    """List all users in the system (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    users = await get_all_users(db)
    return UserListResponse(
        data=[UserResponse.model_validate(u) for u in users]
    )
