import os
import tempfile
import unittest

from core.executor import CapabilityExecutor
from core.response_renderer import StructuredResponseRenderer
from capability_orchestration.registry import SkillRegistry


class OrchestrationLayerTests(unittest.IsolatedAsyncioTestCase):
    async def test_executor_script_route_and_renderer(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = os.path.join(tmp, "demo")
            scripts_dir = os.path.join(skill_dir, "scripts")
            os.makedirs(scripts_dir)

            with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("""---
name: demo
description: demo skill
---
body
""")

            with open(os.path.join(scripts_dir, "process.py"), "w", encoding="utf-8") as f:
                f.write("import sys\nprint(sys.stdin.read())\n")

            registry = SkillRegistry()
            registry.discover_skills(tmp)

            import capability_orchestration
            capability_orchestration.skill_registry = registry
            import core.executor as executor_module
            executor_module.skill_registry = registry

            executor = CapabilityExecutor()
            execution = await executor.execute(
                session_id="s1",
                plan={"skill": "demo", "action": "process", "input": {"user_input": "hello"}},
                context={},
            )
            self.assertTrue(execution["success"])

            renderer = StructuredResponseRenderer()
            response = renderer.render(plan={"skill": "demo"}, execution=execution)
            self.assertEqual(response["type"], "json")
            self.assertIn("content", response)


if __name__ == "__main__":
    unittest.main()
