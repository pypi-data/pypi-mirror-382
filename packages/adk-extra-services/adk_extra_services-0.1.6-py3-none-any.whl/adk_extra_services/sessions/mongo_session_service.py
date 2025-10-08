"""MongoDB session service implementation for Google ADK."""

import copy
import time
import uuid
from typing import Any, Optional

import motor.motor_asyncio
from google.adk.events.event import Event
from google.adk.sessions.base_session_service import (
    BaseSessionService,
    GetSessionConfig,
    ListSessionsResponse,
)
from google.adk.sessions.session import Session
from google.adk.sessions.state import State


class MongoSessionService(BaseSessionService):

    def __init__(self, mongo_url: str, db_name: Optional[str] = None, **kwargs: Any):
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url, **kwargs)
        self.db = client[db_name] if db_name else client.get_default_database()
        self.sessions = self.db.sessions
        self.events = self.db.events
        self.app_states = self.db.app_states
        self.user_states = self.db.user_states

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        sid = session_id or uuid.uuid4().hex
        now = time.time()
        session_state = state or {}

        await self.sessions.insert_one(
            {
                "app_name": app_name,
                "user_id": user_id,
                "id": sid,
                "state": session_state,
                "last_update_time": now,
            }
        )

        session = Session(
            id=sid,
            app_name=app_name,
            user_id=user_id,
            state=session_state,
            events=[],
            last_update_time=now,
        )
        return await self._merge_state(app_name, user_id, copy.deepcopy(session))

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        filt = {"app_name": app_name, "user_id": user_id, "id": session_id}
        doc = await self.sessions.find_one(filt)
        if not doc:
            return None

        # Get all events for this session
        raw_events = (
            await self.events.find(filt).sort("timestamp", 1).to_list(length=None)
        )
        events = [Event.model_validate_json(e["raw"]) for e in raw_events]

        # Apply config filters if provided
        if config:
            if config.after_timestamp is not None:
                events = [e for e in events if e.timestamp >= config.after_timestamp]
            if config.num_recent_events is not None and events:
                events = events[-config.num_recent_events :]

        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=doc.get("state", {}),
            events=events,
            last_update_time=doc.get("last_update_time", 0.0),
        )

        return await self._merge_state(app_name, user_id, copy.deepcopy(session))

    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        cursor = self.sessions.find({"app_name": app_name, "user_id": user_id})
        sessions: list[Session] = []
        async for doc in cursor:
            sessions.append(
                Session(
                    id=doc["id"],
                    app_name=app_name,
                    user_id=user_id,
                    state={},
                    events=[],
                    last_update_time=doc.get("last_update_time", 0.0),
                )
            )
        return ListSessionsResponse(sessions=sessions)

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        filt = {"app_name": app_name, "user_id": user_id, "id": session_id}
        await self.sessions.delete_one(filt)
        await self.events.delete_many(filt)

    async def _merge_state(
        self, app_name: str, user_id: str, session: Session
    ) -> Session:
        """Merge app and user state into the session."""
        # Merge app state
        app_states = await self.app_states.find({"app_name": app_name}).to_list(
            length=None
        )
        for state in app_states:
            session.state[State.APP_PREFIX + state["key"]] = state["value"]

        # Merge user state
        user_states = await self.user_states.find(
            {"app_name": app_name, "user_id": user_id}
        ).to_list(length=None)
        for state in user_states:
            session.state[State.USER_PREFIX + state["key"]] = state["value"]

        return session

    async def append_event(self, session: Session, event: Event) -> Event:
        if event.partial:
            return event

        filt = {
            "app_name": session.app_name,
            "user_id": session.user_id,
            "id": session.id,
        }
        doc = await self.sessions.find_one(filt)
        if not doc:
            raise ValueError("session not found")

        if doc.get("last_update_time", 0.0) > session.last_update_time:
            raise ValueError("stale session")

        new_event = await super().append_event(session=session, event=event)

        # Store the event
        await self.events.insert_one(
            {
                **filt,
                "raw": new_event.model_dump_json(),
                "timestamp": new_event.timestamp,
            }
        )

        # Update session state and timestamp
        await self.sessions.update_one(
            filt,
            {
                "$set": {
                    "state": session.state,
                    "last_update_time": session.last_update_time,
                }
            },
        )

        # Process state deltas if present
        if event.actions and event.actions.state_delta:
            for key, value in event.actions.state_delta.items():
                if key.startswith(State.APP_PREFIX):
                    # Update app state
                    app_key = key.removeprefix(State.APP_PREFIX)
                    await self.app_states.update_one(
                        {"app_name": session.app_name, "key": app_key},
                        {"$set": {"value": value}},
                        upsert=True,
                    )

                elif key.startswith(State.USER_PREFIX):
                    # Update user state
                    user_key = key.removeprefix(State.USER_PREFIX)
                    await self.user_states.update_one(
                        {
                            "app_name": session.app_name,
                            "user_id": session.user_id,
                            "key": user_key,
                        },
                        {"$set": {"value": value}},
                        upsert=True,
                    )

        return new_event
