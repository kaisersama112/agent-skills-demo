from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    GENERATE_APP = "generate_app"
    CHAT = "chat"
    QUERY = "query"
    ACTION = "action"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Message(BaseModel):
    role: str = Field(..., description="消息角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class Session(BaseModel):
    id: str = Field(..., description="会话ID")
    user_id: str = Field(default="default_user", description="用户ID")
    messages: List[Message] = Field(default_factory=list)
    context_state: Dict[str, Any] = Field(default_factory=dict, description="上下文状态")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="会话元数据")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class IntentResult(BaseModel):
    intent: IntentType
    domain: Optional[str] = None
    components: List[str] = Field(default_factory=list)
    raw_output: Optional[str] = None


class Task(BaseModel):
    id: str = Field(..., description="任务ID")
    agent: str = Field(..., description="Agent名称")
    action: str = Field(..., description="执行动作")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    output: Optional[Any] = None
    error: Optional[str] = None


class Plan(BaseModel):
    tasks: List[Task] = Field(default_factory=list)
    execution_order: List[str] = Field(default_factory=list)


class AppSpec(BaseModel):
    name: str = Field(..., description="应用名称")
    description: str = Field(..., description="应用描述")
    domain: str = Field(..., description="应用领域")
    components: List[str] = Field(default_factory=list, description="所需组件")
    requirements: Dict[str, Any] = Field(default_factory=dict)


class GeneratedApp(BaseModel):
    id: str = Field(..., description="应用ID")
    spec: AppSpec
    code: Dict[str, str] = Field(default_factory=dict, description="生成的代码")
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.now)
    url: Optional[str] = None


class TextBlock(BaseModel):
    type: str = Field(default="text")
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ImageBlock(BaseModel):
    type: str = Field(default="image")
    url: str
    alt_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SvgBlock(BaseModel):
    type: str = Field(default="svg")
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ArtifactBlock(BaseModel):
    type: str = Field(default="artifact")
    artifact_id: str
    name: str
    description: str
    url: str
    metadata: Optional[Dict[str, Any]] = None


class FollowUpBlock(BaseModel):
    type: str = Field(default="follow_up")
    questions: List[str]
    metadata: Optional[Dict[str, Any]] = None


class ChartBlock(BaseModel):
    type: str = Field(default="chart")
    config: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class StructuredResponse(BaseModel):
    text_blocks: List[TextBlock] = Field(default_factory=list)
    image_blocks: List[ImageBlock] = Field(default_factory=list)
    svg_blocks: List[SvgBlock] = Field(default_factory=list)
    chart_blocks: List[ChartBlock] = Field(default_factory=list)
    artifact_blocks: List[ArtifactBlock] = Field(default_factory=list)
    follow_up_blocks: List[FollowUpBlock] = Field(default_factory=list)
    session_id: Optional[str] = None


class AgentResult(BaseModel):
    agent: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
