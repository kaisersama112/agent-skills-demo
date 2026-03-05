from typing import Dict, Any, List, Optional
import uuid

from services.candyjar_service import candyjar_service
from capability_orchestration import skill_registry
from core.planner import LLMPlanner
from core.executor import CapabilityExecutor
from core.response_renderer import StructuredResponseRenderer


class ChatOrchestrator:
    """聊天编排器：编排 Planner -> Executor -> Renderer。"""

    def __init__(self):
        self.planner = LLMPlanner()
        self.executor = CapabilityExecutor()
        self.renderer = StructuredResponseRenderer()

    async def handle_message(self, session_id: str, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        trace_id = context.get("trace_id") or f"trace-{uuid.uuid4().hex[:12]}"
        context["trace_id"] = trace_id

        try:
            plan = await self.planner.plan(user_input, context=context)
        except TypeError:
            # 兼容旧 planner 接口（仅接收 user_input）
            plan = await self.planner.plan(user_input)
        execution = await self.executor.execute(session_id=session_id, plan=plan, context=context)

        return self.renderer.render(user_input=user_input, plan=plan, execution=execution, trace_id=trace_id)

    async def handle_candyjar_call(self, api_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await candyjar_service.handle_call(api_name, payload)

    def list_skills(self) -> List[Dict[str, Any]]:
        return skill_registry.list_skills()


chat_orchestrator = ChatOrchestrator()
