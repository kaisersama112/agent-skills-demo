from typing import Dict, Any, List
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class InternalCommsInput(SkillInput):
    """
    内部通信输入
    """
    message_type: str = Field(..., description="消息类型")
    recipients: List[str] = Field(..., description="接收者列表")
    content: str = Field(..., description="消息内容")


class InternalCommsOutput(SkillOutput):
    """
    内部通信输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def internal_comms_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    内部通信执行函数
    """
    # 模拟内部通信
    message_type = input_data.get("message_type")
    recipients = input_data.get("recipients", [])
    content = input_data.get("content")
    
    # 模拟发送过程
    result = send_message(message_type, recipients, content)
    
    return {
        "result": result,
        "message_type": message_type,
        "recipients": recipients,
        "content": content
    }


def send_message(message_type: str, recipients: List[str], content: str) -> Dict[str, Any]:
    """
    发送消息
    """
    # 模拟发送消息
    return {
        "status": "success",
        "message": f"Sent {message_type} message to {len(recipients)} recipients",
        "recipients": recipients
    }


# 技能定义
skill = AgentSkill(
    name="internal-comms",
    description="Handling internal communications within the organization",
    input_schema=InternalCommsInput,
    output_schema=InternalCommsOutput,
    execute=internal_comms_execute
)
