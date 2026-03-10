from openai import AsyncOpenAI
from config import settings
from typing import Optional, Dict, Any, List
import json


class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model = settings.openai_model
    
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        response_format: Optional[str] = None,
        model_name: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        kwargs = {
            "model": model_name or self.model,
            "messages": messages,
            "temperature": temperature
        }
        if response_format:
            kwargs["response_format"] = {"type": response_format}
        if tools:
            kwargs["tools"] = tools
        if tool_choice:
            kwargs["tool_choice"] = tool_choice
        
        response = await self.client.chat.completions.create(**kwargs)
        return response
    
    async def chat_json(self,
                        messages: List[Dict[str, Any]], 
                        model_name: str=None,  
                        temperature: float = 0.3) -> Dict[str, Any]:
        content = await self.chat(messages, temperature=temperature, response_format="json_object", model_name=model_name)
        return json.loads(content.choices[0].message.content)
    
    async def chat_str(self, messages: List[Dict[str, Any]], temperature: float = 0.7) -> str:
        response = await self.chat(messages, temperature=temperature)
        return response.choices[0].message.content
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict],
        temperature: float = 0.7,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """带工具调用的聊天"""
        return await self.chat(
            messages=messages,
            tools=tools,
            temperature=temperature,
            model_name=model_name
        )


llm_client = LLMClient()
