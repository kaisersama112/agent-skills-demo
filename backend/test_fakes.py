from typing import Any, Dict, Optional


class FakePlanner:
    """测试用 Planner：支持 context，并可按关键词返回不同计划。"""

    async def plan(self, user_input: str, context: Optional[Dict[str, Any]] = None):
        context = context or {}
        lowered = user_input.lower()

        if "失败" in user_input or "fail" in lowered:
            return {
                "skill": "none",
                "action": "",
                "input": {"user_input": user_input},
                "reason": "forced-failure-plan",
            }

        action = "merge" if ("合并" in user_input or "merge" in lowered) else "analyze"
        return {
            "skill": "pdf",
            "action": action,
            "input": {
                "user_input": user_input,
                "history_size": len(context.get("history", [])),
            },
            "reason": "fake-planner",
        }


class FakeExecutor:
    """测试用 Executor：透传 trace_id，支持成功/失败分支。"""

    async def execute(self, session_id: str, plan, context):
        if plan.get("skill") == "none":
            return {
                "status": "error",
                "skill": "none",
                "action": "",
                "error_code": "missing_skill",
                "message": "未匹配到可执行技能",
                "trace_id": context.get("trace_id", ""),
            }

        return {
            "status": "success",
            "skill": plan.get("skill", "pdf"),
            "action": plan.get("action", "merge"),
            "script": f"scripts/{plan.get('action', 'merge')}.py",
            "returncode": 0,
            "stdout": "ok",
            "stderr": "",
            "trace_id": context.get("trace_id", ""),
        }
