from typing import Dict, List, Optional
from backend.agents.base_agent import BaseAgent
from backend.agents.implementations import (
    CodeAgent, UIAgent, ChartAgent, LogicAgent, DataAgent, VisionAgent
)
from backend.agents.skill_manager import skill_manager, SkillAgent
from backend.core.capability_registry import capability_registry
from backend.models.schemas import Plan, AgentResult, Task, TaskStatus
import asyncio
import time


class AgentOrchestrator:
    def __init__(self):
        self.registry: Dict[str, BaseAgent] = {
            "code_agent": CodeAgent(),
            "ui_agent": UIAgent(),
            "chart_agent": ChartAgent(),
            "logic_agent": LogicAgent(),
            "data_agent": DataAgent(),
            "vision_agent": VisionAgent(),
        }
        # 重新加载技能以读取最新的capabilities
        skill_manager.reload_skills()
    
    def register_agent(self, agent_name: str, agent: BaseAgent):
        """动态注册Agent"""
        self.registry[agent_name] = agent
    
    def unregister_agent(self, agent_name: str):
        """注销Agent"""
        if agent_name in self.registry:
            del self.registry[agent_name]
    
    def get_agent(self, agent_name: str) -> BaseAgent:
        """获取Agent，优先从注册列表获取，然后从技能管理获取"""
        # 1. 从注册列表获取
        if agent_name in self.registry:
            return self.registry[agent_name]
        
        # 2. 从技能管理获取
        skill_agent = skill_manager.get_skill(agent_name)
        if skill_agent:
            return skill_agent
        
        # 3. 返回默认Agent
        return self.registry["code_agent"]
    
    def list_agents(self) -> List[Dict]:
        """列出所有可用的Agent"""
        agents = []
        
        system_agent_info = {
            "code_agent": {
                "description": "代码生成助手，根据用户需求生成各种编程语言的代码，包括Python、JavaScript、TypeScript、Go、Java等",
                "capabilities": [
                    "生成Python代码（Flask、FastAPI、Django、PyTorch）",
                    "生成JavaScript/TypeScript代码（React、Vue、Node.js）",
                    "生成Go代码（Gin、Echo）",
                    "生成Java代码（Spring Boot）",
                    "提供完整的文件结构和最佳实践"
                ]
            },
            "ui_agent": {
                "description": "UI生成助手，根据需求生成美观、响应式的前端界面代码",
                "capabilities": [
                    "生成React/Vue/Angular组件",
                    "使用Tailwind CSS/Material UI进行样式设计",
                    "创建响应式布局，适配移动端和桌面端",
                    "实现表单、导航栏、卡片等常见UI组件",
                    "添加动画和交互效果"
                ]
            },
            "chart_agent": {
                "description": "图表生成助手，根据需求生成各类图表配置和数据可视化",
                "capabilities": [
                    "生成ECharts图表配置（柱状图、折线图、饼图等）",
                    "生成Chart.js图表配置",
                    "支持D3.js自定义可视化",
                    "提供示例数据和交互功能",
                    "实现响应式图表设计"
                ]
            },
            "logic_agent": {
                "description": "业务逻辑生成助手，根据需求生成清晰、高效的业务逻辑代码",
                "capabilities": [
                    "设计业务流程和函数逻辑",
                    "实现用户管理、订单处理等业务场景",
                    "编写输入验证和业务规则",
                    "提供完善的错误处理机制",
                    "生成测试用例和使用示例"
                ]
            },
            "data_agent": {
                "description": "数据处理助手，根据需求生成数据处理、清洗和分析逻辑",
                "capabilities": [
                    "使用Pandas/NumPy进行数据清洗和转换",
                    "编写SQL查询和数据聚合逻辑",
                    "实现数据验证和质量检查",
                    "进行描述性统计和相关性分析",
                    "提供特征工程和数据预处理方案"
                ]
            },
            "vision_agent": {
                "description": "图像处理助手，根据需求生成图像处理配置和计算机视觉方案",
                "capabilities": [
                    "目标检测（YOLO、Faster R-CNN）",
                    "图像分割（U-Net、Mask R-CNN）",
                    "图像生成（Stable Diffusion）",
                    "图像分类和识别",
                    "提供预处理和后处理步骤"
                ]
            }
        }
        
        for name, agent in self.registry.items():
            agent_info = system_agent_info.get(name, {
                "description": "System agent",
                "capabilities": ["执行系统任务"]
            })
            agents.append({
                "name": name,
                "type": "system",
                "description": agent_info["description"],
                "capabilities": agent_info["capabilities"]
            })
        
        for skill_info in skill_manager.list_skills():
            skill_name = skill_info["name"]
            # 使用从SKILL.md中读取的capabilities，如果没有则使用默认值
            capabilities = skill_info.get("capabilities", ["执行技能特定的任务"])
            # 如果capabilities为空，使用默认值
            if not capabilities:
                capabilities = ["执行技能特定的任务"]
            agents.append({
                "name": skill_name,
                "type": "skill",
                "description": skill_info["description"],
                "path": skill_info["path"],
                "capabilities": capabilities
            })
        
        return agents
    
    async def execute_plan(self, plan: Plan) -> List[AgentResult]:
        print(f"\n=== 执行计划开始 ===")
        print(f"计划包含任务数量: {len(plan.tasks)}")
        print(f"执行顺序: {plan.execution_order}")
        
        results = []
        
        for i, task_id in enumerate(plan.execution_order):
            task = next((t for t in plan.tasks if t.id == task_id), None)
            if not task:
                print(f"任务 {task_id} 未找到，跳过")
                continue
            
            print(f"\n执行任务{i+1}/{len(plan.execution_order)}: {task.id}")
            print(f"  Agent: {task.agent}")
            print(f"  Action: {task.action}")
            print(f"  输入数据: {task.input_data}")
            
            # 首先尝试从能力注册中心执行
            print("  尝试从能力注册中心执行...")
            capability_result = await capability_registry.execute_capability(task.agent, task.input_data)
            print(f"  能力注册中心执行结果: {capability_result}")
            
            if capability_result.get("success"):
                print("  能力注册中心执行成功")
                result = AgentResult(
                    agent=task.agent,
                    success=True,
                    output=capability_result.get("output"),
                    execution_time=capability_result.get("execution_time", 0.0)
                )
                results.append(result)
                print(f"  执行时间: {result.execution_time:.2f}秒")
            else:
                # 如果能力注册中心中没有该能力，尝试从Agent注册中心获取
                print("  能力注册中心执行失败，尝试从Agent注册中心获取")
                agent = self.get_agent(task.agent)
                print(f"  获取到Agent: {type(agent).__name__}")
                
                print("  执行Agent任务...")
                result = await agent.run(task)
                results.append(result)
                print(f"  Agent执行结果: 成功={result.success}")
                print(f"  执行时间: {result.execution_time:.2f}秒")
                if result.success:
                    print(f"  输出类型: {type(result.output).__name__}")
                    print(f"  输出内容: {result.output}")
        
        print(f"\n=== 执行计划完成 ===")
        print(f"执行结果数量: {len(results)}")
        for i, result in enumerate(results):
            print(f"结果{i+1}: Agent={result.agent}, 成功={result.success}, 执行时间={result.execution_time:.2f}秒")
        print(f"=== 执行计划完成 ===\n")
        
        return results
    
    async def execute_task(self, task: Task) -> AgentResult:
        # 首先尝试从能力注册中心执行
        capability_result = await capability_registry.execute_capability(task.agent, task.input_data)
        if capability_result.get("success"):
            return AgentResult(
                agent=task.agent,
                success=True,
                output=capability_result.get("output"),
                execution_time=capability_result.get("execution_time", 0.0)
            )
        
        # 如果能力注册中心中没有该能力，尝试从Agent注册中心获取
        agent = self.get_agent(task.agent)
        return await agent.run(task)
    
    async def execute_parallel(self, tasks: List[Task]) -> List[AgentResult]:
        coroutines = []
        for task in tasks:
            # 首先尝试从能力注册中心执行
            capability_result = await capability_registry.execute_capability(task.agent, task.input_data)
            if capability_result.get("success"):
                result = AgentResult(
                    agent=task.agent,
                    success=True,
                    output=capability_result.get("output"),
                    execution_time=capability_result.get("execution_time", 0.0)
                )
                coroutines.append(asyncio.sleep(0, result))  # 创建一个立即完成的coroutine
            else:
                # 如果能力注册中心中没有该能力，尝试从Agent注册中心获取
                agent = self.get_agent(task.agent)
                coroutines.append(agent.run(task))
        return await asyncio.gather(*coroutines)


agent_orchestrator = AgentOrchestrator()

