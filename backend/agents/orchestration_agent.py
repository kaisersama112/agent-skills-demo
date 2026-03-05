from .base import Agent, AgentInput, AgentOutput
from capability_orchestration import skill_registry
from services.llm_service import llm_service


class OrchestrationAgent(Agent):
    """编排代理"""

    def __init__(self):
        super().__init__(
            name="orchestration_agent",
            description="协调多个技能的执行"
        )

    async def execute(self, input_data: dict) -> dict:
        """执行代理"""
        session_id = input_data.get("session_id")
        user_input = input_data.get("user_input")

        # 分析用户需求，生成任务计划
        task_plan = await self._generate_task_plan(user_input)

        # 执行任务计划
        results = []
        current_context = input_data.get("context", {})

        for task in task_plan:
            # 选择技能
            skill = skill_registry.get_skill(task["skill"])
            if not skill:
                continue

            # 执行技能
            skill_input = {
                "session_id": session_id,
                "user_input": task["input"],
                "context": current_context
            }

            result = await skill.run(skill_input)
            results.append({
                "task": task["task"],
                "skill": task["skill"],
                "result": result
            })

            # 更新上下文
            if result.get("success") and result.get("data"):
                current_context.update(result["data"])

        return {
            "task_plan": task_plan,
            "results": results,
            "final_context": current_context
        }

    async def _generate_task_plan(self, user_input: str) -> list:
        """生成任务计划"""
        prompt = f"""
请根据用户需求生成一个任务计划，包含需要执行的任务和对应的技能。

用户需求：{user_input}

可用技能：
{chr(10).join([f"- {s['name']}: {s['description']}" for s in skill_registry.list_skills()])}

任务计划格式：
[
    {{
        "task": "任务描述",
        "skill": "技能名称",
        "input": "技能输入"
    }},
    ...
]

请只返回任务计划的JSON格式，不要返回其他内容。
        """

        response = await llm_service.generate(prompt, temperature=0.0)

        # 解析JSON
        import json
        try:
            task_plan = json.loads(response)
            return task_plan
        except json.JSONDecodeError:
            # 如果解析失败，返回默认任务计划
            return [
                {
                    "task": "处理用户需求",
                    "skill": "chat",
                    "input": user_input
                }
            ]
