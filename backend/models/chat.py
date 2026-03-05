from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class MessageType(str, enum.Enum):
    """消息类型"""
    TEXT = "text"
    SANDBOX_APP = "sandbox_app"
    JSON = "json"
    HTML = "html"


class ChatSession(Base):
    """聊天会话"""
    __tablename__ = "chat_session"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """聊天消息"""
    __tablename__ = "chat_message"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("chat_session.session_id"))
    message_type = Column(Enum(MessageType))
    content = Column(Text)
    sender = Column(String(50))  # user or system
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    session = relationship("ChatSession", back_populates="messages")
