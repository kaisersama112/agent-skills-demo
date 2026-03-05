from typing import Dict, Any, List

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

    async def handle_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        context: Dict[str, Any] = {}

        plan = await self.planner.plan(user_input)
        execution = await self.executor.execute(session_id=session_id, plan=plan, context=context)

        return self.renderer.render(user_input=user_input, plan=plan, execution=execution)

    async def handle_candyjar_call(self, api_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await candyjar_service.handle_call(api_name, payload)

    def list_skills(self) -> List[Dict[str, Any]]:
        return skill_registry.list_skills()


chat_orchestrator = ChatOrchestrator()
