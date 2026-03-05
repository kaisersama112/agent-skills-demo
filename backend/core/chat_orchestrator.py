from typing import Dict, Any, List

from services.candyjar_service import candyjar_service
from capability_orchestration import skill_registry
from .planner import SkillPlanner
from .executor import CapabilityExecutor
from .response_renderer import StructuredResponseRenderer


class ChatOrchestrator:
    """会话编排层：串联 Planner -> Executor -> Renderer。"""

    def __init__(self):
        self.planner = SkillPlanner()
        self.executor = CapabilityExecutor()
        self.renderer = StructuredResponseRenderer()

    async def handle_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        plan = await self.planner.plan(user_input)
        execution = await self.executor.execute(session_id=session_id, plan=plan, context={})
        return self.renderer.render(plan=plan, execution=execution)

    async def handle_candyjar_call(self, api_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await candyjar_service.handle_call(api_name, payload)

    def list_skills(self) -> List[Dict[str, Any]]:
        return skill_registry.list_skills()


chat_orchestrator = ChatOrchestrator()
