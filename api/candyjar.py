from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.chat_orchestrator import chat_orchestrator
from typing import Dict, Any, Optional

router = APIRouter()


class CandyJarCallRequest(BaseModel):
    """CandyJar调用请求"""
    api: str
    payload: Dict[str, Any]
    callId: str


class CandyJarCallResponse(BaseModel):
    """CandyJar调用响应"""
    type: str = "CANDYJAR_CALLBACK"
    callId: str
    success: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@router.post("/call")
async def candyjar_call(request: CandyJarCallRequest):
    """处理CandyJar API调用"""
    try:
        result = await chat_orchestrator.handle_candyjar_call(
            request.api,
            request.payload
        )
        
        return {
            "type": "CANDYJAR_CALLBACK",
            "callId": request.callId,
            "success": result["success"],
            "error": result["error"],
            "data": result["data"]
        }
    except Exception as e:
        return {
            "type": "CANDYJAR_CALLBACK",
            "callId": request.callId,
            "success": False,
            "error": str(e),
            "data": None
        }
