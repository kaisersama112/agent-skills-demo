import json
from typing import Any, Dict, List

from capability_orchestration import skill_registry


class SkillPlanner:
    """LLM Planner Layer: 负责技能/动作决策。"""

    DEFAULT_ACTIONS = {
        "pdf": "process",
        "pptx": "edit",
        "docx": "comment",
        "xlsx": "recalc",
    }

    def _keyword_match_skill(self, user_input: str) -> str | None:
        lowered = user_input.lower()
        for meta in skill_registry.list_skills():
            name = str(meta.get("name", "")).lower()
            desc = str(meta.get("description", "")).lower()
            if name and name in lowered:
                return meta["name"]
            if any(token for token in lowered.split() if token and token in desc):
                return meta["name"]
        return None

    async def plan(self, user_input: str) -> Dict[str, Any]:
        """返回结构化执行计划。"""
        # 当前实现优先稳定性：先走轻量规则匹配，后续可接入真正 tool-calling planner
        selected_skill = self._keyword_match_skill(user_input)

        if not selected_skill:
            skill = await skill_registry.select_skill_by_llm(user_input)
            selected_skill = skill.name if skill else "chat"

        action = self.DEFAULT_ACTIONS.get(selected_skill)

        return {
            "skill": selected_skill,
            "action": action,
            "operation": action,
            "input": {
                "user_input": user_input,
            },
        }
