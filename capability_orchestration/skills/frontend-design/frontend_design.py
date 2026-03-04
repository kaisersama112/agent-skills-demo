from typing import Dict, Any
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class FrontendDesignInput(SkillInput):
    """
    前端设计输入
    """
    design_type: str = Field(..., description="设计类型")
    requirements: Dict[str, Any] = Field({}, description="设计需求")
    output_format: str = Field("html", description="输出格式")


class FrontendDesignOutput(SkillOutput):
    """
    前端设计输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def frontend_design_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    前端设计执行函数
    """
    # 模拟前端设计
    design_type = input_data.get("design_type")
    requirements = input_data.get("requirements", {})
    output_format = input_data.get("output_format", "html")
    
    # 模拟设计过程
    design = create_design(design_type, requirements, output_format)
    
    return {
        "design": design,
        "design_type": design_type,
        "output_format": output_format
    }


def create_design(design_type: str, requirements: Dict[str, Any], output_format: str) -> Dict[str, Any]:
    """
    创建前端设计
    """
    # 模拟前端设计
    return {
        "status": "success",
        "message": f"Created {design_type} design",
        "output_format": output_format,
        "requirements": requirements,
        "design_content": "<div>Sample design content</div>"
    }


# 技能定义
skill = AgentSkill(
    name="frontend-design",
    description="Creating frontend designs for web applications",
    input_schema=FrontendDesignInput,
    output_schema=FrontendDesignOutput,
    execute=frontend_design_execute
)
