from .base import Agent, AgentInput, AgentOutput
from capability_orchestration import skill_registry
from services.llm_service import llm_service


class ChatAgent(Agent):
    """聊天代理"""

    def __init__(self):
        super().__init__(
            name="chat_agent",
            description="处理聊天请求"
        )

    async def execute(self, input_data: dict) -> dict:
        """执行代理"""
        session_id = input_data.get("session_id")
        user_input = input_data.get("user_input")

        # 分类用户意图
        intent = await llm_service.classify_intent(user_input)

        # 根据意图选择技能
        skill = skill_registry.get_skill_by_intent(intent)

        # 如果没有找到对应技能，使用聊天技能
        if not skill:
            skill = skill_registry.get_skill("chat")

        # 执行技能
        skill_input = {
            "session_id": session_id,
            "user_input": user_input,
            "context": input_data.get("context")
        }

        if skill:
            result = await skill.run(skill_input)
            return result

        # 没有找到技能时的默认处理
        return {
            "success": False,
            "message": "没有找到合适的技能",
            "data": None
        }
