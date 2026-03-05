from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class SandboxApp(Base):
    """沙箱应用"""
    __tablename__ = "sandbox_app"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(String(255), unique=True, index=True)
    session_id = Column(String(255), ForeignKey("chat_session.session_id"))
    name = Column(String(255))
    html_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    session = relationship("ChatSession")
