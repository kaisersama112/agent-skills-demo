import os
import importlib
from typing import Dict, List, Optional
from capability_orchestration.base import AgentSkill


class SkillRegistry:
    """
    技能注册表，负责自动发现和导入技能模块
    """
    
    def __init__(self):
        self.skills: Dict[str, AgentSkill] = {}
    
    def discover_skills(self, skills_dir: str) -> List[AgentSkill]:
        """
        自动发现技能模块
        
        Args:
            skills_dir: 技能目录路径
            
        Returns:
            发现的技能列表
        """
        discovered_skills = []
        
        # 遍历技能目录下的子目录
        for skill_dir in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_dir)
            if os.path.isdir(skill_path):
                # 检查是否有__init__.py文件
                init_file = os.path.join(skill_path, "__init__.py")
                if os.path.exists(init_file):
                    # 导入模块
                    module_name = f"capability_orchestration.skills.{skill_dir}"
                    try:
                        module = importlib.import_module(module_name)
                        # 检查模块是否定义了skill对象
                        if hasattr(module, 'skill') and isinstance(module.skill, AgentSkill):
                            discovered_skills.append(module.skill)
                            print(f"发现技能: {module.skill.name}")
                        else:
                            print(f"模块 {module_name} 未定义有效的 skill 对象")
                    except Exception as e:
                        print(f"导入模块 {module_name} 失败: {str(e)}")
        
        return discovered_skills
    
    def register_skill(self, skill: AgentSkill):
        """
        注册技能
        
        Args:
            skill: 技能对象
        """
        self.skills[skill.name] = skill
        print(f"注册技能: {skill.name}")
    
    def register_all_skills(self, skills_dir: str):
        """
        注册所有发现的技能
        
        Args:
            skills_dir: 技能目录路径
        """
        skills = self.discover_skills(skills_dir)
        for skill in skills:
            self.register_skill(skill)
    
    def get_skill(self, skill_name: str) -> Optional[AgentSkill]:
        """
        获取技能
        
        Args:
            skill_name: 技能名称
            
        Returns:
            技能对象，如果不存在返回None
        """
        return self.skills.get(skill_name)
    
    def list_skills(self) -> List[Dict[str, str]]:
        """
        列出所有技能
        
        Returns:
            技能信息列表
        """
        return [
            {
                "name": skill.name,
                "description": skill.description
            }
            for skill in self.skills.values()
        ]
