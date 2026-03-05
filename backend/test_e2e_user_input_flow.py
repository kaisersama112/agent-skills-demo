import os
import tempfile
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import api.chat as chat_api
from core.chat_orchestrator import chat_orchestrator
from main import app
from models.database import Base


class _FakePlanner:
    async def plan(self, user_input: str):
        return {
            "skill": "pdf",
            "action": "merge",
            "input": {"user_input": user_input, "files": ["a.pdf", "b.pdf"]},
            "reason": "integration-test",
        }


class _FakeExecutor:
    async def execute(self, session_id: str, plan, context):
        return {
            "status": "success",
            "skill": plan["skill"],
            "action": plan["action"],
            "script": "scripts/merge.py",
            "returncode": 0,
            "stdout": "ok",
            "stderr": "",
        }


class EndToEndUserInputFlowTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        db_path = os.path.join(self._tmp.name, "test.db")
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        self.TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        def override_get_db():
            db = self.TestSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[chat_api.get_db] = override_get_db

        # patch orchestrator internals so test starts at HTTP user input but avoids network/script side effects
        self._orig_planner = chat_orchestrator.planner
        self._orig_executor = chat_orchestrator.executor
        chat_orchestrator.planner = _FakePlanner()
        chat_orchestrator.executor = _FakeExecutor()

        self.client = TestClient(app)

    def tearDown(self):
        chat_orchestrator.planner = self._orig_planner
        chat_orchestrator.executor = self._orig_executor
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self._tmp.cleanup()

    def test_send_message_end_to_end_from_user_input(self):
        response = self.client.post(
            "/chat/sendMessage",
            params={"session_id": "s-e2e-1", "message": "请帮我合并两个pdf"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["type"], "json")
        self.assertEqual(payload["data"]["content"]["status"], "success")
        self.assertEqual(payload["data"]["content"]["plan"]["skill"], "pdf")
        self.assertEqual(payload["data"]["content"]["execution"]["script"], "scripts/merge.py")

        # verify history endpoint sees persisted user/system messages
        history_resp = self.client.post(
            "/chat/queryHistoryChatContent.json",
            params={"session_id": "s-e2e-1"},
        )
        self.assertEqual(history_resp.status_code, 200)
        history = history_resp.json()["data"]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["sender"], "user")
        self.assertEqual(history[1]["sender"], "system")


if __name__ == "__main__":
    unittest.main()
