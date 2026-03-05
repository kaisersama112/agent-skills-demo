import os
import re
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from .base import Skill, SkillMetadata, InputField, OutputField, SkillResources

try:
    from backend.services.llm_service import LLMService
except ImportError:
    from services.llm_service import LLMService


class SkillMetadataParser:
    """SKILL.md元数据解析器"""

    @staticmethod
    def parse_file(skill_dir: str) -> Optional[SkillMetadata]:
        """从SKILL.md文件解析元数据"""
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md_path):
            return None

        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return SkillMetadataParser.parse_content(content)

    @staticmethod
    def parse_content(content: str) -> SkillMetadata:
        """解析SKILL.md内容"""
        parsed = SkillMetadataParser.parse_content_with_body(content)
        return parsed.metadata

    @staticmethod
    def parse_content_with_body(content: str) -> "ParsedSkillDocument":
        """解析SKILL.md中的YAML头和正文"""
        yaml_header = ""
        body = content

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) == 3:
                _, yaml_header, body = parts

        metadata_dict: Dict[str, str] = {}
        for line in yaml_header.splitlines():
            if ':' not in line:
                continue

            key, value = line.split(':', 1)
            metadata_dict[key.strip()] = value.strip().strip('"').strip("'")

        metadata = SkillMetadata(
            name=metadata_dict.get("name", "unknown"),
            description=metadata_dict.get("description", ""),
            version=metadata_dict.get("version", "1.0.0"),
            license=metadata_dict.get("license")
        )

        return ParsedSkillDocument(
            metadata=metadata,
            body=body.strip(),
            yaml_header=yaml_header.strip()
        )


@dataclass
class ParsedSkillDocument:
    metadata: SkillMetadata
    body: str
    yaml_header: str


class SkillRegistry:
    """技能注册表 - 通过SKILL.md自动发现技能"""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.skill_metadata: Dict[str, Dict] = {}
        self._skill_dirs: Dict[str, str] = {}
        self._skill_bodies: Dict[str, str] = {}

    def register_skill(self, skill: Skill):
        """注册技能（通过Python对象）"""
        self.skills[skill.name] = skill
        self.skill_metadata[skill.name] = skill.get_metadata().dict()
        print(f"注册技能: {skill.name} - {skill.description}")

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(skill_name)

    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有技能"""
        result = []
        for name, metadata in self.skill_metadata.items():
            skill_dir = self._skill_dirs.get(name)
            resources_info = self._get_resources_info(skill_dir) if skill_dir else {}

            result.append({
                "name": metadata.get("name", name),
                "description": metadata.get("description", ""),
                "version": metadata.get("version", "1.0.0"),
                "has_implementation": name in self.skills,
                "skill_dir": skill_dir,
                "resources": resources_info
            })
        return result

    def _get_resources_info(self, skill_dir: str) -> Dict[str, Any]:
        """获取技能资源信息"""
        if not skill_dir or not os.path.exists(skill_dir):
            return {}

        info = {}
        dirs = ["scripts", "templates", "resources", "examples", "assets", "references"]

        for dir_name in dirs:
            dir_path = os.path.join(skill_dir, dir_name)
            if os.path.exists(dir_path):
                files = []
                for root, _, filenames in os.walk(dir_path):
                    for f in filenames:
                        rel_path = os.path.relpath(os.path.join(root, f), dir_path)
                        files.append(rel_path)
                if files:
                    info[dir_name] = files

        return info

    def get_skill_metadata(self, skill_name: str) -> Optional[Dict]:
        """获取技能元数据"""
        return self.skill_metadata.get(skill_name)

    def list_all_metadata(self) -> List[Dict]:
        """列出所有技能元数据"""
        return list(self.skill_metadata.values())

    def discover_skills(self, skills_dir: str):
        """自动发现技能目录"""
        if not os.path.exists(skills_dir):
            print(f"技能目录不存在: {skills_dir}")
            return

        for item in os.listdir(skills_dir):
            skill_dir = os.path.join(skills_dir, item)

            if not os.path.isdir(skill_dir):
                continue

            skill_md_path = os.path.join(skill_dir, "SKILL.md")
            if not os.path.exists(skill_md_path):
                continue

            with open(skill_md_path, 'r', encoding='utf-8') as f:
                skill_content = f.read()

            parsed = SkillMetadataParser.parse_content_with_body(skill_content)
            metadata = parsed.metadata
            skill_name = metadata.name

            self.skill_metadata[skill_name] = metadata.dict()
            self._skill_dirs[skill_name] = skill_dir
            self._skill_bodies[skill_name] = self._build_full_skill_body(skill_dir, parsed.body)

    def _build_full_skill_body(self, skill_dir: str, skill_main_body: str) -> str:
        """构建Claude Skills风格的聚合上下文（SKILL.md + 其他.md）"""
        parts = [skill_main_body.strip()] if skill_main_body.strip() else []

        markdown_files = sorted(
            file_name
            for file_name in os.listdir(skill_dir)
            if file_name.endswith('.md') and file_name != 'SKILL.md'
        )

        for file_name in markdown_files:
            file_path = os.path.join(skill_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if not content:
                continue

            parts.append(f"## {file_name}\n{content}")

        return "\n\n".join(parts)

    def get_skill_prompt_context(self, skill_name: str) -> str:
        """获取用于Prompt注入的技能内容"""
        return self._skill_bodies.get(skill_name, "")

    def build_skills_prompt(self) -> str:
        """构建完整技能提示词（描述 + 聚合文档）"""
        sections: List[str] = []
        for skill_name, metadata in sorted(self.skill_metadata.items()):
            sections.append(
                "\n".join([
                    f"Skill: {metadata.get('name', skill_name)}",
                    f"Description: {metadata.get('description', '')}",
                    self.get_skill_prompt_context(skill_name)
                ]).strip()
            )

        return "You have access to the following skills:\n\n" + "\n\n".join(sections)

    def get_skill_resources(self, skill_name: str) -> Optional[SkillResources]:
        """获取技能资源"""
        skill_dir = self._skill_dirs.get(skill_name)
        if not skill_dir:
            return None

        return SkillResources(skill_dir)

    def discover_and_register_skills(self, skills_dir: Optional[str] = None):
        """自动发现并注册所有技能"""
        if skills_dir is None:
            skills_dir = os.path.join(os.path.dirname(__file__), "skills")

        self.discover_skills(skills_dir)

    def get_skill_by_intent(self, intent: str) -> Optional[Skill]:
        """根据意图获取技能（静态映射）"""
        intent_skill_map = {
            "sandbox_app": "sandbox_app",
            "chat": "chat",
            "document": "document",
            "algorithmic_art": "algorithmic-art",
            "canvas_design": "canvas-design",
            "docx": "docx",
            "pdf": "pdf",
            "pptx": "pptx",
            "xlsx": "xlsx",
            "theme": "theme-factory",
            "internal_comms": "internal-comms",
            "brand": "brand-guidelines"
        }

        skill_name = intent_skill_map.get(intent)
        return self.get_or_create_skill(skill_name)

    def get_or_create_skill(self, skill_name: str) -> Optional[Skill]:
        """获取或创建技能"""
        if not skill_name:
            return None

        # 检查是否已存在
        if skill_name in self.skills:
            return self.skills[skill_name]

        # 检查元数据是否存在
        if skill_name not in self.skill_metadata:
            return None

        # 创建新的技能实例
        metadata = self.skill_metadata[skill_name]
        skill_dir = self._skill_dirs.get(skill_name)

        skill = Skill(
            name=skill_name,
            description=metadata.get("description", ""),
            version=metadata.get("version", "1.0.0"),
            skill_dir=skill_dir
        )

        # 注册技能
        self.skills[skill_name] = skill
        print(f"创建技能: {skill_name}")

        return skill

    async def select_skill_by_llm(self, user_input: str) -> Optional[Skill]:
        """使用LLM进行意图识别并选择技能"""
        if not self.skill_metadata:
            return None

        skill_list = []
        for name, metadata in self.skill_metadata.items():
            skill_list.append({
                "name": metadata.get("name", name),
                "description": metadata.get("description", "")
            })

        skills_json = json.dumps(skill_list, ensure_ascii=False, indent=2)

        prompt = f"""
你是一个智能技能选择器。根据用户输入，从以下可用技能中选择最合适的一个。

可用技能列表：
{skills_json}

要求：
1. 分析用户输入的意图
2. 从可用技能中选择最匹配的技能
3. 如果没有匹配的技能，返回 "none"
4. 只返回技能名称（与列表中的name字段完全一致），不要返回其他内容

用户输入：{user_input}

请选择最合适的技能：
        """

        llm_service = LLMService()
        response = await llm_service.generate(prompt, temperature=0.0)
        selected_skill_name = response.strip()

        if selected_skill_name.lower() == "none":
            return None

        # 获取或创建技能
        return self.get_or_create_skill(selected_skill_name)
