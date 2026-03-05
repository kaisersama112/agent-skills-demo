from datetime import datetime
from typing import Any, Dict


class StructuredResponseRenderer:
    """Structured Response Renderer: 统一输出结构化响应。"""

    def render(self, plan: Dict[str, Any], execution: Dict[str, Any]) -> Dict[str, Any]:
        success = bool(execution.get("success"))
        timestamp = datetime.utcnow().isoformat()

        if success:
            return {
                "type": "json",
                "content": execution,
                "plan": plan,
                "timestamp": timestamp,
            }

        return {
            "type": "text",
            "content": execution.get("message", "执行失败"),
            "plan": plan,
            "error": execution,
            "timestamp": timestamp,
        }
