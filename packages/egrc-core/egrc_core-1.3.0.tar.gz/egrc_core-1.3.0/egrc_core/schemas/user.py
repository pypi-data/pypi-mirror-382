from ..core.types import TenantMixin


"""
User schemas for EGRC Platform.

This module provides Pydantic schemas for user-related operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field, validator

from .base import BaseSchema, IDMixin, TimestampMixin


class UserBase(BaseSchema):
    """Base schema for user data."""

    email: EmailStr = Field(description="User email address")
    first_name: str = Field(description="User first name")
    last_name: str = Field(description="User last name")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_verified: bool = Field(
        default=False, description="Whether user email is verified"
    )
    roles: list[str] = Field(default_factory=list, description="User roles")
    permissions: list[str] = Field(default_factory=list, description="User permissions")

    @validator("first_name", "last_name")
    def validate_names(cls, v):
        """Validate name fields."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(description="User password")
    confirm_password: str = Field(description="Password confirmation")

    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @validator("confirm_password")
    def validate_confirm_password(cls, v, values):
        """Validate password confirmation."""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    email: EmailStr | None = Field(default=None, description="User email address")
    first_name: str | None = Field(default=None, description="User first name")
    last_name: str | None = Field(default=None, description="User last name")
    is_active: bool | None = Field(default=None, description="Whether user is active")
    is_verified: bool | None = Field(
        default=None, description="Whether user email is verified"
    )
    roles: list[str] | None = Field(default=None, description="User roles")
    permissions: list[str] | None = Field(default=None, description="User permissions")
    password: str | None = Field(default=None, description="New password")

    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if v is not None and len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserResponse(UserBase, IDMixin, TimestampMixin, TenantMixin):
    """Schema for user responses."""

    last_login: datetime | None = Field(
        default=None, description="Last login timestamp"
    )
    login_count: int = Field(default=0, description="Number of logins")
    failed_login_attempts: int = Field(
        default=0, description="Number of failed login attempts"
    )
    locked_until: datetime | None = Field(
        default=None, description="Account lock expiration time"
    )

    class Config:
        from_attributes = True


class UserLogin(BaseSchema):
    """Schema for user login."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")
    remember_me: bool = Field(default=False, description="Whether to remember the user")


class UserLoginResponse(BaseSchema):
    """Schema for login response."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")
    user: UserResponse = Field(description="User information")


class UserPasswordReset(BaseSchema):
    """Schema for password reset request."""

    email: EmailStr = Field(description="User email address")


class UserPasswordResetConfirm(BaseSchema):
    """Schema for password reset confirmation."""

    token: str = Field(description="Password reset token")
    password: str = Field(description="New password")
    confirm_password: str = Field(description="Password confirmation")

    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @validator("confirm_password")
    def validate_confirm_password(cls, v, values):
        """Validate password confirmation."""
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserProfile(BaseSchema):
    """Schema for user profile."""

    user_id: UUID = Field(description="User ID")
    avatar_url: str | None = Field(default=None, description="Avatar URL")
    bio: str | None = Field(default=None, description="User biography")
    phone: str | None = Field(default=None, description="Phone number")
    timezone: str | None = Field(default="UTC", description="User timezone")
    language: str | None = Field(default="en", description="User language preference")
    preferences: dict | None = Field(
        default_factory=dict, description="User preferences"
    )
