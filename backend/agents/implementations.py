from backend.agents.base_agent import BaseAgent
from backend.models.schemas import Task, AgentResult
from backend.core.llm_client import llm_client
import json


class CodeAgent(BaseAgent):
    def __init__(self):
        super().__init__("code_agent")
        self.prompt_template = """你是一个代码生成助手。请根据用户需求生成代码。

需求: {requirement}

可用技术栈:
- Python (Flask/FastAPI)
- JavaScript/TypeScript (React, Node.js)
- HTML/CSS

请返回以下格式的JSON:
{{
    "language": "编程语言",
    "framework": "框架",
    "code": "生成的代码",
    "files": [
        {{"name": "文件名", "content": "文件内容"}}
    ]
}}

只返回JSON，不要其他内容。"""

    async def execute(self, task: Task) -> AgentResult:
        requirement = task.input_data.get("message", task.input_data.get("requirement", ""))
        
        if not requirement:
            return AgentResult(
                agent=self.name,
                success=False,
                error="No requirement provided"
            )
        
        prompt = self.prompt_template.format(requirement=requirement)
        messages = [
            {"role": "system", "content": "你是一个专业的代码生成助手。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages)
            return AgentResult(
                agent=self.name,
                success=True,
                output=result
            )
        except Exception as e:
            return AgentResult(
                agent=self.name,
                success=False,
                error=str(e)
            )


class UIAgent(BaseAgent):
    def __init__(self):
        super().__init__("ui_agent")
        self.prompt_template = """你是一个UI生成助手。请根据需求生成前端界面代码。

需求: {requirement}

技术栈: React + Tailwind CSS

请返回以下格式的JSON:
{{
    "component": "React组件代码",
    "style": "CSS样式",
    "description": "组件说明"
}}

只返回JSON，不要其他内容。"""

    async def execute(self, task: Task) -> AgentResult:
        requirement = task.input_data.get("requirement", "")
        
        prompt = self.prompt_template.format(requirement=requirement)
        messages = [
            {"role": "system", "content": "你是一个专业的UI生成助手。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages)
            return AgentResult(
                agent=self.name,
                success=True,
                output=result
            )
        except Exception as e:
            return AgentResult(
                agent=self.name,
                success=False,
                error=str(e)
            )


class ChartAgent(BaseAgent):
    def __init__(self):
        super().__init__("chart_agent")
        self.prompt_template = """你是一个图表生成助手。请根据需求生成图表配置。

需求: {requirement}

技术栈: ECharts

请返回以下格式的JSON:
{{
    "chart_type": "图表类型(bar/line/pie等)",
    "options": {{ECharts配置}},
    "data": {{数据}}
}}

只返回JSON，不要其他内容。"""

    async def execute(self, task: Task) -> AgentResult:
        requirement = task.input_data.get("requirement", "")
        
        prompt = self.prompt_template.format(requirement=requirement)
        messages = [
            {"role": "system", "content": "你是一个专业的图表生成助手。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages)
            return AgentResult(
                agent=self.name,
                success=True,
                output=result
            )
        except Exception as e:
            return AgentResult(
                agent=self.name,
                success=False,
                error=str(e)
            )


class LogicAgent(BaseAgent):
    def __init__(self):
        super().__init__("logic_agent")
        self.prompt_template = """你是一个业务逻辑生成助手。请根据需求生成业务逻辑代码。

需求: {requirement}

请返回以下格式的JSON:
{{
    "logic": "业务逻辑描述",
    "functions": [
        {{"name": "函数名", "params": ["参数"], "body": "函数体"}}
    ],
    "validation": ["验证规则"]
}}

只返回JSON，不要其他内容。"""

    async def execute(self, task: Task) -> AgentResult:
        requirement = task.input_data.get("requirement", "")
        
        prompt = self.prompt_template.format(requirement=requirement)
        messages = [
            {"role": "system", "content": "你是一个专业的业务逻辑生成助手。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages)
            return AgentResult(
                agent=self.name,
                success=True,
                output=result
            )
        except Exception as e:
            return AgentResult(
                agent=self.name,
                success=False,
                error=str(e)
            )


class DataAgent(BaseAgent):
    def __init__(self):
        super().__init__("data_agent")
        self.prompt_template = """你是一个数据处理助手。请根据需求生成数据处理逻辑。

需求: {requirement}

请返回以下格式的JSON:
{{
    "data_structure": "数据结构描述",
    "processing": ["数据处理步骤"],
    "sample_data": [示例数据]
}}

只返回JSON，不要其他内容。"""

    async def execute(self, task: Task) -> AgentResult:
        requirement = task.input_data.get("requirement", "")
        
        prompt = self.prompt_template.format(requirement=requirement)
        messages = [
            {"role": "system", "content": "你是一个专业的数据处理助手。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages)
            return AgentResult(
                agent=self.name,
                success=True,
                output=result
            )
        except Exception as e:
            return AgentResult(
                agent=self.name,
                success=False,
                error=str(e)
            )


class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("vision_agent")
        self.prompt_template = """你是一个图像处理助手。请根据需求生成图像处理配置。

需求: {requirement}

请返回以下格式的JSON:
{{
    "task_type": "任务类型(classification/detection/generation等)",
    "model": "推荐模型",
    "preprocessing": ["预处理步骤"],
    "postprocessing": ["后处理步骤"]
}}

只返回JSON，不要其他内容。"""

    async def execute(self, task: Task) -> AgentResult:
        requirement = task.input_data.get("requirement", "")
        
        prompt = self.prompt_template.format(requirement=requirement)
        messages = [
            {"role": "system", "content": "你是一个专业的图像处理助手。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages)
            return AgentResult(
                agent=self.name,
                success=True,
                output=result
            )
        except Exception as e:
            return AgentResult(
                agent=self.name,
                success=False,
                error=str(e)
            )
