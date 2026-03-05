from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from models.chat import ChatSession, ChatMessage, MessageType
from core.chat_orchestrator import chat_orchestrator
import json
from datetime import datetime

router = APIRouter()


@router.post("/queryHistoryChatContent.json")
async def query_chat_history(
    session_id: str = Query(...),
    latestTime: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """查询聊天历史"""
    # 查找或创建会话
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        session = ChatSession(session_id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # 查询消息
    query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
    
    # 如果指定了latestTime，则只返回更新的消息
    if latestTime:
        latest_time = datetime.fromisoformat(latestTime)
        query = query.filter(ChatMessage.created_at > latest_time)
    
    messages = query.order_by(ChatMessage.created_at).all()
    
    # 构建响应
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "type": msg.message_type.value,
            "content": msg.content,
            "sender": msg.sender,
            "createdAt": msg.created_at.isoformat()
        })
    
    return {
        "success": True,
        "data": result,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/sendMessage")
async def send_message(
    session_id: str,
    message: str,
    db: Session = Depends(get_db)
):
    """发送消息"""
    # 查找或创建会话
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        session = ChatSession(session_id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # 保存用户消息
    user_message = ChatMessage(
        session_id=session_id,
        message_type=MessageType.TEXT,
        content=message,
        sender="user"
    )
    db.add(user_message)
    
    # 处理消息
    response = await chat_orchestrator.handle_message(session_id, message)
    
    # 保存系统回复
    system_message = ChatMessage(
        session_id=session_id,
        message_type=MessageType(response["type"]),
        content=json.dumps(response) if response["type"] != "text" else response["content"],
        sender="system"
    )
    db.add(system_message)
    
    db.commit()
    
    return {
        "success": True,
        "data": response,
        "timestamp": datetime.utcnow().isoformat()
    }
