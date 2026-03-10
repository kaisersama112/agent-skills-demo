from typing import Dict, List, Optional
from backend.core.llm_client import llm_client
from backend.core.capability_registry import capability_registry
from backend.models.schemas import IntentResult, Plan, Task, AppSpec, TaskStatus
import json
import uuid


class TaskPlanner:
    def __init__(self):
        self.plan_prompt = """你是一个任务规划专家。请根据用户意图和需求生成详细的执行计划。

用户意图: {intent}
领域: {domain}
组件: {components}
用户需求: {user_message}

可用能力:
{capabilities}

请返回以下格式的JSON:
{{
    "tasks": [
        {{
            "id": "任务ID",
            "agent": "能力名称",
            "action": "执行动作",
            "input_data": {{"输入数据"}}
        }}
    ],
    "execution_order": ["任务ID列表"]
}}

只返回JSON，不要其他内容。"""

        self.app_spec_prompt = """你是一个应用规格生成助手。请根据用户需求生成应用规格说明。

用户需求: {user_message}

请返回以下格式的JSON:
{{
    "name": "应用名称",
    "description": "应用描述",
    "domain": "应用领域",
    "components": ["所需组件列表"],
    "requirements": {{
        "功能需求": "描述"
    }}
}}

只返回JSON，不要其他内容。"""

    async def create_plan(self, intent_result: IntentResult, user_message: str) -> Plan:
        print(f"\n=== 任务规划开始 ===")
        print(f"用户消息: {user_message}")
        print(f"意图结果: {intent_result}")
        
        # 获取可用能力
        print("获取可用能力...")
        capabilities = capability_registry.list_capabilities()
        print(f"可用能力数量: {len(capabilities)}")
        for i, cap in enumerate(capabilities):
            print(f"能力{i+1}: {cap['name']} - {cap['description']}")
        
        capabilities_str = "\n".join([f"- {cap['name']}: {cap['description']}" for cap in capabilities])
        
        prompt = self.plan_prompt.format(
            intent=intent_result.intent.value,
            domain=intent_result.domain or "general",
            components=", ".join(intent_result.components),
            user_message=user_message,
            capabilities=capabilities_str
        )
        print(f"生成的提示长度: {len(prompt)} 字符")
        
        messages = [
            {"role": "system", "content": "你是一个专业的任务规划专家。"},
            {"role": "user", "content": prompt}
        ]
        print(f"发送给LLM的消息结构: {messages}")
        
        try:
            print("调用LLM进行任务规划...")
            result = await llm_client.chat_json(messages)
            print(f"LLM返回结果: {result}")
            
            tasks = []
            task_data_list = result.get("tasks", [])
            print(f"LLM生成的任务数量: {len(task_data_list)}")
            
            for i, task_data in enumerate(task_data_list):
                task = Task(
                    id=task_data.get("id", str(uuid.uuid4())),
                    agent=task_data.get("agent", "text_generator"),
                    action=task_data.get("action", "execute"),
                    input_data=task_data.get("input_data", {}),
                    status=TaskStatus.PENDING
                )
                tasks.append(task)
                print(f"任务{i+1}: ID={task.id}, Agent={task.agent}, Action={task.action}")
                print(f"  输入数据: {task.input_data}")
            
            execution_order = result.get("execution_order", [t.id for t in tasks])
            print(f"执行顺序: {execution_order}")
            
            plan = Plan(
                tasks=tasks,
                execution_order=execution_order
            )
            print(f"任务规划成功: {plan}")
            print(f"=== 任务规划完成 ===\n")
            return plan
        except Exception as e:
            error_message = f"任务规划失败: {str(e)}"
            print(error_message)
            # 创建默认计划
            default_task = Task(
                id=str(uuid.uuid4()),
                agent="text_generator",
                action="execute",
                input_data={"prompt": user_message},
                status=TaskStatus.PENDING
            )
            default_plan = Plan(
                tasks=[default_task],
                execution_order=[default_task.id]
            )
            print(f"创建默认计划: {default_plan}")
            print(f"=== 任务规划完成 ===\n")
            return default_plan

    async def create_app_spec(self, user_message: str) -> AppSpec:
        prompt = self.app_spec_prompt.format(user_message=user_message)
        
        messages = [
            {"role": "system", "content": "你是一个专业的应用规格生成助手。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages)
            print("create_app_spec result:", result)
            return AppSpec(
                name=result.get("name", "Generated App"),
                description=result.get("description", ""),
                domain=result.get("domain", "general"),
                components=result.get("components", []),
                requirements=result.get("requirements", {})
            )
        except Exception as e:
            return AppSpec(
                name="Generated App",
                description=user_message,
                domain="general",
                components=[],
                requirements={}
            )


task_planner = TaskPlanner()
