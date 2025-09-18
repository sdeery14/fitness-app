from __future__ import annotations
from datetime import datetime
import uuid
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import String, DateTime, ForeignKey, func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "fa_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # external_id could be an auth provider id or app-level unique string
    external_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)
    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user")


class UserProfile(Base):
    __tablename__ = "fa_user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("fa_users.id", ondelete="CASCADE"), unique=True)

    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    # Add fitness-related profile fields as needed
    height_cm: Mapped[Optional[int]] = mapped_column(nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(nullable=True)

    user: Mapped[User] = relationship(back_populates="profile")


class UserSession(Base):
    __tablename__ = "fa_user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("fa_users.id", ondelete="CASCADE"), index=True)
    # This is the session_id used by the Agents SDK Session implementation
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="sessions")
