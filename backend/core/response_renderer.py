from datetime import datetime
from typing import Any, Dict


class StructuredResponseRenderer:
    """结构化响应层：统一 API 响应格式。"""

    def render(self, user_input: str, plan: Dict[str, Any], execution: Dict[str, Any]) -> Dict[str, Any]:
        status = execution.get("status")
        response_type = "json"

        if status in {"error", "failed"}:
            return {
                "type": response_type,
                "content": {
                    "status": status,
                    "message": execution.get("message") or "执行失败",
                    "error_code": execution.get("error_code", "execution_error"),
                    "user_input": user_input,
                    "plan": plan,
                    "execution": execution,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {
            "type": response_type,
            "content": {
                "status": "success",
                "user_input": user_input,
                "plan": plan,
                "execution": execution,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
