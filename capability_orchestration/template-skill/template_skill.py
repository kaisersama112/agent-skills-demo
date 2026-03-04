from typing import Dict, Any
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class TemplateSkillInput(SkillInput):
    """
    模板技能输入
    """
    param1: str = Field(..., description="参数1")
    param2: int = Field(None, description="参数2")


class TemplateSkillOutput(SkillOutput):
    """
    模板技能输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def template_skill_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    模板技能执行函数
    """
    return {
        "param1": input_data.get("param1"),
        "param2": input_data.get("param2"),
        "result": "success"
    }


# 技能定义
# 注意：创建新技能时，需要修改以下内容：
# 1. 技能名称
# 2. 技能描述
# 3. 输入输出schema
# 4. 执行函数
skill = AgentSkill(
    name="template-skill",
    description="模板技能，用于创建新技能",
    input_schema=TemplateSkillInput,
    output_schema=TemplateSkillOutput,
    execute=template_skill_execute
)
