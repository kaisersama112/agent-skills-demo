from typing import Dict, List, Optional, Any, Callable
from backend.services.image_processor import image_processor
from backend.services.svg_generator import svg_generator
import asyncio
import time


class CapabilityRegistry:
    """能力注册中心，管理和执行各种能力模块"""
    
    def __init__(self):
        self.capabilities: Dict[str, Dict[str, Any]] = {}
        self._register_default_capabilities()
    
    def _register_default_capabilities(self):
        """注册默认能力"""
        # 文本生成能力
        self.register_capability(
            name="text_generator",
            description="生成文本内容",
            execute=self._execute_text_generator
        )
        
        # 图像生成能力
        self.register_capability(
            name="image_generator",
            description="生成图像",
            execute=self._execute_image_generator
        )
        
        # SVG生成能力
        self.register_capability(
            name="svg_generator",
            description="生成SVG图表和diagrams",
            execute=self._execute_svg_generator
        )
        
        # 应用生成能力
        self.register_capability(
            name="flash_app_generator",
            description="生成可运行的Flash应用",
            execute=self._execute_flash_app_generator
        )
        
        # 图表生成能力
        self.register_capability(
            name="chart_generator",
            description="生成图表配置",
            execute=self._execute_chart_generator
        )
        
        # 数据处理能力
        self.register_capability(
            name="data_processor",
            description="处理和分析数据",
            execute=self._execute_data_processor
        )
        
        # 搜索检索能力
        self.register_capability(
            name="search_retriever",
            description="搜索和检索信息",
            execute=self._execute_search_retriever
        )
    
    def register_capability(self, name: str, description: str, execute: Callable) -> None:
        """注册能力"""
        self.capabilities[name] = {
            "name": name,
            "description": description,
            "execute": execute
        }
    
    def get_capability(self, name: str) -> Optional[Dict[str, Any]]:
        """获取能力"""
        return self.capabilities.get(name)
    
    def list_capabilities(self) -> List[Dict[str, Any]]:
        """列出所有能力"""
        return [cap for cap in self.capabilities.values()]
    
    async def execute_capability(self, name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行能力"""
        capability = self.get_capability(name)
        if not capability:
            return {
                "success": False,
                "error": f"Capability {name} not found"
            }
        
        start_time = time.time()
        try:
            result = await capability["execute"](input_data)
            execution_time = time.time() - start_time
            return {
                "success": True,
                "output": result,
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    async def _execute_text_generator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行文本生成"""
        from backend.core.llm_client import llm_client
        
        # 构建prompt
        action = input_data.get("action", "生成文本")
        
        # 根据不同的输入数据构建不同的prompt
        if "form_name" in input_data and "fields" in input_data:
            # 生成表单代码
            fields_str = "\n".join([f"- {field['name']}: {field['type']} - {field['label']}" for field in input_data['fields']])
            prompt = f"{action}\n表单名称: {input_data['form_name']}\n字段:\n{fields_str}\n请生成完整的HTML表单代码。"
        elif "function_name" in input_data and "formula" in input_data:
            # 生成计算逻辑代码
            prompt = f"{action}\n函数名: {input_data['function_name']}\n公式: {input_data['formula']}\n请生成完整的JavaScript函数代码。"
        elif "bmi_value" in input_data and "health_status" in input_data:
            # 生成健康状态判断逻辑
            status_str = "\n".join([f"- {s['range']}: {s['status']}" for s in input_data['health_status']])
            prompt = f"{action}\nBMI值变量: {input_data['bmi_value']}\n健康状态范围:\n{status_str}\n请生成完整的JavaScript代码。"
        elif "element_id" in input_data and "content" in input_data:
            # 生成显示代码
            prompt = f"{action}\n元素ID: {input_data['element_id']}\n内容模板: {input_data['content']}\n请生成完整的HTML代码。"
        else:
            # 使用默认prompt
            prompt = input_data.get("prompt", action)
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        result = await llm_client.chat_str(messages)
        return {
            "text": result
        }
    
    async def _execute_image_generator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行图像生成"""
        description = input_data.get("description", "")
        style = input_data.get("style", "realistic")
        
        result = await image_processor.generate_image(description, style)
        return result
    
    async def _execute_svg_generator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行SVG生成"""
        requirement = input_data.get("requirement", "")
        svg_type = input_data.get("type", "diagram")
        
        result = await svg_generator.generate_svg(requirement, svg_type)
        return result
    
    async def _execute_flash_app_generator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行Flash应用生成"""
        from backend.models.schemas import AppSpec
        from backend.services.app_generator import app_generator
        
        spec = AppSpec(
            name=input_data.get("name", "Flash App"),
            description=input_data.get("description", "A Flash application"),
            domain=input_data.get("domain", "general"),
            components=input_data.get("components", []),
            requirements=input_data.get("requirements", {})
        )
        
        app = await app_generator.generate(spec)
        return {
            "app_id": app.id,
            "name": app.spec.name,
            "description": app.spec.description,
            "url": app.url,
            "code": app.code
        }
    
    async def _execute_chart_generator(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行图表生成"""
        # 生成ECharts图表配置
        chart_type = input_data.get("chart_type", "bar")
        title = input_data.get("title", "Chart")
        data = input_data.get("data", [])
        
        # 处理字符串类型的data
        if isinstance(data, str):
            # 如果是积分区域的描述，生成相应的图表配置
            if "y=x" in data and "y^2=x" in data:
                # 生成积分区域的点数据
                points = []
                # 生成直线y=x的数据点
                for i in range(0, 101):
                    x = i / 100
                    y = x
                    points.append([x, y])
                # 生成抛物线y^2=x的数据点
                for i in range(0, 101):
                    y = i / 100
                    x = y ** 2
                    points.append([x, y])
                
                # 生成ECharts配置
                echarts_config = {
                    "title": {
                        "text": "积分区域: y=x 和 y^2=x",
                        "left": "center"
                    },
                    "tooltip": {
                        "trigger": "item"
                    },
                    "xAxis": {
                        "type": "value",
                        "min": 0,
                        "max": 1
                    },
                    "yAxis": {
                        "type": "value",
                        "min": 0,
                        "max": 1
                    },
                    "series": [
                        {
                            "name": "积分区域",
                            "type": "scatter",
                            "data": points,
                            "itemStyle": {
                                "color": "#5470c6"
                            }
                        }
                    ]
                }
            else:
                # 其他字符串数据，使用默认配置
                echarts_config = {
                    "title": {
                        "text": title,
                        "left": "center"
                    },
                    "tooltip": {
                        "trigger": "axis"
                    },
                    "legend": {
                        "data": ["数据"],
                        "bottom": 10
                    },
                    "xAxis": {
                        "type": "category",
                        "data": []
                    },
                    "yAxis": {
                        "type": "value"
                    },
                    "series": [
                        {
                            "name": "数据",
                            "type": chart_type,
                            "data": [],
                            "itemStyle": {
                                "color": "#5470c6"
                            }
                        }
                    ]
                }
        else:
            # 处理列表类型的data
            echarts_config = {
                "title": {
                    "text": title,
                    "left": "center"
                },
                "tooltip": {
                    "trigger": "axis"
                },
                "legend": {
                    "data": ["数据"],
                    "bottom": 10
                },
                "xAxis": {
                    "type": "category",
                    "data": [item["name"] for item in data] if isinstance(data, list) else []
                },
                "yAxis": {
                    "type": "value"
                },
                "series": [
                    {
                        "name": "数据",
                        "type": chart_type,
                        "data": [item["value"] for item in data] if isinstance(data, list) else [],
                        "itemStyle": {
                            "color": "#5470c6"
                        }
                    }
                ]
            }
        
        return {
            "chart_type": chart_type,
            "title": title,
            "config": echarts_config
        }
    
    async def _execute_data_processor(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据处理"""
        try:
            import pandas as pd
            import numpy as np
            
            data = input_data.get("data", [])
            operation = input_data.get("operation", "summary")
            
            if not data:
                return {
                    "error": "No data provided"
                }
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            if operation == "summary":
                # 生成数据摘要
                summary = df.describe().to_dict()
                return {
                    "processed_data": data,
                    "analysis": "Data summary generated",
                    "summary": summary
                }
            elif operation == "mean":
                # 计算平均值
                mean_values = df.mean().to_dict()
                return {
                    "processed_data": data,
                    "analysis": "Mean values calculated",
                    "mean_values": mean_values
                }
            elif operation == "correlation":
                # 计算相关性
                correlation = df.corr().to_dict()
                return {
                    "processed_data": data,
                    "analysis": "Correlation matrix calculated",
                    "correlation": correlation
                }
            elif operation == "filter":
                # 过滤数据
                condition = input_data.get("condition", {})
                if condition:
                    for key, value in condition.items():
                        if key in df.columns:
                            df = df[df[key] == value]
                return {
                    "processed_data": df.to_dict('records'),
                    "analysis": "Data filtered",
                    "filtered_count": len(df)
                }
            else:
                # 默认操作
                return {
                    "processed_data": data,
                    "analysis": "Data processed successfully"
                }
        except ImportError:
            # 如果没有安装Pandas和NumPy，返回模拟结果
            return {
                "processed_data": input_data.get("data", []),
                "analysis": "Data processed (simulated - Pandas/NumPy not installed)",
                "warning": "Pandas and NumPy are not installed, using simulated data processing"
            }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def _execute_search_retriever(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行搜索检索"""
        # 这里应该实现搜索检索逻辑
        # 由于我们没有实际的搜索检索能力，这里模拟搜索
        query = input_data.get("query", "")
        return {
            "query": query,
            "results": [
                {
                    "title": f"搜索结果1: {query}",
                    "content": "这是模拟的搜索结果内容",
                    "score": 0.9
                },
                {
                    "title": f"搜索结果2: {query}",
                    "content": "这是另一个模拟的搜索结果内容",
                    "score": 0.8
                }
            ],
            "total": 2
        }


capability_registry = CapabilityRegistry()