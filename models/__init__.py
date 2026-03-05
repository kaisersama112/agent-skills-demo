from .database import Base, engine, SessionLocal
from .chat import ChatSession, ChatMessage
from .sandbox import SandboxApp

# 创建所有表
Base.metadata.create_all(bind=engine)
