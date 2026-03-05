from typing import Any, Dict

from capability_orchestration import skill_registry


class CapabilityExecutor:
    """Capability Execution Layer: 执行技能计划。"""

    async def execute(self, session_id: str, plan: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        skill_name = plan.get("skill")
        if not skill_name:
            return {"success": False, "error": "missing_skill", "message": "计划缺少skill"}

        action = plan.get("action") or plan.get("operation")
        if action:
            route_input = {
                "session_id": session_id,
                "context": context,
                "user_input": plan.get("input", {}).get("user_input", ""),
                "action": action,
                "operation": action,
            }
            routed = skill_registry.execute_skill_action(skill_name, route_input)
            return {"success": routed.get("status") == "success", "mode": "script", "result": routed}

        skill = skill_registry.get_or_create_skill(skill_name)
        if not skill:
            return {"success": False, "error": "skill_not_found", "message": f"技能不存在: {skill_name}"}

        skill_input = {
            "session_id": session_id,
            "user_input": plan.get("input", {}).get("user_input", ""),
            "context": context,
        }
        result = await skill.run(skill_input)
        return {"success": bool(result.get("success")), "mode": "skill", "result": result}
