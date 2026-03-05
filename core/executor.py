import asyncio
from typing import Any, Dict, List

from capability_orchestration import skill_registry
from configs.config import settings
from core.telemetry import log_event


class CapabilityExecutor:
    """能力执行层：按 planner 输出路由技能执行。"""

    async def execute(self, session_id: str, plan: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        skill_name = (plan.get("skill") or "").strip()
        action = (plan.get("action") or "").strip()
        payload = dict(plan.get("input") or {})
        task_plan = plan.get("task_plan", [])
        trace_id = context.get("trace_id", "")

        if skill_name.lower() in {"", "none"}:
            return {"status": "error", "message": "未匹配到可执行技能", "skill": "none", "error_code": "missing_skill"}

        # If there's a task plan, execute it
        if task_plan:
            return await self._execute_task_plan(
                session_id=session_id,
                skill_name=skill_name,
                task_plan=task_plan,
                context=context,
                trace_id=trace_id,
            )

        # Fall back to original execution if no task plan
        if action:
            return await self._execute_action_with_retry(
                session_id=session_id,
                skill_name=skill_name,
                action=action,
                payload=payload,
                context=context,
                trace_id=trace_id,
            )

        skill = skill_registry.get_or_create_skill(skill_name)
        if not skill:
            return {"status": "error", "message": f"技能不存在: {skill_name}", "skill": skill_name, "error_code": "skill_not_found"}

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
            "error_code": "" if run_result.get("success") else "skill_run_failed",
        }

    async def _execute_task_plan(self, session_id: str, skill_name: str, task_plan: List[Dict[str, Any]], context: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """执行任务计划"""
        execution_results = []
        overall_status = "success"

        for task in task_plan:
            step = task.get("step", 0)
            description = task.get("description", "")
            script = task.get("script", "")
            parameters = task.get("parameters", {})

            log_event(
                "executor_task_start",
                trace_id=trace_id,
                session_id=session_id,
                skill=skill_name,
                step=step,
                description=description,
                script=script,
            )

            if script:
                # Execute script
                payload = {
                    "action": script,
                    "session_id": session_id,
                    "context": context,
                    **parameters
                }
                result = skill_registry.execute_skill_action(skill_name, payload)
                
                # Check for missing dependencies
                if "ModuleNotFoundError" in result.get("stderr", ""):
                    result["status"] = "warning"
                    result["message"] = f"Step {step}: {description} - Missing dependencies: defusedxml. Please install it with 'pip install defusedxml'"
            else:
                # Skip if no script specified
                result = {
                    "status": "success",
                    "message": f"Step {step}: {description} - No script to execute",
                    "step": step,
                    "description": description
                }

            execution_results.append({
                "step": step,
                "description": description,
                "script": script,
                "result": result
            })

            # Only mark as failed if it's a critical error, not just missing dependencies
            if result.get("status") == "error":
                overall_status = "failed"

            log_event(
                "executor_task_end",
                trace_id=trace_id,
                session_id=session_id,
                skill=skill_name,
                step=step,
                status=result.get("status"),
                error_code=result.get("error_code", ""),
            )

        return {
            "status": overall_status,
            "skill": skill_name,
            "task_plan": task_plan,
            "execution_results": execution_results,
            "error_code": "" if overall_status == "success" else "task_plan_failed"
        }

    async def _execute_action_with_retry(
        self,
        session_id: str,
        skill_name: str,
        action: str,
        payload: Dict[str, Any],
        context: Dict[str, Any],
        trace_id: str,
    ) -> Dict[str, Any]:
        max_attempts = max(1, settings.executor_retry_count + 1)
        last_result: Dict[str, Any] = {}

        for attempt in range(1, max_attempts + 1):
            action_payload = dict(payload)
            action_payload.setdefault("action", action)
            action_payload.setdefault("session_id", session_id)
            action_payload.setdefault("context", context)
            action_payload.setdefault("user_input", payload.get("user_input", ""))

            result = skill_registry.execute_skill_action(skill_name, action_payload)
            result.setdefault("attempt", attempt)
            last_result = result

            log_event(
                "executor_action_attempt",
                trace_id=trace_id,
                session_id=session_id,
                skill=skill_name,
                action=action,
                attempt=attempt,
                status=result.get("status"),
                error_code=result.get("error_code", ""),
            )

            if not self._should_retry(result, attempt, max_attempts):
                return result

            await asyncio.sleep(settings.executor_retry_backoff_seconds * attempt)

        return last_result

    def _should_retry(self, result: Dict[str, Any], attempt: int, max_attempts: int) -> bool:
        if attempt >= max_attempts:
            return False

        status = result.get("status")
        error_code = result.get("error_code", "")

        if status == "failed":
            return True

        if status == "error" and error_code in settings.executor_retryable_error_codes_set:
            return True

        return False
