# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import copy
from datetime import datetime
from typing import Any, Optional

from google.adk.sessions.base_session_service import (
    BaseSessionService,
    GetSessionConfig,
    ListSessionsResponse,
)
from google.adk.sessions.session import Session
from google.adk.sessions.state import State
from pymongo import MongoClient

from .mongodb_session import MongodbSession


def _extract_state_delta(state: dict[str, Any]):
    app_state_delta = {}
    user_state_delta = {}
    session_state_delta = {}
    if state:
        for key in state.keys():
            if key.startswith(State.APP_PREFIX):
                app_state_delta[key.removeprefix(State.APP_PREFIX)] = state[key]
            elif key.startswith(State.USER_PREFIX):
                user_state_delta[key.removeprefix(State.USER_PREFIX)] = state[key]
            elif not key.startswith(State.TEMP_PREFIX):
                session_state_delta[key] = state[key]
    return app_state_delta, user_state_delta, session_state_delta


def _merge_state(app_state, user_state, session_state):
    merged_state = copy.deepcopy(session_state)
    for key in app_state.keys():
        merged_state[State.APP_PREFIX + key] = app_state[key]
    for key in user_state.keys():
        merged_state[State.USER_PREFIX + key] = user_state[key]
    return merged_state


class MongodbSessionService(BaseSessionService):
    def __init__(self, db_url: str, database: str, collection_prefix: str):
        self.client = MongoClient(db_url)
        self.db = self.client[database]
        self.sessions_collection = self.db[f"{collection_prefix}_sessions"]
        self.app_states_collection = self.db[f"{collection_prefix}_app_states"]
        self.user_states_collection = self.db[f"{collection_prefix}_user_states"]

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        app_state_doc = self.app_states_collection.find_one({"_id": app_name})
        user_state_doc = self.user_states_collection.find_one(
            {"_id": f"{app_name}_{user_id}"}
        )

        app_state = app_state_doc.get("state", {}) if app_state_doc else {}
        user_state = user_state_doc.get("state", {}) if user_state_doc else {}

        app_state_delta, user_state_delta, session_state = _extract_state_delta(state)

        if app_state_delta:
            app_state.update(app_state_delta)
            self.app_states_collection.update_one(
                {"_id": app_name}, {"$set": {"state": app_state}}, upsert=True
            )

        if user_state_delta:
            user_state.update(user_state_delta)
            self.user_states_collection.update_one(
                {"_id": f"{app_name}_{user_id}"},
                {"$set": {"state": user_state}},
                upsert=True,
            )

        new_session = MongodbSession(
            app_name=app_name, user_id=user_id, id=session_id
        )

        now = datetime.now()
        session_doc = {
            "_id": new_session.id,
            "app_name": app_name,
            "user_id": user_id,
            "state": session_state,
            "create_time": now,
            "update_time": now,
        }
        self.sessions_collection.insert_one(session_doc)

        merged_state = _merge_state(app_state, user_state, session_state)
        new_session.state = merged_state
        new_session.last_update_time = now.timestamp()
        return new_session

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        session_doc = self.sessions_collection.find_one(
            {"_id": session_id, "app_name": app_name, "user_id": user_id}
        )
        if not session_doc:
            return None

        app_state_doc = self.app_states_collection.find_one({"_id": app_name})
        user_state_doc = self.user_states_collection.find_one(
            {"_id": f"{app_name}_{user_id}"}
        )

        app_state = app_state_doc.get("state", {}) if app_state_doc else {}
        user_state = user_state_doc.get("state", {}) if user_state_doc else {}
        session_state = session_doc.get("state", {})

        merged_state = _merge_state(app_state, user_state, session_state)

        # Event handling is not implemented in this version.
        # The `config` parameter related to events is ignored.

        update_time = session_doc.get("update_time")
        return MongodbSession(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=merged_state,
            last_update_time=update_time.timestamp() if update_time else None,
        )

    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        app_state_doc = self.app_states_collection.find_one({"_id": app_name})
        user_state_doc = self.user_states_collection.find_one(
            {"_id": f"{app_name}_{user_id}"}
        )

        app_state = app_state_doc.get("state", {}) if app_state_doc else {}
        user_state = user_state_doc.get("state", {}) if user_state_doc else {}

        sessions = []
        for session_doc in self.sessions_collection.find(
            {"app_name": app_name, "user_id": user_id}
        ):
            session_state = session_doc.get("state", {})
            merged_state = _merge_state(app_state, user_state, session_state)
            update_time = session_doc.get("update_time")
            sessions.append(
                MongodbSession(
                    app_name=app_name,
                    user_id=user_id,
                    id=session_doc.get("_id"),
                    state=merged_state,
                    last_update_time=update_time.timestamp() if update_time else None,
                )
            )
        return ListSessionsResponse(sessions=sessions)

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        self.sessions_collection.delete_one(
            {"_id": session_id, "app_name": app_name, "user_id": user_id}
        )


    