import httpx
import asyncio
from typing import Optional, Dict, Any, List
from config.config import settings


class LLMService:
    """LLM服务"""
    
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url
        self.default_model = settings.llm_model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """生成文本"""
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            **kwargs
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 重试机制
        for attempt in range(3):
            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
                continue
    
    async def generate_html_app(self, user_input: str) -> str:
        """生成HTML应用"""
        prompt = f"""
你是一个前端应用生成器，根据用户需求创建一个完整的HTML应用。

用户需求：{user_input}

要求：
1. 生成完整的HTML代码，包含所有必要的CSS和JavaScript
2. 代码必须安全，不能包含任何危险操作
3. 应用应该功能完整，界面美观
4. 只生成代码，不生成其他解释性文本
5. 使用内联样式和脚本，确保在iframe中能独立运行
6. 可以使用CandyJar API进行通信

示例输出格式：
```html
完整的HTML代码
```
        """
        
        response = await self.generate(prompt)
        
        # 提取HTML代码
        if "```html" in response:
            html_start = response.find("```html") + 7
            html_end = response.find("```", html_start)
            if html_end != -1:
                return response[html_start:html_end].strip()
        
        return response
    
    async def classify_intent(self, user_input: str) -> str:
        """分类用户意图"""
        prompt = f"""
从以下选项中选择最符合用户输入的意图：
- chat: 普通聊天
- sandbox_app: 生成沙箱应用
- document: 文档处理
- other: 其他

用户输入：{user_input}

请只返回意图名称，不要返回其他内容。
        """
        
        response = await self.generate(prompt, temperature=0.0)
        return response.strip()
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 创建全局LLM服务实例
llm_service = LLMService()
