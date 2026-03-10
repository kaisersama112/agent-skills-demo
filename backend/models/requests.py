from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: Optional[str] = None
    app_id: Optional[str] = None
    app_name: Optional[str] = None
    app_description: Optional[str] = None
    app_domain: Optional[str] = None
    app_url: Optional[str] = None
    app_code: Optional[Dict[str, str]] = None


class GenerateAppRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class GenerateAppResponse(BaseModel):
    app_id: str
    name: str
    description: str
    domain: str
    code: Dict[str, str]
    url: str


class ExecuteTaskRequest(BaseModel):
    agent: str
    action: str
    input_data: Dict[str, Any] = {}


class ExecuteTaskResponse(BaseModel):
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class HealthResponse(BaseModel):
    status: str
    version: str
