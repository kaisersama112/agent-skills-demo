from typing import Dict, Optional
from backend.core.llm_client import llm_client
from backend.core.task_planner import task_planner
from backend.services.sandbox import sandbox_executor
from backend.models.schemas import AppSpec, GeneratedApp, IntentResult
import json
import uuid


class AppGenerator:
    def __init__(self):
        self.ui_prompt = """你是一个React前端开发专家。请根据以下应用规格生成完整的React响应式应用代码。

应用规格:
- 名称: {name}
- 描述: {description}
- 领域: {domain}
- 组件: {components}

要求:
1. 使用 React + Tailwind CSS
2. 生成完整的组件代码
3. 包含必要的状态管理（useState）
4. 响应式设计 - 必须兼容不同屏幕大小：
   - 移动端优先设计（< 640px）
   - 平板适配（640px - 1024px）
   - 桌面端优化（> 1024px）
   - 使用Tailwind的响应式前缀：sm:, md:, lg:, xl:
   - 布局使用flexbox和grid，确保自适应
   - 字体大小使用相对单位（text-sm, text-base, text-lg, text-xl）
   - 间距使用响应式类（p-4, md:p-6, lg:p-8）
   - 图表和可视化组件需要自适应容器大小
5. 代码可以直接在浏览器中运行（使用CDN引入React和Tailwind）
6. 不要使用import语句，将所有代码放在一个HTML文件中
7. 包含交互元素（input、slider、button、dropdown等）
8. 实现参数变化时的实时响应
9. 使用ECharts或Chart.js实现数据可视化（确保图表响应式）
10. 确保代码结构清晰，包含App、ControlPanel、Visualization等组件
11. 正确处理初始状态，避免访问undefined的属性
12. 在useEffect中正确管理图表实例，避免内存泄漏

请返回以下格式的JSON:
{{
    "index.html": "完整的HTML文件，包含所有React代码和样式"
}}"""

        self.logic_prompt = """你是一个Python后端开发专家。请根据以下应用规格生成后端逻辑代码。

应用规格:
- 名称: {name}
- 描述: {description}
- 需求: {requirements}

要求:
1. 使用 FastAPI
2. 包含必要的API端点
3. 业务逻辑实现

请返回以下格式的JSON:
{{
    "main.py": "FastAPI主程序",
    "models.py": "数据模型",
    "utils.py": "工具函数"
}}"""

    async def generate(self, spec: AppSpec) -> GeneratedApp:
        app_id = str(uuid.uuid4())
        
        ui_code = await self._generate_ui(spec)
        # logic_code = await self._generate_logic(spec)
        print("ui_code:", ui_code)
        # print("logic_code:", logic_code)
        
        # 只使用index.html文件，因为它包含了所有代码
        code = ui_code
        
        # 部署应用到sandbox
        deployment_result = await sandbox_executor.run_app(app_id, code)
        
        return GeneratedApp(
            id=app_id,
            spec=spec,
            code=code,
            status=deployment_result.get("status", "generated"),
            url=deployment_result.get("static_url", f"/apps/{app_id}")
        )

    async def generate_from_intent(self, intent_result: IntentResult, user_message: str) -> GeneratedApp:
        spec = await task_planner.create_app_spec(user_message)
        return await self.generate(spec)

    async def _generate_ui(self, spec: AppSpec) -> Dict[str, str]:
        prompt = self.ui_prompt.format(
            name=spec.name,
            description=spec.description,
            domain=spec.domain,
            components=", ".join(spec.components)
        )
        
        messages = [
            {"role": "system", "content": "你是一个专业的React前端开发专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages, model_name="qwen3-coder-plus")
            return result
        except Exception as e:
            return {"error": str(e)}

    async def _generate_logic(self, spec: AppSpec) -> Dict[str, str]:
        prompt = self.logic_prompt.format(
            name=spec.name,
            description=spec.description,
            requirements=json.dumps(spec.requirements)
        )
        
        messages = [
            {"role": "system", "content": "你是一个专业的Python后端开发专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_json(messages)
            return result
        except Exception as e:
            return {"error": str(e)}


app_generator = AppGenerator()
