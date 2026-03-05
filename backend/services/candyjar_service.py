from typing import Dict, Any, Callable, Optional
import uuid


class CandyJarService:
    """CandyJar RPC服务"""
    
    def __init__(self):
        self.api_registry: Dict[str, Callable] = {}
        self._register_default_apis()
    
    def _register_default_apis(self):
        """注册默认API"""
        self.register_api("get_system_info", self.get_system_info)
        self.register_api("echo", self.echo)
        self.register_api("calculate", self.calculate)
    
    def register_api(self, api_name: str, handler: Callable):
        """注册API"""
        self.api_registry[api_name] = handler
    
    async def handle_call(self, api_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理API调用"""
        if api_name not in self.api_registry:
            return {
                "success": False,
                "error": f"API not found: {api_name}",
                "data": None
            }
        
        try:
            result = await self.api_registry[api_name](payload)
            return {
                "success": True,
                "error": None,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def get_system_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "app_name": "LLM App Platform",
            "version": "1.0.0",
            "timestamp": "2026-03-04",
            "apis": list(self.api_registry.keys())
        }
    
    async def echo(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """回显服务"""
        return {
            "message": payload.get("message", ""),
            "timestamp": "2026-03-04"
        }
    
    async def calculate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """计算服务"""
        operation = payload.get("operation")
        a = payload.get("a", 0)
        b = payload.get("b", 0)
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {"error": "除数不能为零"}
            result = a / b
        else:
            return {"error": "不支持的操作"}
        
        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result
        }


# 创建全局CandyJar服务实例
candyjar_service = CandyJarService()
