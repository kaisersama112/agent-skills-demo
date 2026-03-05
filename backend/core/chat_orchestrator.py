from typing import Dict, Any, Optional, List
from services.llm_service import llm_service
from services.candyjar_service import candyjar_service
from capability_orchestration import skill_registry
from agents import ChatAgent
import uuid
from datetime import datetime


class ChatOrchestrator:
    """聊天编排器"""

    def __init__(self):
        self.chat_agent = ChatAgent()

    async def handle_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """处理用户消息"""
        # 使用聊天代理处理消息
        input_data = {
            "session_id": session_id,
            "user_input": user_input,
            "context": {}
        }

        result = await self.chat_agent.run(input_data)

        # 提取技能执行结果
        if result.get("success") and result.get("data"):
            skill_result = result.get("data")
            if skill_result.get("success") and skill_result.get("data"):
                return skill_result.get("data")

        # 回退到默认处理
        return {
            "type": "text",
            "content": "抱歉，处理您的请求时出现了错误。",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def handle_candyjar_call(self, api_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理CandyJar API调用"""
        return await candyjar_service.handle_call(api_name, payload)

    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有技能"""
        return skill_registry.list_skills()


# 创建全局聊天编排器实例
chat_orchestrator = ChatOrchestrator()
