from typing import Dict, Any, List
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class SlackGifCreatorInput(SkillInput):
    """
    Slack GIF创建输入
    """
    text: str = Field(..., description="GIF文本内容")
    duration: int = Field(2, description="GIF持续时间（秒）")
    size: str = Field("500x500", description="GIF尺寸")


class SlackGifCreatorOutput(SkillOutput):
    """
    Slack GIF创建输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def slack_gif_creator_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Slack GIF创建执行函数
    """
    # 模拟GIF创建
    text = input_data.get("text")
    duration = input_data.get("duration", 2)
    size = input_data.get("size", "500x500")
    
    # 模拟GIF创建过程
    gif_url = create_gif(text, duration, size)
    
    return {
        "gif_url": gif_url,
        "text": text,
        "duration": duration,
        "size": size
    }


def create_gif(text: str, duration: int, size: str) -> str:
    """
    创建GIF
    """
    # 模拟GIF创建
    return f"https://example.com/gifs/{text.replace(' ', '_')}_{duration}s_{size}.gif"


# 技能定义
skill = AgentSkill(
    name="slack-gif-creator",
    description="Creating GIFs for Slack messages",
    input_schema=SlackGifCreatorInput,
    output_schema=SlackGifCreatorOutput,
    execute=slack_gif_creator_execute
)
