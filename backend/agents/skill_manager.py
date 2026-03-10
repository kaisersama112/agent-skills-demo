from typing import Dict, List, Optional
import os
import yaml
import re
from backend.agents.base_agent import BaseAgent
from backend.models.schemas import Task, AgentResult
from backend.core.llm_client import llm_client


class SkillAgent(BaseAgent):
    """基于Claude Skills格式的技能Agent"""
    def __init__(self, skill_name: str, skill_path: str):
        super().__init__(skill_name)
        self.skill_path = skill_path
        self.skill_config = self._load_skill_config()
        self.description = self.skill_config.get('description', '')
        self.capabilities = self.skill_config.get('capabilities', [])
        self.allowed_tools = self.skill_config.get('allowed-tools', [])
        self._instructions = None  # 延迟加载
    
    def _load_skill_config(self) -> Dict:
        """加载Skill的YAML配置"""
        skill_file = os.path.join(self.skill_path, 'SKILL.md')
        if not os.path.exists(skill_file):
            return {}
        
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取YAML Frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not yaml_match:
            return {}
        
        try:
            config = yaml.safe_load(yaml_match.group(1))
            return config if isinstance(config, dict) else {}
        except:
            return {}
    
    def _load_skill_instructions(self) -> str:
        """加载Skill的指令内容（按需加载）"""
        if self._instructions is None:
            skill_file = os.path.join(self.skill_path, 'SKILL.md')
            if not os.path.exists(skill_file):
                self._instructions = ''
                return self._instructions
            
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取Markdown指令部分
            instructions_match = re.search(r'^---\n.*?\n---\n(.*)$', content, re.DOTALL)
            if instructions_match:
                self._instructions = instructions_match.group(1).strip()
            else:
                self._instructions = ''
        return self._instructions
    
    @property
    def instructions(self) -> str:
        """获取技能指令（懒加载）"""
        return self._load_skill_instructions()
    
    def get_skill_content(self) -> str:
        """获取完整的技能内容"""
        return f"# Skill: {self.name}\n\n{self.instructions}"
    
    async def execute(self, task: Task) -> AgentResult:
        """执行技能任务"""
        requirement = task.input_data.get("message", task.input_data.get("requirement", ""))
        
        if not requirement:
            return AgentResult(
                agent=self.name,
                success=False,
                error="No requirement provided"
            )
        
        # 构建提示
        prompt = f"{self.instructions}\n\n用户需求: {requirement}"
        messages = [
            {"role": "system", "content": f"你是一个专业的{self.description}"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await llm_client.chat_str(messages)
            return AgentResult(
                agent=self.name,
                success=True,
                output={"result": result}
            )
        except Exception as e:
            return AgentResult(
                agent=self.name,
                success=False,
                error=str(e)
            )


class SkillManager:
    """技能管理器"""
    def __init__(self):
        # 使用绝对路径，确保从任何目录运行都能正确加载技能
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.skills_dirs = [
            os.path.join(current_dir, '../skills'),
        ]
        self.skills: Dict[str, SkillAgent] = {}
        self._load_skills()
        print(f"Loaded {len(self.skills)} skills from: {self.skills_dirs}")
    
    def _load_skills(self):
        """加载所有技能"""
        for skills_dir in self.skills_dirs:
            if os.path.exists(skills_dir):
                for skill_name in os.listdir(skills_dir):
                    skill_path = os.path.join(skills_dir, skill_name)
                    if os.path.isdir(skill_path) and os.path.exists(os.path.join(skill_path, 'SKILL.md')):
                        try:
                            skill_agent = SkillAgent(skill_name, skill_path)
                            self.skills[skill_name] = skill_agent
                        except Exception as e:
                            print(f"Failed to load skill {skill_name}: {e}")
    
    def get_skill(self, skill_name: str) -> Optional[SkillAgent]:
        """获取技能Agent"""
        return self.skills.get(skill_name)
    
    def get_skill_content(self, skill_name: str) -> str:
        """获取技能内容（按需加载）"""
        skill = self.get_skill(skill_name)
        if skill:
            return skill.get_skill_content()
        return f"Skill '{skill_name}' not found."
    
    def list_skills(self) -> List[Dict]:
        """列出所有技能"""
        return [
            {
                "name": name,
                "description": skill.description,
                "capabilities": skill.capabilities,
                "path": skill.skill_path
            }
            for name, skill in self.skills.items()
        ]
    
    def get_skill_descriptions(self) -> str:
        """获取技能描述列表，用于系统提示"""
        if not self.skills:
            return "No skills available."
        
        return "\n".join(
            f"- {name}: {skill.description}"
            for name, skill in self.skills.items()
        )
    
    def reload_skills(self):
        """重新加载技能"""
        self.skills.clear()
        self._load_skills()
        return len(self.skills)


# 全局技能管理器实例
skill_manager = SkillManager()
