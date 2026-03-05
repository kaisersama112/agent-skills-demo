from collections import OrderedDict
from datetime import datetime
import hashlib
import json
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from configs.config import settings
from core.chat_orchestrator import chat_orchestrator
from models.chat import ChatMessage, ChatSession, MessageType
from models.database import get_db

router = APIRouter()

# 简易幂等缓存（进程内，生产可替换 Redis）
_IDEMPOTENCY_CACHE: "OrderedDict[Tuple[str, str], Dict]" = OrderedDict()


def _safe_message_type(response_type: str) -> MessageType:
    try:
        return MessageType(response_type)
    except Exception:
        return MessageType.JSON


def _build_recent_history(db: Session, session_id: str, limit: int = 8) -> List[dict]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    items = []
    for msg in reversed(messages):
        items.append(
            {
                "sender": msg.sender,
                "type": msg.message_type.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
        )
    return items


def _resolve_idempotency_key(session_id: str, message: str, explicit_key: Optional[str]) -> str:
    if explicit_key:
        return explicit_key
    digest = hashlib.sha1(f"{session_id}:{message}".encode("utf-8")).hexdigest()
    return f"auto:{digest}"


def _cache_response(cache_key: Tuple[str, str], response: Dict) -> None:
    _IDEMPOTENCY_CACHE[cache_key] = response
    _IDEMPOTENCY_CACHE.move_to_end(cache_key)

    max_size = max(1, settings.idempotency_cache_size)
    while len(_IDEMPOTENCY_CACHE) > max_size:
        _IDEMPOTENCY_CACHE.popitem(last=False)


@router.post("/queryHistoryChatContent.json")
async def query_chat_history(
    session_id: str = Query(...),
    latestTime: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """查询聊天历史"""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        session = ChatSession(session_id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)

    if latestTime:
        latest_time = datetime.fromisoformat(latestTime)
        query = query.filter(ChatMessage.created_at > latest_time)

    messages = query.order_by(ChatMessage.created_at).all()

    result = []
    for msg in messages:
        result.append(
            {
                "id": msg.id,
                "type": msg.message_type.value,
                "content": msg.content,
                "sender": msg.sender,
                "createdAt": msg.created_at.isoformat(),
            }
        )

    return {"success": True, "data": result, "timestamp": datetime.utcnow().isoformat()}


@router.post("/sendMessage")
async def send_message(
    request: Request,
    session_id: str,
    message: str,
    idempotency_key: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """发送消息"""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        session = ChatSession(session_id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    dedupe_key = _resolve_idempotency_key(session_id, message, idempotency_key)
    cache_key = (session_id, dedupe_key)
    if cache_key in _IDEMPOTENCY_CACHE:
        cached = _IDEMPOTENCY_CACHE[cache_key]
        _IDEMPOTENCY_CACHE.move_to_end(cache_key)
        return {
            "success": True,
            "data": cached,
            "idempotency": {"key": dedupe_key, "hit": True},
            "timestamp": datetime.utcnow().isoformat(),
        }

    user_message = ChatMessage(
        session_id=session_id,
        message_type=MessageType.TEXT,
        content=message,
        sender="user",
    )
    db.add(user_message)

    inbound_trace_id = request.headers.get("X-Trace-Id", "")
    context = {"history": _build_recent_history(db, session_id)}
    if inbound_trace_id:
        context["trace_id"] = inbound_trace_id

    response = await chat_orchestrator.handle_message(session_id, message, context=context)

    response_type = response.get("type", "json")
    message_type = _safe_message_type(response_type)
    system_message = ChatMessage(
        session_id=session_id,
        message_type=message_type,
        content=json.dumps(response, ensure_ascii=False)
        if message_type != MessageType.TEXT
        else response.get("content", ""),
        sender="system",
    )
    db.add(system_message)

    db.commit()

    _cache_response(cache_key, response)

    return {
        "success": True,
        "data": response,
        "idempotency": {"key": dedupe_key, "hit": False},
        "timestamp": datetime.utcnow().isoformat(),
    }
