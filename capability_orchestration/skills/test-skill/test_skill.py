from typing import Dict, Any
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class TestskillInput(SkillInput):
    """
    Test Skill输入
    """
    # 在这里添加输入字段
    pass


class TestskillOutput(SkillOutput):
    """
    Test Skill输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def test_skill_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test Skill执行函数
    """
    # 在这里实现技能逻辑
    return {
        "result": "执行成功",
        "input_data": input_data
    }


# 技能定义
skill = AgentSkill(
    name="test-skill",
    description="A test skill for demonstration",
    input_schema=TestskillInput,
    output_schema=TestskillOutput,
    execute=test_skill_execute
)
