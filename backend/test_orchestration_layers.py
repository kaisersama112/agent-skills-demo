import unittest

from core.chat_orchestrator import ChatOrchestrator
from core.response_renderer import StructuredResponseRenderer
from test_fakes import FakePlanner, FakeExecutor


class OrchestrationLayersTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_orchestrator_pipeline_connected(self):
        orchestrator = ChatOrchestrator()
        orchestrator.planner = FakePlanner()
        orchestrator.executor = FakeExecutor()

        result = await orchestrator.handle_message("s1", "合并两个pdf")

        self.assertEqual(result["type"], "json")
        self.assertEqual(result["content"]["status"], "success")
        self.assertEqual(result["content"]["plan"]["skill"], "pdf")
        self.assertEqual(result["content"]["execution"]["script"], "scripts/merge.py")

    def test_response_renderer_error_shape(self):
        renderer = StructuredResponseRenderer()
        plan = {"skill": "none", "action": "", "input": {}, "reason": "test"}
        execution = {"status": "error", "message": "未匹配到可执行技能", "error_code": "missing_skill"}

        result = renderer.render("hi", plan, execution)
        self.assertEqual(result["type"], "json")
        self.assertEqual(result["content"]["status"], "error")
        self.assertEqual(result["content"]["error_code"], "missing_skill")
        self.assertIn("plan", result["content"])
        self.assertIn("execution", result["content"])


if __name__ == "__main__":
    unittest.main()
