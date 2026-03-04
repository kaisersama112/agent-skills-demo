from typing import Dict, List, Any, Optional, Generator
import json
import asyncio
from pydantic import BaseModel, Field

class StreamObject:
    """
    结构化对象流：负责JSON Schema + 部分解析器的实现
    """
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.buffer = ""
        self.parsed_objects = []
    
    def generate_stream(self, data: Dict[str, Any]) -> Generator[str, None, None]:
        """
        生成流式JSON
        
        Args:
            data: 要输出的数据
            
        Yields:
            JSON数据块
        """
        # 按照Schema的结构逐字段输出
        yield "{"
        
        # 遍历Schema的properties
        if "properties" in self.schema:
            properties = self.schema["properties"]
            keys = list(properties.keys())
            
            for i, key in enumerate(keys):
                # 输出键
                yield f'"{key}":'
                
                # 根据值的类型输出
                value = data.get(key)
                if isinstance(value, dict):
                    # 递归处理嵌套对象
                    yield from self._generate_object_stream(value, properties[key])
                elif isinstance(value, list):
                    # 处理数组
                    yield from self._generate_array_stream(value, properties[key])
                else:
                    # 处理基本类型
                    yield json.dumps(value, ensure_ascii=False)
                
                # 输出逗号（除了最后一个）
                if i < len(keys) - 1:
                    yield ","
        
        yield "}"
    
    def _generate_object_stream(self, obj: Dict[str, Any], schema: Dict[str, Any]) -> Generator[str, None, None]:
        """
        生成对象的流式输出
        """
        yield "{"
        
        if "properties" in schema:
            properties = schema["properties"]
            keys = list(properties.keys())
            
            for i, key in enumerate(keys):
                if key in obj:
                    yield f'"{key}":'
                    
                    value = obj[key]
                    if isinstance(value, dict):
                        yield from self._generate_object_stream(value, properties[key])
                    elif isinstance(value, list):
                        yield from self._generate_array_stream(value, properties[key])
                    else:
                        yield json.dumps(value, ensure_ascii=False)
                    
                    if i < len(keys) - 1:
                        yield ","
        
        yield "}"
    
    def _generate_array_stream(self, arr: List[Any], schema: Dict[str, Any]) -> Generator[str, None, None]:
        """
        生成数组的流式输出
        """
        yield "["
        
        if "items" in schema:
            item_schema = schema["items"]
            
            for i, item in enumerate(arr):
                if isinstance(item, dict):
                    yield from self._generate_object_stream(item, item_schema)
                elif isinstance(item, list):
                    yield from self._generate_array_stream(item, item_schema)
                else:
                    yield json.dumps(item, ensure_ascii=False)
                
                if i < len(arr) - 1:
                    yield ","
        
        yield "]"
    
    def parse_stream(self, chunk: str) -> List[Dict[str, Any]]:
        """
        解析流式JSON
        
        Args:
            chunk: JSON数据块
            
        Returns:
            解析出的完整对象
        """
        self.buffer += chunk
        
        # 尝试解析buffer中的JSON
        parsed = []
        
        try:
            # 尝试解析整个buffer
            obj = json.loads(self.buffer)
            parsed.append(obj)
            self.parsed_objects.append(obj)
            self.buffer = ""
        except json.JSONDecodeError:
            # 尝试解析部分JSON
            # 这里可以实现更复杂的部分解析逻辑
            # 为了演示，我们简单地返回空列表
            pass
        
        return parsed
    
    def get_parsed_objects(self) -> List[Dict[str, Any]]:
        """
        获取已解析的对象
        """
        return self.parsed_objects
    
    def reset(self):
        """
        重置解析状态
        """
        self.buffer = ""
        self.parsed_objects = []
    
    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """
        验证数据是否符合Schema
        """
        # 这里可以实现更复杂的Schema验证逻辑
        # 为了演示，我们简单地返回True
        return True

class JsonRiver:
    """
    JSON流式解析器
    """
    
    def __init__(self):
        self.buffer = ""
        self.state = "start"
        self.parsed_objects = []
    
    def parse(self, chunk: str) -> List[Dict[str, Any]]:
        """
        解析JSON数据块
        
        Args:
            chunk: JSON数据块
            
        Returns:
            解析出的完整对象
        """
        self.buffer += chunk
        parsed = []
        
        # 简单的状态机解析
        # 这里只是一个简化的实现，实际的JSON解析器会更复杂
        
        # 尝试解析整个buffer
        try:
            obj = json.loads(self.buffer)
            parsed.append(obj)
            self.parsed_objects.append(obj)
            self.buffer = ""
            self.state = "start"
        except json.JSONDecodeError:
            # 保持当前状态
            pass
        
        return parsed
    
    def get_parsed_objects(self) -> List[Dict[str, Any]]:
        """
        获取已解析的对象
        """
        return self.parsed_objects
    
    def reset(self):
        """
        重置解析状态
        """
        self.buffer = ""
        self.state = "start"
        self.parsed_objects = []

# 示例Schema
EXAMPLE_SCHEMAS = {
    "todo_item": {
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
        },
        "required": ["id", "content", "completed"]
    },
    "todo_list": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string"
            },
            "tasks": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/todo_item"
                }
            }
        },
        "definitions": {
            "todo_item": {
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
                },
                "required": ["id", "content", "completed"]
            }
        }
    }
}

# 示例用法
if __name__ == "__main__":
    # 创建StreamObject
    stream_obj = StreamObject(EXAMPLE_SCHEMAS["todo_list"])
    
    # 测试数据
    data = {
        "title": "待办事项",
        "tasks": [
            {"id": "1", "content": "学习Python", "completed": False},
            {"id": "2", "content": "练习瑜伽", "completed": True}
        ]
    }
    
    # 生成流式输出
    print("生成流式JSON:")
    stream = ""
    for chunk in stream_obj.generate_stream(data):
        stream += chunk
        print(chunk, end="")
    print()
    
    # 测试解析
    json_river = JsonRiver()
    
    # 模拟分块接收
    chunks = [
        '{"title":"待办事项","tasks":[{"id":"1","content":"学习Python","completed":false},{"id":"2","content":"练习瑜伽","completed":true}]}'
    ]
    
    print("\n解析流式JSON:")
    for chunk in chunks:
        parsed = json_river.parse(chunk)
        if parsed:
            print(f"解析出对象: {parsed}")
    
    print("\n已解析的对象:")
    print(json_river.get_parsed_objects())