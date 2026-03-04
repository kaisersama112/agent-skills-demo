from typing import Dict, List, Any, Optional, Generator
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

class StreamingRenderer:
    """
    流式渲染层：负责结构化JSON Schema和SSE推送
    """
    
    def __init__(self):
        self.schemas = {}
    
    def register_schema(self, name: str, schema: Dict[str, Any]):
        """
        注册JSON Schema
        """
        self.schemas[name] = schema
        print(f"注册Schema: {name}")
    
    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取Schema
        """
        return self.schemas.get(name)
    
    def generate_structured_output(self, data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
        """
        生成结构化输出
        
        Args:
            data: 原始数据
            schema_name: Schema名称
            
        Returns:
            结构化输出
        """
        schema = self.get_schema(schema_name)
        if not schema:
            return data
        
        # 根据Schema生成结构化输出
        return self._validate_and_structure(data, schema)
    
    def _validate_and_structure(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证并结构化数据
        """
        # 这里可以实现更复杂的Schema验证和结构化逻辑
        # 为了演示，我们简单地返回数据
        return data
    
    def stream_json(self, data: Dict[str, Any], chunk_size: int = 1024) -> Generator[str, None, None]:
        """
        流式输出JSON
        
        Args:
            data: 要输出的数据
            chunk_size: 块大小
            
        Yields:
            JSON数据块
        """
        json_str = json.dumps(data, ensure_ascii=False)
        for i in range(0, len(json_str), chunk_size):
            yield json_str[i:i+chunk_size]
            # 模拟流式输出的延迟
            import time
            time.sleep(0.01)
    
    async def stream_sse(self, data: Dict[str, Any], event_type: str = "data") -> Generator[str, None, None]:
        """
        流式输出SSE
        
        Args:
            data: 要输出的数据
            event_type: 事件类型
            
        Yields:
            SSE格式的数据
        """
        # 首先发送事件类型
        yield f"event: {event_type}\n"
        
        # 流式发送数据
        json_str = json.dumps(data, ensure_ascii=False)
        chunk_size = 512
        
        for i in range(0, len(json_str), chunk_size):
            chunk = json_str[i:i+chunk_size]
            yield f"data: {chunk}\n"
            await asyncio.sleep(0.01)
        
        # 发送结束标记
        yield "\n"
    
    def create_streaming_response(self, data: Dict[str, Any], media_type: str = "application/json") -> StreamingResponse:
        """
        创建流式响应
        
        Args:
            data: 要输出的数据
            media_type: 媒体类型
            
        Returns:
            StreamingResponse对象
        """
        def iter_content():
            for chunk in self.stream_json(data):
                yield chunk
        
        return StreamingResponse(
            iter_content(),
            media_type=media_type
        )
    
    def create_sse_response(self, data: Dict[str, Any], event_type: str = "data") -> StreamingResponse:
        """
        创建SSE响应
        
        Args:
            data: 要输出的数据
            event_type: 事件类型
            
        Returns:
            StreamingResponse对象
        """
        async def iter_content():
            async for chunk in self.stream_sse(data, event_type):
                yield chunk
        
        return StreamingResponse(
            iter_content(),
            media_type="text/event-stream"
        )
    
    def generate_skeleton(self, schema_name: str) -> Dict[str, Any]:
        """
        生成骨架屏数据
        
        Args:
            schema_name: Schema名称
            
        Returns:
            骨架屏数据
        """
        schema = self.get_schema(schema_name)
        if not schema:
            return {"skeleton": "loading..."}
        
        # 根据Schema生成骨架屏数据
        return self._generate_skeleton_from_schema(schema)
    
    def _generate_skeleton_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据Schema生成骨架屏数据
        """
        # 这里可以实现更复杂的骨架屏生成逻辑
        # 为了演示，我们返回一个简单的骨架屏结构
        return {
            "skeleton": True,
            "type": schema.get("type", "object"),
            "properties": {}
        }

# 示例Schema
EXAMPLE_SCHEMAS = {
    "todo_app": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string"
            },
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "content": {
                            "type": "string"
                        },
                        "completed": {
                            "type": "boolean"
                        }
                    }
                }
            }
        }
    },
    "dashboard": {
        "type": "object",
        "properties": {
            "widgets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "type": {
                            "type": "string"
                        },
                        "data": {
                            "type": "object"
                        }
                    }
                }
            }
        }
    }
}

# 初始化渲染器并注册示例Schema
def create_renderer() -> StreamingRenderer:
    renderer = StreamingRenderer()
    
    # 注册示例Schema
    for name, schema in EXAMPLE_SCHEMAS.items():
        renderer.register_schema(name, schema)
    
    return renderer

# 示例用法
if __name__ == "__main__":
    renderer = create_renderer()
    
    # 生成结构化输出
    data = {
        "title": "待办事项",
        "tasks": [
            {"id": "1", "content": "学习Python", "completed": False},
            {"id": "2", "content": "练习瑜伽", "completed": True}
        ]
    }
    
    structured_output = renderer.generate_structured_output(data, "todo_app")
    print("结构化输出:")
    print(structured_output)
    
    # 生成骨架屏
    skeleton = renderer.generate_skeleton("todo_app")
    print("\n骨架屏数据:")
    print(skeleton)