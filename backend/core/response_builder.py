from typing import Dict, List, Optional, Any
from backend.models.schemas import (
    StructuredResponse, TextBlock, ImageBlock, SvgBlock, ArtifactBlock, FollowUpBlock, ChartBlock
)


class ResponseBuilder:
    """响应构建器，用于构建结构化响应"""
    
    def __init__(self):
        self.response = StructuredResponse()
    
    def add_text(self, content: str, metadata: Optional[Dict[str, Any]] = None, priority: int = 1) -> 'ResponseBuilder':
        """添加文本块"""
        if metadata is None:
            metadata = {}
        metadata['priority'] = priority
        text_block = TextBlock(content=content, metadata=metadata)
        self.response.text_blocks.append(text_block)
        return self
    
    def add_image(self, url: str, alt_text: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, priority: int = 2) -> 'ResponseBuilder':
        """添加图像块"""
        if metadata is None:
            metadata = {}
        metadata['priority'] = priority
        image_block = ImageBlock(url=url, alt_text=alt_text, metadata=metadata)
        self.response.image_blocks.append(image_block)
        return self
    
    def add_svg(self, content: str, metadata: Optional[Dict[str, Any]] = None, priority: int = 2) -> 'ResponseBuilder':
        """添加SVG块"""
        if metadata is None:
            metadata = {}
        metadata['priority'] = priority
        svg_block = SvgBlock(content=content, metadata=metadata)
        self.response.svg_blocks.append(svg_block)
        return self
    
    def add_artifact(self, artifact_id: str, name: str, description: str, url: str, metadata: Optional[Dict[str, Any]] = None, priority: int = 3) -> 'ResponseBuilder':
        """添加Artifact块"""
        if metadata is None:
            metadata = {}
        metadata['priority'] = priority
        artifact_block = ArtifactBlock(
            artifact_id=artifact_id,
            name=name,
            description=description,
            url=url,
            metadata=metadata
        )
        self.response.artifact_blocks.append(artifact_block)
        return self
    
    def add_follow_up(self, questions: List[str], metadata: Optional[Dict[str, Any]] = None, priority: int = 1) -> 'ResponseBuilder':
        """添加后续问题块"""
        if metadata is None:
            metadata = {}
        metadata['priority'] = priority
        follow_up_block = FollowUpBlock(questions=questions, metadata=metadata)
        self.response.follow_up_blocks.append(follow_up_block)
        return self
    
    def add_chart(self, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None, priority: int = 2) -> 'ResponseBuilder':
        """添加图表块"""
        if metadata is None:
            metadata = {}
        metadata['priority'] = priority
        chart_block = ChartBlock(config=config, metadata=metadata)
        self.response.chart_blocks.append(chart_block)
        return self
    
    def set_session_id(self, session_id: str) -> 'ResponseBuilder':
        """设置会话ID"""
        self.response.session_id = session_id
        return self
    
    def build(self) -> StructuredResponse:
        """构建并返回响应"""
        return self.response
    
    @staticmethod
    def from_chat_response(response: str, session_id: Optional[str] = None) -> StructuredResponse:
        """从聊天响应创建结构化响应"""
        builder = ResponseBuilder()
        builder.add_text(response)
        if session_id:
            builder.set_session_id(session_id)
        return builder.build()
    
    @staticmethod
    def from_app_generation(app_id: str, name: str, description: str, url: str, session_id: Optional[str] = None) -> StructuredResponse:
        """从应用生成创建结构化响应"""
        builder = ResponseBuilder()
        builder.add_text(f"已生成应用: {name} - {description}")
        builder.add_artifact(
            artifact_id=app_id,
            name=name,
            description=description,
            url=url
        )
        builder.add_follow_up([
            "你对生成的应用满意吗？",
            "需要对应用进行哪些修改？",
            "还需要生成其他类型的应用吗？"
        ])
        if session_id:
            builder.set_session_id(session_id)
        return builder.build()