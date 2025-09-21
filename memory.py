from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone
from agents.items import TResponseInputItem
from agents.memory.session import SessionABC
from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_engine, get_sessions_engine
from models import User, UserProfile, UserSession, UserMeasurement


class UserAwareSession(SessionABC):
    """Session wrapper that composes SQLAlchemySession for items and manages users/profiles.

    Responsibilities:
    - Ensure a User exists for a given external_user_id
    - Optionally ensure a UserProfile exists and can be updated
    - Ensure a UserSession row exists binding the user to the session_id
    - Delegate message storage to Agents' SQLAlchemySession
    """

    def __init__(
        self,
        external_user_id: str,
        session_id: str,
        engine: Optional[AsyncEngine] = None,
        create_tables: bool = True,
        label: Optional[str] = None,
    ) -> None:
        self.external_user_id = external_user_id
        self.session_id = session_id
        self.engine = engine or get_async_engine()
        sessions_engine = get_sessions_engine()
        # Delegate that stores/loads conversation items
        self._delegate = SQLAlchemySession(
            session_id=session_id,
            engine=sessions_engine,
            create_tables=create_tables,
        )
        self._session_factory = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        self._label = label

    # ---- User/profile/session helpers ----
    async def ensure_user_and_session(
        self,
        display_name: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> User:
        async with self._session_factory() as db:
            # Upsert user by external_id
            result = await db.execute(select(User).where(User.external_id == self.external_user_id))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(external_id=self.external_user_id)
                db.add(user)
                await db.flush()  # get user.id

            # Ensure profile exists (explicit query to avoid async lazy load)
            if display_name or timezone:
                prof_res = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
                profile = prof_res.scalar_one_or_none()
                if profile is None:
                    profile = UserProfile(
                        user_id=user.id,
                        display_name=display_name,
                        timezone=timezone,
                    )
                    db.add(profile)
                else:
                    if display_name is not None:
                        profile.display_name = display_name
                    if timezone is not None:
                        profile.timezone = timezone

            # Ensure mapping to session exists
            result = await db.execute(
                select(UserSession).where(
                    UserSession.user_id == user.id, UserSession.session_id == self.session_id
                )
            )
            mapping = result.scalar_one_or_none()
            if mapping is None:
                mapping = UserSession(user_id=user.id, session_id=self.session_id, label=self._label)
                db.add(mapping)

            await db.commit()
            return user

    # ---- SessionABC delegation for items ----
    async def get_items(self, limit: int | None = None) -> List[TResponseInputItem]:
        return await self._delegate.get_items(limit=limit)

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        await self._delegate.add_items(items)

    async def pop_item(self) -> TResponseInputItem | None:
        return await self._delegate.pop_item()

    async def clear_session(self) -> None:
        await self._delegate.clear_session()

    # ---- Factories ----
    @classmethod
    def for_user(
        cls,
        external_user_id: str,
        session_id: str,
        *,
        engine: Optional[AsyncEngine] = None,
        label: Optional[str] = None,
        create_tables: bool = True,
        display_name: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> "UserAwareSession":
        instance = cls(
            external_user_id=external_user_id,
            session_id=session_id,
            engine=engine,
            create_tables=create_tables,
            label=label,
        )
        # Kick off an ensure step but don't await here; caller can await via pre_run hook
        # Provide a helper for explicit initialization
        instance._initial_profile = {"display_name": display_name, "timezone": timezone}
        return instance

    async def init_user(self) -> User:
        """Call during app startup or before first run to ensure user/profile/session rows exist."""
        info = getattr(self, "_initial_profile", {}) or {}
        return await self.ensure_user_and_session(
            display_name=info.get("display_name"), timezone=info.get("timezone")
        )

    # ---- Measurements helpers ----
    async def add_measurement(
        self,
        *,
        height_cm: Optional[int] = None,
        weight_kg: Optional[float] = None,
        measured_at: Optional[datetime] = None,
        note: Optional[str] = None,
    ) -> UserMeasurement:
        """Record a new height/weight measurement for the current user.

        Either value can be omitted to record just one of them.
        """
        if height_cm is None and weight_kg is None:
            raise ValueError("Provide at least one of height_cm or weight_kg")
        user = await self.ensure_user_and_session()
        async with self._session_factory() as db:
            measurement = UserMeasurement(
                user_id=user.id,
                measured_at=measured_at or datetime.now(timezone.utc),
                height_cm=height_cm,
                weight_kg=weight_kg,
                note=note,
            )
            db.add(measurement)
            await db.commit()
            await db.refresh(measurement)
            return measurement

    async def get_measurements(self, *, limit: int = 50) -> List[UserMeasurement]:
        """Fetch recent measurements for the current user, newest first."""
        user = await self.ensure_user_and_session()
        async with self._session_factory() as db:
            result = await db.execute(
                select(UserMeasurement)
                .where(UserMeasurement.user_id == user.id)
                .order_by(UserMeasurement.measured_at.desc())
                .limit(limit)
            )
            return list(result.scalars())
