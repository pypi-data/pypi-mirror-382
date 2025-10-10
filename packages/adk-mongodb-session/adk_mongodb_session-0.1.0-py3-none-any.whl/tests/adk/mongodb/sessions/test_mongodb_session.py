import asyncio
import unittest
from unittest.mock import patch, MagicMock
import mongomock
from src.adk.mongodb.sessions.mongodb_session_service import MongodbSessionService
from google.adk.sessions.state import State


class TestMongodbSessionService(unittest.TestCase):
    def setUp(self):
        self.db_url = "mongodb://localhost:27017/"
        self.database = "test_db"
        self.collection_prefix = "test"
        self.app_name = "test_app"
        self.user_id = "test_user"
        self.session_id = "test_session_id"

    @patch("src.adk.mongodb.sessions.mongodb_session_service.MongoClient", new=mongomock.MongoClient)
    def test_session_lifecycle_with_state_management(self):
        service = MongodbSessionService(
            db_url=self.db_url,
            database=self.database,
            collection_prefix=self.collection_prefix,
        )

        async def run_test():
            # 1. Create a session with tiered state
            initial_state = {
                f"{State.APP_PREFIX}app_key": "app_value",
                f"{State.USER_PREFIX}user_key": "user_value",
                "session_key": "session_value",
            }
            session = await service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id,
                state=initial_state,
            )

            # Verify state is merged in the returned session object
            self.assertEqual(initial_state, session.state)

            # Verify state was split correctly in the database
            app_state_doc = service.app_states_collection.find_one({"_id": self.app_name})
            user_state_doc = service.user_states_collection.find_one({"_id": f"{self.app_name}_{self.user_id}"})
            session_doc = service.sessions_collection.find_one({"_id": self.session_id})

            self.assertEqual({"app_key": "app_value"}, app_state_doc["state"])
            self.assertEqual({"user_key": "user_value"}, user_state_doc["state"])
            self.assertEqual({"session_key": "session_value"}, session_doc["state"])

            # 2. Get the session and verify merged state
            retrieved_session = await service.get_session(
                app_name=self.app_name, user_id=self.user_id, session_id=self.session_id
            )
            self.assertEqual(initial_state, retrieved_session.state)

            # 3. Create another session for the same user
            session2_id = "test_session_2"
            await service.create_session(
                app_name=self.app_name, user_id=self.user_id, session_id=session2_id
            )

            # 4. List sessions and verify merged state in each
            list_response = await service.list_sessions(app_name=self.app_name, user_id=self.user_id)
            self.assertEqual(2, len(list_response.sessions))
            for s in list_response.sessions:
                self.assertEqual(initial_state if s.id == self.session_id else {
                    f"{State.APP_PREFIX}app_key": "app_value",
                    f"{State.USER_PREFIX}user_key": "user_value",
                }, s.state)


            # 5. Delete the session
            await service.delete_session(
                app_name=self.app_name, user_id=self.user_id, session_id=self.session_id
            )
            self.assertIsNone(
                service.sessions_collection.find_one({"_id": self.session_id})
            )

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
