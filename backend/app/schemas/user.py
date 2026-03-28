"""Pydantic v2 schemas for user authentication and management."""

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response schema for user data (never expose password)."""

    id: uuid.UUID
    email: str
    name: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Request schema for updating user profile."""

    role: str | None = Field(default=None, pattern=r"^(admin|tech_lead|developer|pm|commercial)$")


class UserDetailResponse(BaseModel):
    """Wrapped response for user profile."""

    data: UserResponse


class UserListResponse(BaseModel):
    """Wrapped response for user list."""

    data: list[UserResponse]


class TokenResponse(BaseModel):
    """Response schema for JWT token."""

    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Response wrapping token + user data."""

    data: TokenResponse
    user: UserResponse
