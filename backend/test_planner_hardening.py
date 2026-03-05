import unittest

from core.planner import LLMPlanner


class PlannerHardeningTests(unittest.IsolatedAsyncioTestCase):
    async def test_normalize_invalid_action_and_unknown_skill(self):
        planner = LLMPlanner()
        normalized = planner._normalize_plan(
            {
                "skill": "non-existing-skill",
                "action": "../../x",
                "input": "bad-input",
                "reason": "raw",
            },
            "hello",
        )

        self.assertEqual(normalized["skill"], "none")
        self.assertEqual(normalized["action"], "")
        self.assertEqual(normalized["input"]["user_input"], "hello")
        self.assertIn("unknown skill", normalized["reason"])


if __name__ == "__main__":
    unittest.main()
