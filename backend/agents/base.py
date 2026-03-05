from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """代理输入基类"""
    session_id: str = Field(..., description="会话ID")
    user_input: str = Field(..., description="用户输入")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class AgentOutput(BaseModel):
    """代理输出基类"""
    success: bool = Field(..., description="执行是否成功")
    message: str = Field(..., description="执行结果消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="执行结果数据")
    agent_name: str = Field(..., description="代理名称")


class Agent:
    """代理基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行代理"""
        raise NotImplementedError("子类必须实现execute方法")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行代理"""
        try:
            result = await self.execute(input_data)
            return {
                "success": True,
                "message": "执行成功",
                "data": result,
                "agent_name": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"执行失败: {str(e)}",
                "data": None,
                "agent_name": self.name
            }
