import os
import tempfile
import unittest

from capability_orchestration.registry import SkillRegistry, SkillMetadataParser


class SkillRegistryClaudeMechanismTests(unittest.TestCase):
    def test_parse_yaml_header_and_body(self):
        content = """---
name: pdf
description: Use this skill whenever the user wants PDF.
license: Proprietary
---
# Skill body
Do things.
"""
        parsed = SkillMetadataParser.parse_content_with_body(content)

        self.assertEqual(parsed.metadata.name, "pdf")
        self.assertIn("wants PDF", parsed.metadata.description)
        self.assertEqual(parsed.metadata.license, "Proprietary")
        self.assertIn("Skill body", parsed.body)

    def test_parse_without_frontmatter(self):
        content = "# no yaml\njust body"
        parsed = SkillMetadataParser.parse_content_with_body(content)
        self.assertEqual(parsed.metadata.name, "unknown")
        self.assertEqual(parsed.body, content)

    def test_discover_only_dirs_with_skill_md_and_merge_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            valid_skill = os.path.join(tmp, "pdf")
            invalid_skill = os.path.join(tmp, "not-a-skill")
            os.makedirs(valid_skill)
            os.makedirs(invalid_skill)

            with open(os.path.join(valid_skill, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("""---
name: pdf
description: Use this skill for PDF work.
---
Main body text.
""")

            with open(os.path.join(valid_skill, "forms.md"), "w", encoding="utf-8") as f:
                f.write("Forms guide")

            registry = SkillRegistry()
            registry.discover_skills(tmp)

            self.assertIn("pdf", registry.skill_metadata)
            self.assertEqual(len(registry.skill_metadata), 1)

            prompt_context = registry.get_skill_prompt_context("pdf")
            self.assertIn("Main body text.", prompt_context)
            self.assertIn("forms.md", prompt_context)
            self.assertIn("Forms guide", prompt_context)

            full_prompt = registry.build_skills_prompt()
            self.assertIn("Skill: pdf", full_prompt)
            self.assertIn("Description: Use this skill for PDF work.", full_prompt)

    def test_execute_skill_action_routes_to_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = os.path.join(tmp, "demo")
            scripts_dir = os.path.join(skill_dir, "scripts")
            os.makedirs(scripts_dir)

            with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("""---
name: demo
description: demo
---
body
""")

            with open(os.path.join(scripts_dir, "echo.py"), "w", encoding="utf-8") as f:
                f.write(
                    "import sys\n"
                    "payload = sys.stdin.read()\n"
                    "print(payload)\n"
                )

            registry = SkillRegistry()
            registry.discover_skills(tmp)
            result = registry.execute_skill_action("demo", {"action": "echo", "x": 1})

            self.assertEqual(result["status"], "success")
            self.assertIn('"x": 1', result["stdout"])

    def test_execute_skill_action_rejects_invalid_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = os.path.join(tmp, "demo")
            os.makedirs(skill_dir)

            with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("""---
name: demo
description: demo
---
body
""")

            registry = SkillRegistry()
            registry.discover_skills(tmp)
            result = registry.execute_skill_action("demo", {"action": "../../evil"})

            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error_code"], "invalid_action")

    def test_execute_skill_action_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = os.path.join(tmp, "demo")
            scripts_dir = os.path.join(skill_dir, "scripts")
            os.makedirs(scripts_dir)

            with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("""---
name: demo
description: demo
---
body
""")

            with open(os.path.join(scripts_dir, "slow.py"), "w", encoding="utf-8") as f:
                f.write(
                    "import time\n"
                    "time.sleep(2)\n"
                    "print('done')\n"
                )

            registry = SkillRegistry()
            registry.discover_skills(tmp)
            result = registry.execute_skill_action("demo", {"action": "slow", "timeout_seconds": 1})

            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error_code"], "script_timeout")


if __name__ == "__main__":
    unittest.main()
