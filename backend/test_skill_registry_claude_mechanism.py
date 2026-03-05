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


if __name__ == "__main__":
    unittest.main()
