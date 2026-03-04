from typing import Dict, Any
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class ThemeFactoryInput(SkillInput):
    """
    主题工厂输入
    """
    theme_type: str = Field(..., description="主题类型")
    config: Dict[str, Any] = Field({}, description="主题配置")


class ThemeFactoryOutput(SkillOutput):
    """
    主题工厂输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def theme_factory_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    主题工厂执行函数
    """
    # 模拟主题生成
    theme_type = input_data.get("theme_type")
    config = input_data.get("config", {})
    
    # 模拟主题生成过程
    theme = generate_theme(theme_type, config)
    
    return {
        "theme": theme,
        "theme_type": theme_type
    }


def generate_theme(theme_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成主题
    """
    # 模拟主题生成
    themes = {
        "tech-innovation": {
            "name": "Tech Innovation",
            "colors": {
                "primary": "#007bff",
                "secondary": "#6c757d",
                "accent": "#17a2b8"
            },
            "fonts": {
                "heading": "Roboto",
                "body": "Open Sans"
            },
            "description": "A modern theme for tech-focused applications"
        },
        "modern-minimalist": {
            "name": "Modern Minimalist",
            "colors": {
                "primary": "#343a40",
                "secondary": "#6c757d",
                "accent": "#28a745"
            },
            "fonts": {
                "heading": "Montserrat",
                "body": "Lato"
            },
            "description": "A clean, minimalist theme with modern aesthetics"
        }
    }
    
    return themes.get(theme_type, {
        "name": "Default Theme",
        "colors": {
            "primary": "#007bff",
            "secondary": "#6c757d",
            "accent": "#28a745"
        },
        "fonts": {
            "heading": "Arial",
            "body": "Helvetica"
        },
        "description": "A default theme"
    })


# 技能定义
skill = AgentSkill(
    name="theme-factory",
    description="Creating themes for applications with various styles",
    input_schema=ThemeFactoryInput,
    output_schema=ThemeFactoryOutput,
    execute=theme_factory_execute
)
