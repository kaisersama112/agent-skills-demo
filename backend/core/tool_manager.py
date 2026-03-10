from typing import Dict, Any, List
from backend.agents.skill_manager import skill_manager


class ToolManager:
    """工具管理器"""
    def __init__(self):
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "Skill",
                    "description": "Load a skill to get domain expertise.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill": {
                                "type": "string",
                                "description": "Name of the skill to load"
                            }
                        },
                        "required": ["skill"]
                    }
                }
            }
        ]
    
    def get_tools(self) -> List[Dict]:
        """获取工具列表"""
        return self.tools
    
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """执行工具"""
        if tool_name == "Skill":
            return self._execute_skill_tool(tool_args)
        return f"Unknown tool: {tool_name}"
    
    def _execute_skill_tool(self, args: Dict[str, Any]) -> str:
        """执行Skill工具"""
        skill_name = args.get("skill")
        if not skill_name:
            return "Error: No skill name provided"
        
        # 获取技能内容
        content = skill_manager.get_skill_content(skill_name)
        
        # 以tool_result形式返回，实现消息注入
        return f"""<skill-loaded name="{skill_name}">
{content}
</skill-loaded>

Follow the instructions in the skill above."""


# 全局工具管理器实例
tool_manager = ToolManager()
