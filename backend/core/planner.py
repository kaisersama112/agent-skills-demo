import json
from typing import Any, Dict, Optional

from capability_orchestration import skill_registry
from services.llm_service import llm_service


class LLMPlanner:
    """LLM 决策层：将用户输入规划为 skill/action/input。"""

    async def plan(self, user_input: str) -> Dict[str, Any]:
        skills_prompt = skill_registry.build_skills_prompt()

        prompt = f"""
你是一个技能规划器。请根据用户请求和可用技能，输出一个 JSON 对象。

{skills_prompt}

输出格式（必须是合法 JSON）：
{{
  "skill": "技能名称，若无法匹配填 none",
  "action": "动作名，可为空字符串",
  "input": {{"user_input": "原始用户输入"}},
  "reason": "简短原因"
}}

用户请求：{user_input}
"""

        try:
            response = await llm_service.generate(prompt, temperature=0.0)
            parsed = self._parse_json_block(response)
            if not isinstance(parsed, dict):
                raise ValueError("planner output is not json object")
            return {
                "skill": str(parsed.get("skill", "none")).strip(),
                "action": str(parsed.get("action", "")).strip(),
                "input": parsed.get("input", {"user_input": user_input}),
                "reason": str(parsed.get("reason", "")),
            }
        except Exception:
            return await self._fallback_plan(user_input)

    async def _fallback_plan(self, user_input: str) -> Dict[str, Any]:
        skill = await skill_registry.select_skill_by_llm(user_input)
        return {
            "skill": skill.name if skill else "none",
            "action": "",
            "input": {"user_input": user_input},
            "reason": "fallback skill selection",
        }

    def _parse_json_block(self, text: str) -> Dict[str, Any]:
        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        if text.startswith("json"):
            text = text[4:].strip()

        return json.loads(text)
