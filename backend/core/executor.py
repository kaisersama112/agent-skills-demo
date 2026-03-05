from typing import Any, Dict

from capability_orchestration import skill_registry


class CapabilityExecutor:
    """能力执行层：按 planner 输出路由技能执行。"""

    async def execute(self, session_id: str, plan: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        skill_name = (plan.get("skill") or "").strip()
        action = (plan.get("action") or "").strip()
        payload = dict(plan.get("input") or {})

        if skill_name.lower() in {"", "none"}:
            return {"status": "error", "message": "未匹配到可执行技能", "skill": "none"}

        if action:
            action_payload = dict(payload)
            action_payload.setdefault("action", action)
            action_payload.setdefault("session_id", session_id)
            action_payload.setdefault("context", context)
            action_payload.setdefault("user_input", payload.get("user_input", ""))
            return skill_registry.execute_skill_action(skill_name, action_payload)

        skill = skill_registry.get_or_create_skill(skill_name)
        if not skill:
            return {"status": "error", "message": f"技能不存在: {skill_name}", "skill": skill_name}

        skill_input = {
            "session_id": session_id,
            "user_input": payload.get("user_input", ""),
            "context": context,
        }
        run_result = await skill.run(skill_input)

        return {
            "status": "success" if run_result.get("success") else "failed",
            "skill": skill_name,
            "action": action,
            "result": run_result,
        }
