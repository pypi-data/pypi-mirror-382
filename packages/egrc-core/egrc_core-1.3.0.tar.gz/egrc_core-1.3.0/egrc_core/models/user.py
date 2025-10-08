# """
# User-related SQLAlchemy models for EGRC Platform.

# This module provides SQLAlchemy models for user management
# across all EGRC services.
# """


# class User(BaseModel, TimestampMixin, SoftDeleteMixin, TenantMixin):
#     """
#     User model for EGRC platform.

#         This model represents users in the EGRC system with authentication
#         and authorization information.
#         """
#
#         __tablename__ = "users"
#
#         email = Column(String(255), nullable=False, unique=True, index=True)

#         first_name = Column(String(100), nullable=False)
#
#         last_name = Column(String(100), nullable=False)
#
#         password_hash = Column(String(255), nullable=False)
#
#         is_active = Column(Boolean, default=True, nullable=False, index=True)
#
#         is_verified = Column(Boolean, default=False, nullable=False)
#
#         is_superuser = Column(Boolean, default=False, nullable=False)
#
#         roles = Column(JSON, default=list, nullable=False)
#
#         permissions = Column(JSON, default=list, nullable=False)
#
#         last_login = Column(DateTime(timezone=True), nullable=True)
#
#         login_count = Column(Integer, default=0, nullable=False)
#
#         failed_login_attempts = Column(Integer, default=0, nullable=False)
#
#         locked_until = Column(DateTime(timezone=True), nullable=True)
#
#         password_reset_token = Column(String(255), nullable=True)
#
#         password_reset_expires = Column(DateTime(timezone=True), nullable=True)
#
#         email_verification_token = Column(String(255), nullable=True)
#
#         email_verification_expires = Column(DateTime(timezone=True), nullable=True)
#
#         preferences = Column(JSON, default=dict, nullable=False)
#
#         # Relationships
#         profile = relationship("UserProfile", back_populates="user", uselist=False)
#         sessions = relationship("UserSession", back_populates="user")
#
#         @property
#         def full_name(self) -> str:
#             """Get user's full name."""
#             return f"{self.first_name} {self.last_name}"
#
#         @property
#         def is_locked(self) -> bool:
#             """Check if user account is locked."""
#             return self.locked_until is not None and self.locked_until > datetime.utcnow()
#
#         def lock_account(self, duration_minutes: int = 30) -> None:
#             """
#             Lock user account for specified duration.
#
#             Args:
#                 duration_minutes: Lock duration in minutes
#             """
#             self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
#
#         def unlock_account(self) -> None:
#             """Unlock user account."""
#             self.locked_until = None
#             self.failed_login_attempts = 0
#
#         def increment_login_count(self) -> None:
#             """Increment login count."""
#             self.login_count += 1
#             self.last_login = datetime.utcnow()
#             self.failed_login_attempts = 0
#
#         def increment_failed_login(self) -> None:
#             """Increment failed login attempts."""
#             self.failed_login_attempts += 1
#
#             # Lock account after 5 failed attempts
#             if self.failed_login_attempts >= 5:
#                 self.lock_account()
#
#
#     # class UserProfile(BaseModel, TimestampMixin, TenantMixin):
#         """
#     User profile model for EGRC platform.
#
#     This model stores additional user profile information.
#     """

#         __tablename__ = "user_profiles"
#
#         user_id = Column(
#             UUID(as_uuid=True),
#             ForeignKey("users.id", ondelete="CASCADE"),
#             nullable=False,
#             unique=True,
#             index=True,
#         )
#
#         avatar_url = Column(String(500), nullable=True)
#
#         bio = Column(Text, nullable=True)
#
#         phone = Column(String(20), nullable=True)
#
#         timezone = Column(String(50), default="UTC", nullable=False)
#
#         language = Column(String(10), default="en", nullable=False)
#
#         date_of_birth = Column(DateTime(timezone=True), nullable=True)
#
#         address = Column(JSON, nullable=True)
#
#         social_links = Column(JSON, default=dict, nullable=False)
#
#         preferences = Column(JSON, default=dict, nullable=False)
#
#         # Relationships
#         user = relationship("User", back_populates="profile")
#
#
#     # class UserSession(BaseModel, TimestampMixin, TenantMixin):
#         """
#         User session model for EGRC platform.
#
#         This model tracks user sessions for security and analytics.
#         """
#
#         __tablename__ = "user_sessions"
#
#         user_id = Column(
#             UUID(as_uuid=True),
#             ForeignKey("users.id", ondelete="CASCADE"),
#             nullable=False,
#             index=True,
#         )
#
#         session_token = Column(String(255), nullable=False, unique=True, index=True)
#
#         refresh_token = Column(String(255), nullable=True, unique=True, index=True)
#
#         ip_address = Column(String(45), nullable=True)
#
#         user_agent = Column(Text, nullable=True)
#
#         device_info = Column(JSON, nullable=True)
#
#         location_info = Column(JSON, nullable=True)
#
#         is_active = Column(Boolean, default=True, nullable=False, index=True)
#
#         expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
#
#         last_activity = Column(
#             DateTime(timezone=True), default=datetime.utcnow, nullable=False
#         )
#
#         # Relationships
#         user = relationship("User", back_populates="sessions")
#
#         @property
#         def is_expired(self) -> bool:
#             """Check if session is expired."""
#             return self.expires_at < datetime.utcnow()
#
#         def extend_session(self, duration_hours: int = 24) -> None:
#             """
#             Extend session expiration.
#
#             Args:
#                 duration_hours: Extension duration in hours
#             """
#             self.expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
#             self.last_activity = datetime.utcnow()

#         def deactivate(self) -> None:
#             """Deactivate session."""
#             self.is_active = False
