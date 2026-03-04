from typing import Dict, List, Any, Optional, Callable
import json
import os
from capability_orchestration.base import AgentSkill, SkillInput, SkillOutput
from capability_orchestration.skills import SkillRegistry

class CapabilityOrchestrator:
    """
    能力编排器
    """
    
    def __init__(self):
        self.skill_registry = SkillRegistry()
        # 自动发现和注册技能
        skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        self.skill_registry.register_all_skills(skills_dir)
    
    def register_skill(self, skill: AgentSkill):
        """
        注册技能
        """
        self.skill_registry.register_skill(skill)
    
    def get_skill(self, skill_name: str) -> Optional[AgentSkill]:
        """
        获取技能
        """
        return self.skill_registry.get_skill(skill_name)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """
        列出所有技能
        """
        skills_info = []
        for skill_name, skill in self.skill_registry.skills.items():
            skills_info.append({
                "name": skill.name,
                "description": skill.description,
                "input_schema": skill.input_schema.__name__,
                "output_schema": skill.output_schema.__name__
            })
        return skills_info
    
    async def execute_skill(self, skill_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个技能
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return {
                "success": False,
                "message": f"技能 {skill_name} 不存在",
                "data": None
            }
        
        return await skill.run(input_data)
    
    async def orchestrate(self, task_plan: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        编排多个技能执行
        
        Args:
            task_plan: 任务计划
            context: 上下文信息
            
        Returns:
            编排执行结果
        """
        results = []
        current_context = context.copy()
        
        for task in task_plan:
            # 根据任务类型选择合适的技能
            skill_name = self._map_task_to_skill(task["task"])
            skill = self.get_skill(skill_name)
            if skill:
                # 准备技能输入数据
                input_data = self._prepare_skill_input(task, current_context, skill_name)
                # 执行技能
                result = await self.execute_skill(skill_name, input_data)
                results.append({
                    "task": task["task"],
                    "skill": skill_name,
                    "result": result
                })
                # 更新上下文
                if result.get("success") and result.get("data"):
                    current_context.update(result["data"])
            else:
                results.append({
                    "task": task["task"],
                    "skill": "unknown",
                    "result": {
                        "success": False,
                        "message": "没有找到合适的技能",
                        "data": None
                    }
                })
        
        return {
            "tasks": task_plan,
            "results": results,
            "final_context": current_context
        }
    
    def _map_task_to_skill(self, task: str) -> Optional[str]:
        """
        将任务映射到技能
        """
        # 任务到技能的映射，使用实际存在的技能
        task_skill_map = {
            "分析用户需求": "doc-coauthoring",  # 使用文档协作技能分析需求
            "设计解决方案": "frontend-design",  # 使用前端设计技能设计解决方案
            "实现核心功能": "web-artifacts-builder",  # 使用Web构件构建技能实现核心功能
            "测试与优化": "webapp-testing"  # 使用Web应用测试技能进行测试与优化
        }
        
        # 首先尝试精确匹配
        for key, value in task_skill_map.items():
            if key in task:
                return value
        
        # 然后尝试基于关键词的匹配
        task_lower = task.lower()
        
        # 技能关键词映射
        skill_keywords = {
            "algorithmic-art": ["art", "algorithm", "p5.js", "generative", "creative"],
            "canvas-design": ["canvas", "design", "draw", "graphics"],
            "doc-coauthoring": ["document", "coauthor", "collaborative", "write", "requirement"],
            "docx": ["docx", "word", "document"],
            "frontend-design": ["frontend", "web", "design", "ui", "ux", "solution"],
            "internal-comms": ["internal", "communication", "notification", "message"],
            "mcp-builder": ["mcp", "model", "context", "protocol"],
            "pdf": ["pdf", "document", "file"],
            "pptx": ["pptx", "powerpoint", "presentation"],
            "skill-creator": ["skill", "create", "develop"],
            "slack-gif-creator": ["slack", "gif", "animation"],
            "test-skill": ["test", "demo"],
            "theme-factory": ["theme", "style", "design"],
            "web-artifacts-builder": ["web", "artifact", "build", "implement", "core"],
            "webapp-testing": ["web", "app", "test", "testing", "optimize"],
            "xlsx": ["xlsx", "excel", "spreadsheet"]
        }
        
        # 找到最匹配的技能
        best_match = None
        best_score = 0
        
        for skill_name in skill_keywords:
            # 确保技能存在
            if skill_name not in self.skills:
                continue
            
            score = 0
            keywords = skill_keywords[skill_name]
            
            # 检查关键词匹配
            for keyword in keywords:
                if keyword in task_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = skill_name
        
        return best_match if best_score > 0 else None
    
    def _prepare_skill_input(self, task: Dict[str, Any], context: Dict[str, Any], skill_name: str) -> Dict[str, Any]:
        """
        准备技能输入数据
        """
        # 根据技能类型准备不同的输入参数
        if skill_name == "doc-coauthoring":
            # 文档协作技能需要的参数
            return {
                "doc_title": f"{task['task']} - 需求分析",
                "doc_content": f"# {task['task']}\n\n## 需求分析\n\n用户需求: {context.get('user_input', '')}\n\n## 任务描述\n\n{task['task']}",
                "collaborators": ["用户", "系统"]
            }
        elif skill_name == "frontend-design":
            # 前端设计技能需要的参数
            return {
                "design_type": "web",
                "requirements": {
                    "task": task['task'],
                    "user_input": context.get('user_input', '')
                },
                "output_format": "html"
            }
        elif skill_name == "web-artifacts-builder":
            # Web构件构建技能需要的参数
            return {
                "artifact_type": "web",
                "config": {
                    "task": task['task'],
                    "user_input": context.get('user_input', '')
                },
                "output_dir": "./output"
            }
        elif skill_name == "webapp-testing":
            # Web应用测试技能需要的参数
            return {
                "url": "http://localhost:8000",  # 模拟测试URL
                "test_cases": [
                    {
                        "id": "1",
                        "description": f"测试{task['task']}",
                        "steps": ["打开应用", "执行操作", "验证结果"]
                    }
                ],
                "browser": "chrome"
            }
        else:
            # 默认输入参数
            return {
                "task": task,
                "context": context
            }

# 初始化编排器
def create_orchestrator() -> CapabilityOrchestrator:
    return CapabilityOrchestrator()

# 示例用法
if __name__ == "__main__":
    import asyncio
    
    orchestrator = create_orchestrator()
    
    # 列出所有技能
    print("注册的技能:")
    for skill in orchestrator.list_skills():
        print(f"- {skill['name']}: {skill['description']}")
    
    # 执行单个技能
    async def test_skill():
        result = await orchestrator.execute_skill("checkin", {"item": "你好"})
        print("\n执行打卡技能结果:")
        print(result)
    
    asyncio.run(test_skill())