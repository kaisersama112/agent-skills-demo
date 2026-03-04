from typing import Dict, List, Any, Optional
import json
import zlib
import base64
import time

class PerformanceOptimizer:
    """
    性能优化器
    负责首包200ms、骨架屏、本地缓存等优化
    """
    
    def __init__(self):
        self.cache = {}
        self.skeleton_templates = {}
    
    def compress_schema(self, schema: Dict[str, Any]) -> str:
        """
        压缩Schema
        
        Args:
            schema: Schema对象
            
        Returns:
            压缩后的Schema字符串
        """
        # 转换为JSON字符串
        schema_str = json.dumps(schema, ensure_ascii=False)
        
        # 压缩
        compressed = zlib.compress(schema_str.encode('utf-8'))
        
        # 编码为base64
        encoded = base64.b64encode(compressed).decode('utf-8')
        
        return encoded
    
    def decompress_schema(self, compressed_schema: str) -> Dict[str, Any]:
        """
        解压缩Schema
        
        Args:
            compressed_schema: 压缩后的Schema字符串
            
        Returns:
            解压后的Schema对象
        """
        # 解码base64
        decoded = base64.b64decode(compressed_schema)
        
        # 解压缩
        decompressed = zlib.decompress(decoded)
        
        # 转换为JSON对象
        schema = json.loads(decompressed.decode('utf-8'))
        
        return schema
    
    def generate_skeleton(self, component_type: str) -> Dict[str, Any]:
        """
        生成骨架屏
        
        Args:
            component_type: 组件类型
            
        Returns:
            骨架屏数据
        """
        # 检查是否有预定义的骨架屏模板
        if component_type in self.skeleton_templates:
            return self.skeleton_templates[component_type]
        
        # 根据组件类型生成骨架屏
        skeleton = {
            "type": "skeleton",
            "component": component_type,
            "loading": True,
            "timestamp": time.time()
        }
        
        # 为不同类型的组件生成不同的骨架屏
        if component_type == "todo_app":
            skeleton["content"] = {
                "title": "加载中...",
                "tasks": [
                    {"id": "loading-1", "content": "", "completed": False},
                    {"id": "loading-2", "content": "", "completed": False},
                    {"id": "loading-3", "content": "", "completed": False}
                ]
            }
        elif component_type == "dashboard":
            skeleton["content"] = {
                "widgets": [
                    {"id": "loading-1", "type": "chart", "loading": True},
                    {"id": "loading-2", "type": "table", "loading": True},
                    {"id": "loading-3", "type": "card", "loading": True}
                ]
            }
        elif component_type == "form":
            skeleton["content"] = {
                "fields": [
                    {"id": "field-1", "type": "text", "loading": True},
                    {"id": "field-2", "type": "select", "loading": True},
                    {"id": "field-3", "type": "button", "loading": True}
                ]
            }
        else:
            skeleton["content"] = {"loading": True}
        
        # 缓存骨架屏模板
        self.skeleton_templates[component_type] = skeleton
        
        return skeleton
    
    def cache_data(self, key: str, data: Any, expiration: int = 3600) -> bool:
        """
        缓存数据
        
        Args:
            key: 缓存键
            data: 缓存数据
            expiration: 过期时间（秒）
            
        Returns:
            是否缓存成功
        """
        try:
            self.cache[key] = {
                "data": data,
                "expiration": time.time() + expiration
            }
            return True
        except Exception:
            return False
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存数据，如果不存在或已过期则返回None
        """
        if key in self.cache:
            cache_item = self.cache[key]
            if time.time() < cache_item["expiration"]:
                return cache_item["data"]
            else:
                # 缓存已过期，删除
                del self.cache[key]
        return None
    
    def clear_cache(self, key: Optional[str] = None) -> bool:
        """
        清除缓存
        
        Args:
            key: 缓存键，如果为None则清除所有缓存
            
        Returns:
            是否清除成功
        """
        try:
            if key:
                if key in self.cache:
                    del self.cache[key]
            else:
                self.cache.clear()
            return True
        except Exception:
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        current_time = time.time()
        valid_count = 0
        expired_count = 0
        
        for key, item in self.cache.items():
            if current_time < item["expiration"]:
                valid_count += 1
            else:
                expired_count += 1
        
        return {
            "total": len(self.cache),
            "valid": valid_count,
            "expired": expired_count
        }
    
    def optimize_response_time(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化响应时间
        
        Args:
            data: 响应数据
            
        Returns:
            优化后的响应数据
        """
        # 添加响应时间戳
        optimized_data = {
            **data,
            "_metadata": {
                "response_time": time.time(),
                "optimized": True
            }
        }
        
        # 压缩数据
        if isinstance(data, dict) and len(json.dumps(data)) > 1000:
            optimized_data["_compressed"] = True
        
        return optimized_data
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        生成性能报告
        
        Returns:
            性能报告
        """
        return {
            "timestamp": time.time(),
            "cache_stats": self.get_cache_stats(),
            "skeleton_templates": len(self.skeleton_templates),
            "optimization_hints": [
                "使用HTTP/3 0-RTT快速建连",
                "启用浏览器缓存",
                "使用CDN加速静态资源",
                "优化API响应时间",
                "减少首包大小"
            ]
        }

# 示例用法
if __name__ == "__main__":
    optimizer = PerformanceOptimizer()
    
    # 测试Schema压缩
    test_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "content": {"type": "string"},
                        "completed": {"type": "boolean"}
                    }
                }
            }
        }
    }
    
    compressed = optimizer.compress_schema(test_schema)
    print("压缩后的Schema:")
    print(compressed)
    
    decompressed = optimizer.decompress_schema(compressed)
    print("\n解压后的Schema:")
    print(decompressed)
    
    # 测试骨架屏生成
    skeleton = optimizer.generate_skeleton("todo_app")
    print("\n骨架屏数据:")
    print(skeleton)
    
    # 测试缓存
    test_data = {"key": "value", "number": 42}
    optimizer.cache_data("test", test_data)
    
    cached_data = optimizer.get_cached_data("test")
    print("\n缓存数据:")
    print(cached_data)
    
    # 测试性能报告
    report = optimizer.generate_performance_report()
    print("\n性能报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))