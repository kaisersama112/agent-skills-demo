import json
import re
from typing import Any, Dict, List

from capability_orchestration import skill_registry
from capability_orchestration.skill_guide_reader import get_skill_guide_reader
from services.llm_service import llm_service


class LLMPlanner:
    """LLM 决策层：将用户输入规划为 skill/action/input。"""

    ACTION_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")

    async def plan(self, user_input: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        skills_prompt = skill_registry.build_skills_prompt()
        history_prompt = self._build_history_prompt(context.get("history", []))

        # Step 1: Select the appropriate skill
        skill_selection_prompt = f"""
你是一个技能选择器。请根据用户请求，从以下可用技能中选择最合适的一个。

{skills_prompt}

要求：
1. 分析用户输入的意图
2. 从可用技能中选择最匹配的技能
3. 如果没有匹配的技能，返回 "none"
4. 只返回技能名称（与列表中的name字段完全一致），不要返回其他内容

用户请求：{user_input}
{history_prompt}

请选择最合适的技能：
"""

        try:
            # Select skill
            skill_response = await llm_service.generate(skill_selection_prompt, temperature=0.0)
            selected_skill_name = skill_response.strip()

            if selected_skill_name.lower() == "none":
                return {
                    "skill": "none",
                    "action": "",
                    "input": {"user_input": user_input},
                    "reason": "No matching skill found",
                    "task_plan": []
                }

            # Step 2: Get skill guide
            skill_guide_reader = get_skill_guide_reader()
            skill_guide = skill_guide_reader.get_skill_guide(selected_skill_name)
            skill_scripts = skill_guide_reader.get_skill_scripts(selected_skill_name)

            # Step 3: Generate detailed task plan
            print(f"Skill scripts: {skill_scripts}")
            scripts_list = "\n".join(skill_scripts) if skill_scripts else "No scripts available"
            task_plan_prompt = """
你是一个任务规划器。请根据用户请求和技能指南，为 %s 技能生成详细的任务执行计划。

技能指南：
%s

可用脚本：
%s

用户请求：%s

要求：
1. 分析用户需求
2. 参考技能指南中的工作流程和最佳实践
3. 生成详细的任务执行计划，包括每个步骤的具体操作
4. 为每个任务指定合适的脚本（如果适用）- 只能使用上面列出的可用脚本，不能使用文档文件（如pptxgenjs.md）作为脚本
5. 考虑可能的边缘情况和错误处理
6. 对于创建新PPT的任务，由于pptxgenjs.md是文档而非脚本，应该使用实际可用的脚本如thumbnail.py、office/pack.py等
7. 对于文件路径，使用相对路径，如office/soffice.py而不是soffice.py

输出格式（必须是合法 JSON）：
{
  "skill": "%s",
  "action": "主要动作",
  "input": {"user_input": "%s"},
  "reason": "选择此技能的原因",
  "task_plan": [
    {
      "step": 1,
      "description": "步骤描述",
      "script": "脚本名称（如果适用）",
      "parameters": {"参数名": "参数值"},
      "expected_output": "预期输出"
    }
  ]
}
""" % (selected_skill_name, skill_guide or "No guide available", scripts_list, user_input, selected_skill_name, user_input)

            response = await llm_service.generate(task_plan_prompt, temperature=0.0)
            print(f"Task plan response: {response[:500]}...")  # Log first 500 chars
            parsed = self._parse_json_block(response)
            if not isinstance(parsed, dict):
                raise ValueError("planner output is not json object")
            normalized_plan = self._normalize_plan(parsed, user_input)
            print(f"Normalized plan: {normalized_plan}")
            return normalized_plan
        except Exception as e:
            print(f"Error in planning: {e}")
            # Instead of falling back, let's return a plan with the selected skill but empty task plan
            return {
                "skill": selected_skill_name,
                "action": "",
                "input": {"user_input": user_input},
                "reason": f"Error in task planning: {str(e)}",
                "task_plan": []
            }

    def _build_history_prompt(self, history: List[Dict[str, Any]]) -> str:
        if not history:
            return ""

        recent = history[-6:]
        lines = ["最近对话上下文（按时间升序）："]
        for item in recent:
            sender = item.get("sender", "unknown")
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            lines.append(f"- {sender}: {content[:300]}")
        return "\n".join(lines)

    async def _fallback_plan(self, user_input: str) -> Dict[str, Any]:
        skill = await skill_registry.select_skill_by_llm(user_input)
        return {
            "skill": skill.name if skill else "none",
            "action": "",
            "input": {"user_input": user_input},
            "reason": "fallback skill selection",
            "task_plan": []
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

    def _normalize_plan(self, raw: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        skill_name = str(raw.get("skill", "none")).strip() or "none"
        action = str(raw.get("action", "")).strip()
        payload = raw.get("input")
        reason = str(raw.get("reason", "")).strip()
        task_plan = raw.get("task_plan", [])

        if not isinstance(payload, dict):
            payload = {"user_input": user_input}

        payload.setdefault("user_input", user_input)

        if skill_name != "none" and not skill_registry.get_skill_metadata(skill_name):
            skill_name = "none"
            action = ""
            reason = (reason + " | unknown skill downgraded to none").strip(" |")

        if action and not self.ACTION_PATTERN.fullmatch(action):
            action = ""
            reason = (reason + " | invalid action ignored").strip(" |")

        return {
            "skill": skill_name,
            "action": action,
            "input": payload,
            "reason": reason,
            "task_plan": task_plan if isinstance(task_plan, list) else []
        }
