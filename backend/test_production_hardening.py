import asyncio
import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import api.chat as chat_api
from core.executor import CapabilityExecutor
from core.chat_orchestrator import chat_orchestrator
from main import app
from models.database import Base


class _FakePlanner:
    async def plan(self, user_input: str):
        return {
            "skill": "pdf",
            "action": "merge",
            "input": {"user_input": user_input},
            "reason": "integration-test",
        }


class _FakeExecutor:
    async def execute(self, session_id: str, plan, context):
        return {
            "status": "success",
            "skill": "pdf",
            "action": "merge",
            "script": "scripts/merge.py",
            "returncode": 0,
        }


class ProductionHardeningTests(unittest.TestCase):
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

    def test_send_message_idempotency_cache_hit(self):
        params = {
            "session_id": "s-idem-1",
            "message": "hello",
            "idempotency_key": "req-1",
        }
        first = self.client.post("/chat/sendMessage", params=params)
        second = self.client.post("/chat/sendMessage", params=params)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertFalse(first.json()["idempotency"]["hit"])
        self.assertTrue(second.json()["idempotency"]["hit"])


    def test_idempotency_cache_eviction(self):
        original_size = chat_api.settings.idempotency_cache_size
        chat_api.settings.idempotency_cache_size = 2
        chat_api._IDEMPOTENCY_CACHE.clear()
        try:
            self.client.post("/chat/sendMessage", params={"session_id": "s-evict", "message": "m1", "idempotency_key": "k1"})
            self.client.post("/chat/sendMessage", params={"session_id": "s-evict", "message": "m2", "idempotency_key": "k2"})
            self.client.post("/chat/sendMessage", params={"session_id": "s-evict", "message": "m3", "idempotency_key": "k3"})
            self.assertEqual(len(chat_api._IDEMPOTENCY_CACHE), 2)
            self.assertNotIn(("s-evict", "k1"), chat_api._IDEMPOTENCY_CACHE)
        finally:
            chat_api.settings.idempotency_cache_size = original_size
            chat_api._IDEMPOTENCY_CACHE.clear()

    def test_trace_header_roundtrip(self):
        resp = self.client.get("/health", headers={"X-Trace-Id": "trace-test-1"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("X-Trace-Id"), "trace-test-1")


class ExecutorRetryTests(unittest.TestCase):
    def test_retry_on_script_timeout(self):
        executor = CapabilityExecutor()
        calls = {"count": 0}

        def fake_execute(skill_name, payload):
            calls["count"] += 1
            if calls["count"] == 1:
                return {"status": "error", "error_code": "script_timeout"}
            return {"status": "success", "error_code": "", "skill": skill_name}

        with patch("core.executor.skill_registry.execute_skill_action", side_effect=fake_execute):
            result = asyncio.run(
                executor.execute(
                    session_id="s1",
                    plan={"skill": "pdf", "action": "merge", "input": {"user_input": "x"}},
                    context={"trace_id": "t1"},
                )
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(calls["count"], 2)


if __name__ == "__main__":
    unittest.main()
