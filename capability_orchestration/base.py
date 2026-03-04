from typing import Dict, Any, Optional, Callable
from pydantic import BaseModel, Field


class SkillInput(BaseModel):
    """
    技能输入基类
    """
    pass


class SkillOutput(BaseModel):
    """
    技能输出基类
    """
    success: bool = Field(..., description="执行是否成功")
    message: str = Field(..., description="执行结果消息")
    data: Optional[Dict[str, Any]] = Field(None, description="执行结果数据")


class AgentSkill:
    """
    原子化的Agent Skill
    """
    
    def __init__(self, name: str, description: str, input_schema: type, output_schema: type, execute: Callable):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.execute = execute
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据
        """
        try:
            self.input_schema(**input_data)
            return True
        except Exception as e:
            print(f"输入验证失败: {str(e)}")
            return False
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行技能
        """
        if not self.validate_input(input_data):
            return self.output_schema(
                success=False,
                message="输入数据验证失败",
                data=None
            ).dict()
        
        try:
            result = await self.execute(input_data)
            return self.output_schema(
                success=True,
                message="执行成功",
                data=result
            ).dict()
        except Exception as e:
            return self.output_schema(
                success=False,
                message=f"执行失败: {str(e)}",
                data=None
            ).dict()
